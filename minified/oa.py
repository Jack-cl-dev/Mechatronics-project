from microbit import *
import utime
from tn import Tn
from dv import Dv
SD=90
SM=350
SB=3
RM=2000
MX=8
MT=20000
class Oa(Tn,Dv):
 def __init__(s,r,sd=10,ls=None,vb=True):
  s.r=r
  s.sd=sd
  s.ls=ls
  s.vb=vb
  s.dl=0
 def lg(s,m):
  if s.vb:print("[a]"+m)
 def sp(s):s.r.m1(0,0);s.r.m2(0,0)
 def ot(s):return utime.ticks_diff(s.dl,utime.ticks_ms())<=0
 def cd(s):
  s.tu(SD)
  utime.sleep_ms(150)
  if s.ic(s.pb()):return 1
  s.tu(-2*SD)
  utime.sleep_ms(150)
  if s.ic(s.pb()):return -1
  return None
 def ao(s):
  s.lg("avoid")
  s.sp()
  s.dl=utime.ticks_add(utime.ticks_ms(),MT)
  sg=s.cd()
  if sg is None:
   s.lg("boxed")
   s.tu(-SD)
   s.df(RM,True)
   s.sp()
   s.lg("done:reversed")
   return "reversed"
  s.lg("side"+("r" if sg>0 else "l"))
  dt=sg*SD
  st=0
  while st<MX and not s.ot():
   oc=s.df(SM,True)
   if oc=="line":
    s.sp()
    s.lg("done:line")
    return "line"
   if oc=="blocked":
    s.lg("blk"+str(st))
    break
   st+=1
   if st%SB!=0:continue
   s.tu(-dt)
   utime.sleep_ms(150)
   if s.ic(s.pb()):
    s.lg("clr"+str(st))
    oc=s.df(RM,True)
    s.sp()
    rs="line" if oc=="line" else "clear"
    s.lg("done:"+rs)
    return rs
   s.tu(dt)
  s.lg("stuck"+str(st))
  s.tu(-dt)
  s.sp()
  return "stuck"
