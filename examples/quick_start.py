#!/usr/bin/env python3
"""
EthicalDRM Quick Start Example
Demonstrates the main features of the EthicalDRM system.
"""

import os
import time
from pathlib import Path

from ethicaldrm import VideoEncryption, TokenManager, LeakDetector
from ethicaldrm.utils.security import SecurityUtils

def main():
    print("🔐 EthicalDRM Quick Start Example")
    print("=" * 50)
    
    # Setup
    output_dir = "demo_output"
    demo_video = "demo_video.mp4"  # You'll need to provide this
    
    if not Path(demo_video).exists():
        print(f"❌ Please place a demo video file at: {demo_video}")
        print("   You can use any MP4 file for testing.")
        return
    
    # 1. Video Encryption
    print("\n📹 Step 1: Video Encryption")
    print("-" * 30)
    
    encryptor = VideoEncryption(output_dir)
    
    try:
        # Add watermark for user tracking
        user_id = "demo_user_123"
        print(f"🏷️  Adding watermark for user: {user_id}")
        watermarked_video = encryptor.add_watermark(demo_video, user_id)
        
        # Encrypt the video
        video_id = "demo_video_001"
        print(f"🔒 Encrypting video: {demo_video}")
        result = encryptor.encrypt_video(watermarked_video, video_id)
        
        print("✅ Video encrypted successfully!")
        print(f"   📁 Output directory: {result['output_dir']}")
        print(f"   🎬 Playlist: {result['playlist_path']}")
        print(f"   📊 Segments: {result['segments_count']}")
        
        # Clean up watermarked file
        Path(watermarked_video).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return
    
    # 2. Token Management
    print("\n🎫 Step 2: Token Management")
    print("-" * 30)
    
    token_manager = TokenManager()
    
    # Generate access token
    user_id = "demo_user_123"
    token = token_manager.generate_token(user_id, video_id, expires_in=3600)
    print(f"🔑 Generated token for user {user_id}")
    print(f"   Token: {token[:50]}...")
    
    # Validate token
    try:
        payload = token_manager.validate_token(token)
        print(f"✅ Token validated successfully")
        print(f"   User ID: {payload['user_id']}")
        print(f"   Video ID: {payload['video_id']}")
    except Exception as e:
        print(f"❌ Token validation failed: {e}")
    
    # 3. Security Scanning
    print("\n🛡️  Step 3: Security Scanning")
    print("-" * 30)
    
    security = SecurityUtils()
    
    # Scan for screen recorders
    recorders = security.detect_screen_recorders()
    print(f"📹 Screen recorders detected: {len(recorders)}")
    for recorder in recorders[:3]:  # Show first 3
        print(f"   - {recorder['name']} (PID: {recorder['pid']})")
    
    # Scan for suspicious processes
    suspicious = security.detect_suspicious_processes()
    print(f"🚨 Suspicious processes detected: {len(suspicious)}")
    for proc in suspicious[:3]:  # Show first 3
        print(f"   - {proc['name']} (keyword: {proc['keyword']})")
    
    # System info
    sys_info = security.get_system_info()
    print(f"💻 System platform: {sys_info.get('platform')}")
    print(f"⚡ CPU cores: {sys_info.get('cpu_count')}")
    
    # 4. Content Registration and Leak Detection
    print("\n🔍 Step 4: Leak Detection")
    print("-" * 30)
    
    detector = LeakDetector()
    
    # Register original content
    owner_info = {
        'name': 'Demo Creator',
        'email': 'demo@example.com'
    }
    
    print(f"📝 Registering content: {video_id}")
    success = detector.register_content(demo_video, video_id, owner_info)
    
    if success:
        print("✅ Content registered successfully")
        
        # Test leak detection with the same video (should match 100%)
        print("🔍 Testing leak detection...")
        matches = detector.detect_leak(demo_video)
        
        if matches:
            for match in matches:
                print(f"   🎯 Match found:")
                print(f"      Content ID: {match['content_id']}")
                print(f"      Similarity: {match['similarity']:.2%}")
                print(f"      Confidence: {match['confidence']}")
        else:
            print("   ❌ No matches found (unexpected)")
    else:
        print("❌ Content registration failed")
    
    # 5. Generate Client Protection
    print("\n🌐 Step 5: Client Protection")
    print("-" * 30)
    
    # Generate security headers
    headers = security.generate_security_headers()
    print("🔒 Security headers generated:")
    for header, value in list(headers.items())[:3]:
        print(f"   {header}: {value[:50]}...")
    
    # Generate client protection script
    protection_script = security.generate_client_protection_script()
    print(f"📜 Client protection script generated ({len(protection_script)} chars)")
    
    # 6. Access URLs
    print("\n🌐 Step 6: Access URLs")
    print("-" * 30)
    
    base_url = "http://localhost:5000"
    playlist_url = f"{base_url}/get_stream/{video_id}.m3u8?token={token}"
    player_url = f"{base_url}/player.html?video={video_id}&token={token}"
    
    print("🎬 Video access URLs:")
    print(f"   Playlist (HLS): {playlist_url}")
    print(f"   Web Player: {player_url}")
    
    # 7. Demo Complete
    print("\n🎉 Demo Complete!")
    print("-" * 30)
    print("Next steps:")
    print("1. Start the API server: ethicaldrm-api")
    print("2. Open the web player URL in your browser")
    print("3. Enter the token and video ID to view protected content")
    print("")
    print("🔐 Your content is now protected by EthicalDRM!")
    print(f"📁 Encrypted files are in: {output_dir}/{video_id}/")
    print(f"🎫 Access token: {token}")

if __name__ == "__main__":
    main()