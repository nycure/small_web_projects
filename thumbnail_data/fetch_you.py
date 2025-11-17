import requests
import os
import re
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm

API_KEY = 'YOUR_API_KEY_HERE'  # 🔴 Replace with your API key
BATCH_SIZE = 50  # max allowed by YouTube API

# --- Helper to extract video ID from URL ---
def extract_video_id(url):
    parsed = urlparse(url)
    if 'youtube' in parsed.netloc:
        qs = parse_qs(parsed.query)
        return qs.get('v', [None])[0]
    elif 'youtu.be' in parsed.netloc:
        return parsed.path.strip('/')
    return None

# --- Load video URLs and extract IDs ---
video_ids = []
with open("youtube_urls.txt") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        video_id = extract_video_id(line)
        if video_id:
            video_ids.append(video_id)

# --- Setup folders ---
os.makedirs("thumbnails", exist_ok=True)

# --- Batch processing ---
def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

for batch in tqdm(list(chunks(video_ids, BATCH_SIZE)), desc="Fetching video data"):
    ids = ",".join(batch)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={ids}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    for item in data.get('items', []):
        video_id = item['id']
        title = item['snippet']['title']
        thumbnail_url = item['snippet']['thumbnails']['high']['url']
        view_count = item['statistics'].get('viewCount', 'N/A')
        like_count = item['statistics'].get('likeCount', 'Hidden')

        # Download thumbnail
        thumb_data = requests.get(thumbnail_url).content
        with open(f"thumbnails/{video_id}.jpg", "wb") as f:
            f.write(thumb_data)

        # Save metadata
        with open("video_data.csv", "a", encoding="utf-8") as f:
            f.write(f'"{video_id}","{title}","{thumbnail_url}","{view_count}","{like_count}"\n')
