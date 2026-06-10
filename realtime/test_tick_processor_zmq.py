import pytest
from feature_factory.realtime.tick_processor_zmq import ZMQSubscriber

def test_import_zmq_subscriber():
    assert ZMQSubscriber is not None
