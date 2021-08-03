var path_list = [];

function goNext(name) {
    path_list.push(name);
    getFileList();
}

function goBack() {
    if (path_list.length > 0) {
        path_list.pop()
        getFileList();
    } else openSnackbar("不能再返回了");
}

function onItemClick(name, type, mime_type) {
    console.log(name);
    if (type === "Directory")
        goNext(name);
}

Array.prototype.toString = function() {
  if(this.length == 0) {
    return '/';
  }
  return this.join('/');
};

Array.prototype.toPath = function() {
  if(this.length == 0) {
    return '/';
  }
  return '/'+this.join('/') + '/';
};

function getFileList() {
    $.get("/getFileList?path=" + path_list.toPath(), function (data) {
        $('#dir-panel').empty();
        $('#file-panel').empty();
        $('.mdc-top-app-bar__title').text(path_list.toString())
        for (const list of eval(data)) {
            if (list.type === "Directory")
                //其实是不需要url编码的，只需要把+替换一下（+可以存在于文件名，但是在url里面不行）
                $('div#dir-panel').append(String.format(directory_html_data, list.name.substring(list.name.lastIndexOf('/')+1)))
            else {
                let __1 = list.name
                let _0 = __1.substring(__1.lastIndexOf('/')+1)
                console.log(_0)
                let _1 = list.mime_type
                let _2 = __1.replace('+', '%2B')
                let _3 = window.location.host + "/getFile/" + _0 + "?path=" + _2
                let _4 = _2
                let _5 = list.bookmark_state
                let _6 = list.watched
                $('div#file-panel').append(String.format(file_html_data, _0, _1, _2, _3, _4, _5, _6));
            }
        }
    });
}

function getFileDetail(fileName, mime_type) {
    $.get("/getFileDetail?path=" + root + fileName, function (data) {
        //文件名
        $('.file-dialog-name__text').text(fileName);
        $('.mdc-list-detail-panel').empty();
        $('.mdc-dialog__actions_').empty();
        //判断是否是视频文件
        let _2 = "/getVideoPreview?path=" + root + fileName
        //详情
        let bookmark;
        for (const list of eval(data)) {
            if (list.key === "bookmark_state") {
                bookmark = list.value
                continue
            }
        }
        $('div.mdc-dialog__actions_').append(String.format(dialog_actions_html, window.location.host + "/getFile/" + fileName + "?path=" + root + fileName, isVideo, root + fileName, bookmark))
        showDialog();
    });
}

function onDialogButtonClick(url, type) {
    console.log(url)
    if (type === "copy") {
        const clipboard = new ClipboardJS('.dialog-copy', {
            text: function (trigger) {
                return encodeURI(url);
            }
        });
        clipboard.on('success', function (e) {
            openSnackbar("复制成功");
            e.clearSelection();
            clipboard.destroy();
        });
        clipboard.on('error', function (e) {
            openSnackbar("复制失败：" + data + "，请手动复制");
            clipboard.destroy();
        });
    } else if (type === "download") {
        window.open(encodeURI("http://" + url));
    } else if (type === "play") {
        window.open(encodeURI("potplayer://http://" + url));
    } else if (type === "bookmark") {
        $.get("/toggleBookmark?path=" + url, function (data) {
            openSnackbar(data)
            getFileList()
        });
    }
}

String.format = function () {
    if (arguments.length === 0)
        return null;
    let str = arguments[0];
    for (let i = 1; i < arguments.length; i++) {
        const re = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
        str = str.replace(re, arguments[i]);
    }
    return str;
};

function openSnackbar(error_msg) {
    $("div.mdc-snackbar__label").text(error_msg);
    const snackbar = new mdc.snackbar.MDCSnackbar(document.querySelector('.mdc-snackbar'));
    snackbar.open();
}

function showDialog() {
    const dialog = new mdc.dialog.MDCDialog(document.querySelector('#dialog-detail'));
    dialog.open();
}

function addRemoteDownload() {
    const dialog = new mdc.dialog.MDCDialog(document.querySelector('#dialog-download'));
    dialog.open();
}

getFileList()