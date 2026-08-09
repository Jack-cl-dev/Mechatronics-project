from mq import Mq
from microbit import *
import utime
r=Mq()
for x in range(3):
 utime.sleep_ms(1000)
 r.k1(1);r.k2(1)
 utime.sleep_ms(1000)
 r.k1(0);r.k2(0)
