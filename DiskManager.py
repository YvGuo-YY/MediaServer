import ctypes
import os.path
import platform
import shutil


def file_size_desc(size):
    if size >> 30 >= 1.0:
        return f'{size / (1024 * 1024 * 1024):.2f}GB'
    if size >> 20 >= 1.0:
        return f'{size / (1024 * 1024):.2f}MB'
    if size >> 10 >= 1.0:
        return f'{size / 1024:.2f}KB'
    return f'{size:.2f}B'


def get_free_space(folder):
    """
    获取磁盘剩余空间
    :param folder: 磁盘路径 例如 D:\\
    :return: 剩余空间
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize


class DiskManager:
    _disk_manager_dir = "_disk_manager_dir"
    _preview_cache_dir = "_preview_cache_dir"
    # 树莓派4B有两个USB2.0口，降低其优先级
    # 3.0, 3.0, 2.0, 2.0
    _disk_weight = [1.0, 1.0, 3.0, 3.0]

    def __init__(self, disk_list: list):
        # 磁盘绝对路径数组，通过终端传参
        self.disk_list = disk_list
        self.disk_names = []
        if not os.path.exists(self._disk_manager_dir):
            os.mkdir(self._disk_manager_dir)
        else:
            shutil.rmtree(self._disk_manager_dir)
            os.mkdir(self._disk_manager_dir)
        if not os.path.exists(self._preview_cache_dir):
            os.mkdir(self._preview_cache_dir)
        self.root = self._disk_manager_dir
        for path in self.disk_list:
            self.disk_names.append(path[path.rfind("/") + 1:])
            os.system(f'ln -s {path} {os.path.join(self._disk_manager_dir, path[path.rfind("/") + 1:])}')

    def listdir(self, path) -> list:
        li = []
        print(path == '/', path)
        for disk in (self.disk_names if path == '/' else [path[1:]]):
            a = os.listdir(os.path.join(self.root, disk))
            a.sort()
            for f in a:
                li.append(f'{disk}/{f}')
        return li

    def get_max_avl_disk(self):
        _max = (-1, '')
        for i, path in enumerate(self.disk_list):
            free = get_free_space(path) / self._disk_weight[i]
            if free > _max[0]:
                _max = (free, path[path.rfind("/") + 1:])
        return _max[1]

    def __print__(self):
        print('=======DiskManager=======')
        [print(path, '\t', file_size_desc(os.path.getsize(path)), 'used\t', file_size_desc(get_free_space(path)), 'avl')
         for path in self.disk_list]
        print('=======DiskManager=======')

    @property
    def preview_cache_dir(self):
        return self._preview_cache_dir

    @property
    def disk_manager_dir(self):
        return self._disk_manager_dir
