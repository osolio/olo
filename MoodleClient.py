import requests
from yarl import URL
from bs4 import BeautifulSoup
import os
import re
import json

from bs4 import BeautifulSoup

class MoodleClient(object):
    def __init__(self, user,passw):
        self.session = requests.Session()
        self.username = user
        self.password = passw
        self.session = requests.Session()
        self.server = os.environ['SERVER']
        self.repo_id = os.environ['REPO_ID']
        self.headers: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}
        self.session = requests.Session()
    def getsession(self):
        return self.session

    def login(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
        }
        data ={
            'anchor': '',
            'logintoken': "",
            'username': self.username,
            'password': self.password
        }


        r = self.session.get(self.server + "login/index.php", headers=headers)
        html = r.text


        soup = BeautifulSoup(html, 'html.parser')
        data['logintoken'] = soup.find('input',attrs={'name':'logintoken'})['value']
        l = self.session.post(self.server + "login/index.php", headers=headers, data=data)
        print(l.url)
        if l.url == self.server + "my/" or l.url == self.server:
            print("session iniciada")
            return True
        if "es necesario cerrar la sesión antes de volver a iniciar sesión como un usuario diferente." in str(l.text):
            print("session iniciada")
            return True
        if "Datos erróneos. Por favor, inténtelo otra vez." in str(l.text):
            print("Session NO iniciada Datos erróneos")
            return False
        if str(l) != "<Response [200]>":
            print("Session NO iniciada codigo")
            return False
        else:
            print("Session NO iniciada desconocido")
            return False

    def upload_file(self, filename):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
        }
        sesion = self.session
        server = self.server
        repo = self.repo_id
        files = "user/files.php"
        datos = sesion.get(server + files, headers=headers)
        soup = BeautifulSoup(datos.text,'html.parser')
        query = URL(soup.find('object',attrs={'type':'text/html'})['data']).query
        files_filemanager = soup.find('input',attrs={'name':'files_filemanager'})['value']
        submitbutton = soup.find('input',attrs={'name':'submitbutton'})['value']
        client_id_pattern = '"client_id":"\w{13}"'
        client_id = re.findall(client_id_pattern, datos.text)
        client_id = re.findall("\w{13}", client_id[0])[0]
        f = filename
        file = {'repo_upload_file':open(f, "rb")}
        payload_file = {
            'title':'',
            'itemid':query['itemid'],
            'repo_id':repo,
            'p':'',
            'page':'',
            'env':query['env'],
            'sesskey':query['sesskey'],
            'client_id':client_id,
            'maxbytes':query['maxbytes'],
            'areamaxbytes':query['areamaxbytes'],
            'ctx_id':query['ctx_id'],
            'repo_upload_file':open(f, "rb")}
        post_file_url = server + 'repository/repository_ajax.php?action=upload'
        upload = sesion.post(post_file_url, files=file,data=payload_file, headers=headers)
        payload = {
                    'returnurl':server + "user/files.php",
                    'sesskey':query["sesskey"],
                    'files_filemanager':files_filemanager,
                    'cancel':'Cancelar'
                    }
        terminar = sesion.post(server + "user/files.php", data=payload, headers=headers)
        resp = upload.text
        resp = json.loads(resp)
        print(resp["url"])
        return resp["url"]

    def parsejson(self,json):
        print(json)
        return
        data = {}
        tokens = str(json).replace('{','').replace('}','').split(',')
        for t in tokens:
            split = str(t).split(':',1)
            data[str(split[0]).replace('"','')] = str(split[1]).replace('"','')
        return data

    def getclientid(self,html):
        index = str(html).index('client_id')
        max = 25
        ret = html[index:(index+max)]
        return str(ret).replace('client_id":"','')

    def extractQuery(self,url):
        tokens = str(url).split('?')[1].split('&')
        retQuery = {}
        for q in tokens:
            qspl = q.split('=')
            retQuery[qspl[0]] = qspl[1]
        return retQuery
    
