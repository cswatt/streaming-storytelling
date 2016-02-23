### running program
```
websocketd --port 8080 python subway.py
python -m SimpleHTTPServer
```
Open localhost:8000 and click "start."

Data used: MTA subway trains leaving each station. Each trip number is something like "099800_6..S03R", and station names are also in some kind of internal MTA code. To make more sense of what is happening, one would have to find a list of station codes and their corresponding names. The last letter in the station name is always S or N, which denotes south/north (probably Bronx-bound vs Brooklyn-bound trains, more investigation required.)

The refresh rate is quite slow, and updated in large batches. 