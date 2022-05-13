import PySimpleGUI as sg
from pytube import YouTube
from pytube import exceptions
import moviepy.editor as mp
import time, os
from threading import Thread
import requests
from PIL import Image

class Video:
    def __init__(self, url):
        self.url = url
        self.yt = YouTube(url)
    
    def download(self, quality, path):
        '''Download the video in High Quality, Low Quality or MP3'''
        global window
        # Change the buttons to DISABLED buttons
        window['-HQ-'].hide_row()
        window['-LQ-'].hide_row()
        window['-MP3-'].hide_row()
        window['-disHQ-'].unhide_row()
        window['-disLQ-'].unhide_row()
        window['-disMP3-'].unhide_row()
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
            title = str(video.title)
            video.download(path, filename=f'{title} [HQ].mp4')
        elif quality == '-LQ-':
            '''Select the lowest resolution and download them'''
            video = self.yt.streams.get_lowest_resolution()
            title = str(video.title)
            video.download(path, filename=f'{title} [LQ].mp4')
        # Change the buttons to ENABLED buttons again
        window['-HQ-'].unhide_row()
        window['-LQ-'].unhide_row()
        window['-MP3-'].unhide_row()
        window['-disHQ-'].hide_row()
        window['-disLQ-'].hide_row()
        window['-disMP3-'].hide_row()
        print(f'Download Done!')


def main_window():
    '''Configure the layout and return window object'''
    # Download Buttons layout
    in_column1 = [
        [sg.Button('High Quality', size=(15, 4), key='-HQ-', border_width=0)],
        [sg.Button('Low Quality', size=(15, 4), key='-LQ-', border_width=0)],
        [sg.Button('Audio MP3', size=(15, 4), key='-MP3-', border_width=0)],
        [sg.Button('Downloading...', size=(15, 4), key='-disHQ-', border_width=0, disabled=True)],
        [sg.Button('Downloading...', size=(15, 4), key='-disLQ-', border_width=0, disabled=True)],
        [sg.Button('Downloading...', size=(15, 4), key='-disMP3-', border_width=0, disabled=True)],
    ]
    # Space to show the thumbnail
    in_column2 = [
        [sg.Image(source='thumb.png', key='-thumb-', size=(330, 230))]
    ]
    # Layout for the Frame (Select the destination folder)
    select_folder = [
        [
            sg.Text(size=(50, 1), key='-folder-', border_width=0), 
            sg.Button(button_text='Browse', key='-select-', border_width=0)
        ]
    ]
    # Main layout
    layout = [
        [sg.Image('logo.png', size=(480, 100))],
        [
            sg.Input(size=(61, 1), key='-url-', border_width=0), 
            sg.Button(button_text='Done!', key='-paste-', border_width=0, bind_return_key=True)
        ],
        [sg.Column(layout=in_column1), sg.Column(layout=in_column2)],
        [sg.Text(key='-title-', size=(59, 1), justification='center')],
        [sg.Frame(title='Destination folder', title_location='n', layout=select_folder)],
        [sg.Text('Developed by Ezequiel Almeida', size=(60, 1), justification='center', text_color='grey')]
    ]
    # Return the window as Object
    return sg.Window(title='Wish Youtube Downloader', layout = layout, finalize=True)


def set_thumbnail_and_title(video):
    '''Show thumbnail image and title on the interface'''
    video_url = video.url
    video_title = video.yt.title
    download_thumbnail(video_url)
    window['-thumb-'].update(source='temp.png', size=(330, 230))
    window['-title-'].update(video_title)


def download_thumbnail(url):
    '''Download and prepare the thumbnail image to show on the interface'''
    img_data = requests.get(YouTube(url).thumbnail_url).content
    with open('temp.png', 'wb') as handler:
        handler.write(img_data)
    compress_image('temp.png')


def compress_image(path):
    '''Compress and resize a image to appear in the interface'''
    image = Image.open(path)
    image.resize(size=(330, 230), reducing_gap=Image.ANTIALIAS)
    image.save(path, optimize=True, quality=95)


def set_video(url):
    '''Set video throught a valid url'''
    global window
    try:
        video = Video(url)
    except exceptions.RegexMatchError: # Raise RegexMatchError if the url is a invalid youtube url so...
        sg.popup('Invalid Url!')
        window['-url-'].update('') # Clear the Url Field
    else:
        set_thumbnail_and_title(video)
        return video


sg.theme('Black') # Set theme
window = main_window() # Set Window instance
# Hide the disabled buttons
window['-disHQ-'].hide_row()
window['-disLQ-'].hide_row()
window['-disMP3-'].hide_row()
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
        if values['-url-'] == '':
            url = sg.clipboard_get()
            window['-url-'].update(url) # Paste the current clipboard data on the Input
            video = set_video(url) # 
        else: 
            video = set_video(values['-url-']) # Try to set the video with the current url on the -url- field
    else:
        '''If the user click in a Download button'''
        video = set_video(values['-url-'])
        # Download the video in the quality of the clicked button and in the place selected
        start_download = Thread(target=video.download, args=(event, path)).start()
