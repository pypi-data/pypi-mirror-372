
"""
X_Cleaner: Delete all posts from your X (formerly Twitter) account.

Instructions:
1. Set your X API credentials as environment variables or pass them as command line arguments.
2. Run the script using Python: python main.py
Note: Be cautious as this will permanently delete all your posts.
Example using environment variables in Windows PowerShell:
    $env:X_API_KEY="your_api_key"
    $env:X_API_SECRET_KEY="your_api_secret_key"
    $env:X_ACCESS_TOKEN="your_access_token"
    $env:X_ACCESS_TOKEN_SECRET="your_access_token_secret"
    python main.py

Example using command line arguments:
    python main.py \
        --api-key your_api_key \
        --api-secret-key your_api_secret_key \
        --access-token your_access_token \
        --access-token-secret your_access_token_secret
"""

import os
import sys
import argparse
from .authenticate_x import authenticate_x
from .delete_all_x_posts import delete_all_x_posts, delete_posts_from_json


def get_args():
    """Parse command line arguments for X API credentials and JSON file."""
    parser = argparse.ArgumentParser(
        description="Delete all posts from your X (formerly Twitter) account."
    )
    parser.add_argument('--api-key', help='X API Key')
    parser.add_argument('--api-secret-key', help='X API Secret Key')
    parser.add_argument('--access-token', help='X Access Token')
    parser.add_argument('--access-token-secret', help='X Access Token Secret')
    parser.add_argument('--json', help='Path to X archive JSON file (post.js or posts.json)')
    return parser.parse_args()

def get_x_credentials(parsed_args):
    """Get X API credentials from arguments or environment variables."""
    api_key = parsed_args.api_key or os.getenv('X_API_KEY')
    api_secret_key = parsed_args.api_secret_key or os.getenv('X_API_SECRET_KEY')
    access_token = parsed_args.access_token or os.getenv('X_ACCESS_TOKEN')
    access_token_secret = parsed_args.access_token_secret or os.getenv('X_ACCESS_TOKEN_SECRET')
    # Validate that none are null or empty
    if not all([api_key, api_secret_key, access_token, access_token_secret]):
        print(
            "Error: All X API credentials must be provided via environment variables "
            "or command line arguments."
        )
        sys.exit(1)
    return api_key, api_secret_key, access_token, access_token_secret



def main():
    """Main entry point for deleting X posts via API or JSON archive."""
    parsed_args = get_args()
    if parsed_args.json:
        # Use API credentials if provided, otherwise just print post IDs
        if any([
            parsed_args.api_key, parsed_args.api_secret_key,
            parsed_args.access_token, parsed_args.access_token_secret
        ]) or all([
            os.getenv('X_API_KEY'), os.getenv('X_API_SECRET_KEY'),
            os.getenv('X_ACCESS_TOKEN'), os.getenv('X_ACCESS_TOKEN_SECRET')
        ]):
            api_key, api_secret_key, access_token, access_token_secret = \
                get_x_credentials(parsed_args)
            x_api = authenticate_x(
                api_key, api_secret_key, access_token, access_token_secret
            )
            delete_posts_from_json(
                parsed_args.json,
                x_api
            )
        else:
            print(
                "No API credentials provided. "
                "Listing post IDs from JSON:"
            )
            delete_posts_from_json(parsed_args.json, x_api=None)
    else:
        api_key, api_secret_key, access_token, access_token_secret = get_x_credentials(parsed_args)
        x_api = authenticate_x(
            api_key, api_secret_key, access_token, access_token_secret
        )
        delete_all_x_posts(x_api)


if __name__ == "__main__":
    main()
