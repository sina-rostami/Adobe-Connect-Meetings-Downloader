from tkinter import Scrollbar
from tkinter.constants import CENTER
import PySimpleGUI as sg
import export_only
import kntu_vc_dl
import ut_vc_dl
import ikiu_vc_dl

sg.theme("Topanga")


def download_meeting(values, window):
    window.close()
    pasted_urls = [l for l in values['-LINKS-'].split("\n") if len(l) > 0]
    if values['-UNI-'] == 'Khaje Nasir Toosi University Of Technology':
        kntu_vc_dl.kntu_download(
            values['-USERNAME-'], values['-PASSWD-'], pasted_urls)
    elif values['-UNI-'] == 'University Of Tehran':
        ut_vc_dl.ut_download(values['-USERNAME-'], values['-PASSWD-'], pasted_urls)
    elif values['-UNI-'] == 'Imam Khomeini International University':
        ikiu_vc_dl.ikiu_download(values['-USERNAME-'], values['-PASSWD-'], pasted_urls)


layout = [
    [sg.T('"Welcome To Adobe Connect Meetings Downloader"', pad=(220, 0))],
    [sg.T('University:')], [sg.Combo(['Khaje Nasir Toosi University Of Technology', 'University Of Tehran', 'Imam Khomeini International University'], key='-UNI-')],
    [sg.T('UserName:')], [sg.Input(key='-USERNAME-', size=(25, 1))],
    [sg.T('Password:')], [sg.Input(key='-PASSWD-', size=(25, 1))],
    [sg.T('Mettings Links:')], [sg.MLine(key='-LINKS-', size=(150, 8))],
    [sg.Button('Download'), sg.Button('Export-Only')],
]

window = sg.Window('Adobe Connect Meetings Downloader',
                   layout, size=(800, 450), grab_anywhere=True, resizable=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    elif event == "Download":
        download_meeting(values, window)
        break
    elif event == "Export-Only":
        window.close()
        export_only.export_only()
        break
