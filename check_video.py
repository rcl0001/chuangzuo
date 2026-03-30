import os
import json
import urllib.request
import urllib.error
import time
import sys

def load_env():
    """读取 .env 文件并将变量加载到环境变量中"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print("[ERROR] 找不到 .env 文件，请确保该文件与脚本在同一目录下。")
        exit(1)

def check_task_status(task_id):
    """查询任务状态"""
    load_env()
    
    api_key = os.environ.get('VOLCENGINE_API_KEY')
    if not api_key:
        print("[ERROR] 环境变量中未找到 VOLCENGINE_API_KEY")
        exit(1)

    url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"\n[ERROR] API 请求失败 (HTTP {e.code})")
        print(f"原因: {e.reason}")
        try:
            parsed_error = json.loads(error_msg)
            print(json.dumps(parsed_error, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print(error_msg)
        return None
    except Exception as e:
        print(f"\n[ERROR] 发生未知错误: {str(e)}")
        return None

def download_video(url, filename):
    """下载视频到本地"""
    print(f"[INFO] 正在下载视频到 {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"[SUCCESS] 视频已成功下载: {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] 下载视频失败: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python3 check_video.py <task_id>")
        print("示例: python3 check_video.py cgt-20260330112943-zjbbv")
        exit(1)
        
    task_id = sys.argv[1]
    print(f"[INFO] 开始轮询任务状态，任务ID: {task_id}")
    
    max_retries = 60  # 最多等待约10分钟
    retry_count = 0
    
    while retry_count < max_retries:
        result = check_task_status(task_id)
        if not result:
            print("[ERROR] 获取状态失败，退出。")
            exit(1)
            
        status = result.get('status')
        print(f"[INFO] 第 {retry_count+1} 次检查，当前状态: {status}")
        
        if status == 'succeeded':
            content = result.get('content', {})
            video_url = content.get('video_url')
            if video_url:
                print("\n🎉 视频生成成功！")
                print(f"视频 URL: {video_url}")
                
                # 开始下载
                filename = f"video_{task_id}.mp4"
                filepath = os.path.join(os.path.dirname(__file__), filename)
                download_video(video_url, filepath)
                break
            else:
                print("[ERROR] 任务状态为成功，但未找到视频URL。")
                print(json.dumps(result, indent=4, ensure_ascii=False))
                break
        elif status == 'failed':
            print("\n❌ 视频生成失败！")
            print(json.dumps(result, indent=4, ensure_ascii=False))
            break
            
        # 还在处理中，等待后重试
        retry_count += 1
        time.sleep(10)  # 每10秒检查一次
        
    if retry_count >= max_retries:
        print("\n[WARNING] 轮询超时，视频可能还在生成中。请稍后手动检查。")

if __name__ == "__main__":
    main()