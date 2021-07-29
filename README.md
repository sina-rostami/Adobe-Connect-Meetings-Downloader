<p align="center">
<b>Adobe-Connect-Based-Meetings-Downloader</b><br>
<b> دانلودر جلسات ادوبی کانکت </b><br>
<a href="https://github.com/online-meeting-downloader/Adobe-Connect-Based-Meetings/wiki"> آموزش فارسی</a><br>
</p>


### requirements
it's enough to just you've installed `python` and `pip` on your device.

then to install requierments for the first time
run the command below in your terminal in the repository directory:
```
pip install -r requirements.txt
```


### Usage

+ simply run `GUI.py` file for the Graphical User Interface (for export-only mode, you should first follow cli instructions):
```
python GUI.py
```

or to use Command Line Interface (CLI) follow these steps :
+ to use full-featured mode:
  + open `info.txt` file,<br>
  + replace username and password with your username and password,<br>
  + paste links you want to download in place of urls
  + run your university module.
  >#### KNTU
  >```
  >python kntu_vc_dl.py
  >```

<br>

+ and if your institute isn't supported yet, you can use export-only mode by following these steps:
  + open your recorded class in browser.
  + it's link must be something like this :<br>
  `my-uni.com/ABCDEFGHIJK/...*`
  + change it to this format:<br>
  `my-uni.com/ABCDEFGHIJK/output/temp.zip?download=zip`
  + paste generated link in the same tab and press enter.
  + a file named `temp.zip` starts downloading.
  + create a directory named `temp` in repository and move all your zip files in it.
  + now run this command:<br>
  `python export_only.py`



#### Example
After editing the `info.txt` file, it should be like this:<br>
```
9123456
mypassword
https://vc.kntu.ac.ir/mod/adobeconnect/joinrecording.php?id=1111&recording=2222&groupid=0&sesskey=aaaaaaa
https://vc.kntu.ac.ir/mod/adobeconnect/joinrecording.php?id=2222&recording=3333&groupid=0&sesskey=bbbbbbb
```

### Supported Univesities
+ Khaje Nasir Toosi University Of Technology
+ University Of Tehran
+ Imam Khomeini International University