#! /bin/sh

#bash initialise
run_time=`date +%Y%m%d%H%M`
mkdir /home/pi/logfiles
log_file="/home/pi/logfiles/ap_setup_log.${run_time}"
cat /dev/null > ${log_file}   #create a empty log_file. truncate a file.

echo "Welcome,  we will start installing access point for raspberryPi"


#file info & disclaimer
echo ""
echo " ====================================================================== "          | tee -a ${log_file}
echo "title           :install_AP.sh"                                                | tee -a ${log_file}
echo "description     :Automatic access point setup for raspberry pi."                   | tee -a ${log_file}
echo "author          :Tianheng Zhao(tianheng.zhao@waterscope.org)"		                 | tee -a ${log_file}
echo "original author          :Jacek Tokar (jacek@raspberry-at-home.com)"		                 | tee -a ${log_file}
echo "original author          :Tomasz Szczerba (tomek@raspberry-at-home.com)"	                 | tee -a ${log_file}
echo "original author site     :raspberry-at-home.com"                                            | tee -a ${log_file}
echo "github site      :  "                                                     | tee -a ${log_file}
echo "date            :20160610"                                                         | tee -a ${log_file}
echo "version         :1.0"                                                              | tee -a ${log_file}
echo "usage           :sudo  bash ap_setup.sh"                                               | tee -a ${log_file}
echo "This is designed to work with newest RaspberryPi3, not optimised for any other wifi dongle"	 | tee -a ${log_file}	
echo "You can improve the script. Once you do it, share it with us. Keep credentials!"	 | tee -a ${log_file}	
echo " ====================================================================== "          | tee -a ${log_file}
echo " DISCLAIMER:   "                                                                   | tee -a ${log_file}
echo "     Tianheng, waterscope.org, "  | tee -a ${log_file}
echo "     Jacek, raspberry-at-home.com or anyone else on this blog is not responsible"  | tee -a ${log_file}
echo "     for bricked devices, dead SD cards, thermonuclear war, or any other things "  | tee -a ${log_file}
echo "     script may break. You are using this at your own responsibility...."          | tee -a ${log_file}
echo "     				....and usually it works just fine :)"          				 | tee -a ${log_file}
echo " ====================================================================== "          | tee -a ${log_file}
read -n 1 -p "Do you accept above terms? (y/n)" terms_answer
echo "" 

if [ "${terms_answer,,}" = "y" ]; then
        echo "Thank you!"                                                                | tee -a ${log_file}
else
        echo "Head to ${post_link} read, comment and let us clear your doubts :)"        | tee -a ${log_file}
        exit 1
fi

#update repo 
echo "Updating repositories..."
apt-get update
echo ""					  | tee -a ${log_file} 

#install the packages
echo "Downloading and installing packages: hostapd,  isc-dhcp-server,  iptables."
sudo apt-get install hostapd isc-dhcp-server iptables
service hostapd stop | tee -a ${log_file} > /dev/null
service isc-dhcp-server stop  | tee -a ${log_file}  > /dev/null
echo ""					  | tee -a ${log_file} 



# User input SSID and password for access point
read -e -p "WIFI SSID (i.e. WaterScopi): "  -i "WaterScopi" AP_SSID
AP_WPA_PASSPHRASE = 0

while [ `echo $AP_WPA_PASSPHRASE | wc -c` -lt 8 ] || [ `echo $AP_WPA_PASSPHRASE | wc -c` -gt 63 ]; 
do    
echo "Input the password with correct length (8-63)"
	read -e -p "Password for your WIFI (i.e. waterscope): " -i "waterscope" AP_WPA_PASSPHRASE
	echo ""
done  



#backup existing config files
echo "Backups:"                                                                                         | tee -a ${log_file}

if [ -f /etc/dhcp/dhcpd.conf ]; then
        cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bak.${run_time}
        echo " /etc/dhcp/dhcpd.conf to /etc/dhcp/dhcpd.conf.bak.${run_time}"                              | tee -a ${log_file}
fi

if [ -f /etc/hostapd/hostapd.conf ]; then
        cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bak.${run_time}
        echo "/etc/hostapd/hostapd.conf to /etc/hostapd/hostapd.conf.bak.${run_time}"                   | tee -a ${log_file}
fi

if [ -f /etc/default/isc-dhcp-server ]; then
        cp /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.bak.${run_time}
        echo "/etc/default/isc-dhcp-server to /etc/default/isc-dhcp-server.bak.${run_time}"             | tee -a ${log_file}
fi

if [ -f /etc/sysctl.conf ]; then
        cp /etc/sysctl.conf /etc/sysctl.conf.bak.${run_time}
        echo "/etc/sysctl.conf /etc/sysctl.conf.bak.${run_time}"                                        | tee -a ${log_file}
fi

if [ -f /etc/network/interfaces ]; then
        cp /etc/network/interfaces /etc/network/interfaces.bak.${run_time}
        echo "/etc/network/interfaces to /etc/network/interfaces.bak.${run_time}"                       | tee -a ${log_file}
fi



#report to users
echo ""
echo ""
echo "+========================================================================"
echo "Your network settings will be:"                                                                   | tee -a ${log_file}
echo "AP NIC address: 10.0.0.1  "                                                                  | tee -a ${log_file}
echo "Subnet:  255.255.255.0 "																				| tee -a ${log_file}
echo "Addresses assigned by DHCP will be from  10.0.0.2 to 10.0.0.255"                    | tee -a ${log_file}
echo "Netmask: 255.255.255.0"                                                                           | tee -a ${log_file}


 
echo "Setting up AP..."                                                                                 | tee -a ${log_file} 

#isc-dhcp-sserver
echo "Configure: /etc/default/isc-dhcp-server"                                                          | tee -a ${log_file} 

echo "INTERFACES=\"wlan0\""                                         >> /etc/default/isc-dhcp-server
#echo "DHCPD_CONF=\"/etc/dhcp/dhcpd.conf\""                         >  /etc/default/isc-dhcp-server

#/etc/dhcp/dhcpd.conf
echo "Configure: /etc/dhcp/dhcpd.conf"                                                          | tee -a ${log_file} 

echo "ddns-update-style none;"                                     >  /etc/dhcp/dhcpd.conf
echo "default-lease-time 600;"                                     >> /etc/dhcp/dhcpd.conf
echo "max-lease-time 7200;"                                        >> /etc/dhcp/dhcpd.conf
echo "authoritative;"                                        >> /etc/dhcp/dhcpd.conf
echo "log-facility local7;"                                        >> /etc/dhcp/dhcpd.conf
echo "subnet 10.0.0.0 netmask 255.255.255.0 {"                    >> /etc/dhcp/dhcpd.conf
echo "  range 10.0.0.5 10.0.0.55  ;"                >> /etc/dhcp/dhcpd.conf
echo "  option broadcast-address 10.0.0.255;"                >> /etc/dhcp/dhcpd.conf
echo "  option routers 10.0.0.1 ;"                >> /etc/dhcp/dhcpd.conf
echo "  default-lease-time 600;"                >> /etc/dhcp/dhcpd.conf
echo "   max-lease-time 7200;"                >> /etc/dhcp/dhcpd.conf
echo "  option domain-name \"local\";"                              >> /etc/dhcp/dhcpd.conf
echo "  option domain-name-servers 8.8.8.8, 8.8.4.4  ;"                       >> /etc/dhcp/dhcpd.conf
echo "}"                                                           >> /etc/dhcp/dhcpd.conf




#setup /etc/default/hostapd
echo "Configure: /etc/default/hostapd"                                                          | tee -a ${log_file} 

echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\""                   > /etc/default/hostapd


# set up hostapd.conf
echo "Configure: /etc/hostapd/hostapd.conf"   | tee -a ${log_file} 
		#create the hostapd.conf file
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



#setup /etc/network/interfaces
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


#prepare the iptables

#/etc/sysctl/sysctrl.conf
echo "Configure: /etc/sysctl.conf"                                                              | tee -a ${log_file} 
echo "net.ipv4.ip_forward=1"                             >> /etc/sysctl.conf 

echo "Configure: iptables"                                                                      | tee -a ${log_file} 
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT  
sh -c "iptables-save > /etc/iptables.ipv4.nat"



#set hostapd and dhcp server to run on boot up
echo "Configure: startup"                                                              | tee -a ${log_file}
update-rc.d hostapd enable
update-rc.d isc-dhcp-server enable 


#iptables
echo "Configure: iptables"                                                                      | tee -a  ${log_file}


echo ""                                                                                        | tee -a ${log_file}
echo "Do not worry if you see something like: [FAIL] Starting ISC DHCP server above... this is normal :)"               | tee -a ${log_file}
echo ""                                                                                        | tee -a ${log_file}
echo "REMEMBER TO RESTART YOUR RASPBERRY PI!!!"                                                | tee -a ${log_file}
echo ""                                                                                        | tee -a ${log_file}

exit 0
