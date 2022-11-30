import re
from bs4 import BeautifulSoup as bs
import requests
import os
import json

class Base():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    }

    def __init__(self):
        pass

    def make_dir(self, dir: str):
        if os.path.exists(dir):
            pass
        else:
            print(f'Making the directory {dir}')
            os.mkdir(dir)

    def get_text(self, url: str):
        url = self.url
        text = requests.get(url, headers=self.headers).text

        return text


class Playlist(Base):
    def __init__(self, url: str):
        self.url = url
        text = self.get_text(url)
        links = self.get_info(text)
        self.songs = self.get_songs(links)

    def get_info(self, text: str):
        print('Getting the information of the playlist.')

        soup = bs(text, 'html.parser')
        song_link_regex = re.compile('https://www.kugou.com/mixsong/[0-9A-Za-z]*\.html')
        links = soup.find_all('a', {'href': self.song_link_regex})

        self.name = soup.find_all('p', {'class': 'detail'})[0].contents[2]
        self.intro = str(soup.find_all('div', {'class': 'intro'})[0].contents[0].contents[1])
        self.pic = soup.find('div', {'class': 'pic'}).img['_src']

        return links

    def get_songs(self, links):
        print('Getting the songs.')
        songs = []
        for link in links:
            song = Song(link['href'])
            songs.append(song)
        return songs

    def save_data(self, dir='./'):
        print('Saving the data into a json file.')
        data = {
            'name': self.name,
            'intro': self.intro,
            'pic': self.pic,
        }
        songs_info = []
        for song in self.songs:
            song_info = {
                'name': song.name,
                'lrc': song.lrc,
                'url': song.url,
                'audio': song.audio_url,
            }
            songs_info.append(song_info)
        data['songs'] = songs_info

        text = json.dumps(data, indent=4, ensure_ascii=False)
        file = os.path.join(dir, f'{self.name}.json')

        with open(file, 'w', encoding='utf-8') as f:
            f.write(text)

    def create_lrc(self, dir='./', encoding='utf-8'):
        self.make_dir(dir)
        songs = self.songs
        print('Saving lyrics files.')
        for song in songs:
            song.save_lrc(dir, encoding)

    def download_songs(self, dir='./'):
        songs = self.songs
        for song in songs:
            song.download(dir)

    def download_image(self, dir='./'):
        pic = self.pic
        suf = os.path.splitext(pic)[-1]
        file = os.path.join(dir, self.name + suf)
        content = requests.get(pic, headers=self.headers).content
        with open(file, 'wb') as f:
            f.write(content)


class Song(Base):
    # the regex
    hash_regex = re.compile('"hash":"([0-9A-Za-z]*)",')
    album_id_regex = re.compile('"album_id":([0-9]*),')
    song_link_regex = re.compile('https://www.kugou.com/mixsong/[0-9A-Za-z]*.html')
    data_regex = re.compile(r'jQuery.*?[({].*?"data":(.*?)}[)]', re.S)

    def __init__(self, url):
        self.url = url
        text = self.get_text(url)
        self.get_info(text)

    def get_info(self, text):
        song_soup = bs(text, 'html.parser')
        script = str(song_soup.script.string)
        hash = self.hash_regex.search(script).group(1)
        album_id = self.album_id_regex.search(script).group(1)

        data_url = f"https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery191053318263960215_1626866592344&hash={hash}&dfid=1tXkst0i97Rq4RW0pz15GjrP&mid=3196606d7d3ff0207a473da58e0b44b3&platid=4&album_id={album_id}&_=1626866592346"
        resp = requests.get(data_url, headers=self.headers).text
        data_text = self.data_regex.findall(resp)[0]
        data = json.loads(data_text)

        self.name = data['song_name']
        self.lrc = data['lyrics']
        self.audio_url = data['play_url']

    def save_lrc(self, dir = './', encoding ='utf-8'):
        self.make_dir(dir)
        title = self.name
        lrc = self.lrc
        path = os.path.join(dir, f'{title}.lrc')

        with open(path, 'w', encoding=encoding) as file:
            file.write(lrc)

    def download(self, dir = './'):
        self.make_dir(dir)
        title = self.name
        url = self.audio_url
        path = os.path.join(dir, f'{title}.mp3')

        print(f'Downloading {title}')

        try:
            content = requests.get(url, headers=self.headers).content
        except:
            content = bytes()

        with open(path, 'wb') as f:
            f.write(content)


# 可以自行更改这两个函数
def run_playlist(url):
    "下载歌单"

    pl = Playlist(url)
    # 输出目录，默认为 当前目录/歌单名称
    dir = os.path.join('.', pl.name)

    # 下载全部歌曲
    pl.download_songs(dir)
    # 创建lrc文件
    pl.create_lrc(dir)
    # 保存歌单信息
    pl.save_data(dir)
    # 下载歌单封面
    pl.download_image(dir)


def run_song(url):
    """
    下载单曲
    """
    regex = re.compile('https://www.kugou.com/mixsong/[a-zA-Z0-9]*?\.html')
    url = regex.match(url).group()
    # 输出目录
    dir = './'

    song = Song(url)
    # 下载歌曲
    song.download(dir)
    # 创建lrc文件
    song.save_lrc(dir, encoding='utf-8')


if __name__ == '__main__':
    print('如果想要下载单首歌请输入song。\n想要下载歌单请输入playlist\n退出请输入q\n想要定制功能自己下代码。\n')
    mode = False
    while True:
        if mode:
            url = input('输入歌曲链接：')
        else:
            url = input('输入歌单链接：')

        if url == 'song':
            mode = True
        elif url == 'playlist':
            mode = False
        elif url == 'q':
            break
        else:
            if mode:
                run_song(url)
            else:
                run_playlist(url)
