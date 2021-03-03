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
            self.login_page_url, headers=self.login_headers)
        soup = BeautifulSoup(req.content, 'html5lib')
        for elem in extra_data:
            self.login_data[elem] = soup.find(
                'input', attrs={'name': elem})['value']
        post = self.dl_session.post(self.login_page_url,
                                    data=self.login_data, headers=self.login_headers)
        if "loginerrormessage" in post.text:
            print("Username or Password is Incorrect")
            time.sleep(10)
            return False
        print('Logged in!')
        return True

    def set_cookies(self):
        print('Setting cookies...')
        self.meeting_page_req = self.dl_session.get(
            self.pasted_url, headers=self.download_headers)
        session_cookie = ''
        for item in self.dl_session.cookies.get_dict():
            session_cookie = session_cookie + item + "=" + \
                self.dl_session.cookies.get_dict()[item] + "; "
        self.download_headers['Cookie'] = session_cookie
        print('Cookies set!')

    def create_downlaod_link(self):
        print('Creating download link...')
        bs = BeautifulSoup(self.meeting_page_req.content, 'html5lib')
        script_dl = bs.find_all('script', attrs={'language': 'JavaScript'})
        meeting_real_link = re.findall(
            "var urlPath = '/(.*)/';", str(script_dl))
        if len(meeting_real_link) == 0:
            print("Invalid Link (maybe you are not authorized!)")
            time.sleep(10)
            return False
        self.download_link = self.base_download_url + \
            meeting_real_link[0] + '/output/temp.zip?download=zip'
        print('Download link created!')
        return True

    def download_file(self):
        print('Downloading...')
        self.download_req = self.dl_session.get(
            self.download_link, headers=self.download_headers, stream=True)

    def save_file(self):
        print('Saving file...')
        if not os.path.exists('temp'):
            os.mkdir('temp')
        if not os.path.exists('temp/'+self.name_to_save):
            os.mkdir('temp/'+self.name_to_save)
        with open('./temp/'+self.name_to_save+'/'+self.name_to_save+'.zip', 'wb') as file:
            t = tqdm(unit_scale=True, desc=self.name_to_save,
                     unit='B', total=int(self.download_req.headers['content-length']))
            for data in self.download_req.iter_content(8192):
                file.write(data)
                t.update(8192)
            t.close()
        print(self.name_to_save + ' Downloaded and Saved')

    def extract_zip_file(self):
        print('Extracting data...')
        zipfile.ZipFile('./temp/'+self.name_to_save+'/'+self.name_to_save +
                        '.zip', 'r').extractall('temp/'+self.name_to_save)
        print('Extracted!')

    def convert_media(self):
        print('Converting media...')
        convert_media(self.name_to_save)
        print('Converted!')

    def download_other_files(self):
        output_directory = './output/'+self.name_to_save+'/'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        print('Downloading pdfs...')
        index_stream_xml = ET.parse(
            './temp/' + self.name_to_save + '/indexstream.xml')
        pdfs = index_stream_xml.findall(
            'Message/Array/Object/newValue/documentDescriptor/downloadUrl')
        for pdf in list(pdfs):
            try:
                pdf_name = re.split('/', pdf.text)[6][6:]
                pdf_url = self.base_download_url + \
                    re.split('/', pdf.text)[4] + '/source/' + \
                    pdf_name + '?download=true'
                path_to_save = './output/' + self.name_to_save + '/' + pdf_name
                if os.path.isfile(path_to_save):
                    continue
                print('Downloading ' + pdf_name)
                with self.dl_session.get(pdf_url, headers=self.download_headers, stream=True) as req:
                    with open(path_to_save, 'wb') as pdf_file:
                        t = tqdm(unit_scale=True, desc=pdf_name,
                                 unit='B', total=int(req.headers['content-length']))
                        for data in req.iter_content(2048):
                            pdf_file.write(data)
                            t.update(2048)
                        t.close()
            except:
                continue
        print('Pdfs Downloaded!')

    def remove_temp_directory(self):
        if os.path.isdir('./temp'):
            shutil.rmtree('./temp')
        if os.path.isdir('./__pycache__'):
            shutil.rmtree('./__pycache__')
