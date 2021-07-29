import smtplib
import socket
from email.header import Header
from email.mime.text import MIMEText
from time import sleep


def get_host_ip():
    """
    查询本机局域网ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        s.close()
        return "0.0.0.0"
    return ip


def sendMail(msg_to: str, message: str, subject: str):
    msg_from = ''  # 发送方邮箱地址。
    password = ''  # 发送方QQ邮箱授权码，不是QQ邮箱密码。

    # subject = "体温填报"  # 主题。
    content = message  # 邮件正文内容。
    msg = MIMEText(content, 'plain', 'utf-8')

    msg_header = Header('花生酱', 'utf-8')
    msg_header.append('<290120506@qq.com>', 'ascii')

    msg['Subject'] = subject
    msg['From'] = msg_header
    msg['To'] = msg_to

    try:
        client = smtplib.SMTP_SSL('smtp.qq.com', smtplib.SMTP_SSL_PORT)
        client.login(msg_from, password)
        client.sendmail(msg_from, msg_to, msg.as_string())
        client.quit()
        return True
    except Exception:
        print("error")

    return False


if __name__ == '__main__':
    result = False
    ip = ''
    while True:
        host_ip = get_host_ip()
        print(f'current_ip:{host_ip} last_ava_ip:{ip} last_send_result:{result}')
        if ip != host_ip or not result:
            result = sendMail("290120506@qq.com", "当前IP:" + host_ip, "Raspberry 4B")
            if result:
                ip = host_ip
                print("save ip=" + ip)
        sleep(60)
