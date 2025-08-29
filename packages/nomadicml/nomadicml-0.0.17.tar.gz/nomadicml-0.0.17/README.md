# NomadicML Python SDK

A Python client library for the NomadicML DriveMonitor API, allowing you to upload and analyze driving videos programmatically.

## Installation

### From PyPI (for users)

```bash
pip install nomadicml
```

### For Development (from source)

To install the package in development mode, where changes to the code will be immediately reflected without reinstallation:

```bash
# Clone the repository
git clone https://github.com/nomadic-ml/drivemonitor.git
cd sdk

# For development: Install in editable mode
pip install -e .
```

With this installation, any changes you make to the code will be immediately available when you import the package.

## Quick Start

```python
from nomadicml import NomadicML

# Initialize the client with your API key
client = NomadicML(api_key="your_api_key")

# Upload a video and analyze it in one step
result = client.video.upload_and_analyze("path/to/your/video.mp4")

# Print the detected events
for event in result["events"]:
    print(f"Event: {event['type']} at {event['time']}s - {event['description']}")
#For a batch upload

videos_list = [.....]#list of video paths
batch_results = client.video.upload_and_analyze_videos(videos_list, wait_for_completion=False)

    
video_ids = [
    res.get("video_id")
    for res in batch_results
    if res                                         # safety for None
    ]

    
full_results = client.video.wait_for_analyses(video_ids)

```

## Authentication

You need an API key to use the NomadicML API. You can get one by:

1. Log in to your DriveMonitor account
2. Go to Profile > API Key
3. Generate a new API key

Then use this key when initializing the client:

```python
client = NomadicML(api_key="your_api_key")
```

## Video Upload and Analysis

### Upload a video

```python
# Upload a local video file
result = client.video.upload_video(
    source="file",
    file_path="path/to/video.mp4"
)

# Or upload from YouTube
result = client.video.upload_video(
    source="youtube",
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID"
)

# Get the video ID from the response
video_id = result["video_id"]
```

### Analyze a video

```python
# Start analysis
client.video.analyze_video(video_id)

# Wait for analysis to complete
status = client.video.wait_for_analysis(video_id)

# Get analysis results
analysis = client.video.get_video_analysis(video_id)

# Get detected events
events = client.video.get_video_events(video_id)
```

### Upload and analyze in one step

```python
# Upload and analyze a video, waiting for results
analysis = client.video.upload_and_analyze("path/to/video.mp4")

# Or just start the process without waiting
result = client.video.upload_and_analyze("path/to/video.mp4", wait_for_completion=False)
```

## Advanced Usage

### Filter events by severity or type

```python
# Get only high severity events
high_severity_events = client.video.get_video_events(
    video_id=video_id,
    severity="high"
)

# Get only traffic violation events
traffic_violations = client.video.get_video_events(
    video_id=video_id,
    event_type="Traffic Violation"
)
```

### Custom timeout and polling interval

```python
# Wait for analysis with a custom timeout and polling interval
client.video.wait_for_analysis(
    video_id=video_id,
    timeout=1200,  # 20 minutes
    poll_interval=10  # Check every 10 seconds
)
```

### Custom API endpoint

If you're using a custom deployment of the DriveMonitor backend:

```python
# Connect to a local or custom deployment
client = NomadicML(
    api_key="your_api_key",
    base_url="http://localhost:8099"
)
```

### Search across videos

Run a semantic search on several of your videos at once:

```python
results = client.video.search_videos(
    "red pickup truck overtaking",
    ["vid123", "vid456"]
)
for match in results["matches"]:
    print(match["videoId"], match["eventIndex"], match["similarity"])
```

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from nomadicml import NomadicMLError, AuthenticationError, VideoUploadError

try:
    client.video.upload_and_analyze("path/to/video.mp4")
except AuthenticationError:
    print("API key is invalid or expired")
except VideoUploadError as e:
    print(f"Failed to upload video: {e}")
except NomadicMLError as e:
    print(f"An error occurred: {e}")
```

## Development

### Setup

Clone the repository and install development dependencies:

```bash
git clone https://github.com/nomadicml/nomadicml-python.git
cd nomadicml-python
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

## License

MIT License. See LICENSE file for details.
