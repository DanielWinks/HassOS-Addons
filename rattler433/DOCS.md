# Home Assistant Add-on: Rattler 433 (RTL_433)

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Ensure Mosquitto Broker is installed, it is required for this add-on to function.
3. Find the "Rattler 433" add-on and click it.
4. Click on the "INSTALL" button.

## How to use

The add-on has a couple of options available. To get the add-on running:

1. Start the add-on. The default settings should get you started.
2. Have some patience and wait a couple of minutes.
3. Check the add-on log output to see the result.

## Configuration

Add-on configuration:

```yaml
mqtt_prefix: rtl_433
retain: true
customize:
  active: false
  folder: rattler
```

### Option: `mqtt_prefix` (required)

This is the base topic prefix for publishing MQTT messages. It is required, and the default is rtl_433.


### Option: `retain` (required)

Specify whether to retain messages or not. Retained messages are useful if you have devices which report infrequently. By using retained messages, whenever you restart Home Assistant, your entities will intialize with the values from the last retained message.

Can cause issues when used for devices such as the Sonoff RM433 8 button remote. Workaround decribed below. If you only use sensor devices, you can safely choose `true` here.

Default value: `true`


### Option: `customize.active` (optional)

If set to `true` additional configuration files will be read, see the next option.

Default value: `false`


### Option: `customize.folder` (optional)

The folder to read the additional configuration files (`*.conf`) from. Folder will be located in the `/share` directory. Any files located in this folder will be appended to the end of the default configuration file. This can be used for extending the default configuration, or to alter default settings. Any config option duplicated in a file found in the customize folder will override the default setting.

Default value: `rattler`