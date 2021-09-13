from downloader import Downloader
import time
import re
import exporter

def iut_download(user_name, password, pasted_urls):

    iut_headers = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    iut_login_data = {
    'anchor' : '',
    'username' : user_name,
    'password' : password,
    'rememberusername' : '0'
    }

    iut_downloader = Downloader('https://elearning.iut.ac.ir/login/index.php',
    'https://ve.iut.ac.ir/',
    iut_login_data, iut_headers, iut_headers)

    if not iut_downloader.login({'logintoken'}):
        return

    for url in pasted_urls:
        if re.match(r'https://elearning\d*\.iut\.ac\.ir/mod/adobeconnect/joinrecording\.php.*', url):
            meeting_id=re.findall('recording=(\d+)&', url)[0]
            if not iut_downloader.download_meeting(url):
                print('An error occurred during download...')
                time.sleep(10)
                continue
            exporter.export(meeting_id)
            iut_downloader.download_other_files()
            print(meeting_id + ' is ready!')
        else:
            print('Wrong URL format')
            time.sleep(10)

    iut_downloader.remove_temp_directory()

if __name__ == '__main__':
    with open('info.txt', 'r') as f:
        lines = f.read().splitlines()
        user_name = lines[0]
        password = lines[1]
        iut_download(user_name, password, lines[2:])
