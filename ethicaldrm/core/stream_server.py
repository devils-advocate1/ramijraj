import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from flask import Response
from .token_manager import TokenManager

logger = logging.getLogger(__name__)


class StreamServer:
    """Handles secure streaming of encrypted video content."""
    
    def __init__(self, content_dir: str, token_manager: TokenManager):
        self.content_dir = Path(content_dir)
        self.token_manager = token_manager
        
    def get_playlist(self, video_id: str, token: str) -> Tuple[Optional[str], int]:
        """
        Get HLS playlist file for a video.
        
        Args:
            video_id: Video identifier
            token: Access token
            
        Returns:
            Tuple of (playlist_content, status_code)
        """
        # Validate token
        if not self.token_manager.validate_access(token, video_id):
            logger.warning(f"Unauthorized playlist access for video {video_id}")
            return None, 401
            
        # Find playlist file
        playlist_path = self.content_dir / video_id / f"{video_id}.m3u8"
        
        if not playlist_path.exists():
            logger.error(f"Playlist not found: {playlist_path}")
            return None, 404
            
        try:
            with open(playlist_path, 'r') as f:
                content = f.read()
                
            # Modify playlist to use secure segment URLs
            modified_content = self._secure_playlist_urls(content, video_id, token)
            
            logger.info(f"Served playlist for video {video_id}")
            return modified_content, 200
            
        except Exception as e:
            logger.error(f"Error reading playlist: {e}")
            return None, 500
    
    def get_segment(self, 
                   video_id: str, 
                   segment_name: str, 
                   token: str) -> Tuple[Optional[bytes], int, Dict[str, str]]:
        """
        Get video segment file.
        
        Args:
            video_id: Video identifier
            segment_name: Segment file name
            token: Access token
            
        Returns:
            Tuple of (segment_data, status_code, headers)
        """
        # Validate segment access
        if not self.token_manager.validate_segment_access(token, video_id, segment_name):
            logger.warning(f"Unauthorized segment access: {video_id}/{segment_name}")
            return None, 401, {}
            
        # Find segment file
        segment_path = self.content_dir / video_id / segment_name
        
        if not segment_path.exists():
            logger.error(f"Segment not found: {segment_path}")
            return None, 404, {}
            
        try:
            with open(segment_path, 'rb') as f:
                data = f.read()
                
            headers = {
                'Content-Type': 'video/mp2t',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY'
            }
            
            logger.info(f"Served segment {video_id}/{segment_name}")
            return data, 200, headers
            
        except Exception as e:
            logger.error(f"Error reading segment: {e}")
            return None, 500, {}
    
    def get_encryption_key(self, video_id: str, token: str) -> Tuple[Optional[bytes], int, Dict[str, str]]:
        """
        Get encryption key for video.
        
        Args:
            video_id: Video identifier
            token: Access token
            
        Returns:
            Tuple of (key_data, status_code, headers)
        """
        # Validate access
        if not self.token_manager.validate_access(token, video_id):
            logger.warning(f"Unauthorized key access for video {video_id}")
            return None, 401, {}
            
        # Find key file
        key_path = self.content_dir / video_id / "enc.key"
        
        if not key_path.exists():
            logger.error(f"Encryption key not found: {key_path}")
            return None, 404, {}
            
        try:
            with open(key_path, 'rb') as f:
                key_data = f.read()
                
            headers = {
                'Content-Type': 'application/octet-stream',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
            
            logger.info(f"Served encryption key for video {video_id}")
            return key_data, 200, headers
            
        except Exception as e:
            logger.error(f"Error reading encryption key: {e}")
            return None, 500, {}
    
    def _secure_playlist_urls(self, playlist_content: str, video_id: str, token: str) -> str:
        """
        Modify playlist URLs to include secure access tokens.
        
        Args:
            playlist_content: Original playlist content
            video_id: Video identifier
            token: Access token
            
        Returns:
            Modified playlist with secure URLs
        """
        lines = playlist_content.split('\n')
        modified_lines = []
        
        for line in lines:
            if line.endswith('.ts'):
                # This is a segment line - add token parameter
                segment_name = line.strip()
                
                # Generate a short-lived token for this specific segment
                payload = self.token_manager.validate_token(token)
                segment_token = self.token_manager.create_download_token(
                    user_id=payload['user_id'],
                    video_id=video_id,
                    segment_name=segment_name
                )
                
                secure_url = f"/get_segment?video={video_id}&segment={segment_name}&token={segment_token}"
                modified_lines.append(secure_url)
            elif line.startswith('#EXT-X-KEY:'):
                # This is the key line - update with secure key URL
                key_url = f"/get_key?video={video_id}&token={token}"
                modified_lines.append(f"#EXT-X-KEY:METHOD=AES-128,URI=\"{key_url}\"")
            else:
                modified_lines.append(line)
                
        return '\n'.join(modified_lines)
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get information about available video."""
        video_dir = self.content_dir / video_id
        
        if not video_dir.exists():
            return None
            
        playlist_path = video_dir / f"{video_id}.m3u8"
        if not playlist_path.exists():
            return None
            
        # Count segments
        segments = list(video_dir.glob("*.ts"))
        
        # Get playlist info
        try:
            with open(playlist_path, 'r') as f:
                playlist_content = f.read()
                
            return {
                "video_id": video_id,
                "segments_count": len(segments),
                "has_encryption": "#EXT-X-KEY:" in playlist_content,
                "playlist_size": len(playlist_content),
                "total_size": sum(s.stat().st_size for s in segments)
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None