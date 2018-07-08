"""
Runs http server that handles POST requests and send data to carbon cache.
See http://graphite.readthedocs.io/en/latest/carbon-daemons.html#carbon-cache-py

Example:
```bash
curl --data 'this.is.path.to.graphite.metric 1 1531085939' 127.0.0.1:8081
```

```python
def send2graphite(metric_name, value):
    payload = '1min.dht20.%s %s %s' % (metric_name, str(value), str(int(time.time()))
    r = requests.post("http://127.0.0.1:8081/", data=payload)
    r.raise_for_status()
```
"""

import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
import re
import time
import socket


CARBONE_HOST = '127.0.0.1'
CARBONE_PORT = 2003

LINE_PATTERN = re.compile(r'\n')
WHITESPACE_PATTERN = re.compile(r'\s+')


class MyHandler(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        """
        The only method to handle all POSTs
        """
        if self.path == '/':
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            line = post_body.strip()
            fields = WHITESPACE_PATTERN.split(line)
            if len(fields) == 2:
                fields.append(str(long(time.time())))
            elif len(fields) != 3:
                return self.send_response(400)
            line = ' '.join(fields)

            try:

                conn = socket.create_connection((CARBONE_HOST, CARBONE_PORT))
                conn.send(line + "\n")
                conn.close()

            except Exception as e:
                print(e)
                return self.send_response(500)

        self.send_response(200)
        self.end_headers()

httpd = SocketServer.TCPServer(("127.0.0.1", 8081), MyHandler)
httpd.serve_forever()
