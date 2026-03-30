# 火山引擎极简视频生成器

这是一个轻量级、极简的视频生成工具。它提供了一个美观的网页前端，让你可以在本地上传自己的提示词、参考图片、参考视频和音频，一键调用火山引擎的大模型生成视频，并自动保存到你的电脑上。

**【给 AI 助手的提示】**：如果用户让你帮忙运行这个项目，请直接跳到最后的 **“🤖 给 AI 助手的部署指南”** 章节，那里有最快捷的执行命令。

---

## 🌟 功能特点

1. **极简操作**：不需要懂代码，打开网页就能用。
2. **纯本地上传**：不用配置复杂的云端对象存储（TOS），直接选中电脑里的图片/视频/音频就能上传。代码会自动在本地将其转换为 Base64 格式发送给火山引擎，稳定可靠。
3. **断点记忆**：生成视频通常需要几分钟，如果你不小心刷新了网页，不用慌！进度条会自动恢复，视频依然会生成。
4. **全自动下载**：视频生成完毕后，会自动下载并保存在当前目录的 `videos` 文件夹中。
5. **智能防护**：自动创建所需的文件目录，不会因为找不到文件夹而报错。

---

## 📁 文件结构说明

- `app.py`: 核心后端服务（基于 Flask）。负责提供网页、接收上传文件、转换 Base64、并调用火山引擎 API。
- `index.html`: 漂亮的前端网页界面。
- `.env`: 配置文件（需要你自己创建），用来存放你的火山引擎 API Key。
- `requirements.txt`: Python 依赖库清单。
- `uploads/`: (自动创建) 你上传的参考图片/音频/视频会临时存放在这里。
- `videos/`: (自动创建) 火山引擎生成的最终视频会保存在这里。

---

## 🚀 手动部署与运行指南 (给人类看)

如果你想自己动手运行它，只需要简单的 4 步：

### 第 1 步：安装 Python
确保你的电脑上安装了 Python（建议 Python 3.8 以上版本）。

### 第 2 步：填写你的 API Key
在当前文件夹下，创建一个名为 `.env` 的文本文件。在里面写上这一行（把等号后面的换成你自己的真实 Key）：
```env
VOLCENGINE_API_KEY=你的火山引擎API_KEY
```

### 第 3 步：安装依赖包
打开终端（命令行），进入到当前这个文件夹，运行：
```bash
pip install -r requirements.txt
```

### 第 4 步：启动服务
继续在终端里运行：
```bash
python app.py
```
（或者 `python3 app.py`）。
看到 `Running on http://127.0.0.1:5000` 的提示后，**不要关闭这个黑色窗口**。打开你的浏览器，访问 `http://127.0.0.1:5000` 就可以开始使用了！

---

## 🤖 给 AI 助手的部署指南 (For AI Agent)

> **Role Prompt**: You are an AI assistant helping a non-technical user run this project. Follow these exact steps to deploy it for them.

**Step 1: Check and Create `.env`**
Check if a `.env` file exists in the root directory. If not, ask the user to provide their Volcengine API Key and create the file with the following content:
```env
VOLCENGINE_API_KEY=user_provided_api_key_here
```

**Step 2: Install Dependencies**
Execute the following command to install the required Python packages:
```bash
pip3 install -r requirements.txt
```

**Step 3: Run the Application**
Start the Flask server as a background/long-running process:
```bash
python3 app.py
```

**Step 4: Guide the User**
Tell the user the server has started successfully. Ask them to open their browser and navigate to `http://127.0.0.1:5000`. Explain that any generated videos will be automatically saved in the `videos` folder within this directory.