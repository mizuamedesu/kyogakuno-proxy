from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import request, parse, error
import json

API_BASE_URL = "https://kyogaku-bbs.utopi-a.dev/api/trpc/"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>驚額の掲示板2</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        :root {
            --bg-color: #f5f5f7;
            --text-color: #1d1d1f;
            --accent-color: #0071e3;
            --card-bg: #ffffff;
            --input-border: #d2d2d7;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            letter-spacing: -0.02em;
        }

        .post-form {
            background-color: var(--card-bg);
            border-radius: 18px;
            padding: 30px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .post-form:hover {
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            transform: translateY(-5px);
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid var(--input-border);
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
        }

        button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 20px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            background-color: #005cbd;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .message {
            background-color: var(--card-bg);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeIn 0.5s ease forwards;
        }

        @keyframes fadeIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message:hover {
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
        }

        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .message-number {
            font-weight: 600;
            color: var(--accent-color);
            margin-right: 10px;
        }

        .message-author {
            font-weight: 600;
            color: var(--text-color);
        }

        .message-content {
            margin-bottom: 10px;
            font-size: 1.1rem;
        }

        .message-date {
            font-size: 0.8rem;
            color: #86868b;
            text-align: right;
        }

        #loadingIndicator, #errorMessage {
            text-align: center;
            margin: 20px 0;
            font-style: italic;
            font-weight: 300;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2.5rem;
            }

            .post-form, .message {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>驚額の掲示板2</h1>
        <div class="post-form">
            <input type="text" id="authorInput" placeholder="お名前">
            <textarea id="messageInput" placeholder="メッセージを入力してください" rows="4"></textarea>
            <input type="number" id="repeatCount" placeholder="繰り返し回数" min="1" max="10" value="1">
            <button onclick="postMessage()">投稿する</button>
        </div>
        <div id="loadingIndicator">メッセージを読み込んでいます...</div>
        <div id="errorMessage" style="display: none; color: #ff3b30;"></div>
        <div id="messageBoard"></div>
    </div>

    <script>
        const apiBaseUrl = '/api/';
        const getMessagesEndpoint = 'message.getMessages?batch=1&input=%7B%220%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%7D';
        const postMessageEndpoint = 'message.createMessage?batch=1';

        function fetchMessages() {
            fetch(apiBaseUrl + getMessagesEndpoint)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const messages = data[0].result.data.json;
                    displayMessages(messages);
                    document.getElementById('loadingIndicator').style.display = 'none';
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loadingIndicator').style.display = 'none';
                    document.getElementById('errorMessage').textContent = `メッセージの読み込みに失敗しました: ${error.message}`;
                    document.getElementById('errorMessage').style.display = 'block';
                });
        }

        function displayMessages(messages) {
            const messageBoard = document.getElementById('messageBoard');
            messageBoard.innerHTML = '';
            messages.forEach((message, index) => {
                const messageElement = document.createElement('div');
                messageElement.className = 'message';
                messageElement.style.animationDelay = `${index * 0.1}s`;
                messageElement.innerHTML = `
                    <div class="message-header">
                        <span class="message-number">No.${messages.length - index}</span>
                        <span class="message-author">${escapeHtml(message.author)}</span>
                    </div>
                    <div class="message-content">${escapeHtml(message.content)}</div>
                    <div class="message-date">${new Date(message.createdAt).toLocaleString()}</div>
                `;
                messageBoard.appendChild(messageElement);
            });
        }

        function postMessage() {
            const author = document.getElementById('authorInput').value || '名無しさん';
            const content = document.getElementById('messageInput').value;
            const repeatCount = parseInt(document.getElementById('repeatCount').value) || 1;

            if (!content) {
                alert('メッセージを入力してください。');
                return;
            }

            const postData = {
                "0": {
                    "json": {
                        "content": content,
                        "author": author
                    }
                }
            };

            let postedCount = 0;
            for (let i = 0; i < repeatCount; i++) {
                fetch(apiBaseUrl + postMessageEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(postData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                    postedCount++;
                    if (postedCount === repeatCount) {
                        fetchMessages();
                        document.getElementById('messageInput').value = '';
                        document.getElementById('repeatCount').value = '1';
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert(`メッセージの投稿に失敗しました: ${error.message}`);
                });
            }
        }

        function escapeHtml(unsafe) {
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        fetchMessages();
    </script>
</body>
</html>
"""

class KyogakuHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        elif self.path.startswith('/api/'):
            self.proxy_request('GET')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(404)

    def proxy_request(self, method):
        url = API_BASE_URL + self.path[5:]  
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://kyogaku-bbs.utopi-a.dev/'
        }
        
        try:
            if method == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                headers['Content-Type'] = 'application/json'
                req = request.Request(url, data=post_data, headers=headers, method='POST')
            else:
                req = request.Request(url, headers=headers)

            with request.urlopen(req) as response:
                self.send_response(response.status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response.read())
        except error.HTTPError as e:
            self.send_error(e.code, e.reason)
        except error.URLError as e:
            self.send_error(500, str(e))
        except Exception as e:
            self.send_error(500, str(e))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, KyogakuHandler)
    print(f"サーバーを起動しました。ポート: {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()