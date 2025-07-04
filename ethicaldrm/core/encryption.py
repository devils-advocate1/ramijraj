import os
import secrets
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import ffmpeg

logger = logging.getLogger(__name__)


class VideoEncryption:
    """Handles video encryption using HLS with AES-128 encryption."""
    
    def __init__(self, output_dir: str = "encrypted_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def generate_encryption_key(self) -> bytes:
        """Generate a random 16-byte AES key."""
        return secrets.token_bytes(16)
    
    def create_key_info_file(self, key_path: str, key_uri: str = "enc.key") -> str:
        """Create the key_info.txt file required by ffmpeg."""
        key_info_path = self.output_dir / "key_info.txt"
        
        with open(key_info_path, 'w') as f:
            f.write(f"{key_uri}\n")
            f.write(f"{key_path}\n")
            f.write(f"{key_path}\n")
            
        return str(key_info_path)
    
    def encrypt_video(self, 
                     input_path: str, 
                     video_id: str,
                     segment_duration: int = 10,
                     encryption_key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Encrypt video using HLS with AES-128 encryption.
        
        Args:
            input_path: Path to input video file
            video_id: Unique identifier for the video
            segment_duration: Duration of each HLS segment in seconds
            encryption_key: Optional custom encryption key
            
        Returns:
            Dictionary containing encryption details and output paths
        """
        if encryption_key is None:
            encryption_key = self.generate_encryption_key()
            
        # Create output directory for this video
        video_output_dir = self.output_dir / video_id
        video_output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save encryption key
        key_path = video_output_dir / "enc.key"
        with open(key_path, 'wb') as f:
            f.write(encryption_key)
            
        # Create key info file
        key_info_path = self.create_key_info_file(str(key_path))
        
        # Output paths
        playlist_path = video_output_dir / f"{video_id}.m3u8"
        segment_pattern = video_output_dir / f"{video_id}_%03d.ts"
        
        try:
            # Use ffmpeg-python for better control
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                str(playlist_path),
                format='hls',
                hls_time=segment_duration,
                hls_list_size=0,
                hls_key_info_file=key_info_path,
                hls_segment_filename=str(segment_pattern)
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            logger.info(f"Successfully encrypted video {video_id}")
            
            return {
                "video_id": video_id,
                "playlist_path": str(playlist_path),
                "output_dir": str(video_output_dir),
                "key_path": str(key_path),
                "encryption_key": encryption_key.hex(),
                "segments_count": len(list(video_output_dir.glob("*.ts")))
            }
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during encryption: {e}")
            raise Exception(f"Video encryption failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during encryption: {e}")
            raise
            
    def add_watermark(self, 
                     input_path: str, 
                     user_id: str, 
                     watermark_text: Optional[str] = None) -> str:
        """
        Add invisible watermark to video for user tracking.
        
        Args:
            input_path: Path to input video
            user_id: Unique user identifier
            watermark_text: Optional custom watermark text
            
        Returns:
            Path to watermarked video
        """
        if watermark_text is None:
            watermark_text = f"USER:{user_id}"
            
        output_path = self.output_dir / f"watermarked_{user_id}_{Path(input_path).name}"
        
        try:
            # Add invisible watermark using LSB steganography via ffmpeg
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vf=f"drawtext=text='{watermark_text}':fontcolor=white@0.01:fontsize=1:x=10:y=10"
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            logger.info(f"Added watermark for user {user_id}")
            return str(output_path)
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during watermarking: {e}")
            raise Exception(f"Watermarking failed: {e}")
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information using ffprobe."""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if video_stream is None:
                raise Exception("No video stream found")
                
            return {
                "duration": float(probe['format']['duration']),
                "size": int(probe['format']['size']),
                "bitrate": int(probe['format']['bit_rate']),
                "width": int(video_stream['width']),
                "height": int(video_stream['height']),
                "codec": video_stream['codec_name'],
                "fps": eval(video_stream['r_frame_rate'])
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise