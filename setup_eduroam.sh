#! /bin/sh

#bash initialise
run_time=`date +%Y%m%d%H%M`
log_file="/home/pi/logfiles/ap_setup_log.${run_time}"
cat /dev/null > ${log_file}   #create a empty log_file. truncate a file.

echo "Welcome, this is setup for Eduroam connection."
echo "It cannot work together with access point"



# User input SSID and password
read -e -p "Eduroam account (i.e. xxx@cam.ac.uk): "  -i "@cam.ac.uk" AP_SSID
AP_WPA_PASSPHRASE = 0
  
echo "Input the password for your account (16 lowercase alphabetic characters)"
	read -p "Password for your WIFI (i.e. ): " AP_WPA_PASSPHRASE
	echo ""

#backup current interfaces
echo "backup: /etc/network/interfaces"  

if [ -f /etc/network/interfaces ]; then
        cp /etc/network/interfaces /etc/network/interfaces.bak.${run_time}
        echo "/etc/network/interfaces copied to /etc/network/interfaces.bak.${run_time}"                       | tee -a ${log_file}
fi

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
echo "iface wlan0 inet dhcp"                     >> /etc/network/interfaces
echo "wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf"      >> /etc/network/interfaces


#backup current wpa_supplicant.conf
echo "backup: /etc/wpa_supplicant/wpa_supplicant.conf"  

if [ -f /etc/network/interfaces ]; then
        cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.bak.${run_time}
        echo "/etc/wpa_supplicant/wpa_supplicant.conf copied to /etc/wpa_supplicant/wpa_supplicant.bak.${run_time}"                       | tee -a ${log_file}
fi

#setup interfaces
echo "Configure: /etc/wpa_supplicant/wpa_supplicant.conf"  | tee -a ${log_file} 
echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev"     >  /etc/wpa_supplicant/wpa_supplicant.conf	
echo "update_config=1"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo ""         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "network={"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "ssid="'"eduroam"'"">>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "scan_ssid=1"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "key_mgmt=WPA-EAP"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "pairwise=CCMP TKIP"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "group=CCMP TKIP"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "eap=PEAP"         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "identity="'""${AP_SSID}"'""         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "password="'"${AP_WPA_PASSPHRASE}"'""         >>  /etc/wpa_supplicant/wpa_supplicant.conf
echo "}"         >>  /etc/wpa_supplicant/wpa_supplicant.conf


echo "you may need to reboot for the settings to work"        


