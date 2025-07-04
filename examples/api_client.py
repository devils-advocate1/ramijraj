#!/usr/bin/env python3
"""
EthicalDRM API Client Example
Demonstrates how to interact with the EthicalDRM API programmatically.
"""

import requests
import json
import time
from pathlib import Path

class EthicalDRMClient:
    """Client for interacting with EthicalDRM API."""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self):
        """Check if the API server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def generate_token(self, user_id, video_id, expires_in=3600):
        """Generate an access token for video streaming."""
        data = {
            "user_id": user_id,
            "video_id": video_id,
            "expires_in": expires_in
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate_token",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token generation failed: {e}")
            return None
    
    def validate_token(self, token):
        """Validate an access token."""
        data = {"token": token}
        
        try:
            response = self.session.post(
                f"{self.base_url}/validate_token",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token validation failed: {e}")
            return None
    
    def upload_video(self, video_path, video_id, user_id=None):
        """Upload and encrypt a video."""
        if not Path(video_path).exists():
            print(f"Video file not found: {video_path}")
            return None
        
        files = {"video": open(video_path, "rb")}
        data = {"video_id": video_id}
        
        if user_id:
            data["user_id"] = user_id
        
        try:
            response = self.session.post(
                f"{self.base_url}/upload_video",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Video upload failed: {e}")
            return None
        finally:
            files["video"].close()
    
    def get_video_info(self, video_id):
        """Get information about a video."""
        try:
            response = self.session.get(f"{self.base_url}/video_info/{video_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to get video info: {e}")
            return None
    
    def get_playlist(self, video_id, token):
        """Get HLS playlist for a video."""
        try:
            response = self.session.get(
                f"{self.base_url}/get_stream/{video_id}.m3u8",
                params={"token": token}
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to get playlist: {e}")
            return None
    
    def download_segment(self, video_id, segment_name, token, output_path=None):
        """Download a video segment."""
        try:
            response = self.session.get(
                f"{self.base_url}/get_segment",
                params={
                    "video": video_id,
                    "segment": segment_name,
                    "token": token
                }
            )
            response.raise_for_status()
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Segment saved to: {output_path}")
            
            return response.content
        except requests.RequestException as e:
            print(f"Failed to download segment: {e}")
            return None


def main():
    """Demonstrate API client usage."""
    print("🔐 EthicalDRM API Client Example")
    print("=" * 40)
    
    # Initialize client
    client = EthicalDRMClient("http://localhost:5000")
    
    # 1. Health check
    print("\n📊 Checking API health...")
    health = client.health_check()
    if health:
        print(f"✅ API is healthy: {health['service']}")
    else:
        print("❌ API is not responding")
        return
    
    # 2. Video upload (if you have a video file)
    video_path = "demo_video.mp4"
    video_id = "api_demo_video"
    user_id = "api_demo_user"
    
    if Path(video_path).exists():
        print(f"\n📹 Uploading video: {video_path}")
        upload_result = client.upload_video(video_path, video_id, user_id)
        
        if upload_result:
            print("✅ Video uploaded and encrypted successfully!")
            print(f"   Video ID: {upload_result['video_id']}")
        else:
            print("❌ Video upload failed")
            return
    else:
        print(f"\n⚠️  Video file not found: {video_path}")
        print("   Using existing video for demo...")
        video_id = "demo_video_001"  # Use existing video
    
    # 3. Get video information
    print(f"\n📊 Getting video info for: {video_id}")
    video_info = client.get_video_info(video_id)
    
    if video_info:
        print("✅ Video info retrieved:")
        print(f"   Segments: {video_info['segments_count']}")
        print(f"   Has encryption: {video_info['has_encryption']}")
        print(f"   Total size: {video_info['total_size']} bytes")
    else:
        print(f"❌ Video not found: {video_id}")
        return
    
    # 4. Generate access token
    print(f"\n🎫 Generating access token...")
    token_result = client.generate_token(user_id, video_id, expires_in=1800)
    
    if token_result:
        token = token_result["token"]
        print("✅ Token generated successfully!")
        print(f"   Token: {token[:50]}...")
        print(f"   Expires in: {token_result['expires_in']} seconds")
        print(f"   Playlist URL: {token_result['playlist_url']}")
    else:
        print("❌ Token generation failed")
        return
    
    # 5. Validate token
    print(f"\n🔍 Validating token...")
    validation_result = client.validate_token(token)
    
    if validation_result and validation_result.get("valid"):
        payload = validation_result["payload"]
        print("✅ Token is valid!")
        print(f"   User ID: {payload['user_id']}")
        print(f"   Video ID: {payload['video_id']}")
    else:
        print("❌ Token validation failed")
        return
    
    # 6. Get playlist
    print(f"\n🎬 Fetching HLS playlist...")
    playlist = client.get_playlist(video_id, token)
    
    if playlist:
        print("✅ Playlist retrieved successfully!")
        lines = playlist.split('\n')
        print(f"   Playlist lines: {len(lines)}")
        
        # Find first segment
        segment_name = None
        for line in lines:
            if line.strip().endswith('.ts'):
                # Extract segment name from URL
                if 'segment=' in line:
                    segment_name = line.split('segment=')[1].split('&')[0]
                    break
        
        if segment_name:
            print(f"   First segment: {segment_name}")
            
            # 7. Download a segment
            print(f"\n📥 Downloading segment: {segment_name}")
            
            # Get the segment token from playlist (it should be in the URL)
            segment_token = token  # For demo, using same token
            
            segment_data = client.download_segment(
                video_id, 
                segment_name, 
                segment_token,
                output_path=f"downloaded_{segment_name}"
            )
            
            if segment_data:
                print(f"✅ Segment downloaded: {len(segment_data)} bytes")
            else:
                print("❌ Segment download failed")
        
    else:
        print("❌ Playlist retrieval failed")
    
    # 8. Generate web player URL
    print(f"\n🌐 Web Player Access")
    print("-" * 30)
    base_url = client.base_url
    player_url = f"{base_url}/templates/player.html?video={video_id}&token={token}"
    
    print(f"🎬 Open this URL in your browser:")
    print(f"   {player_url}")
    print("")
    print(f"Or manually enter:")
    print(f"   Video ID: {video_id}")
    print(f"   Token: {token}")
    
    print("\n🎉 API Client Demo Complete!")
    print("=" * 40)
    print("The EthicalDRM API is working correctly.")
    print("You can now integrate this into your applications.")


if __name__ == "__main__":
    main()