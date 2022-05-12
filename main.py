import PySimpleGUI as sg
from pytube import YouTube

def main_window():
    in_column1 = [
        [sg.Button('High Quality', size=(17, 4), key='-HQ-', border_width=0)],
        [sg.Button('Low Quality', size=(17, 4), key='-LQ', border_width=0)],
        [sg.Button('Audio MP3', size=(17, 4), key='-MP3-', border_width=0)]
    ]
    in_column2 = [
        [sg.Canvas(size=(230, 230), background_color='Grey')]
    ]

    layout = [
        [sg.Canvas(size=(400, 100), background_color='Grey')],
        [sg.Input(size=(50, 1), key='-link-', border_width=0), sg.Button(button_text='Colar', key='-paste-', border_width=0)],
        [sg.Column(layout=in_column1), sg.Column(layout=in_column2)],
        [sg.Text('Developed by Ezequiel Almeida', size=(50, 1), justification='center')]
    ]

    return sg.Window(title='Wish Youtube Downloader', layout = layout, finalize=True)

sg.theme('Black')
link = 'https://www.youtube.com/watch?v=_rRkDvCkkLE'
video = YouTube(link)
window = main_window()
while True:
    event, values = window.Read()
    if event == sg.WIN_CLOSED:
        break
    if event == '-paste-':
        window['-link-'].update(sg.clipboard_get())
        link = values['-link-']
