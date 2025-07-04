#!/usr/bin/env python3
"""
EthicalDRM Installation Test
Tests core functionality to verify the installation is working correctly.
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import ethicaldrm
        print(f"✅ Main package imported: v{ethicaldrm.__version__}")
        
        from ethicaldrm import VideoEncryption, TokenManager, LeakDetector
        from ethicaldrm.utils.security import SecurityUtils
        print("✅ Core modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🔍 Testing dependencies...")
    
    dependencies = [
        ('flask', 'Flask'),
        ('jwt', 'PyJWT'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
        ('psutil', 'psutil'),
        ('click', 'Click'),
        ('ffmpeg', 'ffmpeg-python')
    ]
    
    all_good = True
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} not found")
            all_good = False
    
    return all_good

def test_ffmpeg():
    """Test that FFmpeg is available."""
    print("\n🔍 Testing FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ FFmpeg not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ FFmpeg not found in PATH")
        print("   Please install FFmpeg: https://ffmpeg.org/")
        return False

def test_token_manager():
    """Test TokenManager functionality."""
    print("\n🔍 Testing TokenManager...")
    
    try:
        from ethicaldrm import TokenManager
        
        token_mgr = TokenManager("test-secret-key")
        
        # Generate token
        token = token_mgr.generate_token("test_user", "test_video", expires_in=3600)
        print("✅ Token generation")
        
        # Validate token
        payload = token_mgr.validate_token(token)
        assert payload['user_id'] == 'test_user'
        assert payload['video_id'] == 'test_video'
        print("✅ Token validation")
        
        # Check access validation
        assert token_mgr.validate_access(token, "test_video")
        assert not token_mgr.validate_access(token, "wrong_video")
        print("✅ Access validation")
        
        return True
    except Exception as e:
        print(f"❌ TokenManager test failed: {e}")
        return False

def test_security_utils():
    """Test SecurityUtils functionality."""
    print("\n🔍 Testing SecurityUtils...")
    
    try:
        from ethicaldrm.utils.security import SecurityUtils
        
        security = SecurityUtils()
        
        # Test system info
        sys_info = security.get_system_info()
        assert 'platform' in sys_info
        print("✅ System info retrieval")
        
        # Test security headers
        headers = security.generate_security_headers()
        assert 'X-Content-Type-Options' in headers
        print("✅ Security headers generation")
        
        # Test protection script
        script = security.generate_client_protection_script()
        assert len(script) > 100  # Should be a substantial script
        print("✅ Client protection script")
        
        return True
    except Exception as e:
        print(f"❌ SecurityUtils test failed: {e}")
        return False

def test_video_encryption():
    """Test VideoEncryption (basic functionality only)."""
    print("\n🔍 Testing VideoEncryption (basic)...")
    
    try:
        from ethicaldrm import VideoEncryption
        
        with tempfile.TemporaryDirectory() as temp_dir:
            encryptor = VideoEncryption(temp_dir)
            
            # Test key generation
            key = encryptor.generate_encryption_key()
            assert len(key) == 16  # AES-128 key
            print("✅ Encryption key generation")
            
            # Test key info file creation
            key_path = os.path.join(temp_dir, "test.key")
            with open(key_path, 'wb') as f:
                f.write(key)
            
            key_info_path = encryptor.create_key_info_file(key_path)
            assert Path(key_info_path).exists()
            print("✅ Key info file creation")
        
        return True
    except Exception as e:
        print(f"❌ VideoEncryption test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI commands are accessible."""
    print("\n🔍 Testing CLI commands...")
    
    commands = ['ethicaldrm', 'ethicaldrm-api']
    
    all_good = True
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--help'], 
                                  capture_output=True, 
                                  timeout=10)
            if result.returncode == 0:
                print(f"✅ {cmd} command available")
            else:
                print(f"❌ {cmd} command failed")
                all_good = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {cmd} command not found")
            all_good = False
    
    return all_good

def main():
    """Run all installation tests."""
    print("🔐 EthicalDRM Installation Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("FFmpeg", test_ffmpeg),
        ("TokenManager", test_token_manager),
        ("SecurityUtils", test_security_utils),
        ("VideoEncryption", test_video_encryption),
        ("CLI Commands", test_cli_commands),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! EthicalDRM is ready to use.")
        print("\nNext steps:")
        print("1. Try the quick start: python examples/quick_start.py")
        print("2. Start the API server: ethicaldrm-api")
        print("3. Check the documentation: README.md")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed.")
        print("Please check the error messages above and ensure all dependencies are installed.")
        print("See README.md for installation instructions.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())