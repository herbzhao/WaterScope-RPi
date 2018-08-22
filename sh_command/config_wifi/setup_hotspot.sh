echo open another terminal 

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install dnsmasq hostapd

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd


echo Edit /etc/sysctl.conf and uncomment this line:
echo net.ipv4.ip_forward=1

read -p "Modify the file and press enter to continue"

sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"


echo edit /etc/rc.local with the following line above exit 0
echo iptables-restore < /etc/iptables.ipv4.nat

read -p "Modify the file and press enter to continue"


sudo update-rc.d hostapd enable
sudo update-rc.d dnsmasq enable
