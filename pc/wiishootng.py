#!/usr/bin/python
import pygame
import random
import sys
import cwiid
from time import sleep
import datetime
from array import array
import socket
import time
from firmata import * 

#theme        = 'christmas'
theme        = 'steampunk'

xmargin      = 50
ymargin      = 90
bullet_delay  = datetime.timedelta(0, 0.5)
shake_delay   = datetime.timedelta(0, 2)
effect_delay   = datetime.timedelta(0, 0.25)
recoil_delay  = datetime.timedelta(0, 0.5)
ready_delay   = datetime.timedelta(0, 1)
changetarget_delay = datetime.timedelta(0, 4)

maxshots     = 10
maxpoints    = 10
maxtime      = datetime.timedelta(0, 120)
skillramp    = 6

MOTORpins    = [2, 4, 6]
LEDpins      = [3, 5, 7]

arduino = Arduino('/dev/ttyUSB0')
#arduino = Arduino('/dev/ttyACM0')

pygame.init()

congratsnoise= pygame.mixer.Sound('themes/base/20784__wanna73__crowd-cheering-football-01.wav')
missednoise  = pygame.mixer.Sound('themes/base/9891__the-justin__sigh.wav')
gameover     = pygame.mixer.Sound('themes/base/72866__corsica-s__game-over.wav')


ScoreNoises  = [pygame.mixer.Sound('themes/base/numbers/66696__mad-monkey__000.wav'),
                pygame.mixer.Sound('themes/base/numbers/66697__mad-monkey__001.wav'),
                pygame.mixer.Sound('themes/base/numbers/66698__mad-monkey__002.wav'),
                pygame.mixer.Sound('themes/base/numbers/66699__mad-monkey__003.wav'),
                pygame.mixer.Sound('themes/base/numbers/66700__mad-monkey__004.wav'),
                pygame.mixer.Sound('themes/base/numbers/66701__mad-monkey__005.wav'),
                pygame.mixer.Sound('themes/base/numbers/66702__mad-monkey__006.wav'),
                pygame.mixer.Sound('themes/base/numbers/66703__mad-monkey__007.wav'),
                pygame.mixer.Sound('themes/base/numbers/66704__mad-monkey__008.wav'),
                pygame.mixer.Sound('themes/base/numbers/66705__mad-monkey__009.wav'),
                pygame.mixer.Sound('themes/base/numbers/66706__mad-monkey__010.wav')]



if(theme == 'christmas'):
    gunshot      = pygame.mixer.Sound('themes/christmas/sounds/84254__tito-lahaye__45-smith-wesson.wav')
    hit          = pygame.mixer.Sound('themes/christmas/sounds/32304__acclivity__shipsbell.wav')
    startnoise   = pygame.mixer.Sound('themes/christmas/sounds/98296__robinhood76__01788-cartoon-iha.wav')
    connectnoise = pygame.mixer.Sound('themes/christmas/sounds/2324__synapse__trumpetloop02.aif')
    waitingnoise = pygame.mixer.Sound('themes/christmas/music/03-Adrian Charkman-God Rest Ye Merry Gentlemen.wav')
    
    TargetNoises = [pygame.mixer.Sound('themes/christmas/sounds/111350__noisecollector__jinglebells2.wav'),                  
                    pygame.mixer.Sound('themes/christmas/sounds/67675__sinatra314__turkeygobble1.wav'),
                    pygame.mixer.Sound('themes/christmas/sounds/110697__jaqvaar__santahohoho2.wav')]
    
    HitNoises = [pygame.mixer.Sound('themes/christmas/sounds/32304__acclivity__shipsbell.wav'),                  
                    pygame.mixer.Sound('themes/christmas/sounds/32304__acclivity__shipsbell.wav'),
                    pygame.mixer.Sound('themes/christmas/sounds/32304__acclivity__shipsbell.wav')]
    

if(theme == 'steampunk'):
    gunshot      = pygame.mixer.Sound('themes/steampunk/sounds/18389__inferno__medlas.wav')
    hit          = pygame.mixer.Sound('themes/steampunk/sounds/32304__acclivity__shipsbell.wav')
    startnoise   = pygame.mixer.Sound('themes/steampunk/sounds/on_your_marksP.wav')
    connectnoise = pygame.mixer.Sound('themes/steampunk/sounds/147795__setuniman__funfair-mood-0i-23mi2.wav')
    #waitingnoise = pygame.mixer.Sound('themes/steampunk/sounds/147795__setuniman__funfair-mood-0i-23mi2.wav')
    
    waitingnoise = pygame.mixer.Sound('themes/steampunk/music/Celestial_Aeon_Project-Alchemist.ogg')
    
    TargetNoises = [pygame.mixer.Sound('themes/steampunk/sounds/airship1.wav'),                  
                    pygame.mixer.Sound('themes/steampunk/sounds/moustach_01P.wav'),
                    pygame.mixer.Sound('themes/steampunk/sounds/french_01P.wav')]
    
    HitNoises = [pygame.mixer.Sound('themes/steampunk/sounds/65474__robinhood76__00682-farting-flying-baloon-3.wav'),                  
                    pygame.mixer.Sound('themes/steampunk/sounds/moustach_02.0P.wav'),
                    pygame.mixer.Sound('themes/steampunk/sounds/french_02P.wav')]
    


targets = len(LEDpins)

for v in LEDpins:
    arduino.pin_mode(v, firmata.OUTPUT)
for v in MOTORpins:
    arduino.pin_mode(v, firmata.OUTPUT)


print 'Put Wiimote in discoverable mode now (press 1+2)...'
connectnoise.play()

bWiiFound = 0
while bWiiFound == 0:
    try:
        w = cwiid.Wiimote()
        bWiiFound = 1
    except RuntimeError:
        print 'Keep Trying'
        
# Request nunchuk to be active.

w.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR | cwiid.RPT_EXT | cwiid.RPT_ACC

# Turn on LED1 so we know we're connected.

print 'Connected Thanks...'
waitingnoise.set_volume(0.6)
plays = 0

while 1: #infintite games

    w.led  = 0
    points = 0
    shots  = 0
    skill  = 1
    
    target = targets - 1
    targetmaxtime = datetime.timedelta(0, 10)
    
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
    
    
    starttime = datetime.datetime.now()
    targetstarttime = starttime
    currenttime = datetime.datetime.now()
    aEvents = []
    lasttarget = 0
            
    target = 0
    
    
    gamestate = ""
    aEvents.append({"name":'changetarget', "time":currenttime + changetarget_delay})
    triggerstate = 0
    
    while gamestate != "end":
        currenttime = datetime.datetime.now()
        
        if triggerstate == 1  and not (w.state['nunchuk']['buttons']):
            triggerstate = 0
            
        #print "loopstart gamestate", gamestate  
        if (currenttime > (starttime + maxtime)):
            gamestate = "end"
            continue
        
        if currenttime > (targetstarttime + targetmaxtime):
            #missednoise.play()
            aEvents.append({"name":'changetarget', "time":currenttime})
        
        
        aNewEvents = []
        while len(aEvents) > 0:
            oEvent = aEvents.pop()
            if currenttime >= oEvent["time"]:
                #print oEvent, "time", oEvent["time"], "current", currenttime
                
                if oEvent["name"] == "hit":
                    hit.play()
                    arduino.digital_write(MOTORpins[target], firmata.HIGH)
                    #print "pin high", MOTORpins[target]
                    points = points + 1
                    aNewEvents.append({"name":'effect', "time":currenttime + effect_delay})
                    aNewEvents.append({"name":'hit_end', "time":currenttime + shake_delay})
                    
                if oEvent["name"] == "effect":
                    HitNoises[target].play()
                    aNewEvents.append({"name":'changetarget', "time":currenttime + changetarget_delay})
                
                
                if oEvent["name"] == "hit_end":
                    arduino.digital_write(MOTORpins[target], firmata.LOW)
                    #print "pin low", MOTORpins[target]
                    
                if oEvent["name"] == "recoilend":
                    w.rumble = 0
                    
                if oEvent["name"] == "gunready":
                    gamestate = "aim"
                    
                if oEvent["name"] == "changetarget":
                    targetstarttime = currenttime
                    
                    while lasttarget == target:
                        target = random.randint(0, targets - 1)
                    
                    #print 'new target', target
                    
                    for v in LEDpins:
                        arduino.digital_write(v, firmata.LOW)
                    for v in MOTORpins:
                        arduino.digital_write(v, firmata.LOW)

                    arduino.digital_write(LEDpins[target], firmata.HIGH)
                    #print 'pin high', LEDpins[target]
                                
                    TargetNoises[target].play()
                    lasttarget = target
                    gamestate = "aim"
                    continue
            
            else:
                aNewEvents.append(oEvent)
        aEvents = aNewEvents
        
        if len(aEvents) > 0:
            continue
        
        if shots >= maxshots:
            gamestate = "end"
            continue
        
        if gamestate == "aim"  and triggerstate == 0  and  w.state['nunchuk']['buttons']:
            w.rumble = 1
            aEvents.append({"name":'recoilend', "time":currenttime + recoil_delay})
            aEvents.append({"name":'gunready',  "time":currenttime + ready_delay})
            
            gunshot.play()
            triggerstate = 1
            
            if w.state.has_key('ir_src'):            
                if w.state['ir_src'][0] is not None:
                    if w.state['ir_src'][0].has_key('pos'):
                        ir_pos = w.state['ir_src'][0]['pos']
                        
                        x = ir_pos[0]
                        y = ir_pos[1]
                            
                        xdiff = abs(x - 512)
                        ydiff = abs(y - (768/2))
                        
                        #print 'xdiff {0} ydiff {1}'.format(xdiff, ydiff)
                        #recordshot(xdiff, ydiff)            
                                
                        if xdiff < (xmargin * skill):
                            if ydiff < (ymargin * skill):
                                aEvents.append({"name":'hit', "time":currenttime + bullet_delay})
                                
                                
            shots = shots + 1
            #print 'Shot {0}'.format(shots)
            
            if (points == 0)  and  (shots > (maxshots - skillramp)):
                skill = 1 + (1 * (shots - (maxshots - skillramp)))
                #print 'skill changed to {0}'.format(skill)
            
    
    w.rumble = 0
    plays = plays + 1
    print "Play", plays, 'Scored {0} out of {1} shots at skill {2}'.format(points, shots, skill)
    arduino.digital_write(LEDpins[target], firmata.LOW)
    #print "pin low", LEDpins[target]
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
