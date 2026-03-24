#!/usr/bin/env python3
"""
米了个米 - 游戏服务器
提供静态页面 + 排行榜 API
排行榜数据存在本地 rank.json
"""
import json, os, http.server, urllib.parse

PORT = int(os.environ.get("PORT", 8080))
RANK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rank.json")

def load_rank():
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_rank(data):
    with open(RANK_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/rank":
            data = load_rank()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/rank":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                entry = json.loads(body)
                name = str(entry.get("name", ""))[:12]
                seconds = int(entry.get("seconds", 0))
                if not name or seconds <= 0:
                    raise ValueError("invalid")
                rank = load_rank()
                date_str = __import__("datetime").datetime.now().strftime("%Y/%m/%d")
                rank.append({"name": name, "seconds": seconds, "date": date_str})
                rank.sort(key=lambda x: x["seconds"])
                if len(rank) > 50: rank = rank[:50]
                save_rank(rank)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    save_rank(load_rank())  # 确保文件存在
    print(f"🎮 米了个米服务器启动: http://localhost:{PORT}")
    print(f"📱 局域网访问: http://$(hostname -s).local:{PORT}")
    http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
