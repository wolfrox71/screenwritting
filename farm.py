import logging
from time import sleep, perf_counter
from random import randint
from threading import Thread
import os
import math
import keyboard

global money
money = 0
running = True

def UP(number_of_lines: int) -> str:
    return f"\x1B[{number_of_lines}A"

def progress_from_times(current:int, duration:int) -> str:
    """Returns a progress bar as a string of the progress of a time to a duration"""
    percentage = (current/duration)*100

    return progress_from_percentage(percentage)

def progress_from_percentage(percentage: int) -> str:
    """Returns a progress nar as a string given a percentage"""
    used_symbol = "#"
    empty_symbol = "-"

    length_of_bar = 20

    bar = ""

    number_of_used = math.floor((100-percentage)/100 * length_of_bar)

    for i in range(number_of_used):
        bar += used_symbol

    for i in range(length_of_bar-number_of_used):
        bar += empty_symbol

    return bar


class inputs(Thread):
    currentMessage = ""
    previous_keys = []

    def __init__(self):
        Thread.__init__(self)   

    def run(self):
        while running:
            self.updateKey()

    def updateKey(self):
        event = keyboard.read_event()

        special_chars = {"space": " "}
        blank_chars = ["command", "ctrl", "esc", "alt"]

        key = event.name

        if (event.event_type == "up"):
            # if a key is up then remove it from the previously pressed key array
            
            if key in self.previous_keys:
                self.previous_keys.remove(key)

            return

        if key in self.previous_keys:
            # if the key is held down
            # return to not have duplicate keys
            return

        if (event.event_type == "down"):
            if key not in self.previous_keys:
                self.previous_keys.append(key)

        if key == "delete" and len(self.currentMessage) >= 0:
            self.currentMessage = self.currentMessage[:-1]

        elif key in special_chars:
            self.currentMessage += special_chars[key]

        elif key in blank_chars:
            return
        
        else:
            self.currentMessage += key

class farm(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.value = None
        self.name = name
        self.level = randint(1,5)
        self.level_percent = 1.10
        self.delay = randint(1, 100) / 10 # in seconds
        self.number_of_runs = 0
        logging.info(f"{self.name} started with level: {self.level}, delay: {self.delay}")

    def run(self):
        global running
        while running:
            self.one_run()
            if (randint(1,10) == 2):
                self.increase_level()

    def one_run(self):
        global money
        self.number_of_runs += 1
        self.money_to_add = self.level * self.level_percent
        self.startTime = perf_counter()
        self.endTime = self.startTime + self.delay
        sleep(self.delay) # wait the delay
        money += self.money_to_add
        
    
    def outputValues(self):
        self.progress_percent = (self.endTime - perf_counter())*100/self.delay
        self.progress_time = (self.endTime - perf_counter())
        logging.info(f"{self.name}      level: {self.level}     {progress_from_percentage(self.progress_percent)}       {self.number_of_runs}       {self.delay:.2f}        {self.money_to_add:.1f}     {self.progress_percent}")

    def increase_level(self, output=False):
        self.level += 1
        if (output):
            logging.info(f"{self.name} increase to {self.level}")

class count(Thread):
    def __init__(self, delay):
        self.delay = delay

    def run(self):
        sleep(self.delay)
        return

class run(Thread):
    runtime = 10 # in s
    update_delay = 0.1 # in s
    def __init__(self):
        self.inputs = inputs()
        self.inputs.start()
        values = [x for x in range(10)]
        self.threads = []
        for value in values:
            self.threads.append(farm(value))
            self.threads[-1].start()
        
    def end(self):
        global running
        logging.info("Stopping")
        running = False
        # go through each thread and make sure its ended
        for thread in self.threads:
            thread.join()
        logging.info("Everything Stopped")

    def output(self):
        for thread in self.threads:
            thread.outputValues()
    
    def checkInput(self):
        if len(self.inputs.currentMessage) == 0:
            return
        
        last_digit = self.inputs.currentMessage[-1]
        if not last_digit.isdigit():
            return
        last_digit = int(last_digit)
        if (last_digit >= 0 and last_digit < len(self.threads)):
            self.inputs.currentMessage = ""
            self.threads[last_digit].increase_level(output=True)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    main = run()

    start_time = perf_counter()
    while ((perf_counter()-start_time) < main.runtime):
        os.system("clear")
        main.output()
        print(main.inputs.currentMessage)
        main.checkInput()
        sleep(main.update_delay)

    main.end()

    print(money)