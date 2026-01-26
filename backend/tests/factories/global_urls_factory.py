"""Factory for creating GlobalUrls test data."""

from backend.app.db.models import GlobalUrls
from tests.factories.base import commit_and_refresh


def criar_global_url(db, empresa_id, url="https://example.com"):
    """Create a test global URL entry."""
    entry = GlobalUrls(
        empresa_id=empresa_id,
        url=url,
    )
    return commit_and_refresh(db, entry)
