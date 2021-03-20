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
        print(self.download_link)
        return True

    def batch_download(self, links: list[str]):
        for url in links:
            if re.match(r'https://ac\.aminidc\.com/(.*)/.*', url):
                filename = re.findall('https://ac\.aminidc\.com/(.*)/.*', url)[0]
                self.file_id = filename
                print('Downloading ' + filename + '...')
                self.set_name_to_save(filename)
                self.set_pasted_url(url)
                self.set_cookies()
                self.create_downlaod_link()
                self.download_file()
                self.save_file()
                self.extract_zip_file()
                self.convert_media()
                self.download_other_files()
                print(filename + ' downloaded!')
        self.remove_temp_directory()


if __name__ == '__main__':
    with open('info.txt', 'r') as f:
        lines = f.read().splitlines()
        user_name = lines[0]
        password = lines[1]
        iku_dl = IkiuDownloader(user_name, password)
        iku_dl.batch_download(lines[2:])
