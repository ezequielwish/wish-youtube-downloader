

class Video:
    def __init__(self, link):
        self.yt = YouTube(link)
        self.thumb = self.yt.thumbnail_url

    
