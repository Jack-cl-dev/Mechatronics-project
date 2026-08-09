from microbit import *
from mq import Mq
from sw import Sw
from ob import Od
from hd import Hd
from rc import Sc
from lt import Lt
import utime
rb=Mq()
sw=Sw()
hd=Hd(rb)
lt=Lt(rb)
def l1():return 0 if rb.n1() else 1
def l2():return 0 if rb.n2() else 1
def ls():return l1()==1 or l2()==1
dt=Od(rb,10,ls)
sc=Sc()
F0=0
B0=1
BS=85
CO=70
CI=60
PO=80
PI=30
SP=85
DL=5
T1=100
T2=1200
DE=200
GV=1000
ld=1
lo=None
pw=False
tm=utime.ticks_ms()
def dr(v1,d1,v2,d2):
 m=sc.mp
 rb.m1(min(255,int(v1*m)),d1)
 rb.m2(min(255,int(v2*m)),d2)
while True:
 sc.up()
 mr=sw.st
 wo=sw.up(mr,dt.iz())
 hd.up()
 if wo!=pw:
  lt.fc()
  pw=wo
 if not wo:
  dr(0,F0,0,F0)
  lo=None
  lt.up(wo,False)
  utime.sleep_ms(40)
  continue
 if dt.ck():
  lt.up(wo,True)
  dt.ra()
  continue
 lf=l1()
 rt=l2()
 tn=None
 if lf==1 and rt==1:
  dr(BS,F0,BS,F0)
  lo=None
 elif lf==1 and rt==0:
  ld=1
  tn='left'
  dr(CI,F0,CO,F0)
  lo=None
 elif lf==0 and rt==1:
  ld=-1
  tn='right'
  dr(CO,F0,CI,F0)
  lo=None
 else:
  if lo is None:lo=utime.ticks_ms()
  lw=utime.ticks_diff(utime.ticks_ms(),lo)
  if lw<T1:
   if ld>=0:
    tn='left'
    dr(PI,F0,PO,F0)
   else:
    tn='right'
    dr(PO,F0,PI,F0)
  elif lw<T2:
   if ld>=0:
    tn='left'
    dr(PI,B0,PO,F0)
   else:
    tn='right'
    dr(PO,F0,PI,B0)
  elif ld>=0:
   tn='left'
   dr(SP,B0,SP,F0)
  else:
   tn='right'
   dr(SP,F0,SP,B0)
 lt.up(wo,False,tn)
 now=utime.ticks_ms()
 if utime.ticks_diff(now,tm)>=DE:
  tm=now
  mg=accelerometer.get_strength()
  mo=abs(mg-GV)
  rw=mo//200
  if rw>5:rw=5
  pt=[]
  for i in range(5):
   if i>=5-rw:pt.append('99999')
   else:pt.append('00000')
  display.show(Image(':'.join(pt)))
 utime.sleep_ms(DL)
