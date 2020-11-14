from downloader import Downloader
import re
def kntu_download(user_name, password, kntu_url):
    filename=re.findall('recording=(\d+)&', kntu_url)

    kntu_headers = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    kntu_login_data = {
    'anchor' : '',
    'username' : user_name,
    'password' : password,
    'rememberusername' : '0'
    }

    kntu_downloader = Downloader('https://vc.kntu.ac.ir/login/index.php',
    'https://connect.kntu.ac.ir/',
    kntu_url, kntu_login_data, kntu_headers, kntu_headers, filename[0])

    kntu_downloader.login({'logintoken'})
    kntu_downloader.set_cookies()
    kntu_downloader.create_downlaod_link()
    kntu_downloader.download_file()
    kntu_downloader.save_file()
    kntu_downloader.extract_zip_file()
    kntu_downloader.convert_media()
    kntu_downloader.remove_temp_directory()

kntu_download('username', 'pass', 'copied link')
# username and pass is your vc.kntu.ac.ir credentials
# copied_link should be like :
# https://vc.kntu.ac.ir/mod/adobeconnect/joinrecording.php?id=4442&recording=1421241&groupid=0&sesskey=FkpuiUTGx1