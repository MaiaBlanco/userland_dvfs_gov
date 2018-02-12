number=$1
pass=$2
# Set the hostname for the device based on the first input arg
new_hostname=ncps-mc1-$number
echo Setting hostname: $new_hostname
sudo hostname $new_hostname
sudo echo $new_hostname > /etc/hostname
sudo echo 127.0.0.1    $new_hostname > /etc/hosts 

# Make sure maximum space is available
#echo resizing filesystem to fill available space:
#sudo resize2fs /dev/mmcblk1p2

# Install necessary system and python (2.7) packages
#echo performing first-time installations:
#sudo apt-get update
#sudo apt-get install -y python python-dev python-pip git tmux gcc linux-tools-common linux-cloud-tools-common fake-hwclock unzip
#sudo -H pip install pyserial

# Connect to assigned SP2
netname=SP2_$1
echo connecting to wireless network $netname
echo using wifi password $pass
sudo nmcli dev wifi connect $netname password $pass iface wlan0

# Install and compile perf tools
#echo 'Installing perf tools (compiling from linux src)'
#cd /usr/src/
#git clone --depth 1 https://github.com/hardkernel/linux -b odroidxu4-4.14.y
#cd linux/tools/perf
#sudo make
#sudo cp perf /usr/bin/perf

# install PAPI:
#cd /tmp
#git clone https://bitbucket.org/icl/papi.git
#cd papi/src
#sudo ./configure
#sudo make install

# Create a system group with permissions to read/write sysfs
#sudo groupadd --system ncps_students

# Create a new student user for the system
#useroptions='--create-home --shell /bin/bash'
#sudo useradd $useroptions st1
# add st1 to the ncps_students group
#sudo adduser st1 ncps_students
# Add second student
#sudo useradd $useroptions st2
# Add to group
#sudo adduser st2 ncps_students

# Download files for HW1
cd ~
wget -O files_for_students.zip -L https://cmu.box.com/shared/static/6rgm87yc5fcgcmq601cmj9lajfx3p9gl.zip
mkdir /home/st1/hw1_files
unzip -o files_for_students.zip -d /home/st1/hw1_files
mkdir /home/st2/hw1_files
unzip -o files_for_students.zip -d /home/st2/hw1_files

# make sysfs accessible to all in ncps_students (using crontab so this occurs at each reboot)
#sudo crontab -u root -l | { cat; echo "chown -R root:ncps_students /sys 2> /dev/null"; } | sudo crontab -u root
#sudo crontab -u root -l | { cat; echo "chmod -R 775 /sys 2> /dev/null"; } | sudo crontab -u root

# make perf counters available:
#sudo echo "kernel.perf_event_paranoid = -1" >> /etc/sysctl.conf

# make perf accessible to all in ncps_students
#sudo chown root:ncps_students /usr/bin/perf
#sudo chmod 775 /usr/bin/perf

# make TA account (odroid) home directory inaccessible to anyone else:
#sudo chmod 700 /home/odroid 

# Restart
#echo Restarting system. See you shortly!
#sudo reboot
