import http.server
import socketserver
import json
import sys
import os
import base64
import pystray
from PIL import Image
import threading

PORT = 5000

# 生成托盘图标
def create_tray_icon(server):
    image = Image.open("assets\kda.png")
    
    menu = pystray.Menu(
        pystray.MenuItem('CS2KDA小工具', lambda: None, enabled=False),
        pystray.MenuItem('退出', lambda: exit_app(server))
    )
    
    icon = pystray.Icon(
        "cs_stats",
        image,
        "CS2KDA小工具",
        menu
    )
    return icon

# 退出处理
def exit_app(server):
    server.shutdown()
    os._exit(0)

# HTTP服务器线程
def run_server():
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            gamedata = json.loads(post_data.decode('utf-8'))
            #获取steamID
            my_steamid = gamedata['provider']['steamid']
            current_player_steamid = gamedata['player']['steamid']

            if current_player_steamid == my_steamid:
                try:
                    stats = gamedata['player']['match_stats']
                    kills = stats.get('kills', 0)
                    deaths = stats.get('deaths', 0)
                    assists = stats.get('assists', 0)
                except KeyError:
                    kills = deaths = assists = 0

                with open('kills.txt', 'w') as f:
                    f.write(f"{kills}\n")
                with open('deaths.txt', 'w') as f:
                    f.write(f"{deaths}\n")
                with open('assists.txt', 'w') as f:
                    f.write(f"{assists}\n")

            self.send_response(200)
            self.end_headers()

    server = socketserver.TCPServer(("", PORT), MyHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

if __name__ == '__main__':
    # 隐藏控制台窗口
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # 启动服务器
    http_server = run_server()
    
    # 创建系统托盘图标
    icon = create_tray_icon(http_server)
    
    # 运行托盘图标
    icon.run()