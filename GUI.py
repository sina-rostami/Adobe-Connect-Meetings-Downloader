import PySimpleGUI as sg
import kntu_vc_dl

sg.theme("Topanga")


def download_meeting(values, window):
    window.close()
    pasted_urls = [l for l in values['-LINKS-'].split("\n") if len(l) > 0]
    kntu_vc_dl.kntu_download(
        values['-USERNAME-'], values['-PASSWD-'], pasted_urls)


layout = [
    [sg.T('"Welcome To Adobe Connect Meetings Downloader"', pad=(220, 0))],
    [sg.T('UserName:')], [sg.Input(key='-USERNAME-', size=(25, 1))],
    [sg.T('Password:')], [sg.Input(key='-PASSWD-', size=(25, 1))],
    [sg.T('Mettings Links:')], [sg.MLine(key='-LINKS-', size=(150, 20))],
    [sg.Button('Download', pad=(350,1))]
]

window = sg.Window('Adobe Connect Meetings Downloader',
                   layout, size=(800, 520), grab_anywhere=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    elif event == "Download":
        download_meeting(values, window)
        break
