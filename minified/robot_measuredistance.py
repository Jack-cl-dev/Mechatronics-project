from mq import Mq
from microbit import *
import utime
r=Mq()
v0=Image("00000:00000:00900:00000:00000")
v1=Image("00000:00900:09090:00900:00000")
v2=Image("09990:90009:90009:90009:09990")
vs=[v0,v1,v2]
while True:
 dc=r.us()
 dl=max(0,int(10*dc))
 for v in vs:
  display.show(v)
  utime.sleep_ms(dl)
