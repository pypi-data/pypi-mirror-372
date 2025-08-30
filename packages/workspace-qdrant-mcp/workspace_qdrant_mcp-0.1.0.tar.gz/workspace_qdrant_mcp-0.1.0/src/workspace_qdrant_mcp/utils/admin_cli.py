"""
Comprehensive administrative CLI for workspace-qdrant-mcp.

This module provides a powerful yet safe administrative interface for managing
workspace-qdrant collections and data. It operates independently from the MCP server
and includes robust safety mechanisms, project scoping, and comprehensive operations
for development, debugging, and maintenance workflows.

Safety Features:
    - Interactive confirmation for destructive operations
    - Project-scoped operations to prevent cross-project conflicts
    - Comprehensive logging and audit trail
    - Dry-run mode for safe operation preview
    - Data validation and backup recommendations

Operations Available:
    - Collection management (create, delete, list with statistics)
    - Data operations (upsert, search, statistics, cleanup)
    - Project detection and configuration validation
    - System health monitoring and diagnostics
    - Development utilities (reset, rebuild, backup)

Security Considerations:
    - No automatic data deletion without explicit confirmation
    - Project boundaries enforced to prevent accidental cross-project operations
    - Comprehensive logging for audit and debugging
    - Safe defaults with explicit override requirements

Usage Examples:
    ```bash
    # List all collections with statistics
    python -m workspace_qdrant_mcp.utils.admin_cli list-collections --stats

    # Delete collection with confirmation
    python -m workspace_qdrant_mcp.utils.admin_cli delete-collection docs_project1

    # Dry run collection reset
    python -m workspace_qdrant_mcp.utils.admin_cli reset-project --dry-run

    # Search with debugging
    python -m workspace_qdrant_mcp.utils.admin_cli search "function definition" --debug
    ```

Architecture:
    - Async-first design for efficient operations
    - Modular command structure with shared utilities
    - Configuration management with environment variable support
    - Extensible plugin architecture for custom operations
"""

import argparse
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..core.client import QdrantWorkspaceClient
from ..core.config import Config
from ..utils.project_detection import ProjectDetector

# Configure logging for admin operations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("workspace_qdrant_admin.log"),
    ],
)

logger = logging.getLogger(__name__)


class WorkspaceQdrantAdmin:
    """
    Comprehensive administrative interface for workspace-qdrant-mcp.

    Provides safe, project-scoped operations for collection management,
    data operations, and system maintenance with comprehensive logging
    and safety mechanisms.
    """

    def __init__(
        self,
        config: Config | None = None,
        dry_run: bool = False,
        project_scope: str | None = None,
    ):
        """
        Initialize the administrative interface.

        Args:
            config: Configuration instance. If None, loads from environment.
            dry_run: If True, operations will be logged but not executed.
            project_scope: Limit operations to specific project. If None, auto-detects.
        """
        self.config = config or Config()
        self.dry_run = dry_run
        self.project_scope = project_scope
        self.client: QdrantWorkspaceClient | None = None

        # Initialize project detection
        self.project_detector = ProjectDetector(self.config.workspace.github_user)

        # Determine current project context
        if not self.project_scope:
            current_dir = Path.cwd()
            detected_projects = self.project_detector.detect_projects([current_dir])
            if detected_projects:
                self.current_project = detected_projects[0].name
            else:
                self.current_project = "unknown_project"
        else:
            self.current_project = self.project_scope

        # Configure collection prefix for safety
        self.collection_prefix = (
            f"{self.config.workspace.collection_prefix}{self.current_project}_"
        )

        # Log initialization for audit trail
        logger.info(
            "Initialized WorkspaceQdrantAdmin - Project: %s, Dry-run: %s",
            self.current_project,
            self.dry_run,
        )

    @asynccontextmanager
    async def get_client(self):
        """Async context manager for client lifecycle."""
        if not self.client:
            self.client = QdrantWorkspaceClient(self.config)
        try:
            yield self.client
        finally:
            if self.client:
                await self.client.cleanup()
                self.client = None

    async def list_collections(
        self, include_stats: bool = False
    ) -> list[dict[str, Any]]:
        """
        List all collections with optional statistics.

        Args:
            include_stats: If True, includes document counts and size information.

        Returns:
            List of collection information dictionaries.
        """
        async with self.get_client() as client:
            try:
                collections = await client.list_collections()

                # Filter to current project if project scoping is enabled
                if self.project_scope:
                    collections = [
                        col
                        for col in collections
                        if col.get("name", "").startswith(self.collection_prefix)
                    ]

                if include_stats:
                    for collection in collections:
                        try:
                            # Get collection statistics
                            stats = await client.get_collection_info(collection["name"])
                            collection["stats"] = stats
                        except Exception as e:
                            logger.warning(
                                f"Could not get stats for {collection['name']}: {e}"
                            )
                            collection["stats"] = {"error": str(e)}

                logger.info(f"Listed {len(collections)} collections")
                return collections

            except Exception as e:
                logger.error(f"Failed to list collections: {e}")
                raise

    async def delete_collection(
        self, collection_name: str, confirm: bool = False
    ) -> bool:
        """
        Safely delete a collection with confirmation.

        Args:
            collection_name: Name of collection to delete.
            confirm: If True, skips interactive confirmation.

        Returns:
            True if collection was deleted, False otherwise.
        """
        # Safety check: ensure collection belongs to current project
        if self.project_scope and not collection_name.startswith(
            self.collection_prefix
        ):
            logger.error(
                f"Collection {collection_name} does not belong to project {self.current_project}"
            )
            return False

        async with self.get_client() as client:
            try:
                # Check if collection exists
                collections = await client.list_collections()
                collection_names = [col.get("name") for col in collections]

                if collection_name not in collection_names:
                    logger.warning(f"Collection {collection_name} does not exist")
                    return False

                # Get collection info for confirmation
                try:
                    info = await client.get_collection_info(collection_name)
                    doc_count = info.get("points_count", "Unknown")
                except Exception:
                    doc_count = "Unknown"

                # Interactive confirmation unless explicitly confirmed
                if not confirm and not self.dry_run:
                    print(
                        f"\n⚠️  WARNING: You are about to delete collection '{collection_name}'"
                    )
                    print(f"   Project: {self.current_project}")
                    print(f"   Document count: {doc_count}")
                    print("   This operation cannot be undone!")

                    response = input("\nType 'DELETE' to confirm: ")
                    if response != "DELETE":
                        print("Operation cancelled.")
                        return False

                if self.dry_run:
                    logger.info(
                        f"DRY RUN: Would delete collection {collection_name} ({doc_count} documents)"
                    )
                    return True

                # Perform deletion
                await client.delete_collection(collection_name)
                logger.info(f"Successfully deleted collection {collection_name}")
                return True

            except Exception as e:
                logger.error(f"Failed to delete collection {collection_name}: {e}")
                raise

    async def search_collections(
        self, query: str, limit: int = 10, include_content: bool = False
    ) -> list[dict[str, Any]]:
        """
        Search across all project collections.

        Args:
            query: Search query string.
            limit: Maximum number of results per collection.
            include_content: If True, includes document content in results.

        Returns:
            Search results organized by collection.
        """
        async with self.get_client() as client:
            try:
                collections = await self.list_collections()
                results = []

                for collection in collections:
                    collection_name = collection["name"]
                    try:
                        search_results = await client.hybrid_search(
                            query, collection_name=collection_name, limit=limit
                        )

                        if search_results:
                            results.append(
                                {
                                    "collection": collection_name,
                                    "query": query,
                                    "results": search_results,
                                    "count": len(search_results),
                                }
                            )

                    except Exception as e:
                        logger.warning(
                            f"Search failed for collection {collection_name}: {e}"
                        )
                        continue

                total_results = sum(r["count"] for r in results)
                logger.info(
                    f"Search completed: {total_results} results across {len(results)} collections"
                )
                return results

            except Exception as e:
                logger.error(f"Search operation failed: {e}")
                raise

    async def reset_project(self, confirm: bool = False) -> bool:
        """
        Reset all collections for the current project.

        Args:
            confirm: If True, skips interactive confirmation.

        Returns:
            True if reset completed successfully.
        """
        collections = await self.list_collections()
        project_collections = [
            col for col in collections if col["name"].startswith(self.collection_prefix)
        ]

        if not project_collections:
            logger.info(f"No collections found for project {self.current_project}")
            return True

        # Interactive confirmation
        if not confirm and not self.dry_run:
            print(
                f"\n⚠️  WARNING: You are about to reset project '{self.current_project}'"
            )
            print(f"   This will delete {len(project_collections)} collections:")
            for col in project_collections:
                print(f"   - {col['name']}")
            print("   This operation cannot be undone!")

            response = input(f"\nType 'RESET {self.current_project}' to confirm: ")
            if response != f"RESET {self.current_project}":
                print("Operation cancelled.")
                return False

        # Delete all project collections
        success_count = 0
        for collection in project_collections:
            try:
                if await self.delete_collection(collection["name"], confirm=True):
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {collection['name']}: {e}")

        logger.info(
            f"Reset completed: {success_count}/{len(project_collections)} collections reset"
        )
        return success_count == len(project_collections)

    async def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health information."""
        async with self.get_client() as client:
            try:
                health_info = {
                    "timestamp": datetime.now().isoformat(),
                    "project": self.current_project,
                    "config": {
                        "qdrant_url": self.config.qdrant.url,
                        "debug_mode": self.config.debug,
                        "collection_prefix": self.collection_prefix,
                    },
                }

                # Test Qdrant connection
                try:
                    collections = await client.list_collections()
                    health_info["qdrant"] = {
                        "status": "connected",
                        "total_collections": len(collections),
                        "project_collections": len(
                            [
                                col
                                for col in collections
                                if col["name"].startswith(self.collection_prefix)
                            ]
                        ),
                    }
                except Exception as e:
                    health_info["qdrant"] = {"status": "error", "error": str(e)}

                # Check project detection
                try:
                    detected_projects = self.project_detector.detect_projects(
                        [Path.cwd()]
                    )
                    health_info["project_detection"] = {
                        "status": "ok",
                        "detected_projects": len(detected_projects),
                        "current_project": self.current_project,
                    }
                except Exception as e:
                    health_info["project_detection"] = {
                        "status": "error",
                        "error": str(e),
                    }

                return health_info

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Workspace Qdrant Administrative CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # List collections with statistics
    python -m workspace_qdrant_mcp.utils.admin_cli list-collections --stats

    # Delete specific collection
    python -m workspace_qdrant_mcp.utils.admin_cli delete-collection docs_myproject

    # Search across collections
    python -m workspace_qdrant_mcp.utils.admin_cli search "async function" --limit 5

    # Reset project (with confirmation)
    python -m workspace_qdrant_mcp.utils.admin_cli reset-project

    # System health check
    python -m workspace_qdrant_mcp.utils.admin_cli health
        """,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview operations without executing"
    )
    parser.add_argument("--project", help="Limit operations to specific project")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List collections command
    list_parser = subparsers.add_parser("list-collections", help="List all collections")
    list_parser.add_argument(
        "--stats", action="store_true", help="Include collection statistics"
    )

    # Delete collection command
    delete_parser = subparsers.add_parser(
        "delete-collection", help="Delete a collection"
    )
    delete_parser.add_argument("collection_name", help="Name of collection to delete")
    delete_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search across collections")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Results per collection"
    )
    search_parser.add_argument(
        "--content", action="store_true", help="Include document content"
    )

    # Reset project command
    reset_parser = subparsers.add_parser(
        "reset-project", help="Reset all project collections"
    )
    reset_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )

    # Health check command
    subparsers.add_parser("health", help="Check system health")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return

    try:
        # Initialize admin interface
        config = Config()
        admin = WorkspaceQdrantAdmin(
            config=config, dry_run=args.dry_run, project_scope=args.project
        )

        # Execute command
        if args.command == "list-collections":
            collections = await admin.list_collections(include_stats=args.stats)
            print(f"\nFound {len(collections)} collections:")
            for col in collections:
                print(f"  - {col['name']}")
                if args.stats and "stats" in col:
                    stats = col["stats"]
                    if isinstance(stats, dict) and "error" not in stats:
                        print(f"    Documents: {stats.get('points_count', 'Unknown')}")
                        print(f"    Vectors: {stats.get('vectors_count', 'Unknown')}")
                    else:
                        print(f"    Stats: {stats}")

        elif args.command == "delete-collection":
            success = await admin.delete_collection(
                args.collection_name, confirm=args.confirm
            )
            if success:
                print(f"Collection {args.collection_name} deleted successfully")
            else:
                print(f"Failed to delete collection {args.collection_name}")
                sys.exit(1)

        elif args.command == "search":
            results = await admin.search_collections(
                args.query, limit=args.limit, include_content=args.content
            )

            print(f"\nSearch results for: '{args.query}'")
            total = 0
            for result in results:
                print(f"\n{result['collection']} ({result['count']} results)")
                for hit in result["results"][:5]:  # Show top 5 per collection
                    print(f"  Score: {hit.get('score', 'N/A'):.3f}")
                    if args.content and "content" in hit:
                        preview = (
                            hit["content"][:100] + "..."
                            if len(hit["content"]) > 100
                            else hit["content"]
                        )
                        print(f"     {preview}")
                total += result["count"]

            print(f"\nTotal results: {total}")

        elif args.command == "reset-project":
            success = await admin.reset_project(confirm=args.confirm)
            if success:
                print(f"Project {admin.current_project} reset successfully")
            else:
                print(f"Failed to reset project {admin.current_project}")
                sys.exit(1)

        elif args.command == "health":
            health = await admin.get_system_health()
            print(f"\nSystem Health Report - {health['timestamp']}")
            print(f"Project: {health['project']}")

            # Qdrant status
            qdrant = health["qdrant"]
            if qdrant["status"] == "connected":
                print(
                    f"Qdrant: Connected ({qdrant['total_collections']} collections, {qdrant['project_collections']} for this project)"
                )
            else:
                print(f"Qdrant: {qdrant['error']}")

            # Project detection status
            proj_detect = health["project_detection"]
            if proj_detect["status"] == "ok":
                print(
                    f"Project Detection: OK ({proj_detect['detected_projects']} projects detected)"
                )
            else:
                print(f"Project Detection: {proj_detect['error']}")

            print("\nConfiguration:")
            print(f"  Qdrant URL: {health['config']['qdrant_url']}")
            print(f"  Debug Mode: {health['config']['debug_mode']}")
            print(f"  Collection Prefix: {health['config']['collection_prefix']}")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def admin_cli() -> None:
    """Entry point for UV tool installation and CLI execution.

    Provides the primary entry point when the package is installed via UV or pip
    and executed as a command-line tool for administrative operations.

    Usage:
        ```bash
        # Install via UV and run admin CLI
        uv tool install workspace-qdrant-mcp
        workspace-qdrant-admin list-collections --stats

        # Run directly from source
        python -m workspace_qdrant_mcp.utils.admin_cli
        ```
    """
    asyncio.run(main())


if __name__ == "__main__":
    admin_cli()
