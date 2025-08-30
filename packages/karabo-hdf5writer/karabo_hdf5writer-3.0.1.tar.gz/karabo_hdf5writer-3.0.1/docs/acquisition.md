# Data Acquisition

To start acquiring data, first [Configure](configuration.md) the device.
Afterwards, you can cycle between the `MONITORING` and the `ACQUIRING` states
using the `Monitor` and `Record` buttons.

## The MONITORING State

In this state data sources are connected, and monitored for connections
and acquisition can start instantaneously. Data is continuously refreshed
in the internal buffers, of any data within the configure *Maximum wait time*
will be present.

## The ACQUIRING State

In this state data is written to disk, and connections are monitored for
still being present. This state is left by clicking `Monitor` and a delay
in the state transition will ensure that any data arriving within 
*Maximum wait time* will be present.

## Reconfiguration

To reconfigure the data sources, click `Ignore`. Note that this will disconnect
the device to the data sources it is listening to.