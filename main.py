# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask import render_template
from flask import redirect, url_for
from flask import send_from_directory

import sqlite3
import os
import markdown  # 导入 markdown 库

app = Flask(__name__)
DB_FILE = 'users.db'
MARKDOWN_FILE = 'document.md'  # 这里指定你的 Markdown 文件路径
MARKDOWN_DIR = './docs'  # 假设文档存放在 'docs' 目录下

# 初始化数据库
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # 添加一个默认用户
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "123"))
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("usr", "usr"))
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("debug", "debug"))
        conn.commit()
        conn.close()


def read_markdown_file(file_path):
    """读取指定路径的 Markdown 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

@app.route('/login', methods=['POST'])  # 定义路由 /login，允许 POST 方法
def login():
    username = request.form['username']  # 从表单中提取用户名
    password = request.form['password']  # 从表单中提取密码

    print(f"[调试] 接收到用户名: {username}")
    print(f"[调试] 接收到密码: {password}")

    conn = sqlite3.connect(DB_FILE)      # 连接数据库
    cursor = conn.cursor()               # 获取游标
    # 使用参数化查询，防止 SQL 注入攻击
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()             # 获取查询结果（如果存在返回第一条记录，否则返回 None）
    print(f"[调试] 查询结果: {user}")
    conn.close()                         # 关闭数据库连接

    if user:  # 如果找到了用户
        print("[调试] 登录成功")
        return redirect(url_for('dashboard'))  # 登录成功后跳转到 markdown 页面
    else:     # 没有找到匹配的用户
        print("[调试] 登录失败：用户名或密码错误")
        return "用户名或密码错误！", 401  # 返回状态码 401 表示未授权

@app.route('/')
def home():
    return render_template('index.html')  # 假设你有一个 index.html 文件

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # 假设你有一个 dashboard 页面


@app.route('/markdown/<filename>')
def markdown_page(filename):
    """根据文件名渲染 Markdown 文件"""
    # 构建 Markdown 文件路径
    file_path = os.path.join(MARKDOWN_DIR, filename)
    print(f"file_path 位置: {file_path}")
    
    # 读取 Markdown 文件内容
    markdown_content = read_markdown_file(file_path)

    if not markdown_content:
        abort(404, description="文件未找到")
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    # return "OK"
    # # 将 Markdown 内容转换为 HTML
    html_content = markdown.markdown(markdown_content,
                                    extensions=exts)
    return render_template('markdown_page.html', content=html_content)

@app.route('/markdown/pic/<path:filename>')
def markdown_image(filename):
    return send_from_directory(os.path.join(MARKDOWN_DIR, 'pic'), filename)

# 下载文件
@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory("downloads", filename, as_attachment=True)


if __name__ == '__main__':
    init_db()
    print("Flask 路由列表：")
    for rule in app.url_map.iter_rules():
        print(rule)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
