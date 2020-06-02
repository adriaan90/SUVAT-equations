from bs4 import BeautifulSoup as Soup
import numpy as np
from math import sin, cos, atan2, sqrt, pi
from datetime import datetime

FORMAT = '%H:%M:%S'

# You can use BeautifulSoup to parse and extract
# the data you need from the .gpx data that you downloaded.

soup = Soup(open("Evening_run.gpx"))
run_data = soup.findAll("trkpt")

latitude = []
longitude = []
t = []
elevation = []

for tag in run_data:
    latitude.append(str(tag).split('lat="',1)[1].split('" lon=',1)[0])
    longitude.append(str(tag).split('lon="',1)[1].split('">',1)[0])
    time_stamp = tag.find("time").text.split("T",1)[1].split("Z",1)[0]
    t.append(datetime.strptime(time_stamp, FORMAT))
    elevation.append(tag.find("ele").text)
    
elevation = np.asarray(elevation, dtype=np.float32)

# You have to calculate the distance between latitude and longitude in meters.
# The equation to do this is found  at http://www.movable-type.co.uk/scripts/latlong.html.


def distance(latitude, longitude):
    R = 6378 #radius of the earth (km)
    latitude = np.array(latitude)
    longitude = np.array(longitude)
    a = (sin(deg2rad(np.diff(latitude))/2))**2 + cos(deg2rad(latitude[0])) * cos(deg2rad(latitude[1])) * (sin(deg2rad(np.diff(longitude))/2))**2
    c = 2 * atan2( sqrt(a), sqrt(1-a) )
    d = R * c 
    return 1000*d #m


def deg2rad(deg): 
    return deg * pi/180


# The next thing you need to determine is $\Delta t$ to ensure we can
# calculate the correct $v_{average}$.
# This can be done by using the python library `datetime`.

dt = np.zeros(len(t))
dx = np.zeros(len(dt))

for i in range(1,len(longitude)):
    long = [float(longitude[i-1]),
        float(longitude[i])]
    lat = [float(latitude[i-1]),
        float(latitude[i])]
    dx[i] = distance(lat,long)
    dt[i] = (t[i]-t[i-1]).seconds
cumulative_t = np.cumsum(dt)
cumulative_x = np.cumsum(dx)

# Now that we have the `dx` and `dt` variables populated with the running data, we can use the following equations:
# $$v_{avg}=\frac{\Delta x}{\Delta t}$$
# Average velocity can also be expressed as:
# $$v_{avg}=\frac{u+v}{2}$$
# And when we have the beginning velocity ($u$) and the end velocity ($v$), we can calculate acceleration:
# $$a = \frac{v-u}{t}$$

v_avg = np.zeros(len(dx))
u = np.zeros(len(dx))
v = np.zeros(len(dx))
a = np.zeros(len(dx))

for i in range(1,len(v_avg)):
    v_avg[i] = dx[i]/dt[i]
for i in range(1,len(u)):
    v[i] = 2*v_avg[i] - u[i-1]
    u[i] = v[i]
    a[i] = (v[i]-u[i-1])/dt[i]   

# We can calculate the average pace for the whole run with:
# $$pace = \frac{time}{distance}$$

print(f"Total time jogging: {int(np.sum(dt)/60)}:{int(np.sum(dt)%60)} minutes")
print(f"Total distance: {round(np.sum(dx)/1000,2)} km")
print(f"Pace: {int((np.sum(dt)/(np.sum(dx)/1000)//60))}:{int((np.sum(dt)/(np.sum(dx)/1000)%60))} min/km")






