"""
Unit tests for xcleaner.delete_all_x_posts.delete_posts_from_json function.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from xcleaner.delete_all_x_posts import delete_posts_from_json

def test_delete_posts_from_json_prints_ids(capsys):
    """Test delete_posts_from_json prints post IDs from a simulated JSON file."""
    # Simulate a JSON file with two posts
    import tempfile
    import json
    posts = [
        {"id": "123", "full_text": "foo"},
        {"id": "456", "full_text": "bar"}
    ]
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(posts, tmp)
        tmp.flush()
        delete_posts_from_json(tmp.name, x_api=None)
        captured = capsys.readouterr()
        assert "Post ID: 123" in captured.out
        assert "Post ID: 456" in captured.out
