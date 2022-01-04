# console
Appliance UI

## net container

The net container is used on the appliance to control the wifi interface. It utilizes wpa_supplicant to create an access point. To test this locally, you need a wifi interface to use with it. Purchase a usb wifi dongle, I am using a ralink 5370.

On ubuntu or other distros using NetworkManager, you can disable NetworkManager's control of this interface by adding the following to `/etc/NetworkManager/NetworkManager.conf`.

```
[main]
plugins=ifupdown,keyfile

...

[keyfile]
unmanaged-devices=mac:1c:bf:ce:6b:c8:82
```

Replace the mac address above with your mac address.

This container exports the `/var/run/wpa_supplicant` directory, which allows the console application to control wpa_supplicant.
