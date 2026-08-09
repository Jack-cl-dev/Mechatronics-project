import utime
CS=80
F0=0
SC=25
PS=3
PM=20
class Dv:
 def pb(s):
  ne=-1
  for _ in range(PS):
   ds=s.r.us()
   if ds>0 and (ne<0 or ds<ne):ne=ds
   utime.sleep_ms(PM)
  return ne
 @staticmethod
 def ic(ds):return ds<0 or ds>=SC
 def df(s,du,so=False):
  s.r.m1(CS,F0);s.r.m2(CS,F0)
  st=utime.ticks_ms()
  while utime.ticks_diff(utime.ticks_ms(),st)<du:
   ds=s.r.us()
   if 0<ds<=s.sd:
    s.sp()
    return "blocked"
   if so and s.ls is not None and s.ls():
    s.sp()
    return "line"
   utime.sleep_ms(PM)
  s.sp()
  return "done"
