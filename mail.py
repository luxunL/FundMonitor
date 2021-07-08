# -*- coding:utf-8 -*-
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
# 发件人地址，通过控制台创建的发件人地址
username = 'LuxunLServer@163.com'
# 发件人密码，通过控制台创建的发件人密码
password = "BGRHPCEFCKUGHLIZ"
# 自定义的回复地址
replyto = 'LuxunLServer@163.com'
# 收件人地址或是地址列表，支持多个收件人，最多60个
#rcptto = ['***', '***']
rcptto = 'Yujer233@qq.com'

with open('fund.html','r') as f:
    s = f.read()
msg['Subject'] = Header(s.split('<h2>')[1].split('</h2>')[0])
msg['From'] = '%s <%s>' % (Header(''), username)
msg['To'] = rcptto
msg['Reply-to'] = replyto
msg['Message-id'] = email.utils.make_msgid()
msg['Date'] = email.utils.formatdate()
# 构建alternative的text/plain部分
#print(s)
#textplain = MIMEText(s, _subtype='plain', _charset='UTF-8')
#print(textplain)
#msg.attach(textplain)
# 构建alternative的text/html部分
texthtml = MIMEText(s, _subtype='html', _charset='UTF-8')
msg.attach(texthtml)
# 发送邮件
try:
    client = smtplib.SMTP_SSL('smtp.163.com',465)
    #python 2.7以上版本，若需要使用SSL，可以这样创建client
    #client = smtplib.SMTP_SSL()
    #SMTP普通端口为25或80
    #client.connect('smtp.163.com')
    #client.ehlo()
    #client.starttls()
    #开启DEBUG模式
    client.set_debuglevel(0)
    client.login(username, password)
    #发件人和认证地址必须一致
    #备注：若想取到DATA命令返回值,可参考smtplib的sendmaili封装方法:
    #      使用SMTP.mail/SMTP.rcpt/SMTP.data方法
    client.sendmail(username, rcptto, msg.as_string())
    client.quit()
    print('邮件发送成功！')
except smtplib.SMTPConnectError as e:
    print('邮件发送失败，连接失败:', e.smtp_code, e.smtp_error)
except smtplib.SMTPAuthenticationError as e:
    print('邮件发送失败，认证错误:', e.smtp_code, e.smtp_error)
except smtplib.SMTPSenderRefused as e:
    print('邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPRecipientsRefused as e:
    print('邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPDataError as e:
    print('邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPException as e:
    print('邮件发送失败, ', str(e))
except Exception as e:
    print('邮件发送异常, ', str(e))
