"""
Module for deleting all posts from X (formerly Twitter).
"""


import json

def delete_all_x_posts(api):
    """Delete all posts from the authenticated X account using the API."""
    posts = api.user_timeline(count=200, tweet_mode='extended')
    while posts:
        for post in posts:
            try:
                print(
                    f'Deleting post ID: {post.id} - '
                    f'{post.full_text}'
                )
                api.destroy_status(post.id)
            except Exception as err:  # pylint: disable=broad-exception-caught
                print(
                    f'Error deleting post ID {post.id}: {err}'
                )
        posts = api.user_timeline(count=200, tweet_mode='extended')

def delete_posts_from_json(json_path, x_api=None):
    """
    Delete posts from a JSON archive file using the API, 
    or print post IDs if no API is provided.
    """
    with open(json_path, encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        # X archive JSON may be a list or a dict with a 'posts' key
        posts = data.get('posts') if isinstance(data, dict) and 'posts' in data else data
        for post in posts:
            post_id = None
            # X archive formats may vary
            if isinstance(post, dict):
                post_id = post.get('id') or post.get('id_str')
                if not post_id and 'post' in post:
                    post_id = post['post'].get('id') or post['post'].get('id_str')
            if post_id and x_api:
                try:
                    print(f"Deleting post ID: {post_id}")
                    x_api.destroy_status(post_id)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    print(f"Error deleting post ID {post_id}: {err}")
            elif post_id:
                print(f"Post ID: {post_id}")
            else:
                print(f"Post ID not found in entry: {post}")
