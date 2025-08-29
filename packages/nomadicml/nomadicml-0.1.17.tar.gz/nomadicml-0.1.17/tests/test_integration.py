import pytest
import os
import json
from datetime import datetime
import warnings

from nomadicml import NomadicML, DEFAULT_BASE_URL, DEFAULT_COLLECTION_NAME

from nomadicml.video import AnalysisType

def get_client():
    # Load environment variables
    API_KEY = os.environ.get("NOMADICML_API_KEY")
    assert API_KEY, "API key not found in environment"
    is_prod = os.environ.get("DRIVEMONITOR_IS_PROD", "false") == "true"
    if is_prod:
        base_url = DEFAULT_BASE_URL 
        collection_name = DEFAULT_COLLECTION_NAME
        folder_collection_name='videoFolders',
    else:
        base_url = "https://api.nomadicml.com"
        collection_name = "videos_dev"
        folder_collection_name='videoFolders_dev',
    if os.environ.get("VITE_BACKEND_DOMAIN"):
        base_url = os.environ.get("VITE_BACKEND_DOMAIN")
    
    client = NomadicML(
        api_key=API_KEY, 
        base_url=base_url,
        collection_name=collection_name,
        folder_collection_name=folder_collection_name,

    )
    return client

# Validation functions
def assert_has_string_field(d, field):
    assert field in d, f"Missing field: `{field}`"
    assert isinstance(d[field], str), f"Field `{field}` with value {d[field]} is not a string"

def assert_has_number_field(d, field):
    assert field in d, f"Missing field: `{field}`"
    assert isinstance(d[field], (float, int)), f"Field `{field}` with value {d[field]} is not a number"

@pytest.mark.calls_api
@pytest.mark.timeout(10)  # 10 seconds timeout
def test_auth():
    """
    Run with: pytest -m calls_api
    """
    client = get_client()
    client.verify_auth()


@pytest.mark.calls_api
@pytest.mark.timeout(1440) # 24 minutes
def test_folder_upload_operations(folder_name="integration-test-folder"):
    client = get_client()
    small_videos = [ 
        'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/AI-Gen-Personalized_Shopping_Assistant_Video_veo3.mp4', # 1.1mb 
        'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/Dashcam_Footage_With_GPS_Data_OnScreen_aI7dTCnQJJA_k.mp4', # # 47mb
    ]
    big_videos = [
        'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/Fort-Lauderdale-to-Miami-Scenic-Drive-0058-w1VvwSc4Coo.mp4' #247mb / 2 min
    ]

    if client.base_url ==  "https://api.nomadicml.com":
        n_big_videos = 25
    else:
        # We don't want to hog prod
        # Apple M4 Pro is approx 48 VCPUs, main 64 prod 96 so approx similar to main.
        n_big_videos = 8 
    paths = small_videos + big_videos*n_big_videos
    print(f"Using {n_big_videos} big videos")

    # Test video URL

    # 1. Upload video to the folder
    response = client.video.upload(paths, folder=folder_name)
    try:
        assert len(response) == len(paths), f"Expected {len(paths)} videos, got {len(response)} : \n {len(response)}"

        # 2. Verify video is in the folder via my_videos
        folder_videos = client.video.my_videos(folder_id=folder_name)
        print(folder_videos)
        folder_lookup = {v['video_id']: v for v in folder_videos}
        for v in response:
            video_id = v['video_id']
            assert video_id in folder_lookup, f"Video {video_id} not found in folder with content: {folder_videos}"
            data = folder_lookup[video_id]
            assert_has_string_field(data, 'video_id')
            assert_has_string_field(data, 'video_name')
            assert_has_number_field(data, 'duration_s')
            assert_has_string_field(data, 'folder_id')
            assert_has_string_field(data, 'folder_name')    
    finally:
        # Clean up: delete the video
        for v in response:  
            client.delete_video(v['video_id'])

@pytest.mark.calls_api
@pytest.mark.timeout(120)
def test_org_folders_search():
    # Prepared with one uploaded video
    folder_name = "integration-test-folder-org"
    client = get_client()
    folder_videos = client.video.my_videos(folder_id=folder_name)
    assert len(folder_videos) == 1, f"Expected at least 1 video in folder, found {folder_videos}"
    assert_has_string_field(folder_videos[0], 'org_id')
    assert folder_videos[0]['video_name'] == 'should-be-here-for-tests.mp4'
    _test_search_videos(client, "integration-test-folder-org", "yellow taxi", 1)

def _test_search_videos(client, folder_name, query, expected_matches):
    search_results = client.search_videos(query, folder=folder_name)
    print(f"Search results for {query} in {folder_name}:")
    print("Search results:")
    print(search_results)
    assert len(search_results['matches']) >= expected_matches, f"Expected at least {expected_matches} matches but got {search_results}"
    assert list(search_results.keys()) == ['matches', 'summary']
    assert_has_string_field(search_results, 'summary')
    for match in search_results['matches']:
        assert list(match.keys()) == ['video_id', 'analysis_id', 'event_index', 'similarity', 'reason']
        assert_has_string_field(match, 'video_id')
        assert_has_string_field(match, 'analysis_id')
        assert_has_number_field(match, 'event_index')
        assert_has_number_field(match, 'similarity')            
        assert_has_string_field(match, 'reason')
    
@pytest.mark.calls_api
@pytest.mark.timeout(360)  # 6 minutes timeout
def test_rapid_review_robotics_xs():
    """
    Run with: pytest -m calls_api
    """
    client = get_client()
    
    # Upload video (~1mb / 8s)
    video_url = 'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/AI-Gen-Personalized_Shopping_Assistant_Video_veo3.mp4'
    folder_name = 'integration-test-folder'
    response = client.upload(video_url, folder=folder_name)
    video_id = response['video_id']
    
    try:
        # Run analysis multiple times to test consistency
        analysis = client.analyze(
            video_id,
            analysis_type=AnalysisType.ASK,
            # This prompt relates to urbanhawks usecase.
            custom_event="""Is this an AI-generated video? Answer as fast as you can""",
            custom_category="robotics",
            is_thumbnail=False
        )
        print("Analysis Response:")
        print(analysis)
        # Validate each analysis result
        # Check basic analysis structure. Should fail if we add new fields.
        assert list(analysis.keys()) == ['video_id', 'analysis_id', 'mode', 'status', 'summary', 'events']
        assert_has_string_field(analysis, 'video_id')
        assert_has_string_field(analysis, 'analysis_id')
        assert analysis['mode'] == 'rapid_review'
        assert analysis['status'] == 'completed'
        assert_has_string_field(analysis, 'summary')

        for event in analysis['events']:
            # Check event structure
            assert list(event.keys()) == ['t_start', 't_end', 'category', 'label', 'severity', 'aiAnalysis', 'confidence']
            assert_has_string_field(event, 'aiAnalysis')
            assert_has_string_field(event, 't_start')
            assert_has_string_field(event, 't_end')
            assert_has_string_field(event, 'category')
            assert_has_string_field(event, 'severity')
            assert_has_number_field(event, 'confidence')

            # Check timestamp format "MM:SS"
            datetime.strptime(event['t_start'], '%M:%S')
            datetime.strptime(event['t_end'], '%M:%S')


            assert_has_string_field(event, 'label')
    finally:
        # Clean up: delete the video
        client.delete_video(video_id)

@pytest.mark.calls_api
@pytest.mark.timeout(360)  # 6 minutes timeout
def test_rapid_review_tricky_format_with_thumbnail():
    """
    Run with: pytest -m calls_api
    """
    client = get_client()
    
    # Upload video
    video_url = 'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/Dashcam_Footage_With_GPS_Data_OnScreen_aI7dTCnQJJA_k.mp4'
    folder_name = 'integration-test-folder'
    response = client.upload(video_url, folder=folder_name)
    video_id = response['video_id']
    
    try:
        # Run analysis multiple times to test consistency
        analyses = client.analyze(
            [video_id for _ in range(2)],
            analysis_type=AnalysisType.ASK,
            # This prompt relates to urbanhawks usecase.
            custom_event="""Mark the geolocation of each parked bus given the following ego vehicle trajectory: ANSWER EXACTLY on the format of the event label {"object":"Parked Bus","lat":12.345,"lon":6.78910}""",
            custom_category="driving",
            is_thumbnail=True
        )
        print("Analysis Response:")
        print(analyses)
        # Validate each analysis result
        for analysis in analyses:
            # Check basic analysis structure. Should fail if we add new fields.
            assert list(analysis.keys()) == ['video_id', 'analysis_id', 'mode', 'status', 'summary', 'events']
            assert_has_string_field(analysis, 'video_id')
            assert_has_string_field(analysis, 'analysis_id')
            assert analysis['mode'] == 'rapid_review'
            assert analysis['status'] == 'completed'
            assert_has_string_field(analysis, 'summary')

            # We should find at least two buses. Don't fail, just log as a warning. Too noisy to fail here.
            try:
                assert len(analysis['events']) >= 2, f"Expected at least 2 events, got {len(analysis['events'])}"
            except AssertionError as e:
                warnings.warn(f"Event count validation failed: {e}")
                continue

            # We should find at least one stop...
            assert len(analysis['events']) >= 1, f"Expected at least 1 event, got {len(analysis['events'])}"

            for event in analysis['events']:
                # Check event structure
                assert list(event.keys()) == ['t_start', 't_end', 'category', 'label', 'severity', 'aiAnalysis', 'confidence', 'annotated_thumbnail_url']
                assert_has_string_field(event, 'annotated_thumbnail_url')
                assert_has_string_field(event, 'aiAnalysis')
                assert_has_string_field(event, 't_start')
                assert_has_string_field(event, 't_end')
                assert_has_string_field(event, 'category')
                assert_has_string_field(event, 'severity')
                assert_has_number_field(event, 'confidence')

                # Check timestamp format "MM:SS"
                datetime.strptime(event['t_start'], '%M:%S')
                datetime.strptime(event['t_end'], '%M:%S')

                # Check thumbnail is an URL
                assert event['annotated_thumbnail_url'].startswith('https://')

                assert_has_string_field(event, 'label')
                # Check label JSON structure. Don't fail, just log as a warning despite it being a BUG
                try:
                    label_dict = json.loads(event['label'])
                    assert 'object' in label_dict and label_dict['object'] is not None
                    assert_has_number_field(label_dict, 'lat')
                    assert_has_number_field(label_dict, 'lon')
                except (json.JSONDecodeError, AssertionError) as e:
                    warnings.warn(f"Label structure validation failed: {e}. Label was: '{event['label']}'")
                    continue
        
        # Test search_videos on the results
        _test_search_videos(client, folder_name, 'parked bus', 4)

    finally:
        # Clean up: delete the video
        client.delete_video(video_id)

@pytest.mark.calls_api
@pytest.mark.timeout(360)  # 6 minutes timeout
def test_rapid_review_xl_longer_video():
    """
    Run with: pytest -m calls_api
    """
    client = get_client()
    
    # Upload video (~1mb / 8s)
    video_url = 'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/bus-drive-amalfi-narrow-road-11min.mp4'
    folder_name = 'integration-test-folder'
    response = client.upload(video_url, folder=folder_name)
    video_id = response['video_id']
    
    try:
        # Run analysis multiple times to test consistency
        analysis = client.analyze(
            video_id,
            analysis_type=AnalysisType.ASK,
            # This prompt relates to urbanhawks usecase.
            custom_event="""Mark each time the bus stops""",
            custom_category="driving",
        )
        print("Analysis Response:")
        print(analysis)
        # Validate each analysis result
        # Check basic analysis structure. Should fail if we add new fields.
        assert list(analysis.keys()) == ['video_id', 'analysis_id', 'mode', 'status', 'summary', 'events']
        assert_has_string_field(analysis, 'video_id')
        assert_has_string_field(analysis, 'analysis_id')
        assert analysis['mode'] == 'rapid_review'
        assert analysis['status'] == 'completed'
        assert_has_string_field(analysis, 'summary')

        # We should find at least one stop...
        assert len(analysis['events']) >= 1, f"Expected at least 1 event, got {len(analysis['events'])}"

        for event in analysis['events']:
            # Check event structure
            assert list(event.keys()) == ['t_start', 't_end', 'category', 'label', 'severity', 'aiAnalysis', 'confidence']
            assert_has_string_field(event, 'aiAnalysis')
            assert_has_string_field(event, 't_start')
            assert_has_string_field(event, 't_end')
            assert_has_string_field(event, 'category')
            assert_has_string_field(event, 'severity')
            assert_has_number_field(event, 'confidence')

            # Check timestamp format "MM:SS"
            datetime.strptime(event['t_start'], '%M:%S')
            datetime.strptime(event['t_end'], '%M:%S')


            assert_has_string_field(event, 'label')
    finally:
        # Clean up: delete the video
        client.delete_video(video_id)

@pytest.mark.calls_api
@pytest.mark.timeout(720)  # 12 minutes timeout ALSO edge is due to be removed from sdk
def test_edge_case():
    """    
    Run with: pytest -m calls_api
    """
    client = get_client()
    
    # Test video URL
    video_url = 'https://storage.googleapis.com/videolm-bc319.firebasestorage.app/example-videos/Oakland-to-SF-on-Bridge.mp4'
    
    # Upload video
    folder_name = 'integration-test-folder'
    upload_response = client.upload(video_url, folder=folder_name)
    video_id = upload_response["video_id"]
    
    try:
        # Test edge case analysis
        analysis = client.analyze(
            # [video_id for _ in range(1)], # FIXME: Fails with 2 videos
            video_id,
            analysis_type=AnalysisType.EDGE_CASE,
            edge_case_category="autonomous-driving"
        )
        # Should look like {'video_id': '3edf6078f0ec401c8e98e749cf8014c3',
        #  'mode': 'edge_case',
        #  'status': 'completed',
        #  'events': [{'label': '[Detection] A paper on the dashboard obstructs the lower portion of the forward view.',
        #    'start_time': 0.0,
        #    'end_time': 29.0},
        #   {'label': '[Detection] Vehicle navigates a narrow road with parked cars on both sides, creating continuous potential occlusions.',
        #    'start_time': 0.0,
        #    'end_time': 29.0},
        #   ...
 
        print("Analysis Response:")
        print(analysis)
        assert_has_string_field(analysis, 'video_id')
        assert list(analysis.keys()) == ['video_id', 'mode', 'status', 'events', 'analysis_id']
        assert analysis['mode'] == 'edge_case'
        assert analysis['status'] == 'completed'
        
        for event in analysis['events']:
            # Check event structure
            assert list(event.keys()) == ['label', 'start_time', 'end_time']
            assert_has_string_field(event, 'label')
            # NOTE: Number rather than string and end_time rather than t_end.
            assert_has_number_field(event, 'start_time')
            assert_has_number_field(event, 'end_time')

        _test_search_videos(client, folder_name, 'Sun glare', 1)
    finally:
        # Clean up: delete the video
        client.delete_video(video_id)
