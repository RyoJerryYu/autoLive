# autoLive

## 简介
读取时间表，解析后利用[APScheduler][APScheduler]定时启动转播任务。

一个转播任务中，利用[youtube-dl][youtube-dl]获得YouTube直播m3u8地址，并用[ffmpeg][ffmpeg]将对应直播转播到B站直播。运行于`Python3`。

## 测试环境
- CentOS 7
- youtube-dl 2018.10.05
- ffmpeg 4.0.2-static
- Python 3.6
- requests 2.19.1
- APScheduler 3.5.3

## 依赖与安装
#### 软件依赖
安装`youtube-dl`，`ffmpeg`，`python3`。如果系统中没有`wget`需要事先安装`wget`。
```bash
# 安装youtube-dl
wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl
# 安装ffmpeg
wget https://raw.githubusercontent.com/q3aql/ffmpeg-install/master/ffmpeg-install
chmod a+x ffmpeg-install
./ffmpeg-install --install release
# 安装python3
sudo yum install python3
```

#### Python库依赖
安装`requests`，`APScheduler`。需要先安装python3对应的pip。
```bash
# 安装requests
pip3 install requests
# 安装APScheduler
pip3 install APScheduler
```

## 运行
- 先使用`git clone`把代码clone到本地，并cd到对应`autoLive`目录中。需要先安装git。
- 把B站cookies串粘贴到`autoLive/cookies.txt`中。
此时可运行`python3 refresh_area_id.py`更新area_id.txt，同时测试cookies串是否能登陆。
```bash
python3 refresh_area_id.py
```
- 配置`config.ini`，主要根据自己情况更改直播间标题格式、分区及最高清晰度。其中`{time}``{liver}``{site}``{title}`均为时间表中的参数。
- 填写`schedule.txt`。目前只能解析未来24小时内的直播，而且每次重新运行都需要读取一次时间表。
```
# 时间表格式：
# time@liver@site@title
# time：直播时间，格式为HHMM，只接受未来24小时内的直播，检测出直播时间在运行程序之前时，会自动认为直播在运行程序第二天开始。
# liver：只接受liveInfo.json中存在的liver名。（可自行按json格式添加到liveInfo文件中）
# site：直播网站，可选。目前只接受YouTube。而且不填默认为YouTube。
# title：填入config.ini中直播间标题的title中，可选，不填默认为"{liver}"+"转播"

# 例：
# 1900@桜凛月@绝地求生
# 2100@黒井しば
# 2240@飛鳥ひな@YouTube
# 0640@伏見ガク@YouTube@おはガク！
```

其中liver只能接受`liveInfo.json`中存在的liver，可自行按照对应格式添加新直播主至`liveInfo.json`中。格式如下：

```json
[ //list，每一项dictionary对应一位liver
    {
        "liver": "樋口楓", //str，与时间表中liver项对应
        "room": [ //list，每一项dictionary对应一个直播间
            {
                "site": "YouTube", //str，直播网站名，注意大小写
                "url": "https://www.youtube.com/channel/UCsg-YqdqQ-KFF0LNk23BY4A/live" //str，对应直播间url
            },
            //其他网站的直播间
            //但是目前只能解析YouTube上的直播间，所以list的其他项没有意义
        ]
    },
    //相同格式的其他liver信息
]
```

- 运行`main.py`。建议在screen中启动。
```bash
python3 main.py
```

## 缺点与修改方案
- 需要手动填写时间表，手动传输时间表到服务器并手动启动程序。
- 程序不能一直运行，需要每天启动读取时间表。
- 灵活度不足。时间表一旦运行后不能增删改，无法应对突击直播等情况。

以上三点均可通过添加网页端，并在网页端上进行时间表的增删改来解决。

- 只能接受YouTube上的直播

已预留好接口，以后可进行其他网站直播的扩充。

- 直播前只能发文字动态，不能转发直播间

之所以会这样是因为暂时未能找到转发直播间的API。未来可能会扩充此功能。

- 同时只能通过一个B站账号进行转播

以后可能会增加多账号支持，但考虑到VPS的承受能力，不推荐同一服务器同时进行多项转播。

## TODO LIST
- [ ] 可视化网页端
- [ ] 网页端进行时间表增删改查
- [ ] 其他网站支持


[APScheduler]: https://apscheduler.readthedocs.io/en/latest/
[youtube-dl]: https://youtube-dl.org/
[ffmpeg]: https://www.ffmpeg.org/