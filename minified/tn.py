import utime
TS=70
F0=0
B0=1
M9=350
PM=20
class Tn:
 def sn(s,sg):
  if sg>=0:
   s.r.m1(TS,F0);s.r.m2(TS,B0)
  else:
   s.r.m1(TS,B0);s.r.m2(TS,F0)
 def tu(s,dg):
  if not dg:return
  du=int(abs(dg)*M9/90)
  sg=1 if dg>0 else -1
  s.lg("tn{}({}ms)".format(int(dg),du))
  s.sn(sg)
  st=utime.ticks_ms()
  while utime.ticks_diff(utime.ticks_ms(),st)<du:
   utime.sleep_ms(PM)
  s.sp()
