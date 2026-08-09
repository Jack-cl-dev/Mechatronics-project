from microbit import *
import utime
import audio
from oa import Oa
NS=500
CN=3
class Od:
 def __init__(s,r,sd=10,ls=None,av=None):
  s.r=r
  s.sd=sd
  s.cs=0
  s.nu=0
  if av is None:av=Oa(r,sd,ls)
  s.av=av
 def ck(s):
  ds=s.r.us()
  if ds<=0 or ds>s.sd:
   s.cs=0
   return False
  s.cs+=1
  return s.cs>=CN
 def iz(s):return utime.ticks_diff(s.nu,utime.ticks_ms())>0
 def ra(s):
  s.r.m1(0,0);s.r.m2(0,0)
  audio.play(Sound.SAD,wait=False)
  utime.sleep_ms(2000)
  rs=s.av.ao()
  s.nu=utime.ticks_add(utime.ticks_ms(),NS)
  s.cs=0
  return rs
