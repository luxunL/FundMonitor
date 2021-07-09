#!/usr/bin/env python
# coding: utf-8

import json
import requests
from lxml import etree
import requests
import time
import os
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
import platform

mySys = platform.system()
if mySys == 'Linux':
    os.chdir('~/FundMonitor/')
elif  mySys == 'Windows'
    os.chdir('~/FundMonitor/')
if not os.path.exists('mail.ini'):
    if mySys == 'Linux':
        os.chdir('/home/jupyter/FundMonitor/')
    elif  mySys == 'Windows'
        os.chdir('C:/Users/hasee/Desktop/FundMonitor/')
    else:
        print('路径不正确！')
        sys.exit()

def mail():
    with open('mail.ini','r') as f:
        # 发件人地址，通过控制台创建的发件人地址
        username = f.readline().strip()
        # 发件人密码，通过控制台创建的发件人密码
        password = f.readline().strip()
        # 自定义的回复地址
        replyto = username
        # 收件人地址或是地址列表，支持多个收件人，最多60个
        #rcptto = ['***', '***']
        rcptto = [s.strip() for s in f.readlines()]
        
    # 构建alternative结构
    msg = MIMEMultipart('alternative')
    
    with open('fund.html','r') as f:
        s = f.read()
    msg['Subject'] = Header(s.split('<h2>')[1].split('</h2>')[0])
    msg['From'] = '%s <%s>' % (Header(''), username)
    msg['To'] = Header(','.join(rcptto))
    msg['Reply-to'] = replyto
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    texthtml = MIMEText(s, _subtype='html', _charset='UTF-8')
    msg.attach(texthtml)
    
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
        #使用SMTP.mail/SMTP.rcpt/SMTP.data方法
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

def str_rate(new,old):
    s = ''
    if new > old:
        s = '+'
    return s + format((new-old)/old*100,'.2f')+'%'

def wirte_front(fname,string):
    fname = fname
    f = open(fname,'r')
    with open('tmp','w') as t:
        t.write(string)
        t.write(f.read())
    f.close()    
    t.close()
    os.remove(fname)
    os.rename('tmp',fname)

def get(code):
    s = requests.Session()
    s.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    code = str(code)
    url = 'https://fund.10jqka.com.cn/data/client/myfund/'+code
    res = s.get(url).json()['data'][0]
    
    name = res['name']
    net = float(res['net'])
    enddate = res['enddate']
    net1 = float(res['net1'])
    enddate1 = res['enddate1']
    hqcode = res['hqcode']
    
    url = 'https://gz-fund.10jqka.com.cn/?module=api&controller=index&action=chart&info=vm_fd_'+hqcode
    gz_all_raw = s.get(url).content.decode().split(';')[1:]
    gzdate = gz_all_raw[0].split('~')[0].split('|')[1][5:]
    gz_all_raw[0] = gz_all_raw[0].split('~')[-1]

    gz_all = []
    for i in gz_all_raw:
        gz_all.append(float(i.split(',')[1]))
            
    return name+' '+code,gz_all,net,enddate,net1,gzdate

def state(gzdate,enddate,gz_all):
    # 0 还没开盘
    # 1 交易中
    # 2 收盘了
    # 3 中午休市
    # 4 净值更新了
    # 5 今天可能休市吧
    if gzdate == time.strftime('%m-%d'):
        if gzdate in enddate:
            s = '净值更新了!'
            STATE = 4
        elif len(gz_all) == 121:
            s = '中午休市!'
            STATE = 3
        elif len(gz_all) == 242:
            s = '收盘了!'
            STATE = 2
        elif len(gz_all) > 0 :
            s = '交易中!'
            STATE = 1
    else:
        if int(time.strftime('%H%M')) < 930:
            s = '还没开盘!'
            STATE = 0
        else :
            s = '今天可能休市吧!'
            STATE = 5
            
    return STATE,s

def cal(gz_all,net,net1,share,STATE):
    if STATE in [0, 4, 5]:
        gz_now,gz_max,gz_min = (0,0,0)
        amount = net * share
        delta = (net - net1)*share
        
    elif STATE in [1, 2, 3]:
        gz_now = gz_all[-1]
        gz_max = max(gz_all)
        gz_min = min(gz_all)
        amount = gz_now * share
        delta = (gz_now - net)*share
    
    return amount, delta, gz_now, gz_max, gz_min

def td(new,ori,date=None):
    if new > ori:
        c = 'red'
    elif new < ori:
        c = 'green'
    else:
        c = 'gray'
    if date is None:
        return '<td style:"text-align: center;"><span style="color:%s;font-size:20;font-weight:bold;">%s</span><br><span style="color:%s;font-size:15;font-weight:bold;">%s</span></td>'%(c,format(new,'.4f'),c,str_rate(new,ori))
    return '<td style:"text-align: center;"><span style="color:%s;font-size:20;font-weight:bold;">%s</span><br><span style="color:%s;font-size:15;font-weight:bold;">%s</span><br><span style="font-size:10;color=gray;">(%s)</span></td>'%(c,format(new,'.2f'),c,str_rate(new,ori),date)
def html_str(name,gz_all,net,enddate,net1,share,STATE):
    
    amount, delta, gz_now, gz_max, gz_min = cal(gz_all,net,net1,share,STATE)
    s='<tr>'
    s+='<td>'+name.split()[0]+'</td>'
    s+='<td>'+name.split()[1]+'</td>'
    
    if STATE in [0, 4, 5]:
        gz_str = td(gz_all[-1],net1)
        gz_max_str = td(max(gz_all),net1)
        gz_min_str = td(min(gz_all),net1)
    else:
        gz_str = td(gz_all[-1],net)
        gz_max_str = td(max(gz_all),net)
        gz_min_str = td(min(gz_all),net)
    jz_str = td(net,net1,enddate[-5:])
    if STATE in [1, 2, 3]:
        zjz_str = td(gz_all[-1]*share,net*share)
    else:
        zjz_str = td(net*share,net1*share,format((net-net1)*share,'.2f'))
    return s + zjz_str + gz_max_str + gz_min_str + gz_str + jz_str + '</tr>'

def main():

    with open('fund.ini','r') as f:
        list=[]
        for line in f.readlines():
            kv = line.strip().split()
            list.append(kv)

    amount_ori = 0
    amount_now = 0
    jz = True
    s=''
    with open('fund.html','w') as  f:        
        fstr='<table border="1" style="text-align: center;width:750;"><tr><th style="text-align: center;">基金名</th><th>代码</th><th>最新值</th><th>最高估值</th><th>最低估值</th><th>盘中估值</th><th>单位净值</th></tr>'
        f.write(fstr)
        for j in list:
            share = float(j[1])
            name,gz_all,net,enddate,net1,gzdate = get(j[0])
            STATE,strState = state(gzdate,enddate,gz_all)
            amount, delta, gz_now, gz_max, gz_min = cal(gz_all,net,net1,share,STATE)
            if not STATE == 4:
                jz = False
            if STATE in [0, 5, 4]:
                amount_now += net * share
                amount_ori += net1 * share
            elif STATE in [1, 2, 3]:
                amount_now += gz_now * share
                amount_ori += net * share
            fstr = html_str(name,gz_all,net,enddate,net1,share,STATE)
            f.write(fstr)
        fstr = '</table>'
        f.write(fstr)
        f.write('</html>')
    s1 = ''
    if amount_now > amount_ori:
        color = 'red'
        s1 = '+'
    elif amount_now < amount_ori:
        color = 'green'
    else:
        color = 'gray'
    s0 = format(amount_now,'.2f')+' 元 '
    s1 += format(amount_now-amount_ori,'.2f')+' 元 '
    s2 = str_rate(amount_now,amount_ori)
    s3 = ' ('+gzdate+')'
    if not jz:
        s3 += '*'
    s += '<html><head><meta charset="utf-8"></head>'
    s += '<div><p><span style="color:%s;font-size:60;font-weight:900;">%s </span> <span style="color:%s;font-size:40;font-weight:900;">%s </span> <span style="color:%s;font-size:30;font-weight:400;">%s</span> <span style="color:black;font-size:25;">%s</span></p></div>'%(color,s0,color,s1,color,s2,s3)
    s += '<h2>'
    if jz:
        s += '净值更新了！'
    elif STATE in [0, 1, 2, 3, 5]:
        s += strState
    else:
        s += '收盘了！等待更新净值！'
    s += '  ' + time.strftime('%m-%d')
    s += '</h2>'
    s += '<br>'
    wirte_front('fund.html',s)

main()

mail()
