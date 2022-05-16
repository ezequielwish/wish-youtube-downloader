import PySimpleGUI as sg
from pytube import YouTube, exceptions
from threading import Thread
import requests, os
from PIL import Image

class Video:
    def __init__(self, url):
        self.url = url
        self.yt = YouTube(url)

    @staticmethod
    def format_title(title, no_spaces=False):
        '''Turns the video title valid to Windows OS filenames'''
        new = []
        for char in title: # Separate only valid characters and put on the list
            if char == ' ':
                if no_spaces:
                    new.append('_')
                else:
                    new.append(char)
            elif char == '|':
                new.append('-')
            elif char.lower() in (r'aáàãâbcdeéèêfghiíìjklmnopqrstuvwxyz0987654321([{}])/$&~-".,:;?'):
                new.append(char)
        new = ''.join(new) # Convert list on a string
        if len(new) <= 50: # 50 charactere is a good lenght to filenames
            return new
        else:
            return new[:51]+'...' # Return only the first 50 characteres to bypass Filename Lenght eror

    def download(self, quality, path):
        '''Download the video in High Quality, Low Quality or MP3'''
        global window
        # Change the buttons to DISABLED buttons
        try:
            window['-HQ-'].hide_row()
            window['-LQ-'].hide_row()
            window['-MP3-'].hide_row()
            window['-disHQ-'].unhide_row()
            window['-disLQ-'].unhide_row()
            window['-disMP3-'].unhide_row()
            filename = self.yt.title[:]
            window['-status-'].update('Downloading...', text_color='Grey')
            if quality == '-MP3-':
                '''The button pressed is Audio MP3, so download as audio .mp4 and convert to .mp3'''
                filename = self.format_title(filename, no_spaces=True)
                video = self.yt.streams.get_audio_only()
                video.download(path, filename=f'{filename}.mp4') # Download in the specified folder (path)
                window['-status-'].update('Converting to mp3...', text_color='Yellow')
                mp4 = f'{path}\{filename}.mp4' # Set the .mp4 audio path
                mp3 = f'{path}\{filename}.mp3' # Set the .mp3 audio path
                os.system(f'ffmpeg -i {mp4} -vn {mp3} -y') # Convert with ffmpeg
                os.remove(f'{path}/{filename}.mp4') # Delete the .mp4
                window['-status-'].update('Download sucessful! [MP3]', text_color='Green')
            elif quality == '-HQ-':
                '''Select the highest resolution and download them'''
                filename = self.format_title(filename)
                video = self.yt.streams.get_highest_resolution()
                video.download(path, filename=f'{filename} [HQ].mp4')
                window['-status-'].update('Download sucessful! [HQ]', text_color='Green')
            elif quality == '-LQ-':
                '''Select the lowest resolution and download them'''
                filename = self.format_title(filename)
                video = self.yt.streams.get_lowest_resolution()
                video.download(path, filename=f'{filename} [LQ].mp4')
                window['-status-'].update('Download sucessful! [HQ]', text_color='Green')
        except PermissionError:
            window['-status-'].update('Error! That folder needs ADMIN PERMISSION!', text_color='Red')
        finally:
            # Change the buttons to ENABLED buttons again
            window['-disHQ-'].hide_row()
            window['-disLQ-'].hide_row()
            window['-disMP3-'].hide_row()
            window['-HQ-'].unhide_row()
            window['-LQ-'].unhide_row()
            window['-MP3-'].unhide_row()


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
        [sg.Image(source='images/thumb.png', key='-thumb-', size=(350, 230), pad=0)]
    ]
    # Layout for the Frame (Select the destination folder)
    select_folder = [
        [
            sg.Text(size=(50, 1), key='-folder-', border_width=0), 
            sg.Button(button_text='Browse', key='-path-', border_width=0)
        ]
    ]
    # Main layout
    layout = [
        [sg.Image('images/logo.png', size=(480, 100), pad=0)],
        [
            sg.Input(size=(61, 1), key='-url-', border_width=0), 
            sg.Button(button_text='Done!', key='-paste-', border_width=0, bind_return_key=True)
        ],
        [sg.Text(key='-title-', size=(59, 1), justification='center')],
        [sg.Column(layout=in_column1, pad=0), sg.Column(layout=in_column2, pad=0)],
        [sg.Text(key='-status-', size=(54, 1), justification='center', font='Consolas')],
        [sg.Frame(title='Destination folder', title_location='n', layout=select_folder)],
        [sg.Text('Developed by Ezequiel Almeida', size=(60, 1), justification='center', text_color='grey')]
    ]
    # Return the window as Object
    return sg.Window(title='Wish Youtube Downloader', layout = layout, finalize=True)


def set_thumbnail_and_title(video):
    '''Show thumbnail image and title on the interface'''
    video_url = video.url
    if len(video.yt.title) > 67:
        video_title = video.yt.title[:66] + '...'
    else:
        video_title = video.yt.title
    download_thumbnail(video_url)
    window['-thumb-'].update(source='images/temp.png', size=(350, 230))
    window['-title-'].update(video_title)
    os.remove('images/temp.png')


def download_thumbnail(url):
    '''Download and prepare the thumbnail image to show on the interface'''
    img_data = requests.get(YouTube(url).thumbnail_url).content
    with open('images/temp.png', 'wb') as handler:
        handler.write(img_data)
    compress_image('images/temp.png')


def compress_image(path):
    '''Compress and resize a image to appear in the interface'''
    image = Image.open(path)
    image.resize(size=(350, 230))
    image.save(path, optimize=True, quality=50)


def set_video(url):
    '''Set video throught a valid url'''
    global window
    window['-status-'].update('')
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
    elif event == '-path-': # If the user click on the Browse button
        new_path = sg.PopupGetFolder(no_window=True, message='')
        if new_path != '':
            path = new_path
    elif event == '-paste-': # If the user click on the Paste button
        if values['-url-'] == '':
            url = sg.clipboard_get()
            window['-url-'].update(url) # Paste the current clipboard data on the Input
            video = set_video(url)
        else: 
            video = set_video(values['-url-']) # Try to set the video with the current url on the -url- field
    else:
        '''If the user click in a Download button'''
        video = set_video(values['-url-'])
        # Download the video in the quality of the clicked button and in the place selected
        start_download = Thread(target=video.download, args=(event, path)).start()
