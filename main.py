#!/usr/bin/env python

import pyglet
from pyglet.image.codecs.pil import PILImageDecoder

import time

import subprocess

from itertools import cycle, islice, combinations

from random import shuffle 

from sys import platform as _platform

import os

if _platform == "win32":
    import winsound

backend = "Output"
#backend = "MIDI"
#backend = "Beep"

#arpeggiato = False
arpeggiato = True

if backend == "MIDI":
    import rtmidi
    from rtmidi.midiutil import open_midiport
    from rtmidi.midiconstants import *


class PlayGround:

    def __init__(self, batch, order_level, notes, track, rows=12, columns=8, elem_width=64, elem_height=64, origin_x=64, origin_y=64):
        self.rows = rows
        self.columns = columns
        self.state = [-1 for _ in range(rows*columns)]
        self.last_state = [-1 for _ in range(rows*columns)]
        self.elem_width = elem_width
        self.elem_height = elem_height
        self.origin = (origin_x, origin_y)
        self.batch = batch
        self.order_level = order_level
        self.background_image = pyglet.image.load('background.png', decoder=PILImageDecoder())
        self.background_sprite = pyglet.sprite.Sprite(self.background_image, batch=self.batch, group=order_level[0])
        self.background_sprite.set_position(origin_x-64, origin_y-64)
        self.notes_images = notes
        self.grid_sprites = [pyglet.sprite.Sprite(self.notes_images[8], batch=self.batch, group=order_level[1]) for i in range(rows*columns)]
        for index,elem in enumerate(self.grid_sprites):
            pos = ((index % self.columns) * self.elem_width + self.origin[0], (index // self.columns) * self.elem_height + self.origin[1])
            elem.set_position(*pos)

        #self.sound_output = sound_output

        self.track = track

        pyglet.clock.schedule_interval(self.display, 1/60)
    
    def gravity(self):
        #print("INTO GRAVITY")
        #self.last_state = self.state
        gravity_blocs = []
        for index,note in enumerate(self.state):
            #print("Test {} {}".format(self.index2human(index), note))
            if index >= self.columns and note != -1 and self.state[index-self.columns] == -1:
                gravity_blocs.append((index, note))
                self.state[index] = -1
                
                #print(self.state)
                #print("Gravity {} {}".format(self.index2human(index), note))

                #blank = self.human2index(self.searchFirstBlank(self.index2human(index)[0]))
                #print("Blank = {} {}".format(self.index2human(blank), self.state[blank]))
                #self.state[blank] = self.state[index]
                #self.state[index] = -1
                #self.display(0)
                #time.sleep(1)
        
        gravity_blocs_elem = []
        for index, note in gravity_blocs:
            gravity_blocs_elem.append(FloatElemAutoDispense(self.batch, self.order_level, index, self.notes_images, self, note))
            #print("Test {} {}".format(self.index2human(index), note))
        return gravity_blocs_elem

    def check_chord(self, player):
        #print("INTO CHECK_CHORD")
        count = 0
        for index,note in enumerate(self.state):
            notes = []
            if note not in (-1, 7, 8):
                #note = self.toSemiTone(note)
                #print("Note testée : {} {}".format(note, self.index2human(index)))
                if index > self.columns and self.state[index-self.columns] not in (-1, 7, 8):
                    #test = abs(self.toSemiTone(self.state[index-self.columns])-note)
                    #print("DOWN = {}".format(test))
                    #if test in (3,4,7):
                    #f    notes.append(index-self.columns)
                    notes.append(index-self.columns)
                if index < self.rows*self.columns-self.columns and self.state[index+self.columns] not in (-1, 7, 8):
                    #test = abs(self.toSemiTone(self.state[index+self.columns])-note)
                    #print("UP = {}".format(test))
                    #if test in (3,4,7):
                    #    notes.append(index+self.columns)
                    notes.append(index+self.columns)
                if index % self.columns > 0 and self.state[index-1] not in (-1, 7, 8):
                    #test = abs(self.toSemiTone(self.state[index-1])-note)
                    #print("LEFT = {}", format(test))
                    #if test in (3,4,7):
                    #    notes.append(index-1)
                    notes.append(index-1)
                if index % self.columns < self.columns - 1 and self.state[index+1] not in (-1, 7, 8):
                    #test = abs(self.toSemiTone(self.state[index+1])-note)
                    #print("RIGHT = {}".format(test))
                    #if test in (3,4,7):
                    #    notes.append(index+1)
                    notes.append(index+1)
                #print(notes)
                
                combs = list(combinations(notes, 2))
                for comb in combs:
                    comb = list(comb)
                    comb.append(index)
                    comb_values = [self.state[x] for x in comb]
                    comb_values.sort()
                    comb_semitone = [self.toSemiTone(x) for x in comb_values]
                    if comb_semitone[1] - comb_semitone[0] in (3, 4) and comb_semitone[2] - comb_semitone[0] == 7:
                        count += 1
                        #self.sound_output.playChord([self.state[note] for note in notes], 1000)
                        self.track.addChord([self.state[note] for note in comb])
                        for i in comb:
                            self.state[i] = -1
                        new_score = player.score + 20**player.combo
                        text = "{} + 20 ^ {} = {}".format(player.score, player.combo, new_score)
                        player.score_label.text = text
                        player.score = new_score
                        break
        #print(count)
        return count

                
    def check(self, player = -1):
        #print(player)
        wait = False
        while True:
            if self.check_chord(player) > 0:
                #print("COMBO BREAKER !")
                player.combo += 1
                #time.sleep(2)
                #if player != -1:
                #    player.pause()
                gravity_blocs_elem = self.gravity()
                #if player != -1 and len(gravity_blocs_elem) > 0:
                #    pyglet.clock.schedule_interval(func=self.wait, interval=1/60, elems=gravity_blocs_elem)
                #else:
                #    player.unpause()
                if len(gravity_blocs_elem) > 0:
                    pyglet.clock.schedule_interval(func=self.wait, interval=1/60, elems=gravity_blocs_elem, player=player)
                    wait = True
                    break
            else:
                if player.score > 0 and player.damage > 0:
                    player.damage -= player.score
                    if player.damage < 0:
                        player.score = abs(player.damage)
                        player.damage = 0
                    else:
                        player.score = 0
                        player.combo = 1
                if player.score > 0:
                    player.attackEnnemies()
                #print("Player Damage = []".format(player.damage))
                if(player.damage > 0):
                    #print("LOL")
                    player.takeDamage()
                elif wait == False:
                    player.dispense()
                break

    def display(self, dt):
        for index,note in enumerate(self.state):
            self.grid_sprites[index].image = self.notes_images[note]

    def toSemiTone(self, note):
        table = {-7:48, -6:50, -5:52, -4:53, -3:55, -2:57, -1:59,
                0:60, 1:62, 2:64, 3:65, 4:67, 5:69, 6:71,
                7:72, 8:74, 9:76, 10:77, 11:79, 12:81, 13:83}
        return table[note]

    def toMidiMessage(self, note, on):
        if on:
            return [0x90, self.toSemiTone(note), 56]
        else:
            return [0x80, self.toSemiTone(note), 0]

    def searchFirstBlank(self, check_column):
        for i in range(self.rows):
            if self.state[self.human2index((check_column, i))] == -1:
                return (check_column, i)
        return (check_column, self.rows)

    def index2pos(self, index):
        return ((index % self.columns) * self.elem_width + self.origin[0], 
                (index // self.columns) * self.elem_height + self.origin[1])

    def index2human(self, index):
        return ((index % self.columns), (index // self.columns))
    
    def human2index(self, grid):
        return grid[0] + grid[1] * self.columns

    def sendMIDINote(self, note):
        self.midiout.send_message(self.toMidiMessage(note, True))
        pyglet.clock.schedule_once(lambda x: self.midiout.send_message(self.toMidiMessage(note, False)), 5.0)

    def wait(self, dt, elems, player, check=True):
        count = 0
        for elem in elems:
            if elem.exist == True:
                count += 1
        if count == 0:
            #player.unpause()
            pyglet.clock.unschedule(self.wait)
            #player.dispense()
            if check:
                self.check(player)
            else:
                player.dispense()


class FloatElem:

    def __init__(self, batch, order_level, start_pos, notes_images, playground, note=-1, shadow=False, speed=150.0):
        self.start_pos = start_pos
        self.batch = batch
        self.notes_images = notes_images
        self.order_level = order_level
        self.playground = playground
        self.note = note
        self.shadow = shadow
        self.pauseBool = False
        self.old_dy = 0
        self.exist = True
        self.speed = speed
        #self.dispense()
        self.sprite = 0
        self.shadow_sprite = 0
            
    def dispense(self):
        self.pos = self.index2pos(self.start_pos)
        self.grid_pos = self.start_pos
        self.human_pos = self.index2human(self.grid_pos)
        if self.sprite != 0:
            self.sprite.delete()
        self.sprite = pyglet.sprite.Sprite(self.notes_images[self.note], batch=self.batch, group=self.order_level[2])
        if self.pauseBool:
            self.sprite.dy = 0.0
        else:
            self.sprite.dy = self.speed
        self.sprite.set_position(*self.pos)
        pyglet.clock.schedule_interval(self.update, 1/60.0)

        if self.shadow:
            if self.shadow_sprite != 0:
                self.shadow_sprite.delete()
            self.shadow_sprite = pyglet.sprite.Sprite(self.notes_images[self.note], batch=self.batch, group=self.order_level[2])
            self.shadow_sprite.opacity = 128
            blank = self.playground.searchFirstBlank(self.index2human(self.start_pos)[0])
            self.shadow_sprite.set_position(*self.index2pos(self.human2index(blank)))

        self.exist = True


    def update(self, dt):
        self.sprite.y -= self.sprite.dy * dt
        self.grid_pos = int((self.sprite.x - self.playground.origin[0]) // self.playground.elem_height + ((self.sprite.y - self.playground.origin[1]) // self.playground.elem_width) * self.playground.columns)
        self.human_pos = self.index2human(self.grid_pos)
        
        if self.human_pos[1] < 0 or self.playground.state[self.grid_pos] != -1:
            if self.shadow:
                #self.shadow_sprite.delete()
                #self.shadow_sprite.image = self.notes_images[-8]
                self.shadow_sprite.visible = False
            pyglet.clock.unschedule(self.update)
            #self.sprite.delete()
            #self.sprite.image = self.notes_images[-8]
            self.sprite.visible = False
            self.playground.state[self.grid_pos + self.playground.columns] = self.note
            #self.playground.check()
            self.exist = False
            return True
        else:
            return False

    def move_right(self, dt):
        if self.pauseBool:
            return
        if self.human_pos[0] + 1 < self.playground.columns and self.playground.state[self.grid_pos+1] == -1 and self.sprite != None:
            #print(self.sprite)
            self.sprite.x += self.playground.elem_width
            self.grid_pos = int((self.sprite.x - self.playground.origin[0]) // self.playground.elem_height + ((self.sprite.y - self.playground.elem_width) // self.playground.elem_width) * self.playground.columns)
            self.human_pos = self.index2human(self.grid_pos)
            blank = self.playground.searchFirstBlank(self.human_pos[0])
            if self.shadow:
                self.shadow_sprite.set_position(*self.index2pos(self.human2index(blank))) 


    def move_left(self, dt):
        if self.pauseBool:
            return
        if self.human_pos[0] > 0 and self.playground.state[self.grid_pos-1] == -1 and self.sprite != None:
            #print(self.sprite)
            self.sprite.x -= self.playground.elem_width
            self.grid_pos = int((self.sprite.x - self.playground.origin[0]) // self.playground.elem_height + ((self.sprite.y - self.playground.elem_width) // self.playground.elem_width) * self.playground.columns) 
            self.human_pos = self.index2human(self.grid_pos)
            blank = self.playground.searchFirstBlank(self.human_pos[0])
            if self.shadow:
                self.shadow_sprite.set_position(*self.index2pos(self.human2index(blank))) 

    def speedChange(self, speed=150.0):
        if self.pauseBool:
            return
        self.sprite.dy = speed

    def hardDrop(self):
        if self.pauseBool:
            return
        if self.shadow:
            #self.shadow_sprite.delete()
            self.shadow_sprite.visible = False

        check_column = self.human_pos[0]
        blank = self.playground.searchFirstBlank(check_column)
        pyglet.clock.unschedule(self.update)
        #self.sprite.delete()
        self.sprite.visible = False
        self.playground.state[self.human2index(blank)] = self.note
        #self.playground.check()
        self.exist = False

    def pos2index(self, pos):
        pass

    def index2pos(self, index):
        return ((index % self.playground.columns) * self.playground.elem_width + self.playground.origin[0], 
                (index // self.playground.columns) * self.playground.elem_height + self.playground.origin[1])

    def index2human(self, index):
        return ((index % self.playground.columns), (index // self.playground.columns))
    
    def human2index(self, grid):
        return grid[0] + grid[1] * self.playground.columns

    def pause(self):
        self.old_dy = self.sprite.dy
        self.sprite.dy = 0
        self.pauseBool = True

    def unpause(self):
        self.sprite.dy = self.old_dy
        self.pauseBool = False

class FloatElemAutoDispense(FloatElem):

    def __init__(self, batch, order_level, start_pos, notes_images, playground, note=-1, shadow=False):
        super().__init__(batch, order_level, start_pos, notes_images, playground, note, shadow)
        self.dispense()


class Player(FloatElem):

    def __init__(self, batch, order_level, start_pos, distribution, notes_images, playground):
        self.distribution = cycle(distribution)
        self.ennemies = []
        self.score = 0
        self.score_total = 0
        self.damage = 0
        self.damage_alone = []
        self.damage4lines = 0
        self.damage_remaning_lines = 0
        self.combo=1

        super().__init__(batch, order_level, start_pos, notes_images, playground, -1, True)

        self.total_score_label = pyglet.text.Label(str(self.score), font_name='Times New Roman',
                font_size=36, x=self.playground.origin[0], y=self.playground.origin[1]-48, batch=batch, 
                group=order_level[2], color=(0,0,0,255))

        self.score_label = pyglet.text.Label(str(self.score), font_name='Times New Roman',
                font_size=36, 
                x=self.playground.origin[0] + 2 * self.playground.elem_width, 
                y=self.playground.origin[1]-48, batch=batch, 
                group=order_level[2], color=(0,0,0,255))

        #print(str(self.score))

        self.dispense()

    def dispense(self):
        self.note = list(islice(self.distribution, None, 1))[0]
        super().dispense()

    def update(self, dt):
        super().update(dt)
        
        if self.human_pos[1] < 0 or self.playground.state[self.grid_pos] != -1:
            if self.grid_pos == self.start_pos-self.playground.columns:
                self.playground.state = [-1 for _ in range(self.playground.rows*self.playground.columns)]
            self.playground.check(self)
            #self.dispense()

    def hardDrop(self):
        super().hardDrop()

        self.playground.check(self)
        #self.dispense()

    def attackEnnemies(self):
        for ennemie in self.ennemies:
            ennemie.damage += self.score
        self.score_total += self.score
        self.score = 0
        self.total_score_label.text = str(self.score_total)
        self.combo = 1

    def takeDamage(self):
        if(self.damage_alone == [] and self.damage4lines == 0 and self.damage_remaning_lines == 0):
            #print("TEST")
            nb_blocs = self.damage//20
            lines = nb_blocs // self.playground.columns
            alone = nb_blocs % self.playground.columns
            self.damage_alone = [7 for _ in range(alone)] + [-1 for _ in range(self.playground.columns-alone)]
            shuffle(self.damage_alone)
            self.block4lines = lines // 4
            self.damage_remaning_lines = lines % 4
            #print(self.damage_alone)
        if self.block4lines > 0:
            blocs = []
            for index in range(self.playground.columns*self.playground.rows - 4 * self.playground.columns, self.playground.columns*self.playground.rows):
                blocs.append(FloatElemAutoDispense(self.batch, self.order_level, index, self.notes_images, self.playground, 7))
            self.damage -= 4 * 20 * self.playground.columns
            self.block4lines -= 1
        elif self.damage_remaning_lines > 0:
            blocs = []
            for index in range(self.playground.columns*self.playground.rows - self.damage_remaning_lines * self.playground.columns, self.playground.columns*self.playground.rows):
                blocs.append(FloatElemAutoDispense(self.batch, self.order_level, index, self.notes_images, self.playground, 7))
            self.damage -= self.damage_remaning_lines * 20 * self.playground.columns
            self.damage_remaning_lines = 0
        else:
            blocs = []
            for index,elem in enumerate(self.damage_alone):
                if elem == 7:
                    blocs.append(FloatElemAutoDispense(self.batch, self.order_level, self.human2index((index, self.playground.rows-1)), self.notes_images, self.playground, 7))
                    #print(blocs[-1].note)
                self.damage = 0
                self.damage_alone = []
        if len(blocs) > 0:
            pyglet.clock.schedule_interval(self.playground.wait, 1/60, elems=blocs, player=self, check=False)
        else:
            self.dispense()

class OutputSound:
    noteToFreq = {0: 262, 1:294, 2:330, 3:349, 4:392, 5:440, 6:494}
    def __init__(self):
        pass

    def playBeep(self, freq, time):
        pass

    def playNote(self, note, time):
        self.playBeep(self.noteToFreq[note], time)

    def playChord(self, notes, time):
        for note in notes:
            self.playNote(note, time)

class OutputBeep(OutputSound):
    def __init__(self):
        super().__init__()
    
    def playBeep(self, freq, time):
        #print(freq)
        if _platform == "win32":
            winsound.Beep(freq, time)
        elif _platform == "linux" or _platform == "linux2":
            subprocess.Popen(['beep', '-f', str(freq), '-l', str(time)])

        #arpeggiato
    def playChord(self, notes, time):
        number = len(notes)
        for index,note in enumerate(notes):
            #print(note)
            pyglet.clock.schedule_once(lambda x, y: self.playBeep(self.noteToFreq[y], time/number-250), (index+1)*(time/1000)/number, note)

class OutputPlay(OutputSound):
    def __init__(self):
        super().__init__()

    def playBeep(self, freq, time):
        print(freq)
        if _platform == "linux" or _platform == "linux2":
            subprocess.Popen(['/usr/bin/play', '--no-show-progress', '--null', '--channels', '1', 'synth', str(time/1000), 'sine', str(freq)])
            #os.system('play --no-show-progress --null --channels 1 synth {} sine {}'.format(time/1000, freq))
            
    def playArpeggiato(self, notes, time):
        number = len(notes)
        for index,note in enumerate(notes):
            #print(note)
            pyglet.clock.schedule_once(lambda x, y: self.playBeep(self.noteToFreq[y], time/number-250), (index+1)*(time/1000)/number, note)

    def playChord(self, notes, time):
        if arpeggiato:
            self.playArpeggiato(notes, time)
        else:
            super().playChord(notes, time)

class OutputMidi(OutputSound):
    def __init__(self):
        super().__init__()
        try:
            self.midiout, self.port_name = open_midiport(None, "output", api=rtmidi.API_UNIX_JACK,
                    client_name="PuyoMusic", port_name="MIDI Out", use_virtual=True)
        except (EOFError, KeyboardInterrupt):
            sys.exit()

        subprocess.call("./linuxsampler.sh", shell=True)
        time.sleep(6)

    def playNote(self, note, time):
        self.midiout.send_message(self.toMidiMessage(note, True))
        pyglet.clock.schedule_once(lambda x: self.midiout.send_message(self.toMidiMessage(note, False)), time/1000)

    def toSemiTone(self, note):
        table = {-7:48, -6:50, -5:52, -4:53, -3:55, -2:57, -1:59,
                0:60, 1:62, 2:64, 3:65, 4:67, 5:69, 6:71,
                7:72, 8:74, 9:76, 10:77, 11:79, 12:81, 13:83}
        return table[note]

    def toMidiMessage(self, note, on):
        if on:
            return [0x90, self.toSemiTone(note), 56]
        else:
            return [0x80, self.toSemiTone(note), 0]

class Track:
    def __init__(self, batch, order_level, notes_images, sound_output, origin_x=0, origin_y=8):
        self.origin = (origin_x, origin_y)
        self.batch = batch
        self.order_level = order_level
        self.background_image = pyglet.image.load('track.png', decoder=PILImageDecoder())
        self.background_sprite = pyglet.sprite.Sprite(self.background_image, 
                self.origin[0], self.origin[1], batch=self.batch, group=self.order_level[0])
        self.notes_images = notes_images
        self.chords = []
        self.notes_sprites = []
        self.step = 0
        self.sound_output = sound_output
        pyglet.clock.schedule_interval(self.playstep, 1.5)

    def addChord(self, notes, x=-1):
        if x == -1:
            if self.notes_sprites != []:
                x = self.notes_sprites[-1].x + 32
            else:
                x = 16
        self.chords.append(list(set(notes)))
        for note in self.chords[-1]:
            self.notes_sprites.append(pyglet.sprite.Sprite(self.notes_images[note], 
                batch=self.batch, group=self.order_level[1]))
            self.notes_sprites[-1].set_position(x, 8 + 16*note)
            self.notes_sprites[-1].scale = 0.25

    def playstep(self, dt):
        if len(self.chords) == 0:
            return
        if self.step == len(self.chords):
            self.step = 0
        self.sound_output.playChord(self.chords[self.step], 1000)
        self.step += 1

    def displayChord(self, notes):
        pass

    def displayCursor(self, dt):
        pass

    def update(self, dt):
        pass

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(1280, 1024, caption="Puyo Music")

        #self.midiout = rtmidi.MidiOut()
        #avalible_ports = self.midiout.get_ports()

        #if avalible_ports:
        #    self.midiout.open_port(0)
        #else:
        #    self.midiout.open_virtual_port("Puyo Music")

        if backend == "Output":
            self.sound_output = OutputPlay()
        elif backend == "MIDI":
            self.sound_output = OutputMidi()
        else:
            self.sound_output = OutputBeep()

        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.middleground = pyglet.graphics.OrderedGroup(1)
        self.foreground = pyglet.graphics.OrderedGroup(2)
        self.order_level = [self.background, self.middleground, self.foreground]
        
        self.notes_image = pyglet.image.load('notes.png', decoder=PILImageDecoder())
        self.notes_images = pyglet.image.ImageGrid(self.notes_image, 1, 10)[:9]

        self.track = Track(self.batch, self.order_level, self.notes_images, self.sound_output)
        #self.track.addChord([0,2,4], 16)

        self.playground1 = PlayGround(self.batch, self.order_level, self.notes_images, 
                self.track, origin_y = 192)

        self.player1 = Player(self.batch, self.order_level, 90, list(range(7)), self.notes_images, self.playground1)
        #self.player1.dispense()
        
        self.playground2 = PlayGround(self.batch, self.order_level, self.notes_images, 
                self.track, origin_x = 704, origin_y = 192)
        
        self.player2 = Player(self.batch, self.order_level, 90, list(range(7)), self.notes_images, self.playground2)
        #self.player2.dispense()
        self.player1.ennemies = [self.player2]
        self.player2.ennemies = [self.player1]

        #print(len(self.player2.playground.notes_images))
        
        self.fps_display = pyglet.clock.ClockDisplay()

        self.key_repeat_interval = 0.05
        self.time_before_repeat = 0.2
        
    def on_draw(self):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()
        self.batch.draw()
        self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT:
            self.player1.move_right(0)
            self.move_r1 = lambda x: pyglet.clock.schedule_interval(self.player1.move_right, self.key_repeat_interval)
            pyglet.clock.schedule_once(self.move_r1, self.time_before_repeat)
        if symbol == pyglet.window.key.LEFT:
            self.player1.move_left(0)
            self.move_l1 = lambda x: pyglet.clock.schedule_interval(self.player1.move_left, self.key_repeat_interval) 
            pyglet.clock.schedule_once(self.move_l1, self.time_before_repeat)
        if symbol == pyglet.window.key.DOWN:
            self.player1.speedChange(250.0)
        if symbol == pyglet.window.key.UP:
            self.player1.hardDrop()

        if symbol == pyglet.window.key.NUM_6:
            self.player2.move_right(0)
            self.move_r2 = lambda x: pyglet.clock.schedule_interval(self.player2.move_right, self.key_repeat_interval)
            pyglet.clock.schedule_once(self.move_r2, self.time_before_repeat)
        if symbol == pyglet.window.key.NUM_4:
            self.player2.move_left(0)
            self.move_l2 = lambda x: pyglet.clock.schedule_interval(self.player2.move_left, self.key_repeat_interval) 
            pyglet.clock.schedule_once(self.move_l2, self.time_before_repeat)
        if symbol == pyglet.window.key.NUM_5:
            self.player2.speedChange(250.0)
        if symbol == pyglet.window.key.NUM_8:
            self.player2.hardDrop()



    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT:
            pyglet.clock.unschedule(self.move_r1)
            pyglet.clock.unschedule(self.player1.move_right)
        if symbol == pyglet.window.key.LEFT:
            pyglet.clock.unschedule(self.move_l1)
            pyglet.clock.unschedule(self.player1.move_left)
        if symbol == pyglet.window.key.DOWN:
            self.player1.speedChange()

        if symbol == pyglet.window.key.NUM_6:
            pyglet.clock.unschedule(self.move_r2)
            pyglet.clock.unschedule(self.player2.move_right)
        if symbol == pyglet.window.key.NUM_4:
            pyglet.clock.unschedule(self.move_l2)
            pyglet.clock.unschedule(self.player2.move_left)
        if symbol == pyglet.window.key.NUM_5:
            self.player2.speedChange()

    def on_exit(self):
        subprocess.Popen("./linuxsampler_stop.sh", shell=True)

    
def gen_distribution(seed):
    pass

def main():
    window = Window()
    pyglet.app.run()

if __name__ == '__main__':
    main()
