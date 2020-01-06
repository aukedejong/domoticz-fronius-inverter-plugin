Not maintained anymore.
-----------------------

# domoticz-fronius-inverter-plugin
Domoticz Fronius Inverter plugin
--------------------------------

This version of the plugin is running on my Domoticz 3.8799 sinds 2 feb 2018 now.
It's not feature complete, but it's working, so I decided to share.

It creates 2 devices on the Utility page.
One custom meter showing only the current generated Watts.
The other is a kWh type meter

The Fronius API only returns the generated kWhs as an integer.
To make the graphs more fluent the plugin calculates the fractions by using the current Watts generated,
until the intverter return one kWh more. Then the fraction part is reset and starts calculating again.

Comparing the Fronius phone app with this plugin, there is a small difference. Acceptable for me.

- Fronius app - Dommoticz plugin (kWh generated per day)
- 10.4 - 10.692
- 8.62 - 8.431
- 5.72 - 5.859

Installation
------------

In your `domoticz/plugins` directory do

```bash
git clone https://github.com/aukedejong/domoticz-fronius-inverter-plugin.git
```

Restart your Domoticz service with:

```bash
sudo service domoticz.sh restart
```

Now go to **Setup**, **Hardware** in Domoticz. There you add
**Fronius Inverter**.

Fill in the IP address and device ID.
For me the device ID is 1.

Currently the plugin only supports Fronius API version 1

Feature to add
--------------

- Debug options.
- Option to select which devices should be created
- Option the disable the fraction calculation feature
- Detection of Fronius API version
- Some things I can't remember now.

I don't have much spare time, so this can take a while.


This plugin uses an icon by 
<a href="https://www.flaticon.com/authors/vectors-market" title="Vectors Market">
Vectors Market</a> from 
<a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>
and is licensed by 
<a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">
CC 3.0 BY</a>
