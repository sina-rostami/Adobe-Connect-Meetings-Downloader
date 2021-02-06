import PySimpleGUI as sg
import kntu_vc_dl
import threading

sg.theme("Reddit")

def download_thread(values, window):
    pasted_urls = values['-LINKS-'].split("\n")
    kntu_vc_dl.kntu_download(values['-USERNAME-'], values['-PASSWD-'], pasted_urls)
    window.reappear()


layout = [[sg.T("Username:")], [sg.Input(key="-USERNAME-", size=(20,1))],
        [sg.T("Password:")], [sg.Input(key="-PASSWD-", size=(20,1))],
        [sg.T("Links:")], [sg.MLine(key="-LINKS-", size=(60, 15))],
        [sg.Button("START")]]


window = sg.Window('Adobe Connect Based Meeting Downloader', layout, size=(500, 500))

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    elif event == "START":
        window.disappear()
        threading.Thread(target=download_thread, args=(values,window)).start()
