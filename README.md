# autoLive

## 简介
利用[APScheduler][APScheduler]，按时间表定时启动转播任务。

利用[flask框架][flask]构建浏览器端，动态查询或增删时间表中的转播任务。

一个转播任务中，利用[youtube-dl][youtube-dl]获得YouTube直播m3u8地址，并用[ffmpeg][ffmpeg]将对应直播转播到B站直播。

程序运行于`Python3`。

## 一键安装脚本
- 以下所有步骤中的粘贴不能使用ctrl+v！应使用右键->粘贴。
- 将以下几行命令粘贴入Xshell，自动下载安装脚本并运行：
```bash
cd ~
rm -f install.sh
sudo yum install -y wget
wget https://raw.githubusercontent.com/RyoJerryYu/autoLive/master/install.sh
chmod +x install.sh
bash install.sh
```
- 运行大概3分钟左右后，会出现如下提示：
```
###############################
#                             #
# paste your bilibili cookies #
#                             #
###############################
```
- 此时将直播所用的账号的cookie串粘贴，回车继续运行
- 出现此`nohup: redirectiong stderr to stdout`提示后，可以直接关闭Xshell
- 然后浏览器登陆`<服务器ip>:2434/autoLive/`，如果没有报错，则安装成功。
- 后续更新时只需重新粘贴最初的两行命令即可。
- 使用一键安装脚本，而不进行其他设置的话，以下的部分可以不看了。
- 默认自带的VTuber只包括にじさんじ。如果需要转播其他VTuber需要手动修改`liveInfo.json`，格式请参照下面`liveInfo.json`的格式。

## 测试环境
- CentOS 7
- youtube-dl 2018.10.05
- ffmpeg 4.0.2-static
- Python 3.6
- requests 2.19.1
- APScheduler 3.5.3
- Flask 1.0.2

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
安装`requests`，`APScheduler`，`Flask`。需要先安装python3对应的pip。
```bash
# 安装requests
pip3 install requests
# 安装APScheduler
pip3 install APScheduler
# 安装Flask
pip3 install Flask
```

## 运行
- 先使用`git clone`把代码clone到本地，并cd到对应`autoLive`目录中。需要先安装git。
- 把B站cookies串粘贴到`autoLive/cookies.txt`中。
此时可运行`python3 refresh_area_id.py`更新area_id.txt，同时测试cookies串是否能登陆。
```bash
python3 refresh_area_id.py
```
- 配置`config.ini`，主要根据自己情况更改直播间标题格式、分区及最高清晰度。其中`{time}``{liver}``{site}``{title}`均为时间表中的参数。
- （可选）填写`schedule.txt`。目前只能解析未来24小时内的直播，而且每次重新运行都需要读取一次时间表。因为时间表增删也可从网页端设置，此步可忽略。
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

```python
[ # list，每一项dictionary对应一位liver
    {
        "liver": "樋口楓", # str，与时间表中liver项对应
        "room": [ # list，每一项dictionary对应一个直播间
            {
                "site": "YouTube", # str，直播网站名，注意大小写
                "url": "https://www.youtube.com/channel/UCsg-YqdqQ-KFF0LNk23BY4A/live" # str，对应直播间url
            },
            # 其他网站的直播间
            # 但是目前只能解析YouTube上的直播间，所以list的其他项没有意义
        ]
    },
    # 相同格式的其他liver信息
]
```

- 运行`main.py`。建议在screen中启动。
```bash
python3 main.py
```
- 登入网页端。`<ip地址>:2434/autoLive/`，其中ip地址为服务器ip地址。按需要添加或删除时间项。

其中'时间'格式为HHMM，只接受未来24小时内的直播，检测出直播时间在运行程序之前时，会自动认为直播在运行程序第二天开始。

'自定义标题'可不填，不填时默认为"{liver}"+"转播"

- 准备完成，现在只需等待程序自动转播到你的B站账号了！

## 已进行过的修改
- 需要手动填写时间表，手动传输时间表到服务器并手动启动程序。
- 程序不能一直运行，需要每天启动读取时间表。
- 灵活度不足。时间表一旦运行后不能增删改，无法应对突击直播等情况。

以上三点已通过添加网页端，并在网页端上进行时间表的增删改来解决。


## 缺点与修改方案
- 设置不够灵活，只能通过config.ini手动修改

以后会增加在网页端进行设置、添加liveInfo等功能

- 只能接受YouTube上的直播

已预留好接口，以后可进行其他网站直播的扩充。

- 直播前只能发文字动态，不能转发直播间

虽未获得转发直播间的API，但已通过增加直播间链接的方法暂时解决。

- 同时只能通过一个B站账号进行转播

以后可能会增加多账号支持，但考虑到VPS的承受能力，不推荐同一服务器同时进行多项转播。

## TODO LIST
- [X] 可视化网页端
- [X] 网页端进行时间表增删改查
- [X] 每日自动发送每日时间表
- [X] 退出程序时保存时间表
- [X] 网页端现在可以查看正在运行中的项目了
- [ ] 增加网页端设置页面
- [ ] 增加可以设置的项目
- [ ] 可以从网页端增删liveInfo
- [ ] 修正因每日动态过长而无法发送问题
- [ ] 尝试使用streamlink代替ffmpeg
- [ ] 其他网站支持

## 特别鸣谢
- B站id: 一生的等待
- [HalfMAI/AutoYtB](https://github.com/HalfMAI/AutoYtB)
- [7rikka/autoLive](https://github.com/7rikka/autoLive)
- [pandaGao/bilibili-live](https://github.com/pandaGao/bilibili-live)

本程序有参考以上个人或项目的思路或代码内容，遇到困难时也得到了他们的援助，在此表示感谢。


[APScheduler]: https://apscheduler.readthedocs.io/en/latest/
[youtube-dl]: https://youtube-dl.org/
[ffmpeg]: https://www.ffmpeg.org/
[flask]: http://flask.pocoo.org/