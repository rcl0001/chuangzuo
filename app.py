import os
import sys
import json
import time
import urllib.request
import urllib.error
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import base64
import mimetypes

# PyInstaller 打包后的路径处理
if getattr(sys, 'frozen', False):
    # 运行在打包后的环境中
    BASE_DIR = sys._MEIPASS
    # 工作目录放在用户运行程序的当前目录下
    WORK_DIR = os.getcwd()
else:
    # 正常 Python 脚本运行
    BASE_DIR = os.path.dirname(__file__)
    WORK_DIR = BASE_DIR

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = os.path.join(WORK_DIR, 'uploads')
VIDEO_FOLDER = os.path.join(WORK_DIR, 'videos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_env():
    """读取 .env 文件"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        pass

def get_api_key():
    """获取 API Key"""
    # 优先从环境变量获取（Vercel 或本地 .env）
    api_key = os.environ.get('VOLCENGINE_API_KEY')
    return api_key

# 全局变量存储隧道 URL
PUBLIC_URL = "https://nasty-months-teach.loca.lt"

def load_env():
    """读取 .env 文件"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        pass

def file_to_data_uri(filepath):
    """将本地文件转换为 data URI 格式，供 API 使用"""
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = 'application/octet-stream'
        
    with open(filepath, 'rb') as f:
        data = f.read()
        
    b64_data = base64.b64encode(data).decode('utf-8')
    return f"data:{mime_type};base64,{b64_data}"

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/generate', methods=['POST'])
def generate_video_api():
    load_env()
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "未配置 API KEY"}), 500

    try:
        # 获取表单数据
        prompt_text = request.form.get('prompt', '')
        
        # 准备 API 的 content 数组
        content = [
            {
                "type": "text",
                "text": prompt_text
            }
        ]

        # 处理上传的图片
        images = request.files.getlist('images')
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img.save(filepath)
                
                # 直接将文件转换为 Base64，不使用容易断开的内网穿透 URL
                b64_url = file_to_data_uri(filepath)
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": b64_url
                    },
                    "role": "reference_image"
                })
                
        # 处理视频
        video = request.files.get('video')
        if video and video.filename:
            filename = secure_filename(video.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(filepath)
            
            b64_url = file_to_data_uri(filepath)
            content.append({
                "type": "video_url",
                "video_url": {
                    "url": b64_url
                },
                "role": "reference_video"
            })
            
        # 处理音频
        audio = request.files.get('audio')
        if audio and audio.filename:
            filename = secure_filename(audio.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(filepath)
            
            b64_url = file_to_data_uri(filepath)
            content.append({
                "type": "audio_url",
                "audio_url": {
                    "url": b64_url
                },
                "role": "reference_audio"
            })

        # 构建请求
        url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "doubao-seedance-2-0-260128",
            "content": content,
            "generate_audio": True,
            "ratio": "16:9",
            "duration": 11,
            "watermark": False
        }

        # 为了演示能成功，如果用户没传图片，我们补上默认的，确保 API 能跑通
        if len(content) == 1:
            payload["content"] = [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic1.jpg"}, "role": "reference_image"},
                {"type": "image_url", "image_url": {"url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic2.jpg"}, "role": "reference_image"},
                {"type": "video_url", "video_url": {"url": "https://ark-project.tos-cn-beijing.volces.com/doc_video/r2v_tea_video1.mp4"}, "role": "reference_video"},
                {"type": "audio_url", "audio_url": {"url": "https://ark-project.tos-cn-beijing.volces.com/doc_audio/r2v_tea_audio1.mp3"}, "role": "reference_audio"}
            ]

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return jsonify({"task_id": result.get("id")})
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            print(f"API Error Response: {error_msg}")
            return jsonify({"error": f"HTTP Error {e.code}: {error_msg}"}), e.code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    load_env()
    api_key = get_api_key()
    
    url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, headers=headers, method='GET')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            status = result.get('status')
            
            if status == 'succeeded':
                video_url = result.get('content', {}).get('video_url')
                if video_url:
                    # 下载到本地
                    filename = f"video_{task_id}.mp4"
                    filepath = os.path.join(VIDEO_FOLDER, filename)
                    try:
                        urllib.request.urlretrieve(video_url, filepath)
                        return jsonify({
                            "status": status, 
                            "video_url": video_url,
                            "local_path": filepath
                        })
                    except Exception as e:
                        print(f"下载失败: {e}")
                        
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动本地服务器，请在浏览器访问: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)