import re
import xml.etree.ElementTree as ET
import requests
import os
from bs4 import BeautifulSoup
from requests.sessions import session
import zipfile
import shutil

from media_converter import convert_audio, convert_video, print_events_time_table


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
        self.dl_session.post(self.login_page_url,
                             data=self.login_data, headers=self.login_headers)
        print('Logged in!')

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
        self.download_link = self.base_download_url + \
            meeting_real_link[0] + '/output/temp.zip?download=zip'
        print('Download link created!')

    def download_file(self):
        print('Downloading...')
        self.download_req = self.dl_session.get(
            self.download_link, headers=self.download_headers)
        print('Downloaded!')

    def save_file(self):
        print('Saving file...')
        if not os.path.exists('temp'):
            os.mkdir('temp')
        if not os.path.exists('temp/'+self.name_to_save):
            os.mkdir('temp/'+self.name_to_save)
        with open('./temp/'+self.name_to_save+'/'+self.name_to_save+'.zip', 'wb') as file:
            file.write(self.download_req.content)
        print('File Saved')

    def extract_zip_file(self):
        print('Extracting data...')
        zipfile.ZipFile('./temp/'+self.name_to_save+'/'+self.name_to_save +
                        '.zip', 'r').extractall('temp/'+self.name_to_save)
        print('Extracted!')

    def convert_media(self):
        print('Converting media...')
        print_events_time_table(self.name_to_save)
        #convert_audio(self.name_to_save)
        #convert_video(self.name_to_save)
        print('Converted!')

    def download_other_files(self):
        print('Downloading pdf...')
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
                print('Downloading ' + pdf_name)
                with self.dl_session.get(pdf_url, headers=self.download_headers) as req:
                    with open('./output/' + self.name_to_save + '/' + pdf_name, 'wb') as pdf_file:
                        pdf_file.write(req.content)
            except:
                pass
        print('Pdf Downloaded!')

    def remove_temp_directory(self):
        shutil.rmtree('./temp')