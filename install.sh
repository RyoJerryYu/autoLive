#!/usr/bin/env bash
sudo yum install -y epel-release
sudo yum update -y

sudo rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
sudo rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm

sudo yum install -y wget

wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl

sudo yum install -y python36

wget https://bootstrap.pypa.io/get-pip.py
sudo python36 get-pip.py
rm -f get-pip.py

pip3 install --upgrade pip
pip3 install requests
pip3 install apscheduler
pip3 install flask

firewall-cmd --zone=public --add-port=2434/tcp --permanent
firewall-cmd --reload

sudo yum install -y git

cd ~
wget https://raw.githubusercontent.com/Sporesirius/ffmpeg-install/master/ffmpeg-install
chmod a+x ffmpeg-install
./ffmpeg-install --install release
rm -f ffmpeg-install

cd ~
mkdir autoLiveTemp
mv -f autoLive/*.json autoLiveTemp/
rm -rf autoLive
git clone https://github.com/RyoJerryYu/autoLive.git
mv -f autoLiveTemp/*.json autoLive/
rm -rf autoLiveTemp

sudo yum install -y screen

cd ~/autoLive
python36 updateConfigs.py