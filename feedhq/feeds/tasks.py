from django.conf import settings
from django.db import connection

from ..tasks import raven


@raven
def update_feed(feed_url, use_etags=True):
    from .models import UniqueFeed
    UniqueFeed.objects.update_feed(feed_url, use_etags)
    close_connection()


@raven
def read_later(entry_pk):
    from .models import Entry  # circular imports
    Entry.objects.get(pk=entry_pk).read_later()
    close_connection()


@raven
def update_unique_feed(feed_url):
    from .models import UniqueFeed, Feed
    feed, created = UniqueFeed.objects.get_or_create(
        url=feed_url,
        defaults={'subscribers': 1},
    )
    if not created:
        feed.subscribers = Feed.objects.filter(url=feed_url).count()
        feed.save()


def close_connection():
    """Close the connection only if not in eager mode"""
    if hasattr(settings, 'RQ'):
        if not settings.RQ.get('eager', True):
            connection.close()
