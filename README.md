# Python Homie client

[![PyPI version](https://badge.fury.io/py/homie-client-rx.svg)](https://badge.fury.io/py/homie-client-rx)

This is an implementation of a client for IoT devices following the
[Homie](https://homieiot.github.io/) MQTT convention. Currently, it only
really supports sensor-like devices, i.e., those devices that publish retained
non-settable properties. It is based on [https://github.com/michelwilson/homieclient] 
but intends to extend it by adding :

* Support for URL based MQTT configuration (instead of IP / Port, to allow support for websockets for instance)
* Support for [reactive Rx3](https://pypi.org/project/RxPy3/) events (instead of plain callbacks, to support async and reactive operators)

### Usage

Create an instance of the client, register observables, and connect it to your MQTT server:

```python
from homieclientrx.client import HomieClientRx
from homieclientrx.event import Event, EventType, EVENTS_PROPERTY

mqtt = paho.mqtt.client.Client()
c = HomieClientRx(mqtt)
subj = Subject()
# You can use your favorite reactive operator to triage, filter and debounce Homie events
subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.DEVICE_DISCOVERED)) \
        .subscribe(on_next=lambda evt: print(f"Device discovered, name: {evt.device.name} type: {evt.device.name}"))

subj.pipe(ops.filter(lambda evt: evt.event_type in EVENTS_PROPERTY)) \
        .subscribe(on_next=lambda evt: print(f"Property updated, name: {evt.homie_property.name} new value : {evt.updated_value}"))

# Register the reactive observable to start receiving events
c.register_observable(subj)  

# Likewise, you can unregister observables if you wish to stop receiving messages
c.unregister_observable(subj)

# Do not forget to activate the MQTT connection, or messages will not flow !
mqtt.connect("localhost", 1883)

# Receive property updates (...)

# If you need to update a property, send an MQTT message on the desired topic (Homie won't help you there ;-) )
mqtt.publish("homie/mydevice/mynode/myproperty","my new value")

# When you are done, do not forget to disconnect your MQTT client
mqtt.disconnect()

# Following the similar philosophy, you are in charge of handling MQTT disconnections, reconnections
#  for instance, by using retry decorators.
```

The following event types are supported :

* DEVICE_DISCOVERED : A previously unknown Homie device has been found in the device hierarchy.
* DEVICE_UPDATED : A known Homie device had one of its attributes updated (find the name of the attribute in the event's ```homie_attr``` property)
* NODE_DISCOVERED : A previously unknown node has been found on a known device.
* NODE_UPDATED :  A known node had one of its attributes updated (find the name of the attribute in the event's ```homie_attr``` property)
* PROPERTY_DISCOVERED : A previously unknown property has been found on a known node.
* PROPERTY_UPDATED : The property value has changed (find the name of the attribute in the event's ```homie_property``` property)

It is also possible to access all the devices, nodes and properties via the
client, without using any of the callbacks. Every device is exposed as a property
on the client, the nodes are exposed as properties on the device, and the properties
as properties on the node. So if you have a device with id `outdoor_sensor` with
node `sensor` and property `temperature`, you can do
```
temperature = c.outdoor_sensor.sensor.temperature
print('%s: %.1f %s' % (temperature.name, temperature.value, temperature.unit))
```
This will print something like
```
Temperature: 21.4 °C
```
assuming the name of the property is `Temperature`, and it reports a `float` value,
and the weather is quite nice.
