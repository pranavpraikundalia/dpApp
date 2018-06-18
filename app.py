from flask import Flask, Response, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import datetime, os, shutil
from bson import Binary
from bson.objectid import ObjectId
import time
from itertools import chain
import email
import imaplib
from email.mime.text import MIMEText
import smtplib

from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()
client = MongoClient('localhost', 27017)

db = client['pymongo_test']

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
posts = db.projectX
for i in posts.find({}):
    print(i['_id'])
temp = posts.find_one({'name': 'Vaibhav Sharma'})




@app.route('/')
def hello_world():
    return render_template('homescreen.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['pass']
    if(username == "admin" and password == "admin"):
        tempData = []
        cursor = posts.find({})
        if cursor is not None:
            for i in cursor:
                tempData.append((i['name'],i['_id']))
        else:
            tempData = ["Add users"]

        return render_template('index.html', data=tempData)




@app.route('/login/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        values=["name","dob","ssn","mother","pno","email",'emailPass',"add","fwdadd","hardinq","empat","annsal","lenemp","emppno","empemail"]
        insVal= dict()
        for i in values:
            if request.form[i] =='':
                insVal[i] = "No Data Added"
            else:
                print(request.form[i])
                insVal[i] = request.form[i]
        cursor = posts.find({})
        lstUser = ()

        f = request.files['ssc']
        posts.insert(insVal)
        print("inserted successfully")


        for i in cursor:
            lstUser = (i['_id'])
        print("Last value is {}".format(str(lstUser)))

        tempData = []
        cursor = posts.find({})
        if cursor is not None:
            for i in cursor:
                tempData.append((i['name'],i['_id']))
        else:
            tempData = ["Add users"]
        print(tempData)
        return render_template('index.html', data=tempData)


@app.route('/userInfo/<id>', methods=['POST', 'GET'])
def userInfo(id):
    print("-----------------")
    cursor = posts.find({'_id': ObjectId(id)})
    temp = dict()
    for i in cursor:
        temp = i
    print(temp)
    tList = []
    for k,v in temp.items():
        if k == '_id':
            continue
        else:
            tList.append((k,v))

    print("tList Print :",tList)

    print (tList[0][1],tList[5][1], tList[6][1])
    imap_ssl_host = 'imap.gmail.com'  # imap.mail.yahoo.com
    imap_ssl_port = 993
    username = tList[5][1]
    password =tList[6][1]

    # Restrict mail search. Be very specific.
    # Machine should be very selective to receive messages.
    criteria = {
        'FROM': 'PRIVILEGED EMAIL ADDRESS',
        'SUBJECT': 'SPECIAL SUBJECT LINE',
        'BODY': 'SECRET SIGNATURE',
    }
    uid_max = 0
    server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    server.login(username, password)
    server.select('INBOX')

    result, data = server.uid('search', None, search_string(uid_max, criteria))

    uids = [int(s) for s in data[0].split()]
    if uids:
        uid_max = max(uids)
        # Initialize `uid_max`. Any UID less than or equal to `uid_max` will be ignored subsequently.

    server.logout()

    # Keep checking messages ...
    # I don't like using IDLE because Yahoo does not support it.
    while 1:
        # Have to login/logout each time because that's the only way to get fresh results.

        server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
        server.login(username, password)
        server.select('INBOX')

        result, data = server.uid('search', None, search_string(uid_max, criteria))

        uids = [int(s) for s in data[0].split()]
        for uid in uids:
            # Have to check again because Gmail sometimes does not obey UID criterion.
            #if uid > uid_max:
            result, data = server.uid('fetch', uid, '(RFC822)')  # fetch entire message
            msg = email.message_from_string(data[0][1])

            uid_max = uid

            text = get_first_text_block(msg)
            print ('New message :::::::::::::::::::::')
            print (text)
            break

        server.logout()
        time.sleep(1)

    return render_template('userInformation.html', info=tList)

def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"' + str(t[1]) + '"'), criteria.items())) + [('UID', '%d:*' % (uid_max + 1))]
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)

def get_first_text_block(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()





@app.route('/sendtext/<id>', methods=['POST', 'GET'])
def sendtext(id):
    print("-----------------")
    print(id+"\n")
    cursor = posts.find({'_id': ObjectId(id)})
    temp = dict()
    for i in cursor:
        temp = i
    print(temp)
    tList = []
    for k,v in temp.items():
        tList.append((k,v))
    return render_template('sendtext.html', info = tList)


@app.route('/sendtextmail/<id>', methods=['POST', 'GET'])
def sendtextmail(id):
    print("-----------------")
    print(id)
    #id.replace("%40","@")
    cursor = posts.find({'_id': ObjectId(id.replace(',',""))})
    temp = dict()
    for i in cursor:
        temp = i
    print(temp)
    tList = []
    for k,v in temp.items():
        tList.append((k,v))

    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = tList[6][1]
    password = tList[7][1]
    sender = tList[6][1]
    targets = request.form['sendto']

    msg = MIMEText(request.form['textmail'])
    msg['Subject'] =request.form['subject']
    msg['From'] = sender
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()

    return render_template('userinformation.html', info=tList)

if __name__ == '__main__':
    app.run()