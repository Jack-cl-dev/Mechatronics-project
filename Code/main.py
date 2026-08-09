from microbit import *
from maqueen import Maqueen
from sound_detect import SoundSwitch
from obstacle_detect import ObstacleDetector
from headlights import Headlights
from radio_recieve import SpeedControl
from statuslights import StatusLights
import utime
r = Maqueen()
ss = SoundSwitch()
hl = Headlights(r)
lt = StatusLights(r)
def ll(): return 0 if r.line_left() else 1
def lr(): return 0 if r.line_right() else 1
def seen(): return ll() == 1 or lr() == 1
det = ObstacleDetector(r, stop_distance=10, line_seen=seen)
sc = SpeedControl()
F = 0
B = 1
BASE = 85
CO = 70
CI = 60
PO = 80
PI = 30
SW = 85
LOOP = 5
S1 = 100
S2 = 1200
side = 1
lost = None
pw = False
ldm = utime.ticks_ms()
DE = 200
G = 1000
def drive(ls, ld, rs, rd):
    m = sc.multiplier
    r.motor_left(min(255, int(ls * m)), ld)
    r.motor_right(min(255, int(rs * m)), rd)
while True:
    sc.update()
    mr = ss.state
    w = ss.update(mr, det.is_noisy())
    hl.update()
    if w != pw:
        lt.flash_clap()
        pw = w
    if not w:
        drive(0, F, 0, F)
        lost = None
        lt.update(w, False)
        utime.sleep_ms(40)
        continue
    if det.check():
        lt.update(w, True)
        det.react()
        continue
    L = ll()
    R = lr()
    turn = None
    if L == 1 and R == 1:
        drive(BASE, F, BASE, F)
        lost = None
    elif L == 1 and R == 0:
        side = 1
        turn = 'left'
        drive(CI, F, CO, F)
        lost = None
    elif L == 0 and R == 1:
        side = -1
        turn = 'right'
        drive(CO, F, CI, F)
        lost = None
    else:
        if lost is None:
            lost = utime.ticks_ms()
        lf = utime.ticks_diff(utime.ticks_ms(), lost)
        if lf < S1:
            if side >= 0:
                turn = 'left'
                drive(PI, F, PO, F)
            else:
                turn = 'right'
                drive(PO, F, PI, F)
        elif lf < S2:
            if side >= 0:
                turn = 'left'
                drive(PI, B, PO, F)
            else:
                turn = 'right'
                drive(PO, F, PI, B)
        elif side >= 0:
            turn = 'left'
            drive(SW, B, SW, F)
        else:
            turn = 'right'
            drive(SW, F, SW, B)
    lt.update(w, False, turn)
    now = utime.ticks_ms()
    if utime.ticks_diff(now, ldm) >= DE:
        ldm = now
        mag = accelerometer.get_strength()
        mo = abs(mag - G)
        rows = mo // 200
        if rows > 5:
            rows = 5
        parts = []
        for i in range(5):
            parts.append('99999' if i >= 5 - rows else '00000')
        display.show(Image(':'.join(parts)))
    utime.sleep_ms(LOOP)
