"""
TikTok Upload Module

Handles uploading images to Cloudflare R2 and posting to TikTok via Content Posting API
"""

import os
import base64
import json
import secrets
import threading
import time
import webbrowser
import hashlib
import ssl
import ipaddress
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlencode, parse_qs
import requests
from flask import Flask, request, jsonify
from PIL import Image
import gratient
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import boto3
from botocore.client import Config
from .utils.logger import logger

# Configure Flask logging to only show errors
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)


class TikTokUploadError(Exception):
    """Custom exception for TikTok upload errors"""
    pass


class CloudflareR2Uploader:
    """Cloudflare R2 storage handler"""
    
    def __init__(self):
        self.endpoint_url = os.environ.get('CLOUDFLARE_R2_ENDPOINT_URL')
        self.access_key_id = os.environ.get('CLOUDFLARE_R2_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.environ.get('CLOUDFLARE_R2_BUCKET_NAME')
        self.public_url_base = os.environ.get('CLOUDFLARE_R2_PUBLIC_URL_BASE')
        
        if not all([self.endpoint_url, self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise TikTokUploadError("Missing required Cloudflare R2 environment variables")
        
        # Initialize R2 client - variables guaranteed to be non-None after validation above
        self.client = boto3.client(  # type: ignore
            's3',
            endpoint_url=self.endpoint_url,  # type: ignore
            aws_access_key_id=self.access_key_id,  # type: ignore
            aws_secret_access_key=self.secret_access_key,  # type: ignore
            config=Config(signature_version='s3v4')
        )
    
    def upload_image(self, image_path: str, object_key: Optional[str] = None) -> str:
        """Upload image to Cloudflare R2 and return public URL"""
        if not object_key:
            # Generate unique object key
            timestamp = int(time.time())
            filename = Path(image_path).name
            object_key = f"levibes/{timestamp}_{filename}"
        
        try:
            # Upload file to R2
            with open(image_path, 'rb') as file:
                self.client.upload_fileobj(
                    file,
                    self.bucket_name,
                    object_key,
                    ExtraArgs={
                        'ContentType': 'image/jpeg',
                        'ACL': 'public-read'
                    }
                )
            
            # Return public URL
            if self.public_url_base:
                # Use provided public URL base (r2.dev subdomain or custom domain)
                return f"{self.public_url_base.rstrip('/')}/{object_key}"
            else:
                # Fallback: construct URL using bucket name with endpoint
                # This assumes the bucket has public access enabled
                endpoint_with_bucket = self.endpoint_url.replace('https://', f'https://{self.bucket_name}.')  # type: ignore
                return f"{endpoint_with_bucket}/{object_key}"
                
        except Exception as e:
            raise TikTokUploadError(f"Failed to upload {image_path} to R2: {str(e)}")


class TikTokOAuthServer:
    """Temporary OAuth server for TikTok authentication"""
    
    def __init__(self, client_id: str, client_secret: str, port: int = 8080):
        self.client_id = client_id
        self.client_secret = client_secret
        self.port = port
        self.redirect_uri = f"https://tiktoklocal.com:{port}/callback"
        self.state = secrets.token_urlsafe(32)
        # PKCE parameters
        self.code_verifier = secrets.token_urlsafe(32)
        self.code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self.code_verifier.encode()).digest()
        ).decode().rstrip('=')
        self.authorization_code = None
        self.access_token = None
        
        # Configure Flask app with minimal logging
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.ERROR)
        
        # Disable Flask's default logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        self.cert_path = Path("tiktoklocal.crt")
        self.key_path = Path("tiktoklocal.key")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for OAuth callback"""
        @self.app.route('/callback')
        def callback():
            # Get authorization code from callback
            code = request.args.get('code')
            state = request.args.get('state')
            error = request.args.get('error')
            
            if error:
                return jsonify({'error': f'Authorization failed: {error}'}), 400
            
            if state != self.state:
                return jsonify({'error': 'Invalid state parameter'}), 400
            
            if not code:
                return jsonify({'error': 'No authorization code received'}), 400
            
            self.authorization_code = code
            
            # Exchange code for access token
            try:
                self.access_token = self.exchange_code_for_token(code)
                return '''
                <html>
                <body>
                    <h2>Authorization successful!</h2>
                    <p>You can now close this window and return to the application.</p>
                    <script>setTimeout(function(){window.close();}, 3000);</script>
                </body>
                </html>
                '''
            except Exception as e:
                return jsonify({'error': f'Token exchange failed: {str(e)}'}), 500
    
    def is_cert_valid(self) -> bool:
        """Check if existing certificate is still valid"""
        try:
            if not self.cert_path.exists() or not self.key_path.exists():
                return False
            
            # Load and check certificate expiration
            with open(self.cert_path, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Check if certificate expires within 30 days
            expires_soon = datetime.datetime.utcnow() + datetime.timedelta(days=30)
            return cert.not_valid_after > expires_soon
            
        except Exception:
            return False
    
    def generate_self_signed_cert(self):
        """Generate self-signed SSL certificate for tiktoklocal.com"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "TikTok Local"),
            x509.NameAttribute(NameOID.COMMON_NAME, "tiktoklocal.com"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("tiktoklocal.com"),
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key
        with open(self.key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        
        data = {
            "client_key": self.client_id,  # TikTok now uses client_key instead of client_id
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier,
        }
        
        response = requests.post(token_url, data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        return response.json()["access_token"]
    
    def get_auth_url(self) -> str:
        """Get the authorization URL"""
        auth_url = "https://www.tiktok.com/v2/auth/authorize/"
        params = {
            "client_key": self.client_id,  # TikTok now uses client_key instead of client_id
            "response_type": "code",
            "scope": "user.info.basic,video.upload",
            "redirect_uri": self.redirect_uri,
            "state": self.state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
        
        return f"{auth_url}?{urlencode(params)}"
    
    def start_auth_flow(self, timeout: int = 120) -> str:
        """Start OAuth flow and return access token"""
        # Generate SSL certificate if it doesn't exist or is expired
        if not self.is_cert_valid():
            logger.progress("Generating SSL certificate")
            self.generate_self_signed_cert()
        
        # Start Flask server in a separate thread
        def run_server():
            try:
                # Use threaded=True and disable request logging
                self.app.run(
                    host='0.0.0.0',
                    port=self.port,
                    ssl_context=(str(self.cert_path), str(self.key_path)),
                    threaded=True,
                    use_reloader=False,
                    debug=False
                )
            except Exception as e:
                logger.error(f"Flask server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server time to start
        time.sleep(2)
        
        # Open browser for authentication
        auth_url = self.get_auth_url()
        logger.progress("Opening browser for TikTok authentication")
        webbrowser.open(auth_url)
        
        # Wait for callback
        start_time = time.time()
        while self.access_token is None and time.time() - start_time < timeout:
            time.sleep(1)
        
        if self.access_token is None:
            raise TikTokUploadError("Authentication timed out")
        
        logger.success("TikTok authentication successful")
        return self.access_token
    
    def cleanup(self):
        """Clean up temporary files"""
        # Keep certificate files for reuse - they're valid for 365 days
        # Only clean up if needed in the future
        pass


class TikTokUploader:
    """Main TikTok uploader class"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.r2_uploader = CloudflareR2Uploader()
    
    def authenticate(self) -> str:
        """Authenticate with TikTok and return access token"""
        oauth_server = TikTokOAuthServer(self.client_id, self.client_secret)
        self.access_token = oauth_server.start_auth_flow()
        oauth_server.cleanup()
        return self.access_token
    
    def convert_png_to_jpeg(self, image_path: str) -> str:
        """Convert PNG to JPEG if needed"""
        if not image_path.lower().endswith('.png'):
            return image_path
        
        jpeg_path = image_path.rsplit('.', 1)[0] + '.jpg'
        
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if needed
                if img.mode in ("RGBA", "LA", "P"):
                    # Create white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
                
                # Save as JPEG
                img.save(jpeg_path, "JPEG", quality=95)
            
            return jpeg_path
        except Exception as e:
            logger.error(f"Failed to convert PNG to JPEG: {e}")
            return image_path
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information from TikTok"""
        if not self.access_token:
            raise TikTokUploadError("Not authenticated")
        
        url = "https://open.tiktokapis.com/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise TikTokUploadError(f"Failed to get user info: {response.text}")
        
        return response.json()
    
    def upload_images_to_r2(self, image_paths: List[str]) -> List[str]:
        """Upload images to Cloudflare R2"""
        logger.progress("Uploading images to cloud storage")
        
        urls = []
        for i, image_path in enumerate(image_paths):
            # Convert PNG to JPEG if needed
            converted_path = self.convert_png_to_jpeg(image_path)
            
            # Upload to R2
            url = self.r2_uploader.upload_image(converted_path)
            urls.append(url)
            
            # Clean up converted file if it was created
            if converted_path != image_path and os.path.exists(converted_path):
                os.remove(converted_path)
        
        logger.success(f"Uploaded {len(urls)} images to cloud storage")
        return urls
    
    def upload_photos_as_draft(self, image_urls: List[str], title: str = "", hashtags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upload photos to TikTok as draft"""
        if not self.access_token:
            raise TikTokUploadError("Not authenticated")
        
        logger.progress("Creating TikTok draft")
        
        # Prepare post data
        post_data = {
            "media_type": "PHOTO",
            "post_mode": "MEDIA_UPLOAD",  # Upload to inbox for user to complete
            "post_info": {
                "title": title,
                "description": "",  # Will be set below based on hashtags
                "disable_comment": False,
                "auto_add_music": True,
                "brand_content_toggle": False,
                "brand_organic_toggle": False
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 0,
                "photo_images": image_urls
            }
        }
        
        # Add hashtags to description if provided
        if hashtags:
            hashtag_str = " ".join(f"{tag}" for tag in hashtags)
            post_data["post_info"]["description"] = f"{title} {hashtag_str}".strip()
        else:
            post_data["post_info"]["description"] = title
        
        # Upload to TikTok
        url = "https://open.tiktokapis.com/v2/post/publish/content/init/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        response = requests.post(url, json=post_data, headers=headers)
        
        if response.status_code != 200:
            raise TikTokUploadError(f"Failed to create TikTok draft: {response.text}")
        
        result = response.json()
        logger.success("TikTok draft created successfully")
        return result
    
    def get_upload_status(self, publish_id: str) -> Dict[str, Any]:
        """Get upload status"""
        if not self.access_token:
            raise TikTokUploadError("Not authenticated")
        
        url = f"https://open.tiktokapis.com/v2/post/publish/status/fetch/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {"publish_id": publish_id}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise TikTokUploadError(f"Failed to get upload status: {response.text}")
        
        return response.json()


def validate_tiktok_env() -> Tuple[str, str]:
    """Validate TikTok environment variables"""
    client_id = os.environ.get('TIKTOK_CLIENT_ID')
    client_secret = os.environ.get('TIKTOK_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise TikTokUploadError("TIKTOK_CLIENT_ID and TIKTOK_CLIENT_SECRET must be set")
    
    return client_id, client_secret


def validate_r2_env():
    """Validate Cloudflare R2 environment variables"""
    required_vars = [
        'CLOUDFLARE_R2_ENDPOINT_URL',
        'CLOUDFLARE_R2_ACCESS_KEY_ID',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_BUCKET_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise TikTokUploadError(f"Missing required R2 environment variables: {', '.join(missing_vars)}")


def get_image_files(output_dir: str, outro_image: str = "outro.png") -> List[str]:
    """Get list of image files from output directory"""
    image_files = []
    
    # Get all generated images
    for file in os.listdir(output_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and file.startswith('captioned_'):
            image_files.append(os.path.join(output_dir, file))
    
    # Sort by filename for consistent ordering
    image_files.sort()
    
    # Add outro image if it exists
    if outro_image and os.path.exists(outro_image):
        image_files.append(outro_image)
    elif outro_image:
        logger.warning(f"Outro image not found: {outro_image}")
    
    if not image_files:
        raise TikTokUploadError(f"No images found in {output_dir}")
    
    return image_files


def upload_to_tiktok(output_dir: str, caption_data=None, outro_image: str = "outro.png") -> bool:
    """Upload images to TikTok"""
    try:
        # Validate environment
        client_id, client_secret = validate_tiktok_env()
        validate_r2_env()
        
        # Get image files
        image_files = get_image_files(output_dir, outro_image)
        logger.info(f"Found {len(image_files)} images to upload")
        
        # Initialize uploader
        uploader = TikTokUploader(client_id, client_secret)
        
        # Authenticate
        logger.progress("Authenticating with TikTok")
        uploader.authenticate()
        
        # Upload images to R2
        image_urls = uploader.upload_images_to_r2(image_files)
        
        # Prepare caption data
        title = ""
        hashtags = None
        
        if caption_data:
            if hasattr(caption_data, 'title') and hasattr(caption_data, 'hashtags'):
                # TikTokCaption object
                title = caption_data.title
                hashtags = caption_data.hashtags
            else:
                # String caption
                title = str(caption_data)
        
        # Upload to TikTok
        result = uploader.upload_photos_as_draft(image_urls, title, hashtags)
        
        logger.success("Images uploaded to TikTok as draft")
        logger.info("Check your TikTok app inbox to review and publish")
        
        return True
        
    except TikTokUploadError as e:
        logger.error(f"TikTok upload failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during TikTok upload: {e}")
        return False
