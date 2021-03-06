from flask import Flask
from flask import request

from py_zipkin.util import generate_random_64bit_string
from py_zipkin.zipkin import create_http_headers_for_new_span
from py_zipkin.zipkin import ZipkinAttrs
from py_zipkin.zipkin import zipkin_span

import os
import requests

app = Flask(__name__)

TRACE_HEADERS_TO_PROPAGATE = [
    'X-Ot-Span-Context',
    'X-Request-Id',
    'X-B3-TraceId',
    'X-B3-SpanId',
    'X-B3-ParentSpanId',
    'X-B3-Sampled',
    'X-B3-Flags'
]

def http_transport(encoded_span):
    requests.post(
        'http://zipkin:9411/api/v1/spans',
        data=encoded_span,
        headers={'Content-Type': 'application/x-thrift'},
    )

def extract_zipkin_attrs(headers):
    return ZipkinAttrs(
            headers['X-B3-TraceId'],
            generate_random_64bit_string(),
            headers['X-B3-SpanId'],
            headers.get('X-B3-Flags', ''),
            headers['X-B3-Sampled'],
            )

@app.route('/')
def trace():
    headers = {}
    for header in TRACE_HEADERS_TO_PROPAGATE:
        if header in request.headers:
            headers[header] = request.headers[header]

    with zipkin_span(
            service_name='service{}'.format('SRV'),
            span_name='service',
            transport_handler=http_transport,
            port=int(9411),
            zipkin_attrs=extract_zipkin_attrs(headers)):
        return ('Hello from service {}!\n'.format('TEST'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(6666), debug=True)
