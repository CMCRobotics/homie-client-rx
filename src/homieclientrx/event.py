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
EVENTS_PROPERTY = [EventType.PROPERTY_DISCOVERED, EventType.PROPERTY_UPDATED]


class Event:
    """Represents a Homie event.
    Events are propagated asynchronously and can be processed with reactive operators.
    """
    def __init__(self, event_type:EventType, device=None, node=None, homie_attr: str = None, homie_property: str=None, updated_value = None) -> None:
        self.__event_type = event_type
        self.__device = device
        self.__node = node
        self.__homie_attr = homie_attr
        self.__homie_property = homie_property
        self.__updated_value = updated_value

    @property
    def event_type(self) -> EventType:
        return self.__event_type

    @property
    def device(self):
        return self.__device

    @property
    def node(self):
        return self.__node
    
    @property
    def homie_property(self) -> str:
        return self.__homie_property
    
    @property
    def homie_attr(self) -> str:
        return self.__homie_attr
    
    @property
    def updated_value(self):
        return self.__updated_value
    
    
