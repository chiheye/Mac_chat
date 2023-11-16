import tkinter as tk
from tkinter import scrolledtext
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk  # Pillow library for image processing
import requests
import os
import threading
import psycopg2
from datetime import datetime
from html import escape

def send_request():
    user_input = input_text.get("1.0", "end-1c")
    
    # Disable the button while waiting for the response
    send_button.config(state=tk.DISABLED)
    
    # Start a new thread to make the request in the background
    threading.Thread(target=make_request, args=(user_input,), daemon=True).start()

def make_request(user_input):
    headers = {
        'Authorization': f'Bearer {os.getenv("sk-aaabbbcccdddeeefffggghhhiiijjjkkk")}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "chatglm3",
        "messages": [{"role": "user", "content": user_input}]
    }
    response = requests.post('http://172.24.0.1:6006/v1/chat/completions', headers=headers, json=data)
    
    try:
        print(response.status_code)  # Print HTTP status code
        print(response.text)  # Print response text
        response_data = response.json()
        
        # Get content from the first choice
        chat_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '没有数据')

        # Update the GUI in the main thread
        window.after(0, lambda: update_gui(user_input, chat_response))
    except Exception as e:
        window.after(0, lambda: update_gui(user_input, f'处理响应时出现错误: {str(e)}'))

def update_gui(user_input, chat_response):
    global chat_history, last_user_input

    if user_input != last_user_input:
        # Add an extra line break when the user input changes
        chat_history += "<br>"

    # Check if the response contains code, and wrap it in <pre> tags
    if "```" in chat_response:
        chat_response_html = f'<pre>{escape(chat_response)}</pre>'
    else:
        chat_response_html = escape(chat_response)

    chat_history += f'用户: {user_input}<br>模型回复: {chat_response_html}<br><br>'

    # Display the updated chat history in the HTML widget
    chat_text.set_html(chat_history)

    input_text.delete("1.0", tk.END)
    
    # Re-enable the button after receiving the response
    send_button.config(state=tk.NORMAL)

    # Scroll to the bottom to show the latest message
    chat_text.yview(tk.END)

    # 将用户提问和模型回答插入数据库
    insert_into_database(user_input, chat_response)

    # Update the last user input
    last_user_input = user_input

def insert_into_database(user_input, chat_response):
    # 替换为你的实际数据库连接参数
    db_params = {
        "host": "127.0.0.1",
        "port": 54326,
        "user": "postgres",
        "password": "postgres",
        "database": "llmchat"
    }

    # 连接到数据库
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # 替换为你的实际表名
    table_name = "chat"
    
    # 获取当前时间戳
    timestamp = datetime.now()

    # 执行插入语句
    insert_query = f"INSERT INTO public.{table_name} (question, answer, timestamp) VALUES (%s, %s, %s);"
    cursor.execute(insert_query, (user_input, chat_response, timestamp))

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()

# 创建主窗口
window = tk.Tk()
window.title("😊Chat")

# Load background image
bg_image = Image.open("File0316.png")  # Replace with the path to your image
bg_image = bg_image.resize((window.winfo_screenwidth(), window.winfo_screenheight()), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Set background image
bg_label = tk.Label(window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Add transparency to the main window
window.wm_attributes('-alpha', 0.9)  # Adjust the alpha value as needed

# 创建 HTML 文本框用于显示聊天记录
chat_text = HTMLLabel(window, width=100, height=30, wrap=tk.WORD, background="#f0f0f0", font=("Arial", 12))
chat_text.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

# 创建垂直滚动条
scrollbar = tk.Scrollbar(window, command=chat_text.yview)
scrollbar.grid(column=1, row=0, sticky="ns")

# 配置 HTML 文本框使用滚动条
chat_text.configure(yscrollcommand=scrollbar.set)

# 初始化聊天记录
chat_history = "<b>聊天记录:</b><br>"
chat_text.set_html(chat_history)

# 上一次用户输入
last_user_input = ""

# 创建文本框用于用户输入
input_text = tk.Text(window, width=100, height=10, wrap=tk.WORD, background="#f0f0f0", font=("Arial", 12))
input_text.grid(column=0, row=2, padx=10, pady=10, sticky="ew")
input_text.insert("1.0", "提问:")
# 创建按钮用于发送请求
send_button = tk.Button(window, text="发送", command=send_request)
send_button.grid(column=0, row=3, padx=10, pady=10)

# 将回车键绑定到 send_request 函数
window.bind('<Return>', lambda event: send_request())

# 使用 columnconfigure 和 rowconfigure 设置权重，使窗口自动缩放
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
window.rowconfigure(2, weight=0)

# 启动主循环
window.mainloop()
