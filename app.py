import json
import mimetypes
import os
import socket
import sys
import time

from flask import Flask, request, send_file, redirect

root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
PORT = 80


def resource_path(relative_path):
    return sys.path[0] + '/' + relative_path


app = Flask(__name__, static_url_path="", static_folder=resource_path('static'),
            template_folder=resource_path("templates"))


def get_host_ip():
    """
    查询本机局域网ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        print("ip err")
    return 'ip'


@app.errorhandler(404)
def not_found(err):
    return app.send_static_file('index.html')


@app.route('/download')
def remote_download():
    return app.send_static_file('yaaw-zh-hans/index.html'), 200, [("Cache-Control",
                                                                   "no-cache, no-store, must-revalidate"),
                                                                  ("Pragma", "no-cache"), ("Expires", "0"),
                                                                  ("Cache-Control", "public, max-age=0")]


@app.route('/')
def send_index_html():
    if check_client_ip(request.remote_addr):
        return app.send_static_file('index.html'), 200, [("Cache-Control", "no-cache, no-store, must-revalidate"),
                                                         ("Pragma", "no-cache"), ("Expires", "0"),
                                                         ("Cache-Control", "public, max-age=0")]
    else:
        return redirect('/login', code=302)


@app.route('/login')
def send_login_html():
    return app.send_static_file('login.html'), 200, [("Cache-Control", "no-cache, no-store, must-revalidate"),
                                                     ("Pragma", "no-cache"), ("Expires", "0"),
                                                     ("Cache-Control", "public, max-age=0")]


@app.route('/getAssets')
def send_assets(parent=''):
    res = request.args.get("res")
    path = request.args.get("path")
    if res.startswith("mime-type-icon/video/") and path:
        return get_video_preview(path)
    return app.send_static_file(parent + res)


@app.route('/AndroidClientApi')
def android_nas_client():
    # trust my android device, lazy to write android login code..
    if not check_client_ip(request.remote_addr):
        with open(resource_path('') + "user.json", 'r') as f:
            j = json.loads(f.read())
            j['ip'].append(request.remote_addr)
            with open(resource_path('') + "user.json", 'w') as f1:
                f1.write(json.dumps(j))
    api = {}
    a = os.listdir(root)
    a.sort()
    for d in a:
        album = os.path.join(root, d)
        if os.path.isdir(album) and os.path.exists(album + '/.cover'):
            album_item = []
            fs = os.listdir(album)
            fs.sort()
            for f in fs:
                mime = mimetypes.guess_type(f)[0]
                episod = os.path.join(album, f)
                episod_desc = {}
                if os.path.isfile(episod) and ("application/octet-stream" if mime is None else mime).startswith(
                        'video/'):
                    episod_desc['name'] = f
                    bookmark_flag_file = os.path.join(os.path.join(root, 'preview'),
                                                      f'/{d}/{f}'.replace("/", "_") + '.bookmark')
                    episod_desc['watched'] = True if os.path.exists(bookmark_flag_file) else False
                    episod_desc['length'] = os.path.getsize(episod)
                    episod_desc['desc'] = time.ctime(os.path.getmtime(episod))
                    album_item.append(episod_desc)
            api[d] = album_item
    return json.dumps(api, ensure_ascii=False), 200, {"Content-Type": "application/json"}


@app.route('/getFileList')
def send_file_list():
    json_array = []
    path = request.args.get("path")
    a = os.listdir(root + path)
    a.sort()
    for f in a:
        mime = mimetypes.guess_type(f)[0]
        bookmark_flag_file = os.path.join(os.path.join(root, 'preview'), (path + f).replace("/", "_") + '.bookmark')
        if os.path.isdir(root + path + f) and not os.path.exists(root + path + f + '/.cover'):
            # skip folders that might not contains media file
            continue
        if os.path.isfile(root + path + f) and not (
                "application/octet-stream" if mime is None else mime).startswith('video/'):
            # skip file that is not media file
            continue
        json_array.append({
            "name": f,
            "type": "File" if os.path.isfile(root + path + f) else "Directory",
            "mime_type": "application/octet-stream" if mime is None else mime,
            "watched": "watched" if os.path.exists(bookmark_flag_file) else "",
            "bookmark_state": "bookmark_add" if not os.path.exists(bookmark_flag_file) else "bookmark_added"
        })
    return json.dumps(json_array), 200, {"Content-Type": "application/json"}


def file_size_desc(size):
    if size >> 30 >= 1.0:
        return f'{size / (1024 * 1024 * 1024):.2f}GB'
    if size >> 20 >= 1.0:
        return f'{size / (1024 * 1024):.2f}MB'
    if size >> 10 >= 1.0:
        return f'{size / 1024:.2f}KB'
    return f'{size:.2f}B'


@app.route('/toggleBookmark')
def toggle_bookmark():
    if check_client_ip(request.remote_addr):
        path = request.args.get("path")
        bookmark_flag_file = os.path.join(os.path.join(root, 'preview'), path.replace("/", "_") + '.bookmark')
        state = os.path.exists(bookmark_flag_file)
        if state:
            os.remove(bookmark_flag_file)
        else:
            with open(bookmark_flag_file, 'w') as fp:
                fp.write("This is a Bookmark file!")
        return "成功取消标记" if state else "成功标记为看过"
    else:
        return "Permission Denied"


@app.route("/getFile/<file_name>")
def get_file(file_name):
    if check_client_ip(request.remote_addr):
        # url中加一个文件名避免播放器不知道视频文件名
        path = request.args.get("path").replace('%2B', '+')
        return send_file(root + path, as_attachment=True, attachment_filename=path[path.rindex("/") + 1:],
                         conditional=True)
    else:
        return redirect('/login', code=302)


@app.route("/getVideoPreview")
def get_video_preview(_path=None):
    path = _path if _path else request.args.get("path")
    cache_file_name = path.replace("/", "_")
    try:
        # 判断是否有缓存
        new_file = os.path.join(os.path.join(root, 'preview'), cache_file_name + '.jpg')
        if not os.path.exists(new_file):
            import cv2
            cap = cv2.VideoCapture(root + path)  # 读取视频文件
            cap.set(cv2.CAP_PROP_POS_FRAMES, float(1800))
            _, frame = cap.read()
            if not os.path.exists(root + "preview"):
                os.mkdir(root + "preview")
            cv2.imencode('.jpg', frame)[1].tofile(new_file)
        return send_file(new_file)
    except BaseException as a:
        print(a.__str__())
        return a.__str__()


@app.route("/getCover")
def get_cover(_path=None):
    path = request.args.get("cover")
    try:
        new_file = root + f'/{path}/.cover'
        return send_file(new_file)
    except BaseException as a:
        print(a.__str__())
        return a.__str__()


@app.route("/getDeviceName")
def get_device_name():
    import platform
    return platform.node()


def check_client_ip(ip):
    with open(resource_path('') + "user.json", 'r') as f:
        return ip in json.loads(f.read())['ip']


@app.route("/userLogin")
def user_login():
    name = request.args.get("name")
    psw = request.args.get("psw")
    with open(resource_path('') + "user.json", 'r') as f:
        j = json.loads(f.read())
        try:
            if j[name] == psw and not check_client_ip(request.remote_addr):
                j['ip'].append(request.remote_addr)
                with open(resource_path('') + "user.json", 'w') as f1:
                    f1.write(json.dumps(j))
                return "OK"
            else:
                return "用户名或密码错误"
        except KeyError:
            return "用户名或密码错误"


# 不管是什么路径的链接都发送模板html，读取路径然后通过api来加载文件夹与文件
# api
#      √http://localhost:8081/getDeviceName --获取文件Device Name
#      √http://localhost:8081/getFileList?path=/ --获取文件list[{name,type}]
#      √http://localhost:8081/getAssets?res=style.css --获取html模板资源
#      √http://localhost:8081/getFileDetail?path=style.css --获取文件信息[{mime_type,size,last_edit_time}]
#      √http://localhost:8081/getFile?path= --下载文件
#      √http://localhost:8081/getVideoPreview?path= --下载视频文件缩略图
#      ?http://localhost:8081/settings?key=&value= --设置
#      √http://localhost:8081/download --远程下载
#      √http://localhost:8081/else --获取index.html
if __name__ == '__main__':
    print('挂载目录		' + root)
    print('脚本目录		' + resource_path(''))
    print('访问地址		' + 'http://' + get_host_ip() + f':{PORT}/')
    app.run(host="0.0.0.0", port=PORT)
