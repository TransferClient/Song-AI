import base64
import binascii
import subprocess
import os

def copy_to_clipboard(text):
    """自动尝试把文本复制到系统剪贴板"""
    try:
        # 尝试1: xclip (Linux图形界面常见)
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
        return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    try:
        # 尝试2: xsel (另一个Linux剪贴板工具)
        subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
        return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    try:
        # 尝试3: termux-clipboard-set (如果你用的是安卓Termux环境)
        subprocess.run(['termux-clipboard-set'], input=text.encode('utf-8'), check=True)
        return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    return False

def encrypt_api_key(real_key):
    print("\n\033[96m[ ⚙️ ] 正在执行四层套娃加密...\033[0m")
    
    # 1. Base64 编码
    step1 = base64.b64encode(real_key.encode('utf-8')).decode('utf-8')
    print(f"\033[90m  1️⃣ 层 1 (Base64): {step1[:20]}...\033[0m")
    
    # 2. 转成十六进制 (Hex)
    step2 = binascii.hexlify(step1.encode('utf-8')).decode('utf-8')
    print(f"\033[90m  2️⃣ 层 2 (Hex): {step2[:20]}...\033[0m")
    
    # 3. 字符串反转 (倒过来)
    step3 = step2[::-1]
    print(f"\033[90m  3️⃣ 层 3 (反转): {step3[:20]}...\033[0m")
    
    # 4. 再次 Base64
    step4 = base64.b64encode(step3.encode('utf-8')).decode('utf-8')
    print(f"\033[92m  4️⃣ 层 4 (终极): 完成！\033[0m")

    # 组装成最终要填进主程序的格式
    final_code = f'ENCRYPTED_KEY = "{step4}"'
    
    print("\n\033[93m" + "="*60 + "\033[0m")
    print("\033[92m✅ 加密成功！以下是你要填进 ai.py 的代码：\033[0m\n")
    print(f"\033[96m{final_code}\033[0m\n")
    
    # 自动复制
    if copy_to_clipboard(final_code):
        print("\033[92m📋 已经自动帮你复制到剪贴板啦！直接去 ai.py 里面粘贴覆盖即可。\033[0m")
    else:
        print("\033[91m⚠️ 提示：未能自动复制（可能是缺少剪贴板工具），请手动选中上面那行代码复制。\033[0m")
        print("\033[90m(如果想支持自动复制，可以在终端运行: sudo apt install xclip)\033[0m")
        
    print("\033[93m" + "="*60 + "\033[0m")

if __name__ == "__main__":
    os.system('clear') # 清屏，让界面更干净
    print("\033[96m" + """
    ╔══════════════════════════════════════════════════════════╗
    ║        🔐 宋雨泽AI - 绝密级 API Key 加密生成器 🔐        ║
    ╚══════════════════════════════════════════════════════════╝
    """ + "\033[0m")
    
    try:
        key_input = input("\033[93m👉 请输入你真实的 OpenRouter API Key:\033[0m\n> ").strip()
        if key_input:
            encrypt_api_key(key_input)
        else:
            print("\033[91m[ ❌ ] 错误：你没有输入任何内容！\033[0m")
    except KeyboardInterrupt:
        print("\n\033[91m[ ❌ ] 已取消操作。\033[0m")