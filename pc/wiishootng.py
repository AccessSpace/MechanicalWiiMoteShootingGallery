#!/usr/bin/python
import pygame
import random

pygame.init()
gunshot = pygame.mixer.Sound('84254__tito-lahaye__45-smith-wesson.wav')
hit = pygame.mixer.Sound('32304__acclivity__shipsbell.wav')
startnoise = pygame.mixer.Sound('98296__robinhood76__01788-cartoon-iha.wav')
connectnoise = pygame.mixer.Sound('2324__synapse__trumpetloop02.aif')
waitingnoise = pygame.mixer.Sound('music/03-Adrian Charkman-God Rest Ye Merry Gentlemen.wav')
congratsnoise = pygame.mixer.Sound('20784__wanna73__crowd-cheering-football-01.wav')
missednoise = pygame.mixer.Sound('9891__the-justin__sigh.wav')
gameover = pygame.mixer.Sound('72866__corsica-s__game-over.wav')



xmargin = 50
ymargin = 90
#gunshot = pyglet.resource.media('84254__tito-lahaye__45-smith-wesson.wav', streaming=False)

bullet_time = 0.25
shake_time = 0.2
maxshots = 10
maxpoints = 10
maxtime = 60
skillramp = 6


import cwiid

from time import sleep

from array import array
import socket
import time

from firmata import * 


MOTORpins = [2, 4, 6]

LEDpins = [3, 5, 7]

TargetNoises = [
                  pygame.mixer.Sound('111350__noisecollector__jinglebells2.wav'),
                  
                  pygame.mixer.Sound('67675__sinatra314__turkeygobble1.wav'),
                  pygame.mixer.Sound('110697__jaqvaar__santahohoho2.wav')]


ScoreNoises = [
                  pygame.mixer.Sound('numbers/66696__mad-monkey__000.wav'),
                  pygame.mixer.Sound('numbers/66697__mad-monkey__001.wav'),
                  pygame.mixer.Sound('numbers/66698__mad-monkey__002.wav'),
                  pygame.mixer.Sound('numbers/66699__mad-monkey__003.wav'),
                  pygame.mixer.Sound('numbers/66700__mad-monkey__004.wav'),
                  pygame.mixer.Sound('numbers/66701__mad-monkey__005.wav'),
                  pygame.mixer.Sound('numbers/66702__mad-monkey__006.wav'),
                  pygame.mixer.Sound('numbers/66703__mad-monkey__007.wav'),
                  pygame.mixer.Sound('numbers/66704__mad-monkey__008.wav'),
                  pygame.mixer.Sound('numbers/66705__mad-monkey__009.wav'),
                  pygame.mixer.Sound('numbers/66706__mad-monkey__010.wav')]


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
    
    #lasttarget = targets
    target = targets - 1
    targetmaxtime = 10
    targetstarttime = 0
    changetarget = 1
    
    #a.digital_write(LEDpins[lasttarget], firmata.LOW)
    #a.digital_write(LEDpins[target], firmata.HIGH)
    
    
    # If nunchuk is active then dump the values.
    #if not w.state.has_key('nunchuk'):
    #  print "No nunchuk."
    #  exit( 0 )
    
    connectnoise.stop()
    
    print "Press A on WiiMote to Start"
    waitingnoise.play(-1)
    
    
    lightstate = 1
    
    while not w.state['buttons']:
        if lightstate == 1:
            w.led = cwiid.LED1_ON
        if lightstate == 2:
            w.led = cwiid.LED2_ON
        if lightstate == 3:
            w.led = cwiid.LED3_ON
        if lightstate == 4:
            w.led = cwiid.LED4_ON
        
        lightstate = lightstate + 1
        if lightstate == 5:
            lightstate = 1
          
        sleep(0.1)
            
    
    waitingnoise.stop()
    startnoise.play()
    sleep(1)
    
    starttime = time.clock()
    targetstarttime = starttime
    
    while (shots < maxshots) & (points < maxpoints) & ((starttime + maxtime) > time.clock()):
      
        if (targetstarttime + targetmaxtime) <= time.clock():
            #missednoise.play()
            changetarget = 1
            
        if changetarget:    
            targetstarttime = time.clock()
            changetarget = 0
            lasttarget = target
            
            while lasttarget == target:
                target = random.randint(0, targets - 1)
            
            a.digital_write(LEDpins[lasttarget], firmata.LOW)
            a.digital_write(LEDpins[target], firmata.HIGH)
            TargetNoises[target].play()
            
        
        if w.state['nunchuk']['buttons']:
            w.rumble = 1
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
                                w.rumble = 0
                                a.digital_write(MOTORpins[target], firmata.HIGH)
                                hit.play()
                                points = points + 1
                                sleep( shake_time )    
                                a.digital_write(MOTORpins[target], firmata.LOW)
                                changetarget = 1
                
            shots = shots + 1
            #print 'Shot {0}'.format(shots)
            
            if (points == 0) & (shots > (maxshots - skillramp)):
                skill = 1 + (1 * (shots - (maxshots - skillramp)))
                print 'skill changed to {0}'.format(skill)
            
            sleep( 0.2 )
            w.rumble = 0
    
    print 'Scored {0} out of {1} shots at skill {2}'.format(points, shots, skill)
    a.digital_write(LEDpins[target], firmata.LOW)
    
    
    
    gameover.play()
    sleep( 2 )
    
    ScoreNoises[points].play()
    sleep( 2 )
    
    if (points > 0):          
        congratsnoise.play()
        sleep( 2 )
        congratsnoise.fadeout(1000)
    else:
        missednoise.play()
        sleep( 2 ) 
        missednoise.fadeout(1000)
    
    #connectnoise.play()
