import os
import time
from datetime import datetime
import asyncio
import threading
from pywebio import start_server
from pywebio.input import input, file_upload
from pywebio.output import put_text, put_markdown, put_table, clear, put_loading, put_warning, put_error
from pywebio.session import hold
import whisper

# --- Configuration ---
# 简单密钥验证
SECRET_KEY = "AlwaysBernard"
# 用于存储历史任务的文件 (简单实现，实际应用建议用数据库)
HISTORY_FILE = "transcription_history.txt"
# Whisper模型 (根据需要选择 'tiny', 'base', 'small', 'medium', 'large')
WHISPER_MODEL_PATH = "/home/bernard/projects/Whisper-large-v3/large-v3.pt" 

# --- Global State ---
# 使用线程锁保护历史记录文件的读写
history_lock = threading.Lock()

# --- Helper Functions ---

def load_history():
    """从文件加载历史记录"""
    history = []
    if os.path.exists(HISTORY_FILE):
        with history_lock: # 加锁
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split(' | ', 3) # 分割成最多4部分
                            if len(parts) == 4:
                                history.append(parts)
            except Exception as e:
                put_error(f"加载历史记录时出错: {e}")
    return history

def save_to_history(timestamp, filename, output):
    """将任务结果保存到历史记录"""
    with history_lock: # 加锁
        try:
            with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} | {filename} | {output}\n")
        except Exception as e:
            put_error(f"保存历史记录时出错: {e}")

def transcribe_audio(file_content, filename):
    """使用Whisper模型转录音频"""
    # 注意：PyWebIO的file_upload返回的是bytes，whisper需要文件路径或numpy数组
    # 这里采用将bytes写入临时文件的方式处理
    
    # 从文件名提取扩展名
    file_ext = os.path.splitext(filename)[1].lower()
    
    # 创建带时间戳的临时文件名，存储在data目录中
    timestamp = int(time.time())
    temp_filename = f"data/temp_audio_{timestamp}{file_ext}"
    
    try:
        with open(temp_filename, 'wb') as f:
            f.write(file_content)
        
        # 加载模型并转录
        model = whisper.load_model(WHISPER_MODEL_PATH)
        result = model.transcribe(temp_filename, verbose=True)
        
        # 清理临时文件
        os.remove(temp_filename)
        return result["text"]
    except Exception as e:
        # 如果失败，清理临时文件
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return f"转录失败，无法处理该音频文件。错误信息: {str(e)}"

# --- Main Application Logic ---

async def main():
    """Bernard's音频转录工具"""
    # """主应用逻辑"""
    clear() # 清空页面
    put_markdown("# Bernard's音频转录工具 (Powered by Whisper)")
    
    # 1. 简单密钥验证
    user_key = await input("请输入访问密钥", type='password')
    if user_key != SECRET_KEY:
        put_error("密钥错误，程序结束。")
        hold() # 保持页面，让用户看到错误信息
        return # 结束函数

    put_text("密钥验证成功！")
    
    while True:
        put_markdown("## 上传并转录音频")
        
        # 2. 上传音频文件
        uploaded_file = await file_upload("请选择一个音频文件 (支持 mp3, wav, m4a, flac):", accept="audio/*", required=True)
        
        if uploaded_file:
            filename = uploaded_file['filename']
            file_content = uploaded_file['content']
            
            put_text(f"已上传文件: {filename}")
            
            # 3. 调用Whisper (显示加载动画)
            with put_loading(shape='border', color='primary'):
                put_text('正在转录音频，请稍候...')
                # 使用 run_in_executor 将同步的转录任务放到线程池执行，避免阻塞事件循环
                loop = asyncio.get_event_loop()
                # 传递文件名给transcribe_audio函数以获取正确扩展名
                transcription_result = await loop.run_in_executor(None, transcribe_audio, file_content, filename)
         
            # 4. 打印输出
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            put_markdown(f"### 转录完成 ({timestamp})")
            put_markdown(f"**文件名:** {filename}")
            put_markdown(f"**转录结果:**\n{transcription_result}")
            
            # 保存到历史记录
            save_to_history(timestamp, filename, transcription_result)
            
            put_markdown("---")
            
            # 5. 显示历史任务
            put_markdown("## 历史转录任务")
            history_data = load_history()
            if history_data:
                # 为了美观，限制显示的字符长度
                formatted_history = [
                    [item[0], item[1][:30] + ('...' if len(item[1]) > 30 else ''), item[2][:100] + ('...' if len(item[2]) > 100 else '')]
                    for item in reversed(history_data) # 最新的在前
                ]
                put_table(formatted_history, header=['时间', '音频文件', '转录输出'])
            else:
                put_text("暂无历史记录。")
            
            put_markdown("---")
            # 可以选择继续上传或退出
            # 这里设计为循环，可以继续上传新文件
            # 如果要结束，可以添加一个按钮或输入来break循环

        else:
            put_warning("未选择文件。")

if __name__ == '__main__':
    # 启动PyWebIO服务器
    start_server(main, port=8080, debug=True, cdn=False)




