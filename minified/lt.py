from microbit import *
import utime
OF=(0,0,0)
GR=(0,255,0)
BL=(0,60,255)
AM=(255,120,0)
RD=(255,0,0)
WH=(255,255,255)
class Lt:
 def __init__(s,r):
  s.r=r
  s.pp=0
  s.fu=0
 def sa(s,c):
  r,g,b=c
  s.r.c1(r,g,b);s.r.c2(r,g,b);s.r.c3(r,g,b);s.r.c4(r,g,b)
 def sl(s,c):
  r,g,b=c
  s.r.c1(r,g,b);s.r.c2(r,g,b)
 def sr(s,c):
  r,g,b=c
  s.r.c4(r,g,b);s.r.c3(r,g,b)
 def fc(s):s.fu=utime.ticks_ms()+150
 def up(s,wo,oa,tn=None):
  now=utime.ticks_ms()
  if utime.ticks_diff(s.fu,now)>0:
   s.sa(WH)
   return
  if oa:
   s.sa(RD)
   return
  if not wo:
   s.pp=(s.pp+1)%40
   br=abs(20-s.pp)*12
   s.sa((0,br,0))
   return
  if tn=="left":
   s.sl(AM);s.sr(OF)
  elif tn=="right":
   s.sr(AM);s.sl(OF)
  else:
   s.sa(BL)
