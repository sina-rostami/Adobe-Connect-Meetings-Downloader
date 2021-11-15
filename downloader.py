import re
import xml.etree.ElementTree as ET
import requests
import os
from bs4 import BeautifulSoup
from requests.sessions import session
import zipfile
import shutil
from tqdm import tqdm
import time
import exporter

from media_converter import convert_media


class Downloader:

    def __init__(self,
                 login_page_url, base_download_url,
                 login_data,
                 login_headers, download_headers):
        print('Preparing...')
        self.login_page_url = login_page_url
        self.base_download_url = base_download_url
        self.pasted_url = None
        self.login_data = login_data
        self.login_headers = login_headers
        self.download_headers = download_headers
        self.dl_session = requests.Session()
        self.name_to_save = None
        self.download_link = None
        self.meeting_page_req = None

    def set_pasted_url(self, url):
        self.pasted_url = url

    def set_name_to_save(self, name):
        self.name_to_save = name

    def login(self, extra_data):
        print('Logging in...')
        req = self.dl_session.get(
            self.login_page_url, headers=self.login_headers, verify=False)
        soup = BeautifulSoup(req.content, 'html5lib')
        for elem in extra_data:
            self.login_data[elem] = soup.find(
                'input', attrs={'name': elem})['value']
        post = self.dl_session.post(req.url,
                                    data=self.login_data, headers=self.login_headers, verify=False)
        if "Invalid credentials" in post.text or "loginerrormessage" in post.text:
            print("Username or Password is Incorrect")
            time.sleep(10)
            return False
        soup = BeautifulSoup(post.content, 'html5lib')
        if 'user_radio_0' in post.text:
            post = self.dl_session.post(post.url, data={'rdb': soup.find('input', attrs={
                                        'name': 'rdb', 'id': 'user_radio_0'})['value'], 'button': 'Log in'}, headers=self.login_headers, verify=False)
        self.set_cookies()
        print('Logged in!')
        return True

    def set_cookies(self):
        print('Setting cookies...')
        session_cookie = ''
        for item in self.dl_session.cookies.get_dict():
            session_cookie = session_cookie + item + "=" + \
                self.dl_session.cookies.get_dict()[item] + "; "
        self.download_headers['Cookie'] = session_cookie
        print('Cookies set!')

    def create_downlaod_link(self):
        print('Creating download link...')
        self.meeting_page_req = self.dl_session.get(
            self.pasted_url, headers=self.download_headers, verify=False)

        self.set_cookies()
        try:
            host_value = re.findall(
                r'var hostValue = \'(.*)\';', self.meeting_page_req.text)[0]
            url_path = re.findall(
                r'var urlPath = \'(/\w+/)\';', self.meeting_page_req.text)[0]
        except:
            print("Invalid Link (maybe you are not authorized!)")
            time.sleep(10)
            return False
        self.base_download_url = host_value
        self.download_link = host_value + \
            url_path + 'output/temp.zip?download=zip'
        print('Download link created!')
        return True

    def download_file(self):
        print('Downloading...')
        try:
            self.download_req = self.dl_session.get(
                self.download_link, headers=self.download_headers, stream=True, verify=False)
            if not os.path.exists('temp'):
                os.mkdir('temp')
            with open('./temp/'+self.name_to_save+'.zip', 'wb') as file:
                t = tqdm(unit_scale=True, desc=self.name_to_save,
                         unit='B', total=int(self.download_req.headers['content-length']))
                for data in self.download_req.iter_content(8192):
                    file.write(data)
                    t.update(8192)
                t.close()
            print(self.name_to_save + ' Downloaded and Saved')
            return True
        except:
            return False

    def download_meeting(self, url):
        self.set_name_to_save(re.findall('recording=(\d+)&', url)[0])
        self.set_pasted_url(url)
        if not self.create_downlaod_link():
            return False
        return self.download_file()

    def download_other_files(self):
        output_directory = './output/'+self.name_to_save+'/'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        print('Downloading other files...')
        index_stream_xml = ET.parse(
            './temp/' + self.name_to_save + '/indexstream.xml')
        for arr in index_stream_xml.findall('Message'):
            if int(arr.get('time')) > 0:
                files = arr.findall(
                    'Array/Object/newValue/documentDescriptor')
                for file in list(files):
                    try:
                        if file.find('downloadUrl').text != None:
                            file_name = re.split(
                                '/', file.find('downloadUrl').text)[6][6:]
                            file_url = self.base_download_url + '/' + re.split('/', file.find('downloadUrl').text)[4] + '/source/' + \
                                file_name + '?download=true'
                        elif file.find('registerContentUrl').text != None:
                            file_name = file.find('theName').text
                            prefix = re.split(
                                '/', file.find('registerContentUrl').text)[1]
                            file_url = self.base_download_url + '/' + prefix + '/output/' + file_name
                        file_name = requests.utils.unquote(file_name)
                        path_to_save = './output/' + self.name_to_save + \
                            '/' + file_name
                        if os.path.isfile(path_to_save):
                            continue
                        print('Downloading ' + file_name)
                        with self.dl_session.get(file_url, stream=True) as req:
                            with open(path_to_save, 'wb') as file_file:
                                t = tqdm(unit_scale=True, desc=file_name,
                                         unit='B', total=int(req.headers['content-length']))
                                for data in req.iter_content(8192):
                                    file_file.write(data)
                                    t.update(8192)
                                t.close()
                    except:
                        continue
        print('other files Downloaded!')

    def remove_temp_directory(self):
        if os.path.isdir('./temp'):
            shutil.rmtree('./temp')
        if os.path.isdir('./__pycache__'):
            shutil.rmtree('./__pycache__')
