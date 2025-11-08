from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            facebook_url = query_params.get('url', [None])[0]
            
            if not facebook_url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "URL parameter is required"
                }).encode())
                return
            
            # Simulate Facebook video data extraction
            result = self.get_facebook_video_data(facebook_url)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'public, max-age=0, must-revalidate')
            self.send_header('X-Powered-By', 'Lord Axshu Downloader')
            self.end_headers()
            
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode())
    
    def get_facebook_video_data(self, facebook_url):
        """Extract Facebook video data"""
        return {
            "developer": "Lord Axshu",
            "facebook": "https://facebook.com/lordaxshu",
            "source": "axshu-downloader.net",
            "fetched_at": "2025-11-08T11:50:12.642Z",
            "input_url": facebook_url,
            "links": [
                {
                    "quality": "sd",
                    "url": f"https://video-cdn.axshu.net/videos/sd/{hash(facebook_url)}.mp4"
                },
                {
                    "quality": "hd", 
                    "url": f"https://video-cdn.axshu.net/videos/hd/{hash(facebook_url)}.mp4"
                },
                {
                    "quality": "4k",
                    "url": f"https://video-cdn.axshu.net/videos/4k/{hash(facebook_url)}.mp4"
                }
            ]
        }
