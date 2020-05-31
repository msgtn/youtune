#-*-coding:utf-8-*-
import os
os.path.expanduser('~')
import sys
import time
import youtube_dl
import eyed3
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

pref_format = 'mp3'
pref_format = 'wav'

# downloader
ydl_op = {
    'format': '140',
    'extractaudio': True,
    'audioformat': pref_format,
    'outtmpl': '',
    'noplaylist': True,
    'verbose': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',

        'preferredcodec': pref_format,
        'preferredquality': '192',
    }],
    'verbose': False
}
ydl = youtube_dl.YoutubeDL(ydl_op)

opt = Options()
# run headless with fake window size to support scrolling
opt.add_argument('--headless')
opt.add_argument('window-size=1920,1080')

# page class
# stores videos
class Page(object):
    def __init__(self, url, files):
        self.url = url
        self.br = wd.Chrome(
            # executable_path='./chromedriver',
            executable_path=ChromeDriverManager().install(),
            chrome_options=opt)
        self.br.get(self.url)
        self.title = self.br.title.split('-')[0].rstrip().lstrip()
        self.files = files

    def __get_videos__(self,save_dir):
        # get list of videos found
        videos = []
        self.scroll()
        # vid_list = ydl.extract_info(self.url, False)['entries']
        vid_urls = [vid.get_attribute('href') for vid in self.br.find_elements_by_xpath('//*[@id="thumbnail"]')]
        # get rid of Nones - try to clean this up
        vid_urls = [url for url in vid_urls if url is not None]
        vid_titles = [vid.get_attribute('innerHTML') for vid in self.br.find_elements_by_id('video-title')]
        # if vid_urls is too long, trim leading
        vid_urls = vid_urls[-len(vid_titles):]

        for url,title in zip(vid_urls, vid_titles):
            title = title.strip().replace('/','|')
            videos.append(Video(url, '',title,save_dir))

        # reverse so try to download new videos first
        videos = videos[::-1]
        self.videos = videos

        return videos

    def scroll(self, scroll_wait=3.0):
        def get_height():
            return self.br.execute_script('return document.body.scrollHeight;')
            # return self.br.execute_script('return document.body.scrollHeight;')
        last_height = get_height()

        while True:
            # scroll
            for _ in range(3):
                self.br.execute_script("window.scrollTo(0, document.querySelector('#items').scrollHeight)")
                time.sleep(1)
            # wait
            print("Scrolling...")
            time.sleep(scroll_wait)
            # stop scrolling if height didn't change
            new_height = get_height()
            if new_height == last_height:
                break
            last_height = new_height
            print("Finished scrolling")

# artist page
class ArtistPage(Page):
    def __init__(self, url, files):
        super(ArtistPage, self).__init__(url, files)
        self.artist = self.title

    def get_videos(self,save_dir):
        videos = super(ArtistPage, self).__get_videos__(save_dir)
        for video in videos:
            video.artist = self.artist

            # artist name might be in title
            # if '-' in video.title:
            #     video.artist = video.title.split('-')[0].lstrip().rstrip()
            #     print(video.artist)
            #     video.title = ''.join(video.title.split('-')[1:]).lstrip().rstrip()
            
            video.download()

# playlist page
class PlaylistPage(Page):
    def __init__(self, url, files):
        super(PlaylistPage, self).__init__(url, files)

    def get_videos(self, save_dir, auto_add=False, skip_if_exists=True):
        videos = super(PlaylistPage, self).__get_videos__(save_dir)
        for video in videos:
            try:
                if '-' in video.title:
                    vid_split = video.title.split('-')
                    # assume that the artist is what comes before '-'
                    video.artist = vid_split[0].rstrip()
                    # title is the remaining stuff
                    video.title = '-'.join(vid_split[1:]).lstrip().rstrip()
                print(video.title)
                fn_match = [video.title in file for file in self.files]
                if skip_if_exists and sum(fn_match):
                    print("Already downloaded %s"%(video.title))
                    continue
                video.download(save_dir, auto_add)
            except:
                print("Error downloading {}".format(video.title))
                continue

        return [v.title for v in videos]


# video class
class Video(object):
    def __init__(self, url, artist, title, save_dir):
        self.url = url
        self.artist = artist
        self.title = title
        self.save_dir = save_dir
        self.filename = "%s/%s"%(self.save_dir,self.title)

    def download(self, save_dir, auto_add):
        """
        Download
        """
        # check if filename exists and skip if it does
        # fn_match = [self.title.encode('utf-8') in file for file in files]
        

        # download
        # ydl_op['outtmpl'] = unicode(self.filename+'.m4a')
        ydl_op['outtmpl'] = self.filename+'.m4a'
        with youtube_dl.YoutubeDL(ydl_op) as ydl:
            ydl.download([self.url])

        # set ID3 tags and move to autoadd folder
        self.set_id3()
        if auto_add is not None:
            self.move_to_auto()

    def set_id3(self):
        """
        Set ID3 tags
        """
        # os.listdir('~/')
        # os.listdir(self.filename[:self.filename.rfind('/')])
        # af = eyed3.load(self.filename+'.mp3')
        af = eyed3.load(self.filename+'.'+pref_format)
        # af.tag.artist = unicode(self.artist)
        # af.tag.title = unicode(self.title)
        # af.tag.album = unicode('YouTube')
        af.tag.artist = self.artist
        af.tag.title = self.title
        af.tag.album = 'YouTube'
        # af.tag.album = 'End of Evangelion'
        af.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION,encoding='utf-8')

    def move_to_auto(self):
        temp_f = self.save_dir+'/temp'
        auto_f = self.save_dir+'/Automatically Add to iTunes.localized'
        for f in os.listdir(temp_f):
            print(f)
            os.rename(
                "%s/%s"%(temp_f,f),
                "%s/%s"%(auto_f,f)
                )
        # print("%s/%s.mp3"%(self.folder,self.title))
        # print("%s/%s.mp3"%(itunes_folder+auto_add,self.title))
        # os.rename(
        #     "%s/%s.mp3"%(self.folder,self.title),
        #     "%s/%s.mp3"%(itunes_folder+auto_add,self.title),
        #     )
