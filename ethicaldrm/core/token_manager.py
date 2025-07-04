import jwt
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import base64

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages JWT tokens for secure video access control."""
    
    def __init__(self, secret_key: Optional[str] = None):
        if secret_key is None:
            secret_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        self.secret_key = secret_key
        self.algorithm = "HS256"
        
    def generate_token(self, 
                      user_id: str, 
                      video_id: str, 
                      expires_in: int = 7200,
                      additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a JWT token for video access.
        
        Args:
            user_id: Unique user identifier
            video_id: Video identifier
            expires_in: Token expiration time in seconds (default: 2 hours)
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        
        payload = {
            "user_id": user_id,
            "video_id": video_id,
            "iat": now,
            "exp": now + timedelta(seconds=expires_in),
            "jti": secrets.token_urlsafe(16),  # Token ID for revocation
        }
        
        if additional_claims:
            payload.update(additional_claims)
            
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Generated token for user {user_id}, video {video_id}")
            return token
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"Token validated for user {payload.get('user_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise
    
    def validate_access(self, token: str, video_id: str, user_id: Optional[str] = None) -> bool:
        """
        Validate if token allows access to specific video.
        
        Args:
            token: JWT token string
            video_id: Video identifier to check access for
            user_id: Optional user ID to verify against token
            
        Returns:
            True if access is allowed, False otherwise
        """
        try:
            payload = self.validate_token(token)
            
            # Check video access
            if payload.get("video_id") != video_id:
                logger.warning(f"Token video mismatch: expected {video_id}, got {payload.get('video_id')}")
                return False
            
            # Check user if provided
            if user_id and payload.get("user_id") != user_id:
                logger.warning(f"Token user mismatch: expected {user_id}, got {payload.get('user_id')}")
                return False
                
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information without validation (for debugging)."""
        try:
            # Decode without verification
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None
    
    def create_download_token(self, 
                            user_id: str, 
                            video_id: str, 
                            segment_name: str,
                            expires_in: int = 300) -> str:
        """
        Create a short-lived token for segment download.
        
        Args:
            user_id: User identifier
            video_id: Video identifier
            segment_name: Specific segment file name
            expires_in: Token expiration (default: 5 minutes)
            
        Returns:
            JWT token for segment access
        """
        return self.generate_token(
            user_id=user_id,
            video_id=video_id,
            expires_in=expires_in,
            additional_claims={
                "segment": segment_name,
                "type": "download"
            }
        )
    
    def validate_segment_access(self, token: str, video_id: str, segment_name: str) -> bool:
        """Validate access to specific video segment."""
        try:
            payload = self.validate_token(token)
            
            # Check basic access
            if not self.validate_access(token, video_id):
                return False
            
            # For download tokens, check segment access
            if payload.get("type") == "download":
                allowed_segment = payload.get("segment")
                if allowed_segment and allowed_segment != segment_name:
                    logger.warning(f"Segment access denied: {segment_name} not in token")
                    return False
            
            return True
            
        except jwt.InvalidTokenError:
            return False