import re
from bs4 import BeautifulSoup
import requests
import threading
import os
import json

def make_dir(dir: str):
    if os.path.exists(dir):
        pass
    else:
        os.mkdir(dir)

def get_info(url: str):
    """To get the infomation of every song included in the song list.

    Args:
        url (str): the url of the web page of the song list in 酷狗

    Returns:
        list: In this list every song included in the song list is contained as a dictionary consisting of three keys, title, lrc, and url.
    """
    print('Opening the web page')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')

    # the regex
    hash_regex = re.compile('"hash":"([0-9A-Za-z]*)",')
    album_id_regex = re.compile('"album_id":([0-9]*),')
    song_link_regex = re.compile('https://www.kugou.com/mixsong/[0-9A-Za-z]*.html')
    data_regex = re.compile(r'jQuery.*?[({].*?"data":(.*?)}[)]', re.S)

    # the links of every song in the song list
    links = soup.find_all('a', {'class': '', 'id': '', 'href': song_link_regex})

    # get the information including name, lrc, and url of the song
    songs_info = []
    songs_lrc = []

    print('Getting the info and lrc')

    for link in links:
        text = requests.get(link['href'], headers=headers).text
        song_soup = BeautifulSoup(text, 'html.parser')
        script = str(song_soup.script.string)

        try:
            song_hash = hash_regex.search(script).group(1)
            album_id = album_id_regex.search(script).group(1)

            data_url = f"https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery191053318263960215_1626866592344&hash={song_hash}&dfid=1tXkst0i97Rq4RW0pz15GjrP&mid=3196606d7d3ff0207a473da58e0b44b3&platid=4&album_id={album_id}&_=1626866592346"
            resp = requests.get(data_url, headers=headers).text
            data_text = data_regex.findall(resp)[0]
            data = json.loads(data_text)

            title = data['song_name']
            lrc = data['lyrics']
            song_url = data['play_url']

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

        except AttributeError:
            continue

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


def save_all(songs: list, file: str='./songs/songs.json'):
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


def download(songs: list, output: str = './songs/'):
    """利用you-get下载音乐

    Args:
        songs (list): the list containing the songs
        output (str, optional): the directory containing the output. Defaults to './'.
    """

    make_dir(output)
    for song in songs:
        title = song['title']
        url = song['url']
        path = os.path.join(output, f'{title}.mp3')
        content = requests.get(url).content
        with open(path, 'wb') as f:
            f.write(content)


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


def encode_lrc_all(music_dir: str, from_enc: str = 'utf-8', to_enc: str = 'gbk'):
    files = []
    for root, dirs, file_names in os.walk(music_dir):
        for file_name in file_names:
            if os.path.splitext(file_name)[-1] == '.lrc':
                file = {'name': file_name}
                file['path'] = os.path.join(root, file_name)

                files.append(file)
            else:
                pass

    for file in files:
        dir = os.path.split(file['path'])[0]
        dir = os.path.split(dir)[1]
        file['dir'] = dir

    for file in files:
        dir = os.path.join(music_dir, file['dir'])
        file_path = os.path.join(dir, file['name'])

        with open(file['path'], 'r', encoding=from_enc, errors='ignore') as f:
            text = f.read()

        with open(file_path, 'w', encoding=to_enc, errors='ignore') as f:
            f.write(text)


def encode_lrc(output_dir: str, from_enc: str = 'utf-8', to_enc: str = 'gbk'):
    for file in os.listdir(output_dir):
        if os.path.splitext(file)[-1] == '.lrc':
            path = os.path.join(output_dir, file)
            with open(path, 'r', encoding=from_enc, errors='ignore') as f:
                text = f.read()

            with open(path, 'w', encoding=to_enc, errors='ignore') as f:
                f.write(text)


def run_all(url: str='', by_step: int=0, save_info: bool=True , info_from_file: bool=False, info_file: str='./songs/songs.json', number: int = 5, output_file: str = './songs/songs.json', output_dir: str = './songs/', if_encode_lrc: bool=False):
    """To download in one key.

    Args:
        url (str, optional): The url of the song list in Kugou Music.
        
        save_info (bool optional): If True, the data produced by the function get_info() will be stored as a json file.
        
        info_from_file (bool, optional): If True, the data will come from the json file produced by function save_all(). Note: If it's True, the info_file is required.
        
        number (int, optional): The number of processes. Defaults to 5.
        
        output_file (str, optional): If the parameter save_info is True, this will be json file containing the infomation of songs. Defaults to './songs.json'.

        output_dir (str, optional): The directory containing the output. Defaults to './songs/'.
    """

    if url:
        print('Geting the information---------')
        songs = get_info(url)
        print('Done!\n\n')
        make_dir(output_dir)

        if save_info:
            print('Saving the information-----------')
            save_all(songs, output_file)
            print('Done!')

    elif info_from_file:
        with open(info_file, 'r', encoding='utf-8') as file:
            songs = json.loads(file.read())
    
    print('Saving the lrc---------------------')
    save_lrc(songs['lrc'], output_dir)
    print('Done')

    if if_encode_lrc:
        print('Encoding the lrc files------------')
        encode_lrc(output_dir)
        print('Done!')

    print('Downloading---------------------')
    if by_step:
        ids = range(by_step + 1)
        song_lists = []

        count = int(len(songs['info']) / by_step)
        for n in ids:
            if n == by_step:
                index = n * count
                songs_downloaded = songs['info'][index:]
            else:
                index = [n * count, (n + 1) * count]
                songs_downloaded = songs['info'][index[0]:index[1]]
            song_lists.append(songs_downloaded)

        for n in range(by_step + 1):
            multiprocessing_download(song_lists[n], output=output_dir)
    else:
        multiprocessing_download(songs['info'], number, output_dir)
    print('Done!')

if __name__ == '__main__':
    run_all('https://www.kugou.com/yy/special/single/5244430.html')
