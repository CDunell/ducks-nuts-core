"""
Bridge Adapter Stub
Handles publishing enriched feature vectors to CTA via ZMQ or gRPC
"""
import os
import json

# ZMQ publish utility
def publish_zmq(topic: str, message: dict, zmq_url: str):
    import zmq
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUB)
    socket.connect(zmq_url)
    socket.send_multipart([topic.encode(), json.dumps(message).encode()])

class BridgeAdapter:
    def __init__(self, zmq_url: str = None, grpc_channel=None):
        self.zmq_url = zmq_url or os.getenv('ZMQ_URL')
        self.grpc_channel = grpc_channel

    def publish(self, feature_vector: dict):
        """
        Publish a feature vector dictionary to the CTA bridge.
        By default, uses ZMQ; gRPC support can be added.
        """
        if self.zmq_url:
            publish_zmq('features', feature_vector, self.zmq_url)
        # TODO: add gRPC publish if grpc_channel is configured
