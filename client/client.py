#!/usr/bin/env python3

import time
import requests

from py_zipkin.zipkin import zipkin_span
from py_zipkin.transport import BaseTransportHandler

class HttpTransport(BaseTransportHandler):

    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        # The collector expects a thrift-encoded list of spans.
        requests.post(
            'http://localhost:8000/api/v1/spans',
            data=encoded_span,
            headers={'Content-Type': 'application/x-thrift'},
        )

def do_stuff(a, b):
    return 5 + 6

@zipkin_span(
        service_name='my_service',
        span_name='some_function',
        transport_handler=HttpTransport,
        )
def some_function(a, b):
    time.sleep(1)
    return do_stuff(a, b)

if __name__ == "__main__":
    some_function(6,7)

