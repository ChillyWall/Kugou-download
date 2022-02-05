import re
from bs4 import BeautifulSoup
import urllib.request
import threading
import os
import json


def get_info(url: str):
    """To get the infomation of every song included in the song list.

    Args:
        url (str): the url of the web page of the song list in 酷狗

    Returns:
        list: In this list every song included in the song list is contained as a dictionary consisting of three keys, title, lrc, and url.
    """
    print('Opening the web page')
    soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')

    # the regex
    hash_regex = re.compile('"hash":"([0-9A-Za-z]*)",')
    album_id_regex = re.compile('"album_id":([0-9]*),')
    mixsong_id_regex = re.compile('"mixsongid":([0-9]*)')
    song_link_regex = re.compile(
        'https://www.kugou.com/mixsong/[0-9A-Za-z]*.html')
    baned_char = re.compile(r'[\?\$\*\/\\"\';,\|:]')

    # the links of every song in the song list
    links = soup.find_all('a', {'class': '', 'id': '', 'href': song_link_regex})

    # get the information including name, lrc, and url of the song
    songs_info = []
    songs_lrc = []
    print('Geting the info and lrc')
    for link in links:
        song_soup = BeautifulSoup(urllib.request.urlopen(link['href']), 'html.parser')
        script = str(song_soup.script.string)
        try:
            song_hash = hash_regex.search(script).group(1)
            album_id = album_id_regex.search(script).group(1)
            mixsong_id = mixsong_id_regex.search(script).group(1)
        except AttributeError:
            pass

        song_url = '{0}#hash={1}&album_id={2}&album_audio_id={3}'.format(
            link['href'], song_hash, album_id, mixsong_id)
        lrc = song_soup.find('div', attrs={'class': 'displayNone'}).string
        title = re.sub(baned_char, '_', link['title'])

        song_info = {
            'title': title,
            'url': song_url
        }

        song_lrc = {
            'title': title,
            'lrc': lrc
        }

        songs_info.append(song_info)
        songs_lrc.append(song_lrc)

    songs = {
        'info': songs_info,
        'lrc': songs_lrc
    }

    return songs


def save_lrc(songs: list, output_dir: str='./lrc/'):
    """To make the lrc files.

    Args:
        songs (list): The list of dictionaries containing of two key-value pairs including 'title' and 'lrc' with strings as the value.

        output_dir (str, optional): The directory containing the lrc files. Defaults to './lrc/'.
    """
    make_dir(output_dir)
    for song in songs:
        with open(output_dir + r'/{0}.lrc'.format(song['title']), mode='w', encoding='utf-8') as file:
            file.write(song['lrc'])


def save_all(songs: list, file: str='./songs.json'):
    text = json.dumps(songs, indent=4)
    with open(file, 'w', encoding='utf-8') as file:
        file.write(text)


def read_info(file: str):
    """Read the information saved by save_info().

    Args:
        file (str): The file produced by save_info()

    Returns:
        [list]: the list of the dictionaries consisting of the information of songs.
    """
    with open(file, 'r', encoding='utf-8') as file:
        text = file.read()
    songs = json.loads(text)

    return songs


def download(songs: list, output: str = './'):
    """利用you-get下载音乐

    Args:
        songs (list): the list containing the songs
        output (str, optional): the directory containing the output. Defaults to './'.
    """
    make_dir(output)
    for song in songs:
        title = song['title']
        url = song['url']
        os.system('you-get -o {0} -O "{1}" "{2}"'.format(output, title, url))


def multiprocessing_download(songs: list, number: int = 5, output: str = './'):
    """多线程下载

    Args:
        songs (list): 
        number (int, optional): 线程数量. Defaults to 5.
    """

    ids = range(number + 1)
    processes = []

    count = int(len(songs) / number)
    for n in ids:
        if n == number:
            index = n * count
            songs_downloaded = songs[index: ]
        else:
            index = [n * count, (n + 1) * count]
            songs_downloaded = songs[index[0]:index[1]]

        new_process = threading.Thread(
            target=download, args=(songs_downloaded, output))
        processes.append(new_process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()


def make_dir(dir: str):
    if os.path.exists(dir):
        pass
    else:
        os.mkdir(dir)


def run_all(url: str='', save_info: bool=True , info_from_file: bool=False, info_file: str='./songs.json', number: int = 5, output_file: str = './songs.json', output_dir: str = './'):
    """To download in one key.

    Args:
        url (str, optional): The url of the song list in Kugou Music.
        
        save_info (bool optional): If True, the data produced by the function get_info() will be stored as a json file.
        
        info_from_file (bool, optional): If True, the data will come from the json file produced by function save_all(). Note: If it's True, the info_file is required.
        
        number (int, optional): The number of processes. Defaults to 5.
        
        output_file (str, optional): If the parameter save_info is True, this will be json file containing the infomation of songs. Defaults to './songs.json'.

        output_dir (str, optional): The directory containing the output. Defaults to './'.
    """
    if url:
        print('geting the information---------')
        songs = get_info(url)
        print('done!\n\n')

        if save_info:
            print('saving the information-----------')
            save_all(songs, output_file)
            print('done!')

    elif info_from_file:
        with open(info_file, 'r', encoding='utf-8') as file:
            songs = json.loads(file.read())

    print('saving the lrc---------------------')
    save_lrc(songs['lrc'], output_dir)
    print('done')

    print('downloading---------------------')
    multiprocessing_download(songs['info'], number, output_dir)
    print('done!')
