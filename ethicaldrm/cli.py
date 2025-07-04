import click
import logging
import json
from pathlib import Path
from typing import Optional

from .core.encryption import VideoEncryption
from .core.token_manager import TokenManager
from .detectors.leak_detector import LeakDetector
from .utils.security import SecurityUtils
from .api.app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def main():
    """🔐 EthicalDRM - Content Protection Toolkit"""
    click.echo("🔐 EthicalDRM - Protecting your content, empowering creators")


@main.command()
@click.option('--input', '-i', required=True, help='Input video file path')
@click.option('--output', '-o', default='encrypted_output', help='Output directory')
@click.option('--video-id', required=True, help='Unique video identifier')
@click.option('--user-id', help='User ID for watermarking (optional)')
@click.option('--segment-duration', default=10, help='HLS segment duration in seconds')
def encrypt(input, output, video_id, user_id, segment_duration):
    """Encrypt video using HLS with AES-128 encryption."""
    try:
        encryptor = VideoEncryption(output)
        
        input_file = input
        
        # Add watermark if user_id provided
        if user_id:
            click.echo(f"🏷️  Adding watermark for user: {user_id}")
            input_file = encryptor.add_watermark(input, user_id)
        
        click.echo(f"🔒 Encrypting video: {input}")
        result = encryptor.encrypt_video(input_file, video_id, segment_duration)
        
        click.echo("✅ Video encrypted successfully!")
        click.echo(f"📁 Output directory: {result['output_dir']}")
        click.echo(f"🎬 Playlist: {result['playlist_path']}")
        click.echo(f"🔑 Encryption key: {result['encryption_key']}")
        click.echo(f"📊 Segments created: {result['segments_count']}")
        
        # Clean up watermarked file if created
        if user_id and input_file != input:
            Path(input_file).unlink(missing_ok=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--dir', '-d', default='encrypted_output', help='Content directory to serve')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def serve(dir, host, port, debug):
    """Start the EthicalDRM API server."""
    try:
        content_dir = Path(dir)
        if not content_dir.exists():
            click.echo(f"❌ Content directory does not exist: {dir}")
            exit(1)
            
        click.echo(f"🚀 Starting EthicalDRM server...")
        click.echo(f"📁 Content directory: {dir}")
        click.echo(f"🌐 Server URL: http://{host}:{port}")
        
        app = create_app({'CONTENT_DIR': dir})
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--user-id', required=True, help='User identifier')
@click.option('--video-id', required=True, help='Video identifier')
@click.option('--expires-in', default=3600, help='Token expiration in seconds')
@click.option('--secret-key', help='Secret key for token signing')
def generate_token(user_id, video_id, expires_in, secret_key):
    """Generate access token for video streaming."""
    try:
        token_manager = TokenManager(secret_key)
        token = token_manager.generate_token(user_id, video_id, expires_in)
        
        click.echo("🎫 Token generated successfully!")
        click.echo(f"🔑 Token: {token}")
        click.echo(f"⏰ Expires in: {expires_in} seconds")
        click.echo(f"👤 User ID: {user_id}")
        click.echo(f"🎬 Video ID: {video_id}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--token', required=True, help='Token to validate')
@click.option('--secret-key', help='Secret key for token validation')
def validate_token(token, secret_key):
    """Validate an access token."""
    try:
        token_manager = TokenManager(secret_key)
        payload = token_manager.validate_token(token)
        
        click.echo("✅ Token is valid!")
        click.echo(f"👤 User ID: {payload.get('user_id')}")
        click.echo(f"🎬 Video ID: {payload.get('video_id')}")
        click.echo(f"⏰ Issued at: {payload.get('iat')}")
        click.echo(f"⏰ Expires at: {payload.get('exp')}")
        
    except Exception as e:
        click.echo(f"❌ Token invalid: {e}", err=True)
        exit(1)


@main.command()
@click.option('--video', required=True, help='Video file to fingerprint')
@click.option('--content-id', required=True, help='Content identifier')
@click.option('--owner-name', required=True, help='Content owner name')
@click.option('--owner-email', required=True, help='Content owner email')
def register_content(video, content_id, owner_name, owner_email):
    """Register content for leak detection."""
    try:
        detector = LeakDetector()
        
        owner_info = {
            'name': owner_name,
            'email': owner_email
        }
        
        click.echo(f"🔍 Analyzing video: {video}")
        success = detector.register_content(video, content_id, owner_info)
        
        if success:
            click.echo("✅ Content registered successfully!")
            click.echo(f"🆔 Content ID: {content_id}")
            click.echo(f"👤 Owner: {owner_name}")
        else:
            click.echo("❌ Failed to register content")
            exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--suspect-video', required=True, help='Suspect video file to check')
@click.option('--threshold', default=0.8, help='Similarity threshold for detection')
def detect_leak(suspect_video, threshold):
    """Detect if a video matches registered content."""
    try:
        detector = LeakDetector()
        
        click.echo(f"🔍 Scanning video: {suspect_video}")
        matches = detector.detect_leak(suspect_video)
        
        if matches:
            click.echo(f"⚠️  Found {len(matches)} potential matches:")
            for match in matches:
                click.echo(f"  🆔 Content ID: {match['content_id']}")
                click.echo(f"  📊 Similarity: {match['similarity']:.2%}")
                click.echo(f"  🎯 Confidence: {match['confidence']}")
                click.echo(f"  👤 Owner: {match['owner_info']['name']}")
                click.echo("")
        else:
            click.echo("✅ No matches found - content appears to be original")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--content-id', required=True, help='Content ID for takedown')
@click.option('--infringing-url', required=True, help='URL where infringement was found')
@click.option('--output', '-o', help='Output file for takedown notice')
def generate_takedown(content_id, infringing_url, output):
    """Generate DMCA takedown notice."""
    try:
        detector = LeakDetector()
        notice = detector.generate_takedown_notice(content_id, infringing_url)
        
        if output:
            with open(output, 'w') as f:
                f.write(notice)
            click.echo(f"📄 Takedown notice saved to: {output}")
        else:
            click.echo("📄 DMCA Takedown Notice:")
            click.echo(notice)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
def security_scan():
    """Scan system for screen recorders and security threats."""
    try:
        security = SecurityUtils()
        
        click.echo("🔍 Scanning for security threats...")
        
        # Detect screen recorders
        recorders = security.detect_screen_recorders()
        if recorders:
            click.echo(f"⚠️  Found {len(recorders)} screen recording applications:")
            for recorder in recorders:
                click.echo(f"  📹 {recorder['name']} (PID: {recorder['pid']})")
        else:
            click.echo("✅ No screen recorders detected")
        
        # Detect suspicious processes
        suspicious = security.detect_suspicious_processes()
        if suspicious:
            click.echo(f"⚠️  Found {len(suspicious)} suspicious processes:")
            for proc in suspicious:
                click.echo(f"  🚨 {proc['name']} - Keyword: {proc['keyword']}")
        else:
            click.echo("✅ No suspicious processes detected")
        
        # System info
        sys_info = security.get_system_info()
        click.echo(f"💻 System: {sys_info.get('platform', 'Unknown')}")
        click.echo(f"⚡ CPU cores: {sys_info.get('cpu_count', 'Unknown')}")
        click.echo(f"🧠 Memory: {sys_info.get('memory_available', 0) // (1024**3)} GB available")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--video', required=True, help='Video file to analyze')
def extract_watermark(video):
    """Extract watermark information from video."""
    try:
        detector = LeakDetector()
        
        click.echo(f"🔍 Analyzing video: {video}")
        watermark = detector.extract_watermark(video)
        
        if watermark:
            click.echo(f"🏷️  Watermark found: {watermark}")
        else:
            click.echo("❌ No watermark detected")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@main.command()
@click.option('--input-dir', required=True, help='Directory containing videos to process')
@click.option('--output-dir', default='batch_output', help='Output directory')
@click.option('--watermark-users', help='JSON file with user watermark mappings')
def batch_encrypt(input_dir, output_dir, watermark_users):
    """Batch encrypt multiple videos."""
    try:
        input_path = Path(input_dir)
        if not input_path.exists():
            click.echo(f"❌ Input directory does not exist: {input_dir}")
            exit(1)
        
        # Load user mappings if provided
        user_mappings = {}
        if watermark_users:
            with open(watermark_users, 'r') as f:
                user_mappings = json.load(f)
        
        encryptor = VideoEncryption(output_dir)
        
        # Find all video files
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        video_files = []
        for ext in video_extensions:
            video_files.extend(input_path.glob(f"*{ext}"))
            video_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        click.echo(f"🎬 Found {len(video_files)} video files")
        
        for video_file in video_files:
            try:
                video_id = video_file.stem
                user_id = user_mappings.get(video_id)
                
                click.echo(f"🔒 Processing: {video_file.name}")
                
                input_file = str(video_file)
                if user_id:
                    click.echo(f"  🏷️  Adding watermark for user: {user_id}")
                    input_file = encryptor.add_watermark(str(video_file), user_id)
                
                result = encryptor.encrypt_video(input_file, video_id)
                click.echo(f"  ✅ Encrypted: {result['segments_count']} segments")
                
                # Clean up watermarked file
                if user_id and input_file != str(video_file):
                    Path(input_file).unlink(missing_ok=True)
                    
            except Exception as e:
                click.echo(f"  ❌ Error processing {video_file.name}: {e}")
        
        click.echo("🎉 Batch processing completed!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


if __name__ == '__main__':
    main()