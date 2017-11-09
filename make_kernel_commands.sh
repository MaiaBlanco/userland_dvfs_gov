sudo apt-get install git ncurses-dev make gcc-arm-linux-gnueabi
echo 'Then get the source (use the reset_linux script!)'
cd linux-*
cp /arch/arm/configs/exynos-defconfig .config
# Then configure build kernel:
#make ARCH=arm CROSS_COMPILE=/usr/bin/arm-linux-gnueabi- oldconfig
# optional: customize the build with the nicer menu
make ARCH=arm CROSS_COMPILE=/usr/bin/arm-linux-gnueabi- menuconfig
# Run compilation
make ARCH=arm CROSS_COMPILE=/usr/bin/arm-linux-gnueabi- -k

# References:
#https://raspberrypi.stackexchange.com/questions/192/how-do-i-cross-compile-the-kernel-on-a-ubuntu-host
