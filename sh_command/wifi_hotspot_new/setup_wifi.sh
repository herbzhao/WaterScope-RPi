sudo cp dhcpcd.conf_wifi /etc/dhcpcd.conf
sudo cp dnsmasq.conf_wifi /etc/dnsmasq.conf
sudo cp hostapd_wifi /etc/default/hostapd

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
