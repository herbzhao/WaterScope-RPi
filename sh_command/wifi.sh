sudo cp /etc/network/interfaces_wifi /etc/network/interfaces

#services
sudo systemctl stop dnsmasq
sleep 2
sudo systemctl stop hostapd

sleep 2
sudo ifdown wlan0
sleep 2
sudo ifup wlan0

