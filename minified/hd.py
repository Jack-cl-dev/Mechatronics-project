from microbit import *
import utime
class Hd:
 def __init__(s,r,ot=60,ft=90,ci=250):
  s.r=r
  s.ot=ot
  s.ft=ft
  s.ci=ci
  s.on=False
  s.lc=utime.ticks_ms()
 def up(s):
  now=utime.ticks_ms()
  if utime.ticks_diff(now,s.lc)<s.ci:return s.on
  s.lc=now
  lv=display.read_light_level()
  if s.on and lv>s.ft:
   s.on=False
   s.r.k1(0);s.r.k2(0)
  elif not s.on and lv<s.ot:
   s.on=True
   s.r.k1(1);s.r.k2(1)
  return s.on
