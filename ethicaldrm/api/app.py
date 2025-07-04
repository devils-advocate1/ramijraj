import os
import logging
from pathlib import Path
from flask import Flask, request, jsonify, Response, send_file, abort
from flask_cors import CORS
import click

from ..core.token_manager import TokenManager
from ..core.stream_server import StreamServer
from ..core.encryption import VideoEncryption
from ..utils.security import SecurityUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['CONTENT_DIR'] = os.getenv('CONTENT_DIR', 'encrypted_output')
app.config['MAX_TOKEN_DURATION'] = int(os.getenv('MAX_TOKEN_DURATION', '7200'))  # 2 hours

# Initialize components
token_manager = TokenManager(app.config['SECRET_KEY'])
stream_server = StreamServer(app.config['CONTENT_DIR'], token_manager)
video_encryption = VideoEncryption(app.config['CONTENT_DIR'])
security_utils = SecurityUtils()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "EthicalDRM API"})


@app.route('/generate_token', methods=['POST'])
def generate_token():
    """
    Generate access token for video streaming.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "video_id": "video456", 
        "expires_in": 3600
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON payload required"}), 400
            
        user_id = data.get('user_id')
        video_id = data.get('video_id')
        expires_in = data.get('expires_in', 3600)
        
        if not user_id or not video_id:
            return jsonify({"error": "user_id and video_id are required"}), 400
            
        # Validate expiration time
        if expires_in > app.config['MAX_TOKEN_DURATION']:
            expires_in = app.config['MAX_TOKEN_DURATION']
            
        # Check if video exists
        video_info = stream_server.get_video_info(video_id)
        if not video_info:
            return jsonify({"error": "Video not found"}), 404
            
        # Generate token
        token = token_manager.generate_token(user_id, video_id, expires_in)
        
        return jsonify({
            "token": token,
            "expires_in": expires_in,
            "user_id": user_id,
            "video_id": video_id,
            "playlist_url": f"/get_stream/{video_id}.m3u8?token={token}"
        })
        
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/get_stream/<video_id>.m3u8', methods=['GET'])
def get_playlist(video_id):
    """Get HLS playlist with secure URLs."""
    token = request.args.get('token')
    
    if not token:
        return jsonify({"error": "Token required"}), 401
        
    content, status_code = stream_server.get_playlist(video_id, token)
    
    if content is None:
        if status_code == 401:
            return jsonify({"error": "Invalid or expired token"}), 401
        elif status_code == 404:
            return jsonify({"error": "Video not found"}), 404
        else:
            return jsonify({"error": "Internal server error"}), 500
            
    return Response(content, 
                   mimetype='application/vnd.apple.mpegurl',
                   headers={
                       'Cache-Control': 'no-cache, no-store, must-revalidate',
                       'Pragma': 'no-cache',
                       'Expires': '0'
                   })


@app.route('/get_segment', methods=['GET'])
def get_segment():
    """Get video segment."""
    video_id = request.args.get('video')
    segment = request.args.get('segment')
    token = request.args.get('token')
    
    if not all([video_id, segment, token]):
        return jsonify({"error": "video, segment, and token parameters required"}), 400
        
    data, status_code, headers = stream_server.get_segment(video_id, segment, token)
    
    if data is None:
        if status_code == 401:
            return jsonify({"error": "Invalid or expired token"}), 401
        elif status_code == 404:
            return jsonify({"error": "Segment not found"}), 404
        else:
            return jsonify({"error": "Internal server error"}), 500
            
    return Response(data, mimetype='video/mp2t', headers=headers)


@app.route('/get_key', methods=['GET'])
def get_encryption_key():
    """Get encryption key for video."""
    video_id = request.args.get('video')
    token = request.args.get('token')
    
    if not video_id or not token:
        return jsonify({"error": "video and token parameters required"}), 400
        
    data, status_code, headers = stream_server.get_encryption_key(video_id, token)
    
    if data is None:
        if status_code == 401:
            return jsonify({"error": "Invalid or expired token"}), 401
        elif status_code == 404:
            return jsonify({"error": "Key not found"}), 404
        else:
            return jsonify({"error": "Internal server error"}), 500
            
    return Response(data, mimetype='application/octet-stream', headers=headers)


@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Upload and encrypt video."""
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
        
    file = request.files['video']
    video_id = request.form.get('video_id')
    user_id = request.form.get('user_id')  # For watermarking
    
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400
        
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    try:
        # Save uploaded file temporarily
        upload_path = Path('temp_uploads')
        upload_path.mkdir(exist_ok=True)
        temp_file = upload_path / f"{video_id}_{file.filename}"
        file.save(temp_file)
        
        # Add watermark if user_id provided
        input_file = str(temp_file)
        if user_id:
            input_file = video_encryption.add_watermark(input_file, user_id)
            
        # Encrypt video
        result = video_encryption.encrypt_video(input_file, video_id)
        
        # Clean up temporary files
        temp_file.unlink(missing_ok=True)
        if user_id and Path(input_file).exists():
            Path(input_file).unlink(missing_ok=True)
            
        return jsonify({
            "message": "Video encrypted successfully",
            "video_id": video_id,
            "details": result
        })
        
    except Exception as e:
        logger.error(f"Video upload/encryption error: {e}")
        return jsonify({"error": "Video processing failed"}), 500


@app.route('/video_info/<video_id>', methods=['GET'])
def get_video_info(video_id):
    """Get video information."""
    info = stream_server.get_video_info(video_id)
    
    if not info:
        return jsonify({"error": "Video not found"}), 404
        
    return jsonify(info)


@app.route('/validate_token', methods=['POST'])
def validate_token():
    """Validate token and return information."""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({"error": "Token required"}), 400
        
    token = data['token']
    
    try:
        payload = token_manager.validate_token(token)
        return jsonify({
            "valid": True,
            "payload": payload
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


def create_app(config=None):
    """Application factory."""
    if config:
        app.config.update(config)
    return app


@click.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--content-dir', default='encrypted_output', help='Content directory')
def main(host, port, debug, content_dir):
    """Run the EthicalDRM API server."""
    app.config['CONTENT_DIR'] = content_dir
    
    # Ensure content directory exists
    Path(content_dir).mkdir(exist_ok=True, parents=True)
    
    print(f"🔐 EthicalDRM API starting on http://{host}:{port}")
    print(f"📁 Content directory: {content_dir}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()