from flask import Flask,request,Response,render_template
from cctv import CCTV

app = Flask(__name__)

token = "zyg19960622"

cctv = CCTV(save_path='/home/yaosheng/cctv/')
cctv.start_record()

@app.route('/video')
def index():
    return render_template('index.html')

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/stop')
def stop():
    cctv.stop_record()
    return "Stopped"


@app.route('/start')
def start():
    cctv.start_record()
    return "Started"


def gen(cctv):
    while True:
        frame = cctv.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    if request.args['token'] == token:
        return Response(gen(cctv), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Wrong Token"


if __name__ == '__main__':
    app.run(host='0.0.0.0')

