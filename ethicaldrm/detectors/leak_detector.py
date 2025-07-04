import hashlib
import imagehash
import cv2
import numpy as np
import logging
import requests
from PIL import Image
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class LeakDetector:
    """AI-powered leak detection and content monitoring system."""
    
    def __init__(self, content_database: Optional[str] = None):
        self.content_database = content_database or "content_fingerprints.db"
        self.fingerprints = {}
        self.load_fingerprints()
        
    def load_fingerprints(self):
        """Load content fingerprints from database."""
        # In a real implementation, this would load from a proper database
        # For now, we'll use a simple in-memory dictionary
        self.fingerprints = {}
        
    def generate_video_fingerprint(self, video_path: str, 
                                 sample_frames: int = 10) -> Dict[str, Any]:
        """
        Generate a unique fingerprint for a video file.
        
        Args:
            video_path: Path to video file
            sample_frames: Number of frames to sample for fingerprinting
            
        Returns:
            Dictionary containing various fingerprint data
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames evenly throughout the video
            frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
            
            frame_hashes = []
            frame_features = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert to PIL Image for hashing
                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    # Generate perceptual hash
                    phash = str(imagehash.phash(pil_image))
                    dhash = str(imagehash.dhash(pil_image))
                    
                    frame_hashes.append({
                        'frame_idx': frame_idx,
                        'phash': phash,
                        'dhash': dhash,
                        'timestamp': frame_idx / fps if fps > 0 else 0
                    })
                    
                    # Extract additional features (color histogram, etc.)
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
                    frame_features.append(hist.flatten())
            
            cap.release()
            
            # Generate overall video hash
            video_data = open(video_path, 'rb').read()
            file_hash = hashlib.sha256(video_data).hexdigest()
            
            fingerprint = {
                'file_hash': file_hash,
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'frame_hashes': frame_hashes,
                'frame_features': frame_features,
                'sample_count': len(frame_hashes)
            }
            
            logger.info(f"Generated fingerprint for {video_path}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating video fingerprint: {e}")
            raise
    
    def register_content(self, video_path: str, content_id: str, 
                        owner_info: Dict[str, Any]) -> bool:
        """
        Register content in the fingerprint database.
        
        Args:
            video_path: Path to original video
            content_id: Unique content identifier
            owner_info: Information about content owner
            
        Returns:
            True if registration successful
        """
        try:
            fingerprint = self.generate_video_fingerprint(video_path)
            
            self.fingerprints[content_id] = {
                'fingerprint': fingerprint,
                'owner_info': owner_info,
                'registered_at': np.datetime64('now'),
                'video_path': video_path
            }
            
            logger.info(f"Registered content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering content: {e}")
            return False
    
    def compare_fingerprints(self, fp1: Dict[str, Any], fp2: Dict[str, Any], 
                           threshold: float = 0.8) -> float:
        """
        Compare two video fingerprints for similarity.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            threshold: Similarity threshold
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Compare file hashes first (exact match)
            if fp1['file_hash'] == fp2['file_hash']:
                return 1.0
            
            # Compare frame hashes
            frame_similarities = []
            
            for f1 in fp1['frame_hashes']:
                best_match = 0.0
                for f2 in fp2['frame_hashes']:
                    # Compare perceptual hashes
                    phash_diff = imagehash.hex_to_hash(f1['phash']) - imagehash.hex_to_hash(f2['phash'])
                    dhash_diff = imagehash.hex_to_hash(f1['dhash']) - imagehash.hex_to_hash(f2['dhash'])
                    
                    # Convert hamming distance to similarity
                    phash_sim = 1.0 - (phash_diff / 64.0)
                    dhash_sim = 1.0 - (dhash_diff / 64.0)
                    
                    combined_sim = (phash_sim + dhash_sim) / 2.0
                    best_match = max(best_match, combined_sim)
                
                frame_similarities.append(best_match)
            
            # Average similarity across all frames
            overall_similarity = np.mean(frame_similarities) if frame_similarities else 0.0
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error comparing fingerprints: {e}")
            return 0.0
    
    def detect_leak(self, suspect_video_path: str) -> List[Dict[str, Any]]:
        """
        Detect if a video matches any registered content.
        
        Args:
            suspect_video_path: Path to suspect video
            
        Returns:
            List of potential matches with similarity scores
        """
        try:
            suspect_fp = self.generate_video_fingerprint(suspect_video_path)
            matches = []
            
            for content_id, content_data in self.fingerprints.items():
                similarity = self.compare_fingerprints(
                    content_data['fingerprint'], 
                    suspect_fp
                )
                
                if similarity > 0.7:  # Threshold for potential match
                    matches.append({
                        'content_id': content_id,
                        'similarity': similarity,
                        'owner_info': content_data['owner_info'],
                        'confidence': 'high' if similarity > 0.9 else 'medium' if similarity > 0.8 else 'low'
                    })
            
            # Sort by similarity score
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            if matches:
                logger.warning(f"Detected {len(matches)} potential leaks")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error detecting leaks: {e}")
            return []
    
    async def scan_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scan URLs for potential leaked content.
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            List of scan results
        """
        results = []
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Look for video-related keywords
                            video_keywords = [
                                'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv',
                                'stream', 'download', 'watch', 'video'
                            ]
                            
                            found_keywords = []
                            for keyword in video_keywords:
                                if keyword.lower() in content.lower():
                                    found_keywords.append(keyword)
                            
                            if found_keywords:
                                results.append({
                                    'url': url,
                                    'status': 'suspicious',
                                    'keywords_found': found_keywords,
                                    'content_length': len(content)
                                })
                                
                except Exception as e:
                    logger.error(f"Error scanning URL {url}: {e}")
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return results
    
    def generate_takedown_notice(self, content_id: str, 
                               infringing_url: str) -> str:
        """
        Generate a DMCA takedown notice template.
        
        Args:
            content_id: ID of infringed content
            infringing_url: URL where infringement was found
            
        Returns:
            Formatted takedown notice
        """
        if content_id not in self.fingerprints:
            raise ValueError(f"Content ID {content_id} not found in database")
        
        owner_info = self.fingerprints[content_id]['owner_info']
        
        template = f"""
DMCA TAKEDOWN NOTICE

To: {infringing_url}

I am writing to notify you of copyright infringement occurring on your platform.

COPYRIGHTED WORK:
Content ID: {content_id}
Owner: {owner_info.get('name', 'N/A')}
Contact: {owner_info.get('email', 'N/A')}

INFRINGING MATERIAL:
URL: {infringing_url}
Description: Unauthorized distribution of copyrighted video content

STATEMENT OF GOOD FAITH:
I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law.

STATEMENT OF ACCURACY:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the copyright owner.

Please remove or disable access to the infringing material immediately.

Generated by EthicalDRM on {np.datetime64('now')}
        """
        
        return template.strip()
    
    def extract_watermark(self, video_path: str) -> Optional[str]:
        """
        Extract watermark information from video (if present).
        
        Args:
            video_path: Path to video file
            
        Returns:
            Watermark text if found, None otherwise
        """
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Look for text in specific regions where watermarks are commonly placed
            regions = [
                (10, 10, 200, 50),  # Top-left
                (gray.shape[1]-200, 10, 200, 50),  # Top-right
                (10, gray.shape[0]-50, 200, 50),  # Bottom-left
                (gray.shape[1]-200, gray.shape[0]-50, 200, 50)  # Bottom-right
            ]
            
            for x, y, w, h in regions:
                roi = gray[y:y+h, x:x+w]
                
                # Apply threshold to make text more visible
                _, thresh = cv2.threshold(roi, 240, 255, cv2.THRESH_BINARY)
                
                # Look for patterns that might be watermarks
                # This is a simplified approach - in practice, you'd use more sophisticated techniques
                non_zero = cv2.countNonZero(thresh)
                if non_zero > 100:  # Arbitrary threshold
                    # Potential watermark found
                    logger.info(f"Potential watermark found in region {x},{y}")
                    # Here you would apply OCR or steganography extraction
                    return f"WATERMARK_REGION_{x}_{y}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting watermark: {e}")
            return None