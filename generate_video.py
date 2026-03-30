import os
import json
import urllib.request
import urllib.error

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
        print("[INFO] 环境变量加载成功")
    except FileNotFoundError:
        print("[ERROR] 找不到 .env 文件，请确保该文件与脚本在同一目录下。")
        exit(1)

def generate_video():
    """调用 API 生成视频"""
    load_env()
    
    api_key = os.environ.get('VOLCENGINE_API_KEY')
    if not api_key:
        print("[ERROR] 环境变量中未找到 VOLCENGINE_API_KEY，请检查 .env 文件。")
        exit(1)

    url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构造请求数据
    payload = {
        "model": "doubao-seedance-2-0-260128",
        "content": [
            {
                "type": "text",
                "text": "全程使用视频1的第一视角构图，全程使用音频1作为背景音乐。第一人称视角果茶宣传广告，seedance牌「苹苹安安」苹果果茶限定款；首帧为图片1，你的手摘下一颗带晨露的阿克苏红苹果，轻脆的苹果碰撞声；2-4 秒：快速切镜，你的手将苹果块投入雪克杯，加入冰块与茶底，用力摇晃，冰块碰撞声与摇晃声卡点轻快鼓点，背景音：「鲜切现摇」；4-6 秒：第一人称成品特写，分层果茶倒入透明杯，你的手轻挤奶盖在顶部铺展，在杯身贴上粉红包标，镜头拉近看奶盖与果茶的分层纹理；6-8 秒：第一人称手持举杯，你将图片2中的果茶举到镜头前（模拟递到观众面前的视角），杯身标签清晰可见，背景音「来一口鲜爽」，尾帧定格为图片2。背景声音统一为女生音色。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic1.jpg"
                },
                "role": "reference_image"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic2.jpg"
                },
                "role": "reference_image"
            },
            {
                "type": "video_url",
                "video_url": {
                    "url": "https://ark-project.tos-cn-beijing.volces.com/doc_video/r2v_tea_video1.mp4"
                },
                "role": "reference_video"
            },
            {
                "type": "audio_url",
                "audio_url": {
                    "url": "https://ark-project.tos-cn-beijing.volces.com/doc_audio/r2v_tea_audio1.mp3"
                },
                "role": "reference_audio"
            }
        ],
        "generate_audio": True,
        "ratio": "16:9",
        "duration": 11,
        "watermark": False
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    print(f"[INFO] 正在发送请求到 {url} ...")
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("[SUCCESS] 请求成功！返回结果如下：")
            print(json.dumps(result, indent=4, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"\n[ERROR] API 请求失败 (HTTP {e.code})")
        print(f"原因: {e.reason}")
        print("详细错误日志:")
        try:
            parsed_error = json.loads(error_msg)
            print(json.dumps(parsed_error, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print(error_msg)
    except Exception as e:
        print(f"\n[ERROR] 发生未知错误:")
        print(str(e))

if __name__ == "__main__":
    generate_video()
