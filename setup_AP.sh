#! /bin/sh

#bash initialise
run_time=`date +%Y%m%d%H%M`
log_file="/home/pi/logfiles/ap_setup_log.${run_time}"
cat /dev/null > ${log_file}   #create a empty log_file. truncate a file.

echo "Welcome, you can now set up your access point for raspberryPi"

# User input SSID and password
read -e -p "WIFI SSID (i.e. WaterScopi): "  -i "WaterScopi" AP_SSID
AP_WPA_PASSPHRASE = 0

while [ `echo $AP_WPA_PASSPHRASE | wc -c` -lt 8 ] || [ `echo $AP_WPA_PASSPHRASE | wc -c` -gt 63 ]; 
do    
echo "Input the password with correct length (8-63)"
	read -e -p "Password for your WIFI (i.e. waterscope): " -i "waterscope" AP_WPA_PASSPHRASE
	echo ""
done  

#backup current interfaces
echo "backup: /etc/network/interfaces"  

if [ -f /etc/network/interfaces ]; then
        cp /etc/network/interfaces /etc/network/interfaces.bak.${run_time}
        echo "/etc/network/interfaces copied to /etc/network/interfaces.bak.${run_time}"                       | tee -a ${log_file}
fi


# set up hostapd.conf
echo "Configure: /etc/hostapd/hostapd.conf"   | tee -a ${log_file} 
if [ ! -f /etc/hostapd/hostapd.conf ]; then
	touch /etc/hostapd/hostapd.conf
fi
	
echo "interface=wlan0"                                    >  /etc/hostapd/hostapd.conf
echo "ssid=${AP_SSID}"                                   >> /etc/hostapd/hostapd.conf
echo "channel=6"                             				>> /etc/hostapd/hostapd.conf
echo "hw_mode=g"                             				>> /etc/hostapd/hostapd.conf
echo "macaddr_acl=0"                                     >> /etc/hostapd/hostapd.conf
echo "auth_algs=1"                                       >> /etc/hostapd/hostapd.conf
echo "ignore_broadcast_ssid=0"                           >> /etc/hostapd/hostapd.conf
echo "wpa=2"                                             >> /etc/hostapd/hostapd.conf
echo "wpa_passphrase=${AP_WPA_PASSPHRASE}"               >> /etc/hostapd/hostapd.conf
echo "wpa_key_mgmt=WPA-PSK"                              >> /etc/hostapd/hostapd.conf
echo "wpa_pairwise=TKIP"                                 >> /etc/hostapd/hostapd.conf
echo "rsn_pairwise=CCMP"                                 >> /etc/hostapd/hostapd.conf


#setup interfaces
echo "Configure: /etc/network/interfaces"  | tee -a ${log_file} 
echo "# interfaces(5) file used by ifup(8) and ifdown(8)"     >  /etc/network/interfaces	
echo "# Please note that this file is written to be used with dhcpcd"         >>  /etc/network/interfaces
echo "# For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'"        >>  /etc/network/interfaces
echo "# Include files from /etc/network/interfaces.d:"                        >>  /etc/network/interfaces
echo "source-directory /etc/network/interfaces.d"            >>  /etc/network/interfaces
echo "auto lo"                                         >>  /etc/network/interfaces
echo "iface lo inet loopback"                          >> /etc/network/interfaces
echo ""                                         >>  /etc/network/interfaces
echo "iface eth0 inet dhcp"                           >> /etc/network/interfaces
echo ""                                         >>  /etc/network/interfaces
echo "allow-hotplug wlan0"                       >> /etc/network/interfaces
echo "iface wlan0 inet static"                     >> /etc/network/interfaces
echo "address 10.0.0.1"      >> /etc/network/interfaces
echo "netmask 255.255.255.0"      >> /etc/network/interfaces
echo "up iptables-restore < /etc/iptables.ipv4.nat"      >> /etc/network/interfaces


echo "you may need to reboot for the settings to work"        



