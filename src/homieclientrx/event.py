from .device import Device
from .node import Node

import enum

@enum.unique
class EventType(enum.Enum):

    DEVICE_DISCOVERED = "device_discovered"
    DEVICE_UPDATED = "device_updated"
    NODE_DISCOVERED = "node_discovered"
    NODE_UPDATED = "node_updated"
    PROPERTY_DISCOVERED = "property_discovered"
    PROPERTY_UPDATED = "property_updated"

    def equals(self, string):
       return self.value == string

EVENTS_DEVICE = [EventType.DEVICE_DISCOVERED,EventType.DEVICE_UPDATED]
EVENTS_NODE = [EventType.NODE_DISCOVERED, EventType.NODE_UPDATED]
EVENTS_PROPERTY = [EventType.PROPERTY_DISCOVERED, EventType.PROPERTY_UPDATEDs]


class Event:
    """Represents a Homie event.
    Events are propagated asynchronously and can be processed with reactive operators.
    """
    def __init__(self, event_type:EventType, device: Device =None, node: Node=None, attribute: str = None, property: str=None, value_update = None) -> None:
        self.__event_type = event_type
        self.__device = device
        self.__node = node
        self.__attribute = attribute
        self.__property = property
        self.__value_update = value_update

    @property
    def event_type(self) -> EventType:
        return self.__event_type

    @property
    def device(self) -> Device:
        return self.__device

    @property
    def node(self) -> Node:
        return self.__node
    
    @property
    def property(self) -> str:
        return self.__property
    
    @property
    def attribute(self) -> str:
        return self.__attribute
    
    @property
    def value_update(self):
        return self.__value_update
    
    
