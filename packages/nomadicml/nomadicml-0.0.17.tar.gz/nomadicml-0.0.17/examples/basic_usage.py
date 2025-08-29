"""
Basic usage examples for the NomadicML SDK.
"""

import os
import logging
from nomadicml import NomadicML

# Set up logging to see progress information
logging.basicConfig(level=logging.INFO)

# Get API key from environment variable or input
API_KEY = os.environ.get("NOMADICML_API_KEY") or input("Enter your NomadicML API key: ")

# Path to a video file for testing
VIDEO_PATH = os.environ.get("VIDEO_PATH") or input("Enter path to a video file: ")

# Initialize the client with your API key
# Add base_url for development use
# Change collection_name to "videos" for production use
client = NomadicML(api_key=API_KEY, collection_name="videos_dev")

def verify_authentication():
    """
    Verify that the API key is valid.
    """
    print("\n=== Verifying Authentication ===")
    try:
        # Verify authentication
        auth_info = client.verify_auth()
        print(f"Authentication successful: {auth_info}")
        return True
    except Exception as e:
        print(f"Authentication failed due to error: {e}")
        return False

def upload_video():
    """
    Upload a video file to the DriveMonitor API.
    """
    print("\n=== Uploading Video ===")
    try:
        # Upload the video
        result = client.video._upload_video(file_path=VIDEO_PATH)
        video_id = result["video_id"]
        print(f"Video uploaded successfully. ID: {video_id}")
        return video_id
    except Exception as e:
        print(f"Video upload failed: {e}")
        return None

def analyze_video(video_id):
    """
    Start analysis for the uploaded video.
    """
    print("\n=== Starting Video Analysis ===")
    try:
        # Start analysis
        result = client.video.analyze_video(video_id)
        print(f"Analysis started: {result}")
        return True
    except Exception as e:
        print(f"Failed to start analysis: {e}")
        return False

def check_status(video_id):
    """
    Check the status of the video analysis.
    """
    print("\n=== Checking Video Status ===")
    try:
        # Get the status
        status = client.video.get_video_status(video_id)
        print(f"Current status: {status}")
        return status
    except Exception as e:
        print(f"Failed to get status: {e}")
        return None

def wait_for_completion(video_id):
    """
    Wait for the video analysis to complete.
    """
    print("\n=== Waiting for Analysis to Complete ===")
    try:
        # Wait for completion with a shorter timeout for the example
        final_status = client.video.wait_for_analysis(video_id, timeout=180)
        print(f"Analysis completed: {final_status.get('status', 'Unknown')}")
        return True
    except Exception as e:
        print(f"Error waiting for completion: {e}")
        return False

def get_results(video_id):
    """
    Get the full analysis results.
    """
    print("\n=== Getting Analysis Results ===")
    try:
        # Get the analysis
        analysis = client.video.get_video_analysis(video_id)
        print(f"Analysis summary:")
        
        # Print metadata if available
        if "metadata" in analysis:
            metadata = analysis["metadata"]
            print(f"  Video: {metadata.get('filename', 'Unknown')}")
            if "duration" in metadata:
                print(f"  Duration: {metadata['duration']:.2f} seconds")
            if "width" in metadata and "height" in metadata:
                print(f"  Resolution: {metadata['width']}x{metadata['height']}")
        
        # Print events if available
        if "events" in analysis and analysis["events"]:
            print(f"\nDetected events ({len(analysis['events'])}):")
        else:
            print("\nNo events detected.")
            
        return analysis
    except Exception as e:
        print(f"Failed to get analysis results: {e}")
        return None

def upload_and_analyze_in_one_step(return_subset: bool = True):
    """
    Upload and analyze a video in one operation.
    """
    print("\n=== Upload and Analyze in One Step ===")
    try:
        # Upload and analyze with a shorter timeout for the example
        analysis = client.video.upload_and_analyze(
            file_path=VIDEO_PATH,
            timeout=180,
            return_subset=return_subset
        )
        print(f"Upload and analysis completed successfully.")
        
        # Print a summary of the results
        if hasattr(analysis, 'visual_analysis') and analysis.visual_analysis and hasattr(analysis.visual_analysis, 'events') and analysis.visual_analysis.events:
            print(f"\nDetected {len(analysis.visual_analysis.events)} events.")
        elif isinstance(analysis, dict) and "events" in analysis and analysis["events"]: # Keep compatibility if return_subset=False
            print(f"\nDetected {len(analysis['events'])} events.")
        else:
            print("\nNo events detected.")
            
        return analysis
    except Exception as e:
        print(f"Upload and analyze failed: {e}")
        return None

def main():
    """
    Run the examples.
    """
    print("=== NomadicML SDK Basic Usage Example ===")
    
    # Verify authentication
    if not verify_authentication():
        print("Exiting due to authentication failure.")
        return
    
    # Ask which example to run
    print("\nChoose an example to run:")
    print("1. Step-by-step (upload, analyze, get results)")
    print("2. All-in-one (upload and analyze in one step)")
    print("3. Only upload video")
    print("4. Only analyze video")
    
    choice = input("Enter your choice (1, 2, 3 or 4): ").strip()
    
    if choice == "1":
        # Step-by-step example
        video_id = upload_video()
        if not video_id:
            print("Exiting due to upload failure.")
            return
            
        if not analyze_video(video_id):
            print("Exiting due to analysis startup failure.")
            return
            
        status = check_status(video_id)
        if not status:
            print("Exiting due to status check failure.")
            return
            
        if not wait_for_completion(video_id):
            print("Exiting due to timeout or error while waiting for completion.")
            return
            
        results = get_results(video_id)
        if not results:
            print("Exiting due to failure getting results.")
            return
    
    elif choice == "2":
        # All-in-one example
        results = upload_and_analyze_in_one_step()
        if not results:
            print("Exiting due to upload and analyze failure.")
            return
    elif choice == "3":
        # Only upload video
        print("\n=== Only Uploading Video ===")
        video_id = upload_video()
        if not video_id:
            print("Exiting due to upload failure.")
            return
    elif choice == "4":
        # Only analyze video
        print("\n=== Only Analyzing Video ===")
        video_id = input("Enter the video ID to analyze: ")
        if not analyze_video(video_id):
            print("Exiting due to analysis startup failure.")
            return
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\n=== Example Completed Successfully ===")

if __name__ == "__main__":
    main()
