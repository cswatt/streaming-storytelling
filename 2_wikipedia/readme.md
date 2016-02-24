### running program
```
websocketd --port 8080 python listen.py
python -m SimpleHTTPServer
```
Open localhost:8000 and click "start."

### notes on implementation
'listen.py' listens to changes from stream.wikimedia.org and keeps track of their rate. It prints a JSON message for every change received. Every few seconds, it also prints a different JSON message that has message rate information.
'index.html' sees which articles are being changed and displays the current rate. When the rate rises above a certain threshold, the text turns red.