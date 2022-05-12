import PySimpleGUI as sg
from pytube import YouTube
from pytube import exceptions
import moviepy.editor as mp
import time, os


class Video:
    def __init__(self, url):
        self.yt = YouTube(url)
    
    def download(self, quality, path):
        '''Download the video in High Quality, Low Quality or MP3'''
        if quality == '-MP3-':
            '''The button pressed is Audio MP3, so download as audio .mp4 and convert to .mp3'''
            audio = self.yt.streams.get_audio_only()
            title = str(audio.title)
            audio.download(path, filename=f'{title}.mp4') # Download in the specified folder (path)
            mp3 = mp.AudioFileClip(f'{path}/{title}.mp4') # Set the .mp4 audio
            time.sleep(0.5)
            mp3.write_audiofile(f'{path}/{title}.mp3') # Create a .mp3
            os.remove(f'{path}/{title}.mp4') # Delete the .mp4
        elif quality == '-HQ-':
            '''Select the highest resolution and download them'''
            video = self.yt.streams.get_highest_resolution()
            video.download(path)
        elif quality == '-LQ-':
            '''Select the lowest resolution and download them'''
            video = self.yt.streams.get_lowest_resolution()
            video.download(path)


def main_window():
    '''Configure the layout and return window object'''
    # Download Buttons layout
    in_column1 = [
        [sg.Button('High Quality', size=(17, 4), key='-HQ-', border_width=0)],
        [sg.Button('Low Quality', size=(17, 4), key='-LQ-', border_width=0)],
        [sg.Button('Audio MP3', size=(17, 4), key='-MP3-', border_width=0)]
    ]
    # Space to show the thumbnail (not yet implemented)
    in_column2 = [
        [sg.Canvas(size=(230, 230), background_color='Grey')]
    ]
    # Layout for the Frame (Select the destination folder)
    select_folder = [
        [
            sg.Text(size=(40, 1), key='-folder-', border_width=0), 
            sg.Button(button_text='Browse', key='-select-', border_width=0)
        ]
    ]
    # Main layout
    layout = [
        [sg.Canvas(size=(400, 100), background_color='Grey')],
        [sg.Input(size=(49, 1), key='-url-', border_width=0), sg.Button(button_text='Paste', key='-paste-', border_width=0)],
        [sg.Column(layout=in_column1), sg.Column(layout=in_column2)],
        [sg.Frame(title='Destination folder', title_location='n', layout=select_folder)],
        [sg.Text('Developed by Ezequiel Almeida', size=(50, 1), justification='center', text_color='grey')]
    ]
    # Return the window as Object
    return sg.Window(title='Wish Youtube Downloader', layout = layout, finalize=True)


sg.theme('Black') # Set theme
window = main_window() # Set Window instance
path = rf'C:\Users\{os.getlogin()}\Downloads'
# Mainloop
while True:
    window['-folder-'].update(path) # Show the current Destination Folder on the Label
    event, values = window.Read()
    if event == sg.WIN_CLOSED: # If the user closes the window
        break
    elif event == '-select-': # If the user click on the Browse button
        path = sg.PopupGetFolder(no_window=True, message='')
    elif event == '-paste-': # If the user click on the Paste button
        url = sg.clipboard_get() # Paste the current clipboard data on the Input
        window['-url-'].update(url)
        # *Thumb change here*
    else:
        '''If the user click in an Download button'''
        try:
            video = Video(values['-url-'])
            video.download(event, path) # Download the video in the quality of the clicked button and in the place selected
        except exceptions.RegexMatchError: # Raise RegexMatchError if the url is a invalid youtube url so...
            sg.popup('Invalid URL!')
            window['-url-'].update('') # Clear the Url Field
