import os
import json
from datetime import datetime
from atproto import Client

HANDLE = os.environ['BSKY_HANDLE']
PASSWORD = os.environ['BSKY_APP_PASSWORD']

client = Client()
client.login(HANDLE, PASSWORD)

# Load existing posts
try:
    with open('feed_data.json', 'r') as f:
        all_posts = json.load(f)
except:
    all_posts = []

existing_uris = {p['uri'] for p in all_posts}

# Fetch timeline
timeline = client.get_timeline(limit=100)
new_posts = []

for item in timeline.feed:
    post = item.post
    if post.uri in existing_uris:
        continue

    record = post.record
    
    # Get images if any
    images = []
    if hasattr(post, 'embed') and post.embed:
        embed = post.embed
        if hasattr(embed, 'images'):
            for img in embed.images:
                if hasattr(img, 'fullsize'):
                    images.append(img.fullsize)

    # Get video if any
    video_url = None
    if hasattr(post, 'embed') and post.embed:
        embed = post.embed
        if hasattr(embed, 'playlist'):
            video_url = embed.playlist

    new_posts.append({
        'uri': post.uri,
        'author_handle': post.author.handle,
        'author_name': post.author.display_name or post.author.handle,
        'author_avatar': post.author.avatar or '',
        'text': record.text if hasattr(record, 'text') else '',
        'images': images,
        'video_url': video_url,
        'created_at': record.created_at if hasattr(record, 'created_at') else '',
        'like_count': post.like_count or 0,
        'repost_count': post.repost_count or 0,
    })

# Merge and sort
all_posts = new_posts + all_posts
all_posts = all_posts[:5000]  # keep max 5000 posts

with open('feed_data.json', 'w') as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new posts. Total: {len(all_posts)}")
