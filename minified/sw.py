from microbit import *
import utime
CM=70
ML=200
MM=60
MT=1500
QT=300
BR=0.05
class Sw:
 def __init__(s):
  s.st=False
  s.lg=0
  s.am=True
  s.qs=None
  s.bl=microphone.sound_level()
 def up(s,mr=False,ig=False):
  now=utime.ticks_ms()
  if ig:
   s.qs=None
   return s.st
  sd=microphone.sound_level()
  th=max(ML,s.bl+CM)
  if mr:th+=MM
  if s.am:
   if sd>th and utime.ticks_diff(now,s.lg)>MT:
    s.st=not s.st
    s.lg=now
    s.am=False
    s.qs=None
   elif not mr:
    s.bl+=(sd-s.bl)*BR
  else:
   if utime.ticks_diff(now,s.lg)<MT:
    s.qs=None
   elif sd<th:
    if s.qs is None:
     s.qs=now
    elif utime.ticks_diff(now,s.qs)>=QT:
     s.am=True
     s.qs=None
   else:
    s.qs=None
  return s.st
