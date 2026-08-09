import radio
SV={1:0.7,2:1.0,3:1.3}
N1=1
X1=3
class Sc:
 def __init__(s,g=7,lv=2):
  radio.config(group=g)
  radio.on()
  s.lv=lv
 def up(s):
  ic=radio.receive()
  if ic=='+':
   s.lv=N1 if s.lv>=X1 else s.lv+1
  elif ic=='-':
   s.lv=X1 if s.lv<=N1 else s.lv-1
  return s.lv
 @property
 def mp(s):return SV[s.lv]
