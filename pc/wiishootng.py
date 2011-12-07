#!/usr/bin/python
import pygame
import random

pygame.init()
gunshot = pygame.mixer.Sound('84254__tito-lahaye__45-smith-wesson.wav')
hit = pygame.mixer.Sound('32304__acclivity__shipsbell.wav')
startnoise = pygame.mixer.Sound('98296__robinhood76__01788-cartoon-iha.wav')
connectnoise = pygame.mixer.Sound('2324__synapse__trumpetloop02.aif')
congratsnoise = pygame.mixer.Sound('20784__wanna73__crowd-cheering-football-01.wav')
missednoise = pygame.mixer.Sound('9891__the-justin__sigh.wav')

xmargin = 50
ymargin = 70
#gunshot = pyglet.resource.media('84254__tito-lahaye__45-smith-wesson.wav', streaming=False)

bullet_time = 0.25
shake_time = 0.1
maxshots = 6
maxpoints = 4
maxtime = 60
skillramp = 4


import cwiid

from time import sleep

from array import array
import socket
import time

from firmata import * 


LEDpins = [13, 2]

MOTORpins = [11, 12]


a = Arduino('/dev/ttyUSB0')

targets = len(LEDpins)

for v in LEDpins:
    a.pin_mode(v, firmata.OUTPUT)
    a.digital_write(v, firmata.LOW)

for v in MOTORpins:
    a.pin_mode(v, firmata.OUTPUT)
    a.digital_write(v, firmata.LOW)


print 'Put Wiimote in discoverable mode now (press 1+2)...'
connectnoise.play()

w = cwiid.Wiimote()

# Request nunchuk to be active.

w.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR | cwiid.RPT_EXT | cwiid.RPT_ACC

# Turn on LED1 so we know we're connected.


print 'Connected Thanks...'


while 1:
    w.led = 0
    points = 0
    shots = 0
    skill = 1
    
    lasttarget = targets
    target = 0
    targetmaxtime = 10
    targetstarttime = 0
    changetarget = 1
    
    #a.digital_write(LEDpins[lasttarget], firmata.LOW)
    #a.digital_write(LEDpins[target], firmata.HIGH)
    
    
    # If nunchuk is active then dump the values.
    #if not w.state.has_key('nunchuk'):
    #  print "No nunchuk."
    #  exit( 0 )
    
    print "Press A on WiiMote to Start"
    
    while not w.state['buttons']:
        pass
    
    startnoise.play()
    
    starttime = time.clock()
    targetstarttime = starttime
    
    while (shots < maxshots) & (points < maxpoints) & ((starttime + maxtime) > time.clock()):
      
        if (targetstarttime + targetmaxtime) <= time.clock():
            missednoise.play()
            changetarget = 1
            
        if changetarget:    
            targetstarttime = time.clock()
            changetarget = 0
            lasttarget = target
            while lasttarget == target:
                target = random.randint(0, targets - 1)
            
            a.digital_write(LEDpins[lasttarget], firmata.LOW)
            a.digital_write(LEDpins[target], firmata.HIGH)
            
        
        
        if w.state['nunchuk']['buttons']:
            gunshot.play()
    
            if w.state.has_key('ir_src'):            
                if w.state['ir_src'][0] is not None:
                    if w.state['ir_src'][0].has_key('pos'):
                        ir_pos = w.state['ir_src'][0]['pos']
                        
                        x = ir_pos[0]
                        y = ir_pos[1]
                            
                        xdiff = abs(x - 512)
                        ydiff = abs(y - (768/2))
                        
                        #print 'xdiff {0} ydiff {1}'.format(xdiff, ydiff)
                        
                                
                        if xdiff < (xmargin * skill):
                            if ydiff < (ymargin * skill):
                                sleep( bullet_time )       
                                hit.play()
                                points = points + 1
                                
                                a.digital_write(MOTORpins[target], firmata.HIGH)
                                sleep( shake_time )    
                                a.digital_write(MOTORpins[target], firmata.LOW)
                                changetarget = 1
            
                                
                                if points == 1:
                                    w.led = cwiid.LED1_ON
                                if points == 2:
                                    w.led = cwiid.LED2_ON
                                if points == 3:
                                    w.led = cwiid.LED3_ON
                                if points == 4:
                                    w.led = cwiid.LED4_ON
                                    
                                    
                                
                
            shots = shots + 1
            #print 'Shot {0}'.format(shots)
            
            if (points == 0) & (shots > (maxshots - skillramp)):
                skill = 1 + (1 * (shots - (maxshots - skillramp)))
                print 'skill changed to {0}'.format(skill)
            sleep( 1 )
    
    print 'Scored {0} out of {1} shots at skill {2}'.format(points, shots, skill)
    a.digital_write(LEDpins[target], firmata.LOW)
    
    if (points > 0):          
        congratsnoise.play()
        sleep( 4 )
        congratsnoise.fadeout(1000)
    else:
        missednoise.play()
        sleep( 4 ) 
    
    connectnoise.play()
