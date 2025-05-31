from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class TestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <html>
            <body>
                <h1>麻雀シャンテン数シミュレーター（シンプル版）</h1>
                <p>サーバーは正常に動作しています。</p>
                <button onclick="testAPI()">APIテスト</button>
                <div id="result"></div>
                <script>
                function testAPI() {
                    document.getElementById('result').innerHTML = 'テスト実行中...';
                    fetch('/test')
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('result').innerHTML = JSON.stringify(data);
                        })
                        .catch(err => {
                            document.getElementById('result').innerHTML = 'エラー: ' + err;
                        });
                }
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'message': 'サーバーは動作しています'}
            self.wfile.write(json.dumps(response).encode())

print('サーバーを起動します: http://localhost:8888')
httpd = HTTPServer(('localhost', 8888), TestHandler)
httpd.serve_forever()