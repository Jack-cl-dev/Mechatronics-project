from microbit import *
import neopixel
import utime
class Mq:
 def __init__(s):
  i2c.init()
  s.np=neopixel.NeoPixel(pin15,4)
  pin1.write_digital(0)
 def k1(s,v):pin8.write_digital(v)
 def k2(s,v):pin12.write_digital(v)
 def c1(s,r,g,b):s.np[0]=(r,g,b);s.np.show()
 def c2(s,r,g,b):s.np[1]=(r,g,b);s.np.show()
 def c3(s,r,g,b):s.np[2]=(r,g,b);s.np.show()
 def c4(s,r,g,b):s.np[3]=(r,g,b);s.np.show()
 def iw(s,b,at=6,rd=25):
  le=None
  for _ in range(at):
   try:
    i2c.write(0x10,b)
    return
   except OSError as e:
    le=e
    utime.sleep_ms(rd)
  raise le
 def m1(s,sp=0,dr=0):
  b=bytearray(3);b[0]=0;b[1]=dr;b[2]=sp;s.iw(b)
 def m2(s,sp=0,dr=0):
  b=bytearray(3);b[0]=2;b[1]=dr;b[2]=sp;s.iw(b)
 def n1(s):return 1 if pin13.read_digital() else 0
 def n2(s):return 1 if pin14.read_digital() else 0
 def s1(s,ag=0):
  b=bytearray(2);b[0]=0x14;b[1]=ag;s.iw(b)
 def s2(s,ag=0):
  b=bytearray(2);b[0]=0x15;b[1]=ag;s.iw(b)
 _lg=0
 _ld=-1
 def us(s):
  MW=5000
  RG=60000
  sl=utime.ticks_diff(utime.ticks_us(),s._lg)
  if sl<RG:return s._ld
  d1=utime.ticks_us()
  while pin2.read_digital()==1:
   if utime.ticks_diff(utime.ticks_us(),d1)>MW:break
  pin1.write_digital(1)
  utime.sleep_us(10)
  pin1.write_digital(0)
  s._lg=utime.ticks_us()
  st=utime.ticks_us()
  while pin2.read_digital()==0:
   if utime.ticks_diff(utime.ticks_us(),st)>MW:
    s._ld=-1
    return -1
  pb=utime.ticks_us()
  while pin2.read_digital()==1:
   if utime.ticks_diff(utime.ticks_us(),pb)>MW:
    s._ld=-2
    return -2
  pe=utime.ticks_us()
  d=int(utime.ticks_diff(pe,pb)/58)
  s._ld=d
  return d
