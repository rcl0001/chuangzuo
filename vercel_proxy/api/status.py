import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 允许跨域
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        api_key = os.environ.get('VOLCENGINE_API_KEY')
        if not api_key:
            self.wfile.write(json.dumps({"error": "Server misconfiguration"}).encode('utf-8'))
            return

        # 解析 URL 路径获取 task_id
        # 例如: /api/status?task_id=cgt-12345
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        task_id = query_params.get('task_id', [None])[0]
        if not task_id:
            self.wfile.write(json.dumps({"error": "Missing task_id parameter"}).encode('utf-8'))
            return
            
        url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        req = urllib.request.Request(url, headers=headers, method='GET')

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                # 直接将火山引擎的状态返回给前端，前端再去下载视频
                self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()