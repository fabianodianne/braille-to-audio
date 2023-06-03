import pyttsx3
from gpiozero import Button, OutputDevice
from gpiozero.pins.mock import MockFactory
from braille_dict import braille_dict

import time

# Set the pin factory to the mock factory
MockFactory.pin_factory = None

# Initialize the TTS engine
engine = pyttsx3.init()

# Set the properties for the speech output
engine.setProperty('rate', 100)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

# Define button pins
button_pins = [23, 24, 16, 25, 20, 26]
vibration_pins = [17, 27, 22, 5, 6, 21]

# Create button objects and associate names
button_names = ["button1", "button2", "button3", "button4", "button5", "button6"]
buttons = {name: Button(pin, pull_up=True) for name, pin in zip(button_names, button_pins)}

#motor_mapping = {name: OutputDevice(pin) for name, pin in zip(button_names, vibration_pins)}

vibration_time = 1.0
motor_mapping = {name: {"motor": OutputDevice(pin), "vibration_time": vibration_time} for name, pin in zip(button_names, vibration_pins)}

# Translate Braille input to audio
def translate_braille_to_audio():
    while True:
        try:
            braille_input = ""
            while True:
                sentence_input = get_sentence_input()
                if sentence_input == "000001":
                    break
                if sentence_input:
                    braille_input += sentence_input
            translated_text = translate_braille_sentence(braille_input)
            if translated_text:
                speak_text(translated_text)
            else:
                speak_text("Please repeat your message.")
        except KeyboardInterrupt:
            print("Exiting...")
            break
            
# Read Braille input for the entire sentence
previous_input = ""
def get_sentence_input():
    global previous_input
    message = ""
    timeout = time.time() + 10
    while all(not button.is_pressed for button in buttons.values()):
        time.sleep(0.1)
        
    for name, button in buttons.items():
        if button.is_pressed:
            message += '1'
            motor = motor_mapping[name]["motor"]
            motor.on()
            time.sleep(1.0)
            motor.off()
        else:
            message += '0'
            motor_mapping[name]["motor"].off()
            
    if message != previous_input and message != '000000':
        previous_input = message
        print(message)
        return message
    
    for motor in motor_mapping.values():
        motor["motor"].off()
    return ""
    
# Convert Braille input to text
def translate_braille_sentence(braille_input):
    braille_tuple = tuple(braille_input[i:i + 6] for i in range(0, len(braille_input), 6))
    braille_tuple_len = len(braille_tuple)
    translated_text = ""
    braille_list = []
    braille_tail_list = []
    tail_len = 0
    print("braille_tuple", braille_tuple_len, braille_tuple)
    
    while len(braille_tuple) > 0:     
        print(".") 
        translate = braille_dict.get(braille_tuple)
        
        # Convert the tuple to a list
        braille_list = list(braille_tuple)
        
        braille_tail_tuple = tuple(braille_tail_list)
        
        if translate:
            translated_text += translate + ' '
            braille_list.clear()
            braille_tuple = tuple(braille_list)
        else:            
            translated_text += ''
            # Get the last element from the tuple
            braille_tail = braille_tuple[-1]
            
            # Add the last element to a list
            braille_tail_list.insert(0, braille_tail)
            braille_tail_tuple = tuple(braille_tail_list)
            
            # Remove the last tuple
            braille_list = braille_list[:-1]
            
            # Convert the list back to a tuple
            braille_tuple = tuple(braille_list)
            
        if len(braille_tuple) == 0 and len(braille_tail_tuple) > 0:
            braille_tuple = braille_tail_tuple
            braille_tail_list.clear()
            braille_tail_tuple = tuple(braille_tail_list)
        if len(braille_tuple) == 1:
            braille_tail_list.clear()
            braille_tail_tuple = tuple(braille_tail_list)
            break
            
    if translated_text:     
        return translated_text
    return False

# Speak the translated text
def speak_text(text):
    print("Translated text:", text)
    engine.say(text)
    engine.save_to_file(text, 'output.wav')  # Save audio to a file
    engine.runAndWait()

# RUN
translate_braille_to_audio()
