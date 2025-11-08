from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs
import re
import time

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
            
            # Extract Facebook video data
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
        """Extract actual Facebook video download links"""
        try:
            # Method 1: Use Facebook's official graph API (if available)
            video_links = self.extract_from_facebook(facebook_url)
            
            # Method 2: Use third-party API as fallback
            if not video_links:
                video_links = self.extract_from_third_party(facebook_url)
            
            # Method 3: Use web scraping as last resort
            if not video_links:
                video_links = self.extract_via_scraping(facebook_url)
            
            return {
                "success": True,
                "developer": "Lord Axshu",
                "facebook": "https://facebook.com/lordaxshu",
                "source": "axshu-downloader.net",
                "fetched_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "input_url": facebook_url,
                "video_id": self.extract_video_id(facebook_url),
                "links": video_links,
                "message": "Use the download URLs to get the video"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "developer": "Lord Axshu",
                "input_url": facebook_url
            }
    
    def extract_from_facebook(self, facebook_url):
        """Try to extract from Facebook directly"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(facebook_url, headers=headers, timeout=10)
            
            # Look for video URLs in the response
            video_patterns = [
                r'"playable_url":"([^"]+)"',
                r'"playable_url_quality_hd":"([^"]+)"',
                r'src="([^"]+\.mp4[^"]*)"',
                r'video_url":"([^"]+)"'
            ]
            
            video_links = []
            for pattern in video_patterns:
                matches = re.findall(pattern, response.text)
                for match in matches:
                    # Clean the URL
                    video_url = match.replace('\\/', '/')
                    if '.mp4' in video_url and 'video' in video_url.lower():
                        video_links.append({
                            "quality": "unknown",
                            "url": video_url,
                            "direct": True
                        })
            
            return video_links[:3]  # Return first 3 links
            
        except:
            return []
    
    def extract_from_third_party(self, facebook_url):
        """Use third-party Facebook video downloader APIs"""
        try:
            # Using a popular Facebook video downloader API
            api_url = "https://getmyfb.com/form"
            payload = {
                'url': facebook_url
            }
            
            response = requests.post(api_url, data=payload, timeout=15)
            
            # Parse response for download links
            if response.status_code == 200:
                # Look for HD quality
                hd_pattern = r'href="(https://[^"]*hd[^"]*\.mp4)"'
                sd_pattern = r'href="(https://[^"]*\.mp4)"'
                
                video_links = []
                
                hd_matches = re.findall(hd_pattern, response.text, re.IGNORECASE)
                for url in hd_matches[:1]:
                    video_links.append({
                        "quality": "hd",
                        "url": url,
                        "direct": True
                    })
                
                sd_matches = re.findall(sd_pattern, response.text, re.IGNORECASE)
                for url in sd_matches[:2]:
                    if not any(url in link['url'] for link in video_links):
                        video_links.append({
                            "quality": "sd",
                            "url": url,
                            "direct": True
                        })
                
                return video_links
                
        except:
            pass
        
        return []
    
    def extract_via_scraping(self, facebook_url):
        """Alternative scraping method"""
        try:
            # Using another third-party service
            services = [
                "https://fbdown.net/download.php",
                "https://getfbstuff.com/facebook-video-downloader"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, params={'url': facebook_url}, timeout=10)
                    
                    # Common patterns in download pages
                    patterns = [
                        r'download.*?href="([^"]+\.mp4)"',
                        r'href="(https://[^"]*fbcdn[^"]*\.mp4)"',
                        r'video_download_url.*?"([^"]+)"'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        for url in matches[:2]:
                            return [{
                                "quality": "sd",
                                "url": url,
                                "direct": True
                            }]
                            
                except:
                    continue
                    
        except:
            pass
        
        return []
    
    def extract_video_id(self, url):
        """Extract video ID from Facebook URL"""
        patterns = [
            r'videos?/(\d+)',
            r'video\.php\?v=(\d+)',
            r'/(\d+)/?$',
            r'share/r/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return "unknown"
