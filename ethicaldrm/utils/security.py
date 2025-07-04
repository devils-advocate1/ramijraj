import os
import sys
import psutil
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utilities for content protection."""
    
    # Common screen recording applications
    SCREEN_RECORDERS = [
        'obs64.exe', 'obs32.exe', 'obs.exe',  # OBS Studio
        'bandicam.exe',  # Bandicam
        'camtasia.exe',  # Camtasia
        'fraps.exe',  # Fraps
        'xboxgamebar.exe',  # Xbox Game Bar
        'simplescreenrecorder',  # Simple Screen Recorder (Linux)
        'kazam',  # Kazam (Linux)
        'recordmydesktop',  # RecordMyDesktop (Linux)
        'quicktime player',  # QuickTime (Mac)
        'screenflow',  # ScreenFlow (Mac)
        'snagit.exe',  # SnagIt
        'flashback.exe',  # FlashBack
        'movavi.exe',  # Movavi Screen Recorder
        'captureone.exe',  # Capture One
    ]
    
    # Browser extensions that might download videos
    SUSPICIOUS_EXTENSIONS = [
        'video downloader',
        'download helper',
        'jdownloader',
        'idm',
        'flashgot',
        'video downloadhelper'
    ]
    
    def __init__(self):
        self.monitoring_enabled = True
        
    def detect_screen_recorders(self) -> List[Dict[str, Any]]:
        """
        Detect running screen recording applications.
        
        Returns:
            List of detected screen recording processes
        """
        detected = []
        
        try:
            for process in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    process_name = process.info['name']
                    if process_name:
                        process_name_lower = process_name.lower()
                        
                        for recorder in self.SCREEN_RECORDERS:
                            if recorder.lower() in process_name_lower:
                                detected.append({
                                    'pid': process.info['pid'],
                                    'name': process.info['name'],
                                    'exe': process.info['exe'],
                                    'type': 'screen_recorder'
                                })
                                logger.warning(f"Detected screen recorder: {process_name}")
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error detecting screen recorders: {e}")
            
        return detected
    
    def detect_suspicious_processes(self) -> List[Dict[str, Any]]:
        """
        Detect processes that might be used for content theft.
        
        Returns:
            List of suspicious processes
        """
        suspicious = []
        
        # Keywords that might indicate downloading/recording tools
        suspicious_keywords = [
            'download', 'capture', 'record', 'rip', 'extract',
            'ffmpeg', 'vlc', 'youtube-dl', 'yt-dlp'
        ]
        
        try:
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    process_name = process.info['name']
                    cmdline = ' '.join(process.info['cmdline'] or [])
                    
                    if process_name:
                        process_text = f"{process_name} {cmdline}".lower()
                        
                        for keyword in suspicious_keywords:
                            if keyword in process_text:
                                suspicious.append({
                                    'pid': process.info['pid'],
                                    'name': process.info['name'],
                                    'cmdline': cmdline,
                                    'keyword': keyword,
                                    'type': 'suspicious'
                                })
                                logger.warning(f"Detected suspicious process: {process_name}")
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error detecting suspicious processes: {e}")
            
        return suspicious
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for security analysis."""
        try:
            return {
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                'running_processes': len(psutil.pids()),
                'network_connections': len(psutil.net_connections()),
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def generate_security_headers(self) -> Dict[str, str]:
        """Generate security headers for HTTP responses."""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "media-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': (
                "camera=(), microphone=(), geolocation=(), "
                "usb=(), screen-wake-lock=(), web-share=()"
            )
        }
    
    def check_browser_extensions(self, user_agent: str) -> List[str]:
        """
        Check for suspicious browser extensions based on user agent.
        
        Args:
            user_agent: HTTP User-Agent header
            
        Returns:
            List of potential security concerns
        """
        concerns = []
        
        ua_lower = user_agent.lower()
        
        # Check for modified user agents that might indicate automation
        if any(keyword in ua_lower for keyword in ['selenium', 'webdriver', 'bot', 'crawler']):
            concerns.append("Automated browser detected")
            
        # Check for common downloading tools
        if any(keyword in ua_lower for keyword in ['wget', 'curl', 'python', 'java']):
            concerns.append("Command-line tool detected")
            
        return concerns
    
    def generate_client_protection_script(self) -> str:
        """
        Generate JavaScript code for client-side protection.
        
        Returns:
            JavaScript code string
        """
        return """
        // EthicalDRM Client Protection
        (function() {
            'use strict';
            
            // Disable right-click context menu
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;
            });
            
            // Disable common keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Disable F12, Ctrl+Shift+I, Ctrl+U, etc.
                if (e.keyCode === 123 || 
                    (e.ctrlKey && e.shiftKey && e.keyCode === 73) ||
                    (e.ctrlKey && e.keyCode === 85) ||
                    (e.ctrlKey && e.shiftKey && e.keyCode === 74)) {
                    e.preventDefault();
                    return false;
                }
            });
            
            // Detect developer tools
            let devtools = {
                open: false,
                orientation: null
            };
            
            const threshold = 160;
            const checkDevTools = () => {
                if (window.outerHeight - window.innerHeight > threshold || 
                    window.outerWidth - window.innerWidth > threshold) {
                    if (!devtools.open) {
                        devtools.open = true;
                        console.warn('Developer tools detected - content access may be restricted');
                        // You could send an alert to your server here
                    }
                } else {
                    devtools.open = false;
                }
            };
            
            setInterval(checkDevTools, 500);
            
            // Disable text selection
            document.addEventListener('selectstart', function(e) {
                e.preventDefault();
                return false;
            });
            
            // Disable drag and drop
            document.addEventListener('dragstart', function(e) {
                e.preventDefault();
                return false;
            });
            
            // Clear console
            if (typeof console !== 'undefined') {
                console.clear();
                console.log('%cEthicalDRM Protected Content', 'color: red; font-size: 20px; font-weight: bold;');
                console.log('%cContent is protected by EthicalDRM. Unauthorized access is prohibited.', 'color: red;');
            }
            
            // Monitor for screen recording APIs
            if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
                const originalGetDisplayMedia = navigator.mediaDevices.getDisplayMedia;
                navigator.mediaDevices.getDisplayMedia = function() {
                    console.warn('Screen recording attempt detected');
                    // You could send an alert to your server here
                    return Promise.reject(new Error('Screen recording is not allowed'));
                };
            }
        })();
        """
    
    def create_security_report(self) -> Dict[str, Any]:
        """Create a comprehensive security report."""
        return {
            'timestamp': psutil.boot_time(),
            'screen_recorders': self.detect_screen_recorders(),
            'suspicious_processes': self.detect_suspicious_processes(),
            'system_info': self.get_system_info(),
            'monitoring_enabled': self.monitoring_enabled
        }