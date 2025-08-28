import os
from flask import Flask, render_template
import webbrowser
import threading
import time


'''Super堡'''
# 搭建flask框架
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

mapping = {
    "面包底": "BottomBun",
    "生菜": "lettuce",
    "番茄": "tomato",
    "牛肉饼": "beef",
    "芝士": "cheese",
    "酱料": "sauce",
    "面包顶": "TopBun"
}

ingredients_order = []


def burger(result):
    global ingredients_order
    inputs = result.strip().split("→")
    ingredients_order = [mapping[i] for i in inputs]
    ingredients_order = ingredients_order[::-1]

    # 自动启动服务器
    start_server()
    return ingredients_order


@app.route('/')
def show_burger():
    return render_template("burger.html", ingredients=ingredients_order)


def run_server(port=5050):
    """在后台线程中运行服务器"""
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)


def start_server(port=5050):
    """启动服务器并打开浏览器"""
    url = f"http://127.0.0.1:{port}/"

    # 在后台线程中启动服务器
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    # 等待服务器启动
    time.sleep(2)

    # 打开浏览器
    webbrowser.open(url)

    # 保持服务器运行
    try:
        server_thread.join()
    except KeyboardInterrupt:
        pass
