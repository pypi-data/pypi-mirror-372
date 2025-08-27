# X Cleaner

Delete all posts from your X (formerly Twitter) account using a simple Python CLI.


## Project Structure

```
x-delete-posts/
├── xcleaner/
│   ├── __init__.py
│   ├── authenticate_x.py
│   ├── delete_all_x_posts.py
│   └── main.py
├── tests/
│   └── test_*.py
├── requirements.txt
├── setup.py
└── README.md
```


## Requirements

- Python 3.11 or newer
- An X (Twitter) Developer account and API keys

## Installation

Install from PyPI (recommended):

```sh
pip install xcleaner
```

Or install locally for development:

```sh
pip install .
```


## Usage

After installing, you can use the CLI tool:

```sh
xcleaner --api-key <your_key> --api-secret-key <your_secret> --access-token <your_token> --access-token-secret <your_token_secret>
```

Or set your credentials as environment variables and simply run:

```sh
xcleaner
```

Environment variables:

```sh
# On Windows (PowerShell)
$env:X_API_KEY="your_api_key"
$env:X_API_SECRET_KEY="your_api_secret_key"
$env:X_ACCESS_TOKEN="your_access_token"
$env:X_ACCESS_TOKEN_SECRET="your_access_token_secret"
xcleaner

# On macOS/Linux
export X_API_KEY="your_api_key"
export X_API_SECRET_KEY="your_api_secret_key"
export X_ACCESS_TOKEN="your_access_token"
export X_ACCESS_TOKEN_SECRET="your_access_token_secret"
xcleaner
```

You can also delete posts from a JSON archive:

```sh
xcleaner --json path/to/posts.json [--api-key ...]
```

**Warning:** This script will permanently delete all posts from your account. Use with caution!