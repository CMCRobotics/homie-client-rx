from paho.mqtt import client

from rx3 import Observable

from .device import Device
from .event import Event, EventType

from typing import List


class HomieClientRx:
    """
    A client for IoT devices adhering to the Homie MQTT specification.

    Devices that are discovered on the MQTT server are exposed as
    properties on this class, based on their id.

    The client is a "battery not included" implementation - you must provide
    and manage the MQTT client connectivity yourself.
    """

    def __init__(
        self,
        mqtt_client: client
    ):
        """Initializes the client class.

        Returns a new client class with the given MQTT client.
        Note that the client is not connected to the broker automatically, you must manage connections and reconnections.
        Also important to note that the client's on_message callback will be overwritten by this class.

        Keyword arguments:
        mqtt_client -- the Paho MQTT client instance to use. We redefine the on_message callback.
        """
        self.client = mqtt_client
        self.client.on_message = self.on_message
        self._complete_devices = {}
        self._incomplete_devices = {}
        self._observables:List[Observable] = []

    def __getattr__(self, name):
        """Get a device based on its id."""
        if name in self._complete_devices:
            return self._complete_devices[name]
        else:
            raise AttributeError('No such attribute: ' + name)


    def register_observable(self, observable:Observable) -> None:
        """
        Register an observable that will receive Homie events. 
        A given observable can only be added once (if already registered, the call is a no-op).
        """
        if(observable not in self._observables):
          self._observables.append(observable)

    def unregister_observable(self, observable: Observable) -> bool:
        """
        Unregister an observable, stopping it from receiving Homie events.
        Parameters:
          - observable (Observable) : the observable that will emit Homie events
        Returns:
           True if the observable was successfully removed from the list of active observables, False otherwise.
        """
        if observable in self._observables:
            try:
                self._observables.remove(observable)
            except ValueError:
                return False
            return True
        return False

    @property
    def devices(self):
        """Returns a list of all devices that have been discovered."""
        return list(self._complete_devices.values())

    def on_message(self, client, userdata, msg):
        """Handler for processing MQTT messages.

        Here, messages are passed to the corresponding device (if known)
        or added to a list of incomplete devices.
        """
        (_, device, device_topic) = msg.topic.split('/', 2)
        payload = msg.payload.decode('utf-8')

        if device in self._complete_devices:
            self._complete_devices[device].on_message(device_topic, payload)
        else:
            if device not in self._incomplete_devices:
                self._incomplete_devices[device] = {}
            self._incomplete_devices[device][device_topic] = payload
            self.check_incomplete_device(device)

    def emit(self, event_type:EventType, device=None, node=None, homie_attr: str = None, homie_property: str=None, updated_value = None) -> None:
        evt = Event(event_type, device=device, node=node,homie_attr=homie_attr, homie_property=homie_property, updated_value=updated_value)
        for obs in self._observables:
            obs.on_next(evt)


    def check_incomplete_device(self, device_name):
        """Check if the given device is complete.

        After every message, this method is invoked to check if all
        required data is known for a device. If so, the device is
        complete, and it can be added to the list of complete
        devices, and the callback is invoked to inform the user.
        """
        device_data = self._incomplete_devices[device_name]

        if '$homie' in device_data and '$name' in device_data and \
                '$state' in device_data and '$nodes' in device_data:
            device = Device(self, device_name)
            self._complete_devices[device_name] = device

            for topic in ['$name', '$homie', '$state', '$nodes']:
                device.on_message(topic, device_data[topic])
                del device_data[topic]

            for topic, payload in device_data.items():
                self._complete_devices[device_name].on_message(topic, payload)

            del self._incomplete_devices[device_name]

            device._initializing = False

            self.emit(EventType.DEVICE_DISCOVERED, device=device)

