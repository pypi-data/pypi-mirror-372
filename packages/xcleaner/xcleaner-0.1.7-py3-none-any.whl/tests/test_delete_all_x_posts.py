"""
Unit tests for xcleaner.delete_all_x_posts module.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from xcleaner.delete_all_x_posts import delete_all_x_posts

def test_delete_all_x_posts(monkeypatch):
    """Test delete_all_x_posts deletes all posts using a DummyAPI."""
    class DummyAPI:
        def __init__(self):
            self.deleted = []
            self._posts = [type('Post', (), {'id': 1, 'full_text': 'foo'}), type('Post', (), {'id': 2, 'full_text': 'bar'})]
        def user_timeline(self, *_args, **_kwargs):
            if self._posts:
                posts, self._posts = self._posts, []
                return posts
            return []
        def destroy_status(self, post_id):
            self.deleted.append(post_id)
    api = DummyAPI()
    delete_all_x_posts(api)
    assert api.deleted == [1, 2]
