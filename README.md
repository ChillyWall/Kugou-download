# 酷狗歌单下载

这个程序可以根据酷狗歌单的网页链接获取歌单中所有的歌曲的链接并使用**you-get**下载.

使用前需要有python3环境, 并且安装有you-get库, 下载方法请自行搜索.

`kugou.py`文件中是所有需要的函数, 使用时需自己另建立新的`.py`文件后或是在python console调用函数进行下载.

下载方法有两个, 分别是单独调用函数一步一步下载和使用`run_all()`函数一键下载.

## 分步下载

一般步骤是

1. 先用`get_info()`函数获取歌单中所有歌曲的信息, 包括名称、链接和歌词. 此函数有返回值, 返回值为一个字典, 键`'info'`值及后面`download()`和`multiprocessing_download()`函数中参数`songs`所需要的数据, 而键`'lrc'`则是`save_lrc()`函数中songs参数所需要的数据.
2. `save_lrc()`此函数用于制作歌词文件.
3. `download()`下载歌曲. 或者使用`multiprocessing_download()`函数进行多线程下载. 

(注意, 线程太多可能会造成占用大量内存甚至有程序崩溃的风险.)

如

```python
import kugou
url = "https://www.kugou.com/yy/special/single/4583068.html"
output_dir = './songs/'

songs = kugou.get_links(url)
kugou.save_lrc(songs=songs['lrc'], output=output_dir)
kugou.multiprocessing_download(songs=songs['info'], number=5, output=output)
```

## 一键下载

`run_all()`函数可以省去一步一步调用的过程, 只需要一个函数填入数据即可自动运行. 

可以用最简方法

```python
import kugou
url = "https://www.kugou.com/yy/special/single/4583068.html"
kugou.run_all(url)
```

也可以自己设置. 

该函数分为两种模式, 一种是直接从网站读取信息然后直接下载, 第二种则是从本地文件中读取数据并下载.

运行此函数推荐在传入数据时加上参数名称, 防止错误传输.

#### 从网站

`run_all()`有很多参数, 这个模式的参数有`url`, `save_info`, `output_dir`, `output_file`, `number`. 其中除了`url`参数是必须的之外, 其它都有默认值, 可以省略. 但是如果多次下载, 输出的`output_file`可能会出现之后的数据覆盖之前的数据, 所以需谨慎使用默认值.

(注: `save_info`默认为True, 及默认将歌曲信息写入到json数据文件中.)

例子:

```python
import kugou
url = "https://www.kugou.com/yy/special/single/4583068.html"
number = 5
output_dir = './songs/'
output_file = './songs.json'

kugou.run_all(url, save_info=True, output_dir=output_dir,output_file=output_file, number=number)
```

#### 从文件

传入参数`info_from_file=True`选择此模式. 这个模式下除了`output_file`和`number`参数不变之外, `url`参数必须是空值, 可以使用`''`代替也可以在每次传入参数时加上参数名; `save_info`, `output_file`两个参数无用; 传入`info_file`参数指定要读取的文件名.

```python
import kugou
url = "https://www.kugou.com/yy/special/single/4583068.html"
number = 5
output_dir = './songs/'
info_file = './songs.json'

kugou.run_all(info_from_file=True, info_file=info_file, number=number, output_dir=output_dir)
```

## 其他功能：

### 保存数据

`save_all()`函数可以将`get_info()`的返回值储存在json文件中, 使用`read_info()`读取之后与`get_info()`的返回值使用方法相同.

```python
info_file = './songs.json'
songs = kugou.get_info(url)
kugou.save_all(songs, info_files)

```

```python
songs = kugou.read_info(info_files)
```
