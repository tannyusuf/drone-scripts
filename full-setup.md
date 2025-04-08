#!/bin/bash

echo "🔧 Sistem güncelleniyor..."
sudo apt-get update && sudo apt-get upgrade -y

echo "📦 Git kuruluyor..."
sudo apt-get install -y git gitk git-gui

echo "⬇️ ArduPilot deposu indiriliyor..."
git clone https://github.com/ArduPilot/ardupilot.git

echo "🐍 Python bağımlılıkları kuruluyor..."
sudo apt-get install -y python3-pip python3-dev

echo "📂 ArduPilot dizinine geçiliyor ve alt modüller güncelleniyor..."
cd ardupilot
git submodule update --init --recursive

echo "🔬 Gerekli Python kütüphaneleri kuruluyor..."
sudo apt install -y python3-matplotlib python3-serial python3-wxgtk4.0 \
python3-lxml python3-scipy python3-opencv python3-pexpect

echo "🛠️ Bash ayarları yapılıyor..."
echo "export PATH=\$PATH:\$HOME/ardupilot/Tools/autotest" >> ~/.bashrc
echo "export PATH=/usr/lib/ccache:\$PATH" >> ~/.bashrc
source ~/.bashrc

echo "📡 MavLink kuruluyor..."
sudo pip3 install future pymavlink MAVProxy

echo "📦 Empy kuruluyor..."
python3 -m pip install empy==3.3.4

echo "🚁 ArduCopter SIM başlatılıyor..."
cd ~/ardupilot/ArduCopter
../Tools/autotest/sim_vehicle.py -w --console --map

echo "🌐 Gazebo kurulumu başlatılıyor..."
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
sudo apt update
sudo apt-get install -y gazebo11 libgazebo11-dev

echo "🧩 Gazebo ArduPilot eklentisi indiriliyor..."
cd ~
git clone https://github.com/khancyr/ardupilot_gazebo
cd ardupilot_gazebo

echo "🏗️ Eklenti derleniyor..."
mkdir build && cd build
cmake ..
make -j4
sudo make install

echo "📂 Gazebo ortam değişkenleri ayarlanıyor..."
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
echo 'export GAZEBO_MODEL_PATH=~/ardupilot_gazebo/models' >> ~/.bashrc
source ~/.bashrc

echo "✅ Kurulum tamamlandı!"
