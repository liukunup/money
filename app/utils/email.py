import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

def send_email(to_email, subject, message):
    try:
        # 创建邮件对象
        email = MIMEMultipart()
        email['From'] = EMAIL_HOST_USER
        email['To'] = to_email
        email['Subject'] = subject

        # 添加邮件正文
        email.attach(MIMEText(message, 'plain'))

        # 连接到 SMTP 服务器
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()

        # 登录邮箱
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        # 发送邮件
        server.sendmail(EMAIL_HOST_USER, to_email, email.as_string())

        # 关闭连接
        server.quit()
        return True
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        return False