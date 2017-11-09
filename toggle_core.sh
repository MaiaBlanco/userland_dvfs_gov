echo WARNING: Running stop mpdecision for this to have effect!
stop mpdecision
# Use to toggle cores on and off:
FNAME=/sys/devices/system/cpu/cpu$1/online
echo $FNAME
ONLINE=$(cat $FNAME)
if [ $ONLINE=="0" ]; then
	echo Enabling CPU $1
	echo "1" >  /sys/devices/system/cpu/cpu$1/online
else
	echo Disabling CPU $1
	echo "0" > /sys/devices/system/cpu/cpu$1/online
fi
