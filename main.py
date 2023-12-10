import os
import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *
from audiorecorder import *
import speech_recognition as sr
from helper import *
from helper import GPIO_helper
from datetime import datetime
from log import logDB
from facerecog import face_recog

# constant
HUMID_HIGH = 65
HUMID_LOW = 30

# instance of assistant classes
audio = Recorder()
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
GP = GPIO_helper()
log = logDB("LOG.db")
face = face_recog()

def audio_to_text(filename):
    speech = sr.AudioFile(filename)
    with speech as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio,language = 'en-US')#,key = "AIzaSyBUHRjjkxUx-sj1ZC5jcOdwPBOXHscZW3I")
    return text

class GUI():
    layer_index = 1
    recording = 0


    # Initialize pygame and the piTFT display
    os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT 
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT 
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((320, 240))

    # path for image log
    image_folder = '/home/pi/proj/photohistory'
    image_files = [file for file in os.listdir(image_folder) if file.startswith('image_') and file.endswith('.jpg')]
    image_files.sort()
    current_index = len(image_files) - 1

    # Define some colors and fonts
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    ICE = (185,205,246)
    ORANGE = (255,165,0)
    PLANT = (169,207,83)
    BROWN = (204,102,51)
    FIRE = (226,88,34)
    WATER = (102,255,230)
    YELLOW = (255,255,0)
    VOICECOLOR = (0,0,255)
    FONT = pygame.font.SysFont('Arial', 20)
    width, height = 320,240
    
    # Define some buttons
    button1 = pygame.Rect(210, 170, 80, 60) # First layer button
    button2 = pygame.Rect(320 // 2 - 35, 240 - 50, 70, 40) # Second layer button
    voice_button = pygame.Rect(30,170,80,60)
    log_button = pygame.Rect(120,170,80,60)
    button_positions = [(width // 4, height//4), (3 * width // 4, height //4),
                            (width // 4, 4* height//6), (3* width // 4, 4* height //6)]
    circle_rect = []
    for position in button_positions:
        rect = pygame.draw.circle(screen, GREEN, position, 40)
        circle_rect.append(rect)

    # Define some variables to keep track of layers and appliance states
    current_layer = 1
    is_new_to_image = 0
    light_on = False
    curtain_open = False
    manual_humid = False
    humidifier_on = False
    manual_humid = False
    fan_on = False
    face_id = 0
    manual_control = False
    room1counter = 0
    room2counter = 1
    lastroom = 0
    curroom = 0
    temperature = 0
    humidity = 0

    # acquire some variables
    GP.dht_init()
    temperature, humidity = GP.humitemp()
    start_time = time.time()
    weather = acquire_Ithaca_weather()
    sunrise_today = sunrise()
    sunset_today = sunset()

    door_counter = 0

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return
    
    # Define a function to draw the first layer
    def draw_first_layer(self):
        if(int(time.time()-self.start_time)%120 == 0):
            self.weather = acquire_Ithaca_weather()
        screen = self.screen
        FONT = self.FONT
        # Clear the screen
        screen.fill(self.BLACK)
        # Draw the button to go to the second layer
        pygame.draw.rect(self.screen, self.GREEN, self.button1)
        pygame.draw.rect(self.screen, self.VOICECOLOR, self.voice_button)
        pygame.draw.rect(self.screen, self.RED, self.log_button)        
        screen.blit(FONT.render('Log', True, self.WHITE), (140, 190))
        screen.blit(FONT.render('Voice', True, self.WHITE), (45, 190))
        screen.blit(FONT.render('Next', True, self.WHITE), (230, 190))
        # Get the current time, temperature and RH
        now = datetime.now() 
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")        
        humidity, temperature = self.humidity, self.temperature
        # Display the time, temperature and RH
        weather_str = 'Temp: ' + str(self.weather[0])+' C, '+str(self.weather[1])
        if self.weather[0] <10 :
            screen.blit(FONT.render(weather_str, True, self.ICE), (30, 20))
        else :
            screen.blit(FONT.render(weather_str, True, self.ORANGE), (30, 20))
        screen.blit(FONT.render('Date&Time: ' + current_time, True, self.YELLOW), (20, 57))
        if temperature < 25 and temperature > 15:
            screen.blit(FONT.render('Room Temp: {:.1f} C'.format(temperature), True, self.ORANGE), (30, 95))
        elif temperature < 0:
            screen.blit(FONT.render('Room Temp: {:.1f} C'.format(temperature), True, self.ICE), (30, 95))
        else : 
            screen.blit(FONT.render('Room Temp: {:.1f} C'.format(temperature), True, self.FIRE), (30, 95))
        if humidity > HUMID_HIGH :
            screen.blit(FONT.render('RH: {:.1f} %'.format(humidity), True, self.WATER), (30, 131))
        elif humidity < HUMID_LOW:
            screen.blit(FONT.render('RH: {:.1f} %'.format(humidity), True, self.BROWN), (30, 131))
        else:
            screen.blit(FONT.render('RH: {:.1f} %'.format(humidity), True, self.PLANT), (30, 131))

        # Update the display
        pygame.display.flip()

    # Define a function to draw the second layer
    def draw_second_layer(self):
        width, height = 320, 240
        screen = self.screen
        FONT = self.FONT
        screen.fill(self.BLACK)

        # Display round buttons for curtain, humidifier, light, and voice control
        button_radius = 40
        
        for position in self.button_positions:
            pygame.draw.circle(self.screen, self.GREEN, position, button_radius)
        screen.blit(FONT.render('Curtain', True, self.WHITE), (width // 4-30, height//4-10))
        screen.blit(FONT.render('Light', True, self.WHITE), (3 * width // 4 -20, height //4-10))
        screen.blit(FONT.render('Humid', True, self.WHITE), (width // 4 -25, 4* height//6-10))
        screen.blit(FONT.render('Fan', True, self.WHITE), (3* width // 4 -23, 4* height //6-10))

        # Display 'Exit' button
        pygame.draw.rect(self.screen, self.RED, (width // 2 - 35, height - 50, 70, 40))
        exit_button_text = FONT.render('Exit', True, self.WHITE)
        screen.blit(exit_button_text, (width // 2 - exit_button_text.get_width() // 2, height-40))

        pygame.display.flip()

    # Define a function to draw the third layer
    def draw_third_layer(self):
        width, height = 320, 240
        screen = self.screen
        FONT = self.FONT
        screen.fill(self.BLACK)

        # Display round buttons for curtain, humidifier, light, and voice control
        button_radius = 40
        
        for position in self.button_positions:
            pygame.draw.circle(self.screen, self.BLUE, position, button_radius)

        screen.blit(FONT.render('Door', True, self.WHITE), (width // 4-25, height//4-10))
        screen.blit(FONT.render('Room', True, self.WHITE), (3 * width // 4 -25, height //4-10))
        screen.blit(FONT.render('Image', True, self.WHITE), (width // 4 -25, 4* height//6-10))
        screen.blit(FONT.render('Back', True, self.WHITE), (3* width // 4 -23, 4* height //6-10))

        pygame.display.flip()

    # Define a function to show the images on the screen
    def show_images(self):
        screen = self.screen

        self.image_files = [file for file in os.listdir(self.image_folder) if file.startswith('image_') and file.endswith('.jpg')]
        self.image_files = sorted(self.image_files, key=extract_number)
        if self.is_new_to_image == 0:
            self.current_index = len(self.image_files) - 1
        self.image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        image = pygame.image.load(self.image_path)
        image = pygame.transform.scale(image, (320, 240))
        image_rect = image.get_rect()
        screen_rect = screen.get_rect()
        image_rect.center = screen_rect.center
        screen.blit(image, image_rect)
        pygame.display.flip()
    
    # Define a function to draw the logt layer
    def draw_logs(self):
        screen = self.screen

        screen.fill(self.BLACK)  # Clear the screen
        font = pygame.font.Font(None, 24)  # Choose a font and size
        start_x = 10
        start_y = 10
        line_height = 25

        if self.layer_index == 5:
            logs = log.list_recent_entries_by_name_or_location_with_limit(9,location="DOOR")
            for count, cur in enumerate(logs):
                # Select the specified columns from the log entry
                selected_columns = [cur[index] for index in [2,3]]

                # Create the display string with the selected columns
                display_string = f'Log {count}: ' + ' | '.join(str(item) for item in selected_columns)

                # Render the text
                text = font.render(display_string, True, self.WHITE)
                screen.blit(text, (start_x, start_y + count * line_height))

            # Update the display
            pygame.display.flip()


        elif self.layer_index == 6:
            logs = log.list_recent_entries_by_name_or_location_with_limit(9,name="NONAME")
            for count, cur in enumerate(logs):
                # Select the specified columns from the log entry
                selected_columns = [cur[index] for index in [1,3]]

                # Create the display string with the selected columns
                display_string = f'Log {count}: ' + ' | '.join(str(item) for item in selected_columns)

                # Render the text
                text = font.render(display_string, True, self.WHITE)
                screen.blit(text, (start_x, start_y + count * line_height))

            # Update the display
            pygame.display.flip()

    # mainloop displaying all the GUI and conduct the finite state machine    
    def mainloop(self):
        code_run = True
        click_counter = 0
        time_limit = 1200
        # print(self.humidity)
        while code_run:    
            #exit button
            if not GPIO.input(17):
                GPIO.cleanup()
                pygame.quit()                
                exit()

            # sunrise set time update and check
            if(int(time.time()-self.start_time)%3600 == 0):
                self.sunrise_today = sunrise()
                self.sunset_today = sunset()
            current_time = datetime.now()
            time_difference1 = current_time - datetime.strptime(self.sunrise_today,'%H:%M:%S')
            time_difference2 = current_time - datetime.strptime(self.sunset_today,'%H:%M:%S')
            total_seconds1 = time_difference1.total_seconds()
            total_seconds2 = time_difference2.total_seconds()

            if abs(total_seconds1) < 1:
                if not self.curtain_open:
                    GP.curtain_open()
                    self.curtain_open = True
            elif  abs(total_seconds2) < 1:
                if self.curtain_open:
                    GP.curtain_close()
                    self.curtain_open = False
            
            # time out
            if time.time() -self.start_time > time_limit:
                print("timeout")
                code_run = False

            # three motion sensors
            if GP.motiondect1():
                # print("motion detected")
                # print("Layer Index :",self.layer_index)
                name, filepath = face.recognize(2)
                if not name == "No Face":
                    print(name+" detected")
                    # if name == "Unknown":
                    #     speak("Unknown person at door")
                    log.insert("DOOR",name,filepath)
                    GP.light3_duration()


            if GP.motiondect2():
                self.room1counter = (self.room1counter+1) % 1000
                if self.room1counter == 0:
                    self.curroom = 1
                    if not self.curroom == self.lastroom:
                        print("ROOM1")
                        GP.light1last()
                        log.insert("ROOM1","NONAME","None")
                    self.lastroom = 1

            if GP.motiondect3():
                self.room2counter = (self.room2counter+1) % 1000
                if self.room2counter == 0:
                    self.curroom = 2
                    if not self.curroom == self.lastroom:
                        print("ROOM2")
                        GP.light2last()
                        log.insert("ROOM2","NONAME","None")
                    self.lastroom = 2

            # button for face recognize
            if not GPIO.input(22):
                name, filepath = face.recognize(2)
                if not name == "No Face":
                    print(name+" detected")
                    # if name == "Unknown":
                    #     speak("Unknown person at door")
                    log.insert("DOOR",name,filepath)
                    GP.light3_duration()
                    speak(name + " is knocking at the door")

            # humidifier and fan control
            self.temperature, self.humidity = GP.humitemp()
            if self.humidity < HUMID_LOW: # and not self.manual_control:
                if not self.humidifier_on:
                    GP.humid_on()
                    self.humidifier_on = True
                if self.fan_on:
                    GP.fan_off()
                    self.fan_on = False

            if self.humidity > HUMID_HIGH:# and not self.manual_control:
                if self.humidifier_on:
                    GP.humid_off()
                    self.humidifier_on = False
                if not self.fan_on:
                    GP.fan_on()
                    self.fan_on = True

            # draw layers
            if self.layer_index == 1:
                self.draw_first_layer()
            elif self.layer_index == 2:
                self.draw_second_layer()
            elif self.layer_index == 3:
                self.draw_third_layer()
            elif self.layer_index == 4:
                self.show_images()
            elif self.layer_index == 5 or self.layer_index == 6:
                self.draw_logs()

            # click detection and state switch
            pos = 0,0
            for event in pygame.event.get(): 
                if(event.type == MOUSEBUTTONDOWN): 
                    pos = pygame.mouse.get_pos()
                    pygame.event.clear([pygame.MOUSEBUTTONDOWN])
                    if self.layer_index == 1:
                        print(pos)
                        if self.button1.collidepoint(pos):
                            self.layer_index = 2
                        elif self.voice_button.collidepoint(pos):
                            if self.recording == 0 :
                                audio.start()
                                self.recording = 1
                                print("recording start")
                                self.VOICECOLOR = self.YELLOW
                            elif self.recording == 1 :
                                self.VOICECOLOR = self.BLUE
                                audio.stop()
                                audio.save("recording")
                                self.recording = 0
                                print("recording stop")
                                command = "NONE"
                                try:
                                    command = audio_to_text("recording.wav")
                                    print(command)
                                except:
                                    print("fail to recognize")
                                    speak("fail to recognize")
                                if "curtain" in command :
                                    if not self.curtain_open:
                                        GP.curtain_open()
                                        self.curtain_open = True
                                    else :
                                        GP.curtain_close()
                                        self.curtain_open = False
                                elif "light" in command :
                                    if not self.light_on:
                                        GP.light_on(1)
                                        self.light_on = True
                                    else :
                                        GP.light_off(1)
                                        self.light_on = False
                                elif ("humid" in command or "humidifier" in command ):
                                    if not self.humidifier_on:
                                        GP.humid_on()
                                        self.humidifier_on = True
                                        self.manual_control = True
                                    else :
                                        GP.humid_off()
                                        self.humidifier_on = False
                                        if(not self.humidifier_on and not self.fan_on):                                        
                                            self.manual_control = False

                                elif "fan" in command or "fun" in command:
                                    if not self.fan_on:
                                        GP.fan_on()
                                        self.fan_on = True                                       
                                        self.manual_control = True
                                    else :
                                        GP.fan_off()
                                        self.fan_on = False
                                        if(not self.humidifier_on and not self.fan_on):                                        
                                            self.manual_control = False

                                elif ("weather" in command) or (("temperature" in command) and not ("room" in command)):
                                    temp, cond = acquire_Ithaca_weather()
                                    speak("Current temperature:" + str(temp) + "Celsius degree, Condition: "+ str(cond))
                                elif ("room temperature" in command) or ("humidity" in command):
                                    humid, roomtemp = self.humidity, self.temperature
                                    speak("Room temperature: "+str(roomtemp)+ "Celsius degree, Relative Humidity: "+str(humid)+"percent")
                                elif ("date" in command) or ("time" in command):
                                    now = datetime.now()
                                    datestring =  "it is " + str(now.strftime("%A, %B %d, %Y, %I:%M %p"))
                                    print(datestring)
                                    speak(datestring)
                                elif "image" in command:
                                    self.layer_index = 4
                                    self.is_new_to_image = 0
                                elif "door" in command:
                                    self.layer_index = 5
                                elif "room" in command:
                                    self.layer_index = 6
                                elif command == "terminate":
                                    GPIO.cleanup()

                        elif self.log_button.collidepoint(pos):
                            self.layer_index = 3
                    elif self.layer_index == 2:
                        if self.button2.collidepoint(pos):
                                self.layer_index = 1
                        if self.circle_rect[0].collidepoint(pos):
                            if not self.curtain_open:
                                GP.curtain_open()
                                self.curtain_open = True
                            else:
                                GP.curtain_close()
                                self.curtain_open = False
                        if self.circle_rect[1].collidepoint(pos):
                            if not self.light_on:
                                GP.light_on(1)
                                self.light_on = True
                            else:
                                GP.light_off(1)
                                self.light_on = False
                        if self.circle_rect[2].collidepoint(pos):
                            if not self.humidifier_on:
                                GP.humid_on()
                                self.humidifier_on = True                                        
                                self.manual_control = True
                            else:
                                GP.humid_off()
                                self.humidifier_on = False
                                if(not self.humidifier_on and not self.fan_on):                                        
                                    self.manual_control = False
                        if self.circle_rect[3].collidepoint(pos):
                            if not self.fan_on:
                                GP.fan_on()
                                self.fan_on = True                                        
                                self.manual_control = True
                            else:
                                GP.fan_off()
                                self.fan_on = False             
                                if(not self.humidifier_on and not self.fan_on):                                        
                                    self.manual_control = False
                    elif self.layer_index == 3:
                        if self.circle_rect[0].collidepoint(pos):
                            self.layer_index = 5
                        if self.circle_rect[1].collidepoint(pos):
                            self.layer_index = 6
                        if self.circle_rect[2].collidepoint(pos):
                            self.layer_index = 4
                            self.is_new_to_image = 0
                        if self.circle_rect[3].collidepoint(pos):
                            self.layer_index = 1

                    elif self.layer_index == 4:
                        mouse_x, mouse_y = event.pos
                        if 100 < mouse_x < 220:
                            self.layer_index = 3
                        elif mouse_x < 100: 
                            self.is_new_to_image = 1
                            self.current_index = (self.current_index - 1) % len(self.image_files)
                        elif mouse_x > 220:
                            self.is_new_to_image = 1
                            self.current_index = (self.current_index + 1) % len(self.image_files)
                    elif self.layer_index == 5 or self.layer_index ==6:
                        click_counter = (click_counter+1)%2
                        if(click_counter == 0):
                            self.layer_index = 3
                        
menu = GUI()
try:
    menu.mainloop()
except KeyboardInterrupt:
    GPIO.cleanup()
    pygame.quit()
    exit()