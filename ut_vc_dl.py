from downloader import Downloader
import exporter
import os
import re
import shutil
import time

def ut_download(user_name, password, pasted_urls):

    ut_headers = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    ut_login_data = {
    'username' : user_name,
    'password' : password,
    '_eventId' : 'submit',
    'geolocation' : '',
    'submit' : 'LOGIN'
    }

    ut_downloader = Downloader('http://elearn.ut.ac.ir/', '', ut_login_data, ut_headers, ut_headers)

    if not ut_downloader.login({'execution'}):
        print("username or password is incorrect!")
        time.sleep(10)
        return

    for url in pasted_urls:
        if re.match(r'https://elearn\d*\.ut\.ac\.ir/mod/adobeconnect\d*/joinrecording\.php.*', url):
            filename=re.findall('recording=(\d+)&', url)[0]
            if not ut_downloader.download_meeting(url):
                print('An error occurred during download...')
                time.sleep(10)
                continue
            exporter.export(filename)
            ut_downloader.download_other_files()
            print(filename + ' is ready!')
        else:
            print('Wrong URL format')
            time.sleep(10)

    ut_downloader.remove_temp_directory()

if __name__ == '__main__':
    with open('info.txt', 'r') as f:
        lines = f.read().splitlines()
        user_name = lines[0]
        password = lines[1]
        ut_download(user_name, password, lines[2:])
