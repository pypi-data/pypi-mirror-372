"""
Nakala User Info Client

Retrieves information about the connected user including personal data,
collections, datasets, and group permissions.
"""

import logging
import json
import argparse
import requests
from typing import Dict, Any, List
from datetime import datetime

# Import common utilities
from .common.config import NakalaConfig
from .common.exceptions import NakalaError, NakalaAPIError
from .common.utils import setup_common_logging, NakalaCommonUtils

logger = logging.getLogger(__name__)


class NakalaUserInfoClient:
    """Client for retrieving user information from Nakala API."""

    def __init__(self, config: NakalaConfig):
        self.config = config
        self.utils = NakalaCommonUtils()

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        try:
            url = f"{self.config.api_url}/users/me"
            headers = {"X-API-KEY": self.config.api_key}

            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            user_data = response.json()
            return {
                "id": user_data.get("userGroupId"),
                "username": user_data.get("username"),
                "email": user_data.get("mail"),
                "firstname": user_data.get("givenname"),
                "lastname": user_data.get("surname"),
                "fullname": user_data.get("fullname"),
                "roles": user_data.get("roles", []),
                "first_login": user_data.get("firstLogin"),
                "last_login": user_data.get("lastLogin"),
                "api_key": user_data.get("apiKey"),
            }
        except requests.exceptions.RequestException as e:
            raise NakalaAPIError(f"Failed to get user info: {e}")

    def get_user_collections(self, scope: str = "all") -> List[Dict[str, Any]]:
        """Get user collections with metadata."""
        try:
            url = f"{self.config.api_url}/users/collections/{scope}"
            headers = {
                "X-API-KEY": self.config.api_key,
                "Content-Type": "application/json",
            }
            query_body = {"page": 1, "limit": 1000}

            response = requests.post(
                url, headers=headers, json=query_body, timeout=self.config.timeout
            )
            response.raise_for_status()

            result = response.json()
            collections = []

            if "data" in result:
                for collection in result["data"]:
                    collections.append(
                        {
                            "id": collection.get("identifier"),
                            "title": self._extract_metadata_value(
                                collection.get("metas", []), "title"
                            ),
                            "description": self._extract_metadata_value(
                                collection.get("metas", []), "description"
                            ),
                            "status": collection.get("status", ""),
                            "created_date": collection.get("creDate", ""),
                            "updated_date": collection.get("modDate", ""),
                            "author": self._extract_metadata_value(
                                collection.get("metas", []), "creator"
                            ),
                            "data_count": collection.get("data_count", 0),
                        }
                    )

            return collections

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get user collections: {e}")
            return []

    def get_user_datasets(self, scope: str = "all") -> List[Dict[str, Any]]:
        """Get user datasets with metadata."""
        try:
            url = f"{self.config.api_url}/users/datas/{scope}"
            headers = {
                "X-API-KEY": self.config.api_key,
                "Content-Type": "application/json",
            }
            query_body = {"page": 1, "limit": 1000}

            response = requests.post(
                url, headers=headers, json=query_body, timeout=self.config.timeout
            )
            response.raise_for_status()

            result = response.json()
            datasets = []

            if "data" in result:
                for data in result["data"]:
                    datasets.append(
                        {
                            "id": data.get("identifier"),
                            "title": self._extract_metadata_value(
                                data.get("metas", []), "title"
                            ),
                            "description": self._extract_metadata_value(
                                data.get("metas", []), "description"
                            ),
                            "status": data.get("status", ""),
                            "created_date": data.get("creDate", ""),
                            "updated_date": data.get("modDate", ""),
                            "author": self._extract_metadata_value(
                                data.get("metas", []), "creator"
                            ),
                            "file_count": len(data.get("files", [])),
                            "data_type": self._extract_metadata_value(
                                data.get("metas", []), "type"
                            ),
                        }
                    )

            return datasets

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get user datasets: {e}")
            return []

    def _extract_metadata_value(
        self, metas: List[Dict], property_name: str, language: str = "fr"
    ) -> str:
        """Extract metadata value by property name and language."""
        if not metas:
            return ""

        # Look for the property with matching language first
        for meta in metas:
            property_uri = meta.get("propertyUri", "")
            meta_lang = meta.get("lang", "")

            if property_name in property_uri.lower() and meta_lang == language:
                return meta.get("value", "")

        # Fall back to any language for the property
        for meta in metas:
            property_uri = meta.get("propertyUri", "")
            if property_name in property_uri.lower():
                return meta.get("value", "")

        return ""

    def get_user_groups(self, scope: str = "all") -> List[Dict[str, Any]]:
        """Get user groups and permissions."""
        try:
            url = f"{self.config.api_url}/users/groups/{scope}"
            headers = {"X-API-KEY": self.config.api_key}

            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            result = response.json()
            groups = []

            if isinstance(result, list):
                for group in result:
                    groups.append(
                        {
                            "id": group.get("id"),
                            "name": group.get("name", ""),
                            "description": group.get("description", ""),
                            "type": group.get("type", ""),
                            "role": group.get("role", ""),
                            "member_count": group.get("member_count", 0),
                        }
                    )

            return groups

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get user groups: {e}")
            return []

    def get_complete_user_profile(self) -> Dict[str, Any]:
        """Get complete user profile including all information."""
        logger.info("Retrieving complete user profile...")

        profile = {
            "retrieved_at": datetime.now().isoformat(),
            "user_info": self.get_user_info(),
            "collections": self.get_user_collections(),
            "datasets": self.get_user_datasets(),
            "groups": self.get_user_groups(),
        }

        # Add summary statistics
        profile["summary"] = {
            "total_collections": len(profile["collections"]),
            "total_datasets": len(profile["datasets"]),
            "total_groups": len(profile["groups"]),
            "collections_by_status": self._count_by_status(profile["collections"]),
            "datasets_by_status": self._count_by_status(profile["datasets"]),
        }

        return profile

    def _count_by_status(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count items by status."""
        counts = {}
        for item in items:
            status = item.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        return counts

    def export_to_json(self, profile: Dict[str, Any], output_path: str):
        """Export user profile to JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"User profile exported to: {output_path}")
        except Exception as e:
            raise NakalaError(f"Failed to export profile: {e}")

    def print_summary(self, profile: Dict[str, Any]):
        """Print a summary of the user profile."""
        user_info = profile["user_info"]
        summary = profile["summary"]

        print("\n" + "=" * 60)
        print("NAKALA USER PROFILE SUMMARY")
        print("=" * 60)

        print("\nUser Information:")
        print(
            f"  Name: {user_info.get('firstname', '')} {user_info.get('lastname', '')}"
        )
        print(f"  Email: {user_info.get('email', '')}")
        print(f"  Institution: {user_info.get('institution', 'N/A')}")
        print(f"  User ID: {user_info.get('id', '')}")
        print(f"  Status: {user_info.get('status', '')}")

        print("\nResource Summary:")
        print(f"  Collections: {summary['total_collections']}")
        print(f"  Datasets: {summary['total_datasets']}")
        print(f"  Groups: {summary['total_groups']}")

        if summary["collections_by_status"]:
            print("\nCollections by Status:")
            for status, count in summary["collections_by_status"].items():
                print(f"  {status}: {count}")

        if summary["datasets_by_status"]:
            print("\nDatasets by Status:")
            for status, count in summary["datasets_by_status"].items():
                print(f"  {status}: {count}")

        print("\n" + "=" * 60)


def main():
    """
    Main entry point for o-nakala-user-info (v2.2.0).

    Examples:
        # Get user collections info (validated v2.2.0):
        o-nakala-user-info --api-key "33170cfe-f53c-550b-5fb6-4814ce981293" \\
            --collections-only

        # Results: Shows 207 collections in test environment
    """
    parser = argparse.ArgumentParser(
        description="Retrieve Nakala user information and export profile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get user info with summary
  python o-nakala-user-info.py

  # Export complete profile to JSON
  python o-nakala-user-info.py --output user_profile.json

  # Get only collections info
  python o-nakala-user-info.py --collections-only

  # Specify different API URL
  python o-nakala-user-info.py --api-url https://api.nakala.fr
        """,
    )

    parser.add_argument(
        "--api-key", help="Nakala API key (or set NAKALA_API_KEY environment variable)"
    )

    parser.add_argument(
        "--api-url",
        default="https://apitest.nakala.fr",
        help="Nakala API URL (default: test API)",
    )

    parser.add_argument(
        "--output", "-o", help="Output JSON file path for complete profile export"
    )

    parser.add_argument(
        "--collections-only",
        action="store_true",
        help="Only retrieve collections information",
    )

    parser.add_argument(
        "--datasets-only",
        action="store_true",
        help="Only retrieve datasets information",
    )

    parser.add_argument(
        "--groups-only", action="store_true", help="Only retrieve groups information"
    )

    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "owner", "contributor"],
        help="Scope for collections/datasets retrieval",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_common_logging(level=log_level)

    try:
        # Create configuration
        config = NakalaConfig(api_url=args.api_url, api_key=args.api_key)

        if not config.validate():
            logger.error("Configuration validation failed")
            return 1

        # Create client
        client = NakalaUserInfoClient(config)

        # Determine what to retrieve
        if args.collections_only:
            collections = client.get_user_collections(scope=args.scope)
            result = {"collections": collections}
            print(f"\nFound {len(collections)} collections")
            for col in collections:
                print(f"  - {col['title']} ({col['status']})")

        elif args.datasets_only:
            datasets = client.get_user_datasets(scope=args.scope)
            result = {"datasets": datasets}
            print(f"\nFound {len(datasets)} datasets")
            for ds in datasets:
                print(f"  - {ds['title']} ({ds['status']})")

        elif args.groups_only:
            groups = client.get_user_groups(scope=args.scope)
            result = {"groups": groups}
            print(f"\nFound {len(groups)} groups")
            for group in groups:
                print(f"  - {group['name']} ({group['role']})")

        else:
            # Get complete profile
            result = client.get_complete_user_profile()
            client.print_summary(result)

        # Export to file if requested
        if args.output:
            client.export_to_json(result, args.output)

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
