sudo cp dhcpcd.conf_hotspot /etc/dhcpcd.conf
sudo cp dnsmasq.conf_hotspot /etc/dnsmasq.conf
sudo cp hostapd_hotspot /etc/default/hostapd

sudo systemctl start hostapd
sudo systemctl start dnsmasq
sudo systemctl start hostapd
