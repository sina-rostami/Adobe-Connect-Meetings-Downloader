import requests
from downloader import Downloader
import time
import re


class IkiuDownloader(Downloader):

    file_id = ""

    def __init__(self, username, password):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        }

        login_data = {
            'anchor': '',
            'username': username,
            'password': password,
            'rememberusername': '0'
        }

        super().__init__('http://lms.ikiu.ac.ir/blocks/whc_backup/login.php',
                         'https://ac.aminidc.com',
                         login_data, headers, headers)

    def login(self):
        return super().login({'logintoken'})

    def create_downlaod_link(self):
        self.download_link = f'{self.base_download_url}/{self.file_id}/output/{self.file_id}.zip?download=zip'
        return True

    def batch_download(self, links: list[str]):
        self.set_cookies()
        for url in links:
            if re.match(r'https://ac\.aminidc\.com/(.*)/.*', url):
                self.file_id = re.findall('https://ac\.aminidc\.com/(.*)/.*', url)[0]
                src = requests.get(url, headers=self.download_headers)
                t = re.findall('roomNameForMobile = "(.*?)";', src.text)[0]
                self.name_to_save = t.encode().decode("unicode-escape")
                print('Downloading ' + self.name_to_save + '...')
                self.set_pasted_url(url)
                self.create_downlaod_link()

                self.download_file()
                self.save_file()
                self.extract_zip_file()
                self.convert_media()
                self.download_other_files()
                print(self.name_to_save + ' downloaded!')
            else:
                print('invalid url ')
        self.remove_temp_directory()

async def convertq(arg):
    pass

if __name__ == '__main__':
    with open('info.txt', 'r') as f:
        lines = f.read().splitlines()
        user_name = lines[0]
        password = lines[1]
        iku_dl = IkiuDownloader(user_name, password)
        iku_dl.batch_download(lines[2:])
