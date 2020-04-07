In a Nutshell
=============

A Home Assistant component providing access to switches and sensors
provided by Broadlink running either as Hassio addon or as a
standalone instance.


Installation
============

Steps to install the component to Hassio:

1. Set up ssh connection to your Hassio host and log in.

2. Clone the git repository to the home directory.

```
$ git clone https://github.com/rinne/broadlink-hub-hass-component.git
```

3. Place the component directory to custom components.

```
$ mv broadlink-hub-hass-component/broadlink_hub /config/custom_components/
```

4. Restart your Hassio core.

5. Install, configure and start Broadlink Hub to the system that has
   access to the local network that your Broadlink switches are
   connected to. This can be either stand-alone
   (https://github.com/rinne/node-broadlink-hub) or Hassio addon
   (https://github.com/rinne/broadlink-hub-hassio-addon).

6. In configuration menu of your Home Assistant, add Broadlink Hub
   integration. If your Broadlink Hub runs as a Hassio addon, the
   hostname should be local-broadlink-hub-hassio-addon and the port
   8525. If it is instead running somewhere else, you should set the
   hostname and port accordingly. Broadlink Hub can also run behind
   TLS reverse proxy /like Nginx), but special attention must be given
   to the configuration, because reverse proxy then needs to be able
   to forward also websockets.

7. All Broadlink devices visible in the Broadlink Hub becomes visible
   also in Home Assistant and are fully configurable to areas etc.

8. Enjoy


Author
======

Timo J. Rinne <tri@iki.fi>


License
=======

MIT
