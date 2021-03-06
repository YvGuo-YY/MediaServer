import json
import mimetypes
import os
import sys
import threading
import time

from flask import Flask, request, send_file, redirect

from DiskManager import DiskManager
from tools import get_season_name, start_services, is_known_ip, resource_path, path_join, name_from_path, \
    triple_path_join

disk_manager = DiskManager(sys.argv[1:])
root = disk_manager.disk_manager_dir
PORT = 80
get_preview_lock = threading.Semaphore(4)

app = Flask(__name__, static_url_path="", static_folder=resource_path('static'),
            template_folder=resource_path("templates"))


@app.errorhandler(404)
def not_found(err):
    return app.send_static_file('index.html')


@app.route('/download')
def remote_download():
    return app.send_static_file('yaaw/index.html'), 200, [("Cache-Control",
                                                           "no-cache, no-store, must-revalidate"),
                                                          ("Pragma", "no-cache"), ("Expires", "0"),
                                                          ("Cache-Control", "public, max-age=0")]


@app.route('/')
def send_index_html():
    if is_known_ip(request.remote_addr):
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


@app.route('/getFileList')
def send_file_list():
    json_array = []
    path = request.args.get("path")
    usr = ''
    ps = ''
    try:
        usr = request.args.get("usr")
        ps = request.args.get("ps")
    except Exception:
        pass
    if not is_known_ip(request.remote_addr) and user_login(usr, ps) != "OK":
        return json.dumps([{
            "name": "?????????",
            "type": "File",
            "mime_type": "application/octet-stream",
            "watched": "watched",
            "bookmark_state": "bookmark_add"
        }]), 403, {"Content-Type": "application/json"}
    a = disk_manager.listdir(path)
    a.sort()
    for f in a:
        mime = mimetypes.guess_type(f)[0]
        bookmark_flag_file = path_join(disk_manager.preview_cache_dir, name_from_path(f).replace('%2B', '+') + '.b')
        if os.path.isdir(path_join(root, f)) and not os.path.exists(triple_path_join(root, f, '.cover')):
            # skip folders that might not contains media file
            continue
        if os.path.isfile(path_join(root, f)):
            if ("application/octet-stream" if mime is None else mime).startswith('video/'):
                f_type = "File"
            elif not f[f.rindex('/') + 1:].startswith('.'):
                f_type = "Attach"
            else:
                continue
        else:
            f_type = "Directory"
        json_array.append({
            "name": f,
            "length": os.path.getsize(path_join(root, f)) if os.path.isfile(path_join(root, f)) else 0,
            "desc": time.ctime(os.path.getmtime(path_join(root, f))),
            "type": f_type,
            "mime_type": "application/octet-stream" if mime is None else mime,
            "watched": "watched" if os.path.exists(bookmark_flag_file) else "",
            "bookmark_state": "bookmark_add" if not os.path.exists(bookmark_flag_file) else "bookmark_added"
        })
    return json.dumps(json_array), 200, {"Content-Type": "application/json"}


@app.route('/toggleBookmark')
def toggle_bookmark():
    if is_known_ip(request.remote_addr):
        path = request.args.get("path")
        bookmark_flag_file = path_join(disk_manager.preview_cache_dir, name_from_path(path).replace('%2B', '+') + '.b')
        state = os.path.exists(bookmark_flag_file)
        if state:
            os.remove(bookmark_flag_file)
        else:
            with open(bookmark_flag_file, 'w') as fp:
                fp.write("This is a Bookmark file!")
        return "??????????????????" if state else "?????????????????????"
    else:
        return "Permission Denied"


@app.route("/getFile/<file_name>")
def get_file(file_name):
    if is_known_ip(request.remote_addr):
        # url????????????????????????????????????????????????????????????
        path = request.args.get("path").replace('%2B', '+')
        return send_file(path_join(root, path), as_attachment=True, download_name=name_from_path(path),
                         conditional=True)
    else:
        return redirect('/login', code=302)


@app.route("/getVideoPreview")
def get_video_preview(_path=None):
    if get_preview_lock.acquire():
        path = _path if _path else request.args.get("path")
        new_file = path_join(disk_manager.preview_cache_dir, name_from_path(path).replace('%2B', '+') + '.jpg')
        try:
            if not os.path.exists(new_file):
                os.system(f'ffmpeg -i \"{path_join(root, path)}\" -ss 00:00:05.000 -vframes 1 \"{new_file}\"')
            get_preview_lock.release()
            return send_file(new_file)
        except BaseException as a:
            print(a.__str__())
            get_preview_lock.release()
            return a.__str__()


@app.route("/getCover")
def get_cover(_path=None):
    return send_file(triple_path_join(root, request.args.get("cover"), '.cover'))


@app.route("/getDeviceName")
def get_device_name():
    import platform
    return platform.node()


@app.route("/notify")
def get_notify():
    return app.send_static_file('notify.html'), 200, [("Cache-Control", "no-cache, no-store, must-revalidate"),
                                                      ("Pragma", "no-cache"), ("Expires", "0"),
                                                      ("Cache-Control", "public, max-age=0")]


@app.route("/userLogin")
def user_login(name=None, psw=None) -> str:
    name = name if name else request.args.get("name")
    psw = psw if psw else request.args.get("psw")
    with open(resource_path('') + "user.json", 'r') as f:
        j = json.loads(f.read())
        if j.__contains__(name):
            if j[name] == psw:
                if not is_known_ip(request.remote_addr):
                    j['ip'].append(request.remote_addr)
                with open(resource_path('') + "user.json", 'w') as f1:
                    f1.write(json.dumps(j))
                return "OK"
            else:
                return "????????????"
        else:
            return "???????????????"


@app.route("/remote_download", methods=['POST', 'GET'])
def add_remote_download():
    if request.method == 'GET':
        return app.send_static_file('remote_download.html'), 200, [("Cache-Control", "no-cache, no-store, "
                                                                                     "must-revalidate"),
                                                                   ("Pragma", "no-cache"), ("Expires", "0"),
                                                                   ("Cache-Control", "public, max-age=0")]
    from pyaria2 import Aria2RPC
    out = request.form['out']
    url = request.form['url']
    jsonrpc = Aria2RPC(token="0930")
    season_name = get_season_name(out)
    options = {"out": out,
               "dir": triple_path_join(disk_manager.disk_manager_dir, disk_manager.get_max_avl_disk(),
                                       'Download' if not season_name else season_name),
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55"}
    jsonrpc.addUri([url], options=options)
    return "<script>window.close();</script>", 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == '__main__':
    logo = r"""
                                                  __                                          
                                                 /\ \__                                       
     _____      __      __       ___     __  __  \ \ ,_\             ___       __       ____  
    /\ '__`\  /'__`\  /'__`\   /' _ `\  /\ \/\ \  \ \ \/   _______ /' _ `\   /'__`\    /',__\ 
    \ \ \L\ \/\  __/ /\ \L\.\_ /\ \/\ \ \ \ \_\ \  \ \ \_ /\______\/\ \/\ \ /\ \L\.\_ /\__, `\
     \ \ ,__/\ \____\\ \__/.\_\\ \_\ \_\ \ \____/   \ \__\\/______/\ \_\ \_\\ \__/.\_\\/\____/
      \ \ \/  \/____/ \/__/\/_/ \/_/\/_/  \/___/     \/__/          \/_/\/_/ \/__/\/_/ \/___/ 
       \ \_\                                                                                  
        \/_/                                                         build.2021.8.3 by ????????????
    """
    print(f"\033[1;33m{logo}\033[0m")
    start_services()
    app.run(host="0.0.0.0", port=PORT)
