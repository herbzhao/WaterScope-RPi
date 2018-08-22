sudo cp /etc/network/interfaces_hotspot /etc/network/interfaces

#services
sudo systemctl start hostapd
sudo service hostapd start

sleep 2
sudo systemctl start dnsmasq
sudo service dnsmasq start


sleep 2
sudo ifdown wlan0
sleep 2
sudo ifup wlan0
