number=$1
pass=$2
new_hostname=ncps-mc1-$number
echo Setting hostname: $new_hostname
sudo hostname $new_hostname
sudo echo $new_hostname > /etc/hostname
sudo echo 127.0.0.1    $new_hostname > /etc/hosts 

echo resizing filesystem to fill available space:
sudo resize2fs /dev/mmcblk1p2

echo performing first-time installations:
sudo apt-get update
sudo apt-get install -y python python-dev python-pip git tmux gcc linux-tools-common linux-cloud-tools-common
sudo -H pip install pyserial

netname=SP2_$1
echo connecting to wireless network $netname
echo using wifi password $pass
sudo nmcli dev wifi connect $netname password $pass iface wlan0

cd ~
wget -O files_for_students.zip -L https://cmu.box.com/shared/static/6rgm87yc5fcgcmq601cmj9lajfx3p9gl.zip
mkdir hw1_files
unzip -o files_for_students.zip -d hw1_files

echo 'Installing perf tools (compiling from linux src)'
cd /usr/src/
git clone --depth 1 https://github.com/hardkernel/linux -b odroidxu4-4.14.y
cd linux/tools/perf
sudo make
sudo cp perf /usr/bin/perf

# install PAPI:
cd /tmp
git clone https://bitbucket.org/icl/papi.git
cd papi/src
sudo ./configure
sudo make install

echo Restarting system. See you shortly!
sudo reboot
