import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')

    def do_OPTIONS(self):
        # 处理浏览器的预检请求 (CORS)
        self.send_response(204) # 204 No Content 是标准的 OPTIONS 返回码
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        # 允许跨域
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # 从 Vercel 环境变量获取真实的 API Key，绝不明文写在代码里！
        api_key = os.environ.get('VOLCENGINE_API_KEY')
        if not api_key:
            self.wfile.write(json.dumps({"error": "Server misconfiguration: Missing API Key"}).encode('utf-8'))
            return

        # 获取前端发来的 JSON 数据 (包含 prompt 和 base64 的文件)
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.wfile.write(json.dumps({"error": "Empty payload"}).encode('utf-8'))
            return
            
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            
            # 构造向火山引擎发送的请求
            url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 为了防止前端恶意修改其他参数，我们可以在这里进行一层校验或重组
            volcengine_payload = {
                "model": "doubao-seedance-2-0-260128",
                "content": payload.get('content', []),
                "generate_audio": True,
                "ratio": "16:9",
                "duration": 11,
                "watermark": False
            }
            
            req_data = json.dumps(volcengine_payload).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

            # 发送给火山引擎并原样返回结果
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.wfile.write(json.dumps({"task_id": result.get("id")}).encode('utf-8'))

        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            self.wfile.write(json.dumps({"error": f"API Error: {error_msg}"}).encode('utf-8'))
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))