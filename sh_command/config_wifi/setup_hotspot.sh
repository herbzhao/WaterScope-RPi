echo open another terminal 

sudo apt-get update
#sudo apt-get upgrade

sudo apt-get install dnsmasq hostapd

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd

echo sudo nano /etc/default/hostapd
echo DAEMON_CONF="/etc/hostapd/hostapd.conf"

read -p "Modify the file and press enter to continue"

echo sudo nano /etc/sysctl.conf and add the line to the bottom
echo net.ipv4.ip_forward=1

read -p "Modify the file and press enter to continue"

sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"


echo sudo nano /etc/rc.local with the following line above exit 0
echo iptables-restore < /etc/iptables.ipv4.nat

read -p "Modify the file and press enter to continue"


sudo update-rc.d hostapd enable
sudo update-rc.d dnsmasq enable

sudo systemctl start hostapd
sudo systemctl start dnsmasq
