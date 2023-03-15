import unittest
from unittest.mock import call, Mock, ANY
from callee.attributes import Attrs

from homieclientrx.client import HomieClientRx
from homieclientrx.event import Event, EventType, EVENTS_DEVICE, EVENTS_NODE, EVENTS_PROPERTY
from paho.mqtt.client import MQTTMessage, Client

from rx3.subject import Subject
import rx3.operators as ops


class TestIntegration(unittest.TestCase):
    def test_integration(self):
        mqtt = Client()
        c = HomieClientRx(mqtt)

        device_discovered_mock = Mock()
        device_updated_mock = Mock()
        node_discovered_mock = Mock()
        property_discovered_mock = Mock()
        property_updated_mock = Mock()

        subj = Subject()
        subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.DEVICE_DISCOVERED)).subscribe(on_next=lambda evt: device_discovered_mock.on_next(evt))
        subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.DEVICE_UPDATED)).subscribe(on_next=lambda evt: device_updated_mock.on_next(evt))
 
        subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.NODE_DISCOVERED)).subscribe(on_next=lambda evt: node_discovered_mock.on_next(evt))
        
        subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.PROPERTY_DISCOVERED)).subscribe(on_next=lambda evt: property_discovered_mock.on_next(evt))
        subj.pipe(ops.filter(lambda evt: evt.event_type == EventType.PROPERTY_UPDATED)).subscribe(on_next=lambda evt: property_updated_mock.on_next(evt))

        c.register_observable(subj)

        with open('tests/messages.txt') as f:
            for line in f.readlines():
                topic, payload = line.split(' ', 1)
                msg = MQTTMessage()
                msg.topic = topic.encode('utf-8')
                msg.payload = payload.strip().encode('utf-8')
                c.on_message(None, None, msg)

        assert c.sensor1.state == 'ready'
        assert len(c.sensor1.nodes) == 2
        assert len(c.sensor1.dht.properties) == 2
        assert len(c.sensor1.bmp.properties) == 1
        assert c.sensor1.dht.temperature == {'name': 'Temperature', 'unit': '°C', 'value': 19.82}
        assert c.sensor1.dht.humidity == {'name': 'Humidity', 'unit': '%', 'value': 61.9}
        assert c.sensor1.bmp.pressure == {'name': 'Pressure', 'unit': 'mbar', 'value': 1021.69}
        assert c.powermeter.state == 'ready'
        assert len(c.powermeter.nodes) == 1
        assert len(c.powermeter.powermeter.properties) == 2
        assert c.powermeter.powermeter.power_delivered == {'name': 'Power delivered', 'unit': 'W', 'value': 410}
        assert c.powermeter.powermeter.power_returned == {'name': 'Power returned', 'unit': 'W', 'value': 1500}

        device_discovered_mock.assert_has_calls([
              call.on_next(Attrs(event_type=EventType.DEVICE_DISCOVERED, device=c.sensor1))
            , call.on_next(Attrs(event_type=EventType.DEVICE_DISCOVERED, device=c.powermeter))
        ])

        device_updated_mock.assert_has_calls([
             call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.sensor1, homie_attr='$name' ))
            ,call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.sensor1, homie_attr='$homie' ))
            ,call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.sensor1, homie_attr='$state'))
            ,call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.powermeter , homie_attr='$name' ))
            ,call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.powermeter , homie_attr='$homie' ))
            , call.on_next(Attrs(event_type=EventType.DEVICE_UPDATED, device=c.powermeter, homie_attr='$state'))
        ])

        node_discovered_mock.assert_has_calls([
             call.on_next(Attrs(event_type=EventType.NODE_DISCOVERED, node=c.sensor1.dht))
            ,call.on_next(Attrs(event_type=EventType.NODE_DISCOVERED, node=c.sensor1.bmp))
            ,call.on_next(Attrs(event_type=EventType.NODE_DISCOVERED, node=c.powermeter.powermeter))
        ], any_order=True)

        property_discovered_mock.assert_has_calls([
             call.on_next(Attrs(event_type=EventType.PROPERTY_DISCOVERED, node=c.sensor1.dht, homie_property='temperature'))
            ,call.on_next(Attrs(event_type=EventType.PROPERTY_DISCOVERED, node=c.sensor1.dht, homie_property='humidity'))
            ,call.on_next(Attrs(event_type=EventType.PROPERTY_DISCOVERED, node=c.sensor1.bmp, homie_property='pressure'))
            ,call.on_next(Attrs(event_type=EventType.PROPERTY_DISCOVERED, node=c.powermeter.powermeter, homie_property='power_delivered'))
            ,call.on_next(Attrs(event_type=EventType.PROPERTY_DISCOVERED, node=c.powermeter.powermeter, homie_property='power_returned'))
        ])

        property_updated_mock.assert_has_calls([
            call.on_next(Attrs(node=c.sensor1.dht, homie_property='temperature', updated_value={'name': 'Temperature', 'unit': '°C', 'value': 20.12}))
            ,call.on_next(Attrs(node=c.sensor1.dht, homie_property='temperature', updated_value={'name': 'Temperature', 'unit': '°C', 'value': 20.08}))
            ,call.on_next(Attrs(node=c.sensor1.dht, homie_property='temperature', updated_value={'name': 'Temperature', 'unit': '°C', 'value': 19.82}))
            ,call.on_next(Attrs(node=c.sensor1.dht, homie_property='humidity',updated_value={'name': 'Humidity', 'unit': '%', 'value': 63.5}))
            ,call.on_next(Attrs(node=c.sensor1.dht, homie_property='humidity',updated_value={'name': 'Humidity', 'unit': '%', 'value': 63.2}))
            ,call.on_next(Attrs(node=c.sensor1.dht, homie_property='humidity',updated_value={'name': 'Humidity', 'unit': '%', 'value': 61.9}))
            ,call.on_next(Attrs(node=c.sensor1.bmp, homie_property='pressure',updated_value={'name': 'Pressure', 'unit': 'mbar', 'value': 1021.7}))
            ,call.on_next(Attrs(node=c.sensor1.bmp, homie_property='pressure',updated_value={'name': 'Pressure', 'unit': 'mbar', 'value': 1021.71}))
            ,call.on_next(Attrs(node=c.sensor1.bmp, homie_property='pressure',updated_value={'name': 'Pressure', 'unit': 'mbar', 'value': 1021.69}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_delivered',updated_value= {'name': 'Power delivered', 'unit': 'W', 'value': 356}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_delivered',updated_value= {'name': 'Power delivered', 'unit': 'W', 'value': 390}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_delivered',updated_value= {'name': 'Power delivered', 'unit': 'W', 'value': 410}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_returned', updated_value={'name': 'Power returned', 'unit': 'W', 'value': 1300}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_returned', updated_value={'name': 'Power returned', 'unit': 'W', 'value': 1400}))
            ,call.on_next(Attrs(node=c.powermeter.powermeter, homie_property='power_returned', updated_value={'name': 'Power returned', 'unit': 'W', 'value': 1500}))
        ], any_order=True)