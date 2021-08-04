import json
import sys


def file_size_desc(size):
    if size >> 30 >= 1.0:
        return f'{size / (1024 * 1024 * 1024):.2f}GB'
    if size >> 20 >= 1.0:
        return f'{size / (1024 * 1024):.2f}MB'
    if size >> 10 >= 1.0:
        return f'{size / 1024:.2f}KB'
    return f'{size:.2f}B'


def get_season_name(name: str):
    import re
    regex = r"(.*)\.S\d{2}"
    matches = re.finditer(regex, name, re.MULTILINE | re.IGNORECASE)
    for matchNum, match in enumerate(matches, start=1):
        return match.group(1).replace('.', ' ').strip()
    return None


def start_services():
    try:
        import plugin.logger
        import plugin.aria2
        import plugin.fan
    except Exception as e:
        print(e)


def is_known_ip(ip):
    with open(resource_path('') + "user.json", 'r') as f:
        return ip in json.loads(f.read())['ip']


def resource_path(relative_path):
    return sys.path[0] + '/' + relative_path
