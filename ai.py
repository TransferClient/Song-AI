import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import urllib.request
import json
import os
import subprocess
import re
import threading
import base64
import binascii

# =====================================================================
# ⚙️ 配置区域
# =====================================================================
# 👇 这里你可以填“明文 Key”，也可以填你用 encrypt_key.py 生成的“加密乱码”！
DEFAULT_API_KEY_OR_CIPHER = "ZDNkMzE0ZjQzMzE1NzVhNTEzNzY0NWU0MjM5NTIzOTU4NmU0NzVmNDIzMzZhNzk1MTM3NjQ1ZjRkNmM2YTZkNDEzNTQ3NTk1ZDYyNTc0YTUzMzU0YTZkNGM2MjU0NWY0NTM1NWQ2OTVjNmE1YTdlNGE2MjQ0NGQ0ODcxNTc0ZDQyMzE0NDRlNDk2NjRhNmQ0ODY2NTc0ZTQ3Nzk1NzRlNDg3NTQ0NGQ0NzczNmE2ZDQ0NzU0YTY0NjQ3OTQzMzI2NDczNzIzMzY="

CONFIG_FILE = "config.json"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
TTS_MODEL = "fish-audio/s2.1-pro-free:free"
TTS_URL = "https://openrouter.ai/api/v1/audio/speech"
VOICE_MALE = "b347db033a6549378b48d00acb0d06cd"
VOICE_FEMALE = "933563129e564b19a115bedd57b7406a"

MODEL_DICT = {
    "笔记预览模型 (dots-3)": "dots-studio/dots-3-note-preview:free",
    "拉古纳代码模型 (laguna-s-2.1)": "poolside/laguna-s-2.1:free",
    "英伟达闪电版": "nvidia/nemotron-3.5-lightning:free",
    "英伟达 550B 旗舰巨兽": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "星尘 4.0 国产大模型": "xingchen-agi/xing4.0-29b-a4b:free",
    "液态极速小模型": "liquid/lfm-2.5-2.6b:free"
}

SYSTEM_PROMPT = """你的唯一名字是『宋雨泽AI』。你说话硬核、直接、懂底层逻辑。
【特殊能力1：操作电脑】
如果用户要求你操作电脑、运行命令，你必须严格按照以下格式输出：
【执行命令: 你要执行的bash命令】
（千万不要用Markdown代码块包裹）
【特殊能力2：写文件】
如果用户要求你写代码并保存，使用以下格式：
【创建文件: 文件名.后缀】
（文件内容）
【文件结束】
正常聊天时直接回复，不要乱用格式。"""

# 四层套娃加密解密函数
def encrypt_api_key(real_key):
    if not real_key: return ""
    step1 = base64.b64encode(real_key.encode('utf-8')).decode('utf-8')
    step2 = binascii.hexlify(step1.encode('utf-8')).decode('utf-8')
    step3 = step2[::-1]
    step4 = base64.b64encode(step3.encode('utf-8')).decode('utf-8')
    return step4

def decrypt_api_key(encrypted_str):
    if not encrypted_str: return ""
    try:
        step3 = base64.b64decode(encrypted_str.encode('utf-8')).decode('utf-8')
        step2 = step3[::-1]
        step1 = binascii.unhexlify(step2.encode('utf-8')).decode('utf-8')
        real_key = base64.b64decode(step1.encode('utf-8')).decode('utf-8')
        # 正常 OpenRouter Key 都以 sk-or-v1- 开头，用这个做校验
        if real_key.startswith("sk-or-v1-"):
            return real_key
        return ""
    except Exception:
        return ""

# UI 颜色与字体
BG_COLOR = "#F5F5F7"       
TEXT_AREA_BG = "#FFFFFF"   
TEXT_COLOR = "#333333"     
ACCENT_COLOR = "#007AFF"   
FONT_MAIN = ("Microsoft YaHei", 12)
FONT_TITLE = ("Microsoft YaHei", 15, "bold")
FONT_BTN = ("Microsoft YaHei", 11, "bold")

class CleanAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("宋雨泽AI - 极客加密版")
        self.geometry("750x700") 
        self.configure(bg=BG_COLOR)
        
        self.api_key = ""
        self.current_model = list(MODEL_DICT.values())[0]
        self.current_voice = VOICE_MALE
        self.work_dir = os.path.expanduser("~")
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        self.load_config()
        self.parse_default_key() # 🚀 解析代码里填写的默认 Key（支持明文和密文）
        
        self.style = ttk.Style(self)
        self.style.configure('TCombobox', font=FONT_MAIN, padding=4)
        
        self.setup_ui()

    def parse_default_key(self):
        """智能识别 DEFAULT_API_KEY_OR_CIPHER 是明文还是密文"""
        raw_val = DEFAULT_API_KEY_OR_CIPHER.strip()
        if not raw_val or "这里填" in raw_val:
            return
            
        # 如果以 sk-or-v1- 开头，说明填的是明文
        if raw_val.startswith("sk-or-v1-"):
            self.api_key = raw_val
        else:
            # 否则当成密文，尝试解密
            decrypted = decrypt_api_key(raw_val)
            if decrypted:
                self.api_key = decrypted
            else:
                print("警告：默认 Key 既不是明文，解密也失败了！")

    def load_config(self):
        """如果本地有 config.json 且有效，会覆盖代码里的默认 Key"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    encrypted_key = cfg.get("api_key", "")
                    if encrypted_key:
                        decrypted = decrypt_api_key(encrypted_key)
                        if decrypted:
                            self.api_key = decrypted # 覆盖默认 Key
                    self.current_model = cfg.get("model", self.current_model)
                    self.current_voice = cfg.get("voice", self.current_voice)
            except Exception:
                pass

    def save_config(self):
        """将 GUI 输入的明文 Key 加密后保存"""
        try:
            encrypted_key = encrypt_api_key(self.api_key)
            cfg = {
                "api_key": encrypted_key,
                "model": self.current_model,
                "voice": self.current_voice
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def setup_ui(self):
        top_frame = tk.Frame(self, bg=TEXT_AREA_BG, pady=12, highlightthickness=1, highlightbackground="#E0E0E0")
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text="宋雨泽 AI (极客加密版)", bg=TEXT_AREA_BG, fg=TEXT_COLOR, font=FONT_TITLE).pack(side=tk.LEFT, padx=20)
        
        self.settings_btn = tk.Button(top_frame, text="⚙️ 设置", bg="#E8E8E8", fg=TEXT_COLOR, 
                                      font=FONT_BTN, relief=tk.FLAT, padx=15, pady=5, command=self.open_settings)
        self.settings_btn.pack(side=tk.RIGHT, padx=20)

        self.chat_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, bg=TEXT_AREA_BG, fg=TEXT_COLOR, 
            font=FONT_MAIN, relief=tk.FLAT, padx=12, pady=12, spacing3=8
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 0))
        self.chat_area.config(state=tk.DISABLED)
        
        self.chat_area.tag_config("user_name", foreground=ACCENT_COLOR, font=FONT_BTN)
        self.chat_area.tag_config("ai_name", foreground="#FF7F50", font=FONT_BTN)
        self.chat_area.tag_config("system_name", foreground="#999999", font=("Microsoft YaHei", 10, "bold"))
        self.chat_area.tag_config("error", foreground="#FF0000", font=FONT_BTN)
        self.chat_area.tag_config("normal_text", foreground=TEXT_COLOR, font=FONT_MAIN)

        self.status_var = tk.StringVar(value="就绪 (已加载加密层)")
        self.status_label = tk.Label(self, textvariable=self.status_var, bg=BG_COLOR, fg="#888888", font=("Microsoft YaHei", 10), anchor="w")
        self.status_label.pack(fill=tk.X, padx=15, pady=(4, 4))

        bottom_frame = tk.Frame(self, bg=TEXT_AREA_BG, pady=12, padx=12, highlightthickness=1, highlightbackground="#E0E0E0")
        bottom_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.input_box = tk.Text(bottom_frame, height=3, bg=TEXT_AREA_BG, fg=TEXT_COLOR, 
                                 font=FONT_MAIN, relief=tk.FLAT, padx=5, pady=5)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_box.bind("<Return>", self.on_enter)
        self.input_box.focus_set()

        self.send_btn = tk.Button(bottom_frame, text="发送", bg=ACCENT_COLOR, fg="#FFFFFF",
                                  font=FONT_BTN, relief=tk.FLAT, width=8,
                                  command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=(12, 0), fill=tk.Y)

        if not self.api_key or "这里填" in DEFAULT_API_KEY_OR_CIPHER:
            if not self.api_key:
                self.append_chat("系统", "⚠️ 未检测到 API Key，请点击右上角【设置】。", "error")
        else:
            self.append_chat("系统", "欢迎！API Key 已加载（可能是代码默认值、密文解密或本地配置）。", "system")

    def on_enter(self, event):
        self.send_message()
        return "break"

    def open_settings(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("系统设置")
        settings_win.geometry("500x480") 
        settings_win.resizable(False, False)
        settings_win.configure(bg=BG_COLOR)
        settings_win.transient(self)
        settings_win.grab_set()

        frame_key = tk.Frame(settings_win, bg=BG_COLOR)
        frame_key.pack(fill=tk.X, padx=30, pady=(20, 5))
        tk.Label(frame_key, text="API Key (输入明文，自动加密):", bg=BG_COLOR, font=FONT_MAIN).pack(anchor="w")
        
        key_entry = tk.Entry(frame_key, show="*", font=FONT_MAIN, relief=tk.SOLID, borderwidth=1)
        if self.api_key:
            key_entry.insert(0, self.api_key) 
        key_entry.pack(fill=tk.X, pady=(2, 0), ipady=4)

        frame_model = tk.Frame(settings_win, bg=BG_COLOR)
        frame_model.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(frame_model, text="选择大脑模型:", bg=BG_COLOR, font=FONT_MAIN).pack(anchor="w")
        model_var = tk.StringVar(value=self.current_model)
        model_combo = ttk.Combobox(frame_model, textvariable=model_var, values=list(MODEL_DICT.values()), state="readonly", font=FONT_MAIN)
        model_combo.pack(fill=tk.X, pady=(2, 0))

        frame_voice = tk.Frame(settings_win, bg=BG_COLOR)
        frame_voice.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(frame_voice, text="AI 说话音色:", bg=BG_COLOR, font=FONT_MAIN).pack(anchor="w")
        voice_var = tk.StringVar(value="男声" if self.current_voice == VOICE_MALE else "女声")
        voice_combo = ttk.Combobox(frame_voice, textvariable=voice_var, values=["男声", "女声"], state="readonly", font=FONT_MAIN)
        voice_combo.pack(fill=tk.X, pady=(2, 0))

        def save_settings():
            self.api_key = key_entry.get().strip()
            self.current_model = model_combo.get()
            self.current_voice = VOICE_MALE if voice_var.get() == "男声" else VOICE_FEMALE
            self.save_config() 
            messagebox.showinfo("成功", "设置已保存！(后台已自动加密)", parent=settings_win)
            settings_win.destroy()

        tk.Button(settings_win, text="保存设置", bg=ACCENT_COLOR, fg="#FFFFFF", font=FONT_BTN, 
                  relief=tk.FLAT, command=save_settings).pack(pady=20, ipadx=30, ipady=5)

    def append_chat(self, sender, text, sender_type="system"):
        self.chat_area.config(state=tk.NORMAL)
        tag_name = "system_name" if sender_type == "system" else ("user_name" if sender_type == "user" else "ai_name")
        if "错误" in sender or "拦截" in sender or "警告" in sender: 
            tag_name = "error"
        self.chat_area.insert(tk.END, f"【{sender}】:\n", tag_name)
        self.chat_area.insert(tk.END, f"{text}\n\n", "normal_text")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def send_message(self):
        user_input = self.input_box.get("1.0", tk.END).strip()
        if not user_input: return
        if not self.api_key:
            messagebox.showwarning("提示", "请先在代码顶部或右上角【设置】中填入 API Key。")
            return

        self.input_box.delete("1.0", tk.END)
        self.append_chat("你", user_input, "user")
        self.send_btn.config(state=tk.DISABLED, text="...")
        self.status_var.set("🤔 正在思考...")
        threading.Thread(target=self.request_ai, args=(user_input,), daemon=True).start()

    def request_ai(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        data = {"model": self.current_model, "messages": self.messages}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        req = urllib.request.Request(CHAT_URL, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_reply = result['choices'][0]['message']['content']
                self.after(0, self.process_ai_reply, ai_reply)
        except Exception as e:
            self.after(0, lambda: self.append_chat("错误", f"网络请求失败: {e}", "system"))
            self.after(0, lambda: self.send_btn.config(state=tk.NORMAL, text="发送"))
            self.after(0, lambda: self.status_var.set("请求失败"))

    def process_ai_reply(self, ai_reply):
        ai_reply = self.parse_and_run_commands(ai_reply)
        ai_reply = self.parse_and_save_files(ai_reply)
        self.messages.append({"role": "assistant", "content": ai_reply})
        self.append_chat("宋雨泽AI", ai_reply, "ai")
        self.send_btn.config(state=tk.NORMAL, text="发送")
        self.status_var.set("就绪")
        threading.Thread(target=self.text_to_speech, args=(ai_reply,), daemon=True).start()

    def parse_and_run_commands(self, reply):
        pattern = r"【执行命令:\s*(.+?)】"
        matches = re.findall(pattern, reply)
        if matches:
            for cmd in matches:
                confirm = messagebox.askyesno("安全警告", f"AI 请求执行命令：\n\n{cmd}\n\n是否允许？")
                if not confirm:
                    self.append_chat("系统终端", f"$ {cmd}\n已被用户拦截。", "system")
                    continue
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    output = result.stdout.strip() if result.stdout else result.stderr.strip()
                    self.append_chat("系统终端", f"$ {cmd}\n{output or '执行完毕'}", "system")
                except Exception as e:
                    self.append_chat("系统终端", f"$ {cmd}\n执行失败: {e}", "error")
            reply = re.sub(pattern, "（命令已处理）", reply).strip()
        return reply

    def parse_and_save_files(self, reply):
        pattern = r"【创建文件:\s*(.+?)】(.*?)【文件结束】"
        matches = re.findall(pattern, reply, re.DOTALL)
        if matches:
            for filename, content in matches:
                safe_filename = os.path.basename(filename.strip())
                filepath = os.path.abspath(os.path.join(self.work_dir, safe_filename))
                if not filepath.startswith(os.path.abspath(self.work_dir)):
                    self.append_chat("错误", "安全拦截：禁止越权写入。", "system")
                    continue
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content.strip())
                    self.append_chat("系统", f"文件已保存: {filepath}", "system")
                except Exception as e:
                    self.append_chat("错误", f"文件保存失败: {e}", "error")
            return re.sub(pattern, "（已成功创建文件）", reply).strip()
        return reply

    def text_to_speech(self, text):
        if not text.strip() or not self.api_key: return
        self.after(0, lambda: self.status_var.set("🔊 正在合成语音..."))
        data = {"model": TTS_MODEL, "input": text, "reference_id": self.current_voice, "response_format": "mp3"}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        req = urllib.request.Request(TTS_URL, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
        filename = "temp_voice.mp3"
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                audio_data = response.read()
                if len(audio_data) > 1000:
                    with open(filename, "wb") as f: f.write(audio_data)
                    subprocess.run(["mpv", "--really-quiet", "--no-video", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        finally:
            if os.path.exists(filename): os.remove(filename)
            if self.status_var.get() == "🔊 正在合成语音...":
                self.after(0, lambda: self.status_var.set("就绪"))

if __name__ == "__main__":
    app = CleanAIApp()
    app.mainloop()