📦 项目名称：《宋雨泽 AI》
👨‍💻 开发者：宋雨泽（12岁独立开发者）
📝 项目简介：一个带 GUI 界面的硬核 AI 桌面助手，完美结合了大模型对话与本地系统底层交互。
💡 项目理念：用最纯粹的 Python 标准库，打造最安全、最极客的智能控制台。

v1.0.0 - 极客首秀版

✨ 核心功能：

· 🎨 清爽 GUI 界面：极简浅色设计，告别纯黑框框。
· 🔐 四层套娃加密：API Key 在本地经过多层加密处理，杜绝明文泄露。
· 🔊 AI 语音播报：接入 OpenRouter 语音大模型，对话自动合成语音。
· 🖥️ 安全终端操控：AI 可生成 Linux 命令，但必须经过人工弹窗确认才会执行。
· 📁 智能文件生成：支持 AI 自动写代码文件，附带防越权路径校验。
· ⚙️ 多模型切换：内置多种免费大模型，可在设置中随时无缝切换。

🚀 运行与依赖安装：

本项目纯基于 Python 标准库开发，无需安装任何第三方 pip 包。

🐧 Linux 环境依赖：

· 运行前请先安装界面、音频和剪贴板库：
  sudo apt update && sudo apt install -y python3 python3-tk mpv xclip
· 启动程序：
  python3 ai.py

🪟 Windows 环境依赖：

· 界面库 tkinter 已随 Python 自带，无需额外安装。
· 需前往 mpv 官网下载 Windows 版 mpv.exe，并将其路径加入系统环境变量 PATH 中（用于语音播放）。
· 启动程序：
  python ai.py

首次使用： 请点击软件右上角 ⚙️ 设置，填入你的 OpenRouter API Key。

Built with 🖤 by a 12-year-old Geek. Keep hacking!
