import logging
from time import sleep, perf_counter
from random import randint
from threading import Thread
import os
import math
import keyboard
from enum import Enum

global money
money = 0
running = True

class UpgradeType(Enum):
    delay = 1
    value = 2

    def next(self):
        members = list(self.__class__)
        index = members.index(self) + 1

        if index >= len(members):
            index = 0
        return members[index]
    

    def previous(self):
        members = list(self.__class__)
        index = members.index(self) - 1

        if index < len(members):
            index = len(members) -1
        return members[index]

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
        self.upgrade_price = self.level * 10
        self.delay = randint(1, 100) / 10 # in seconds
        self.number_of_runs = 0
        self.minimum_delay = 1.0
        self.delay_reduction = 0.9
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
        logging.info(f"{self.name}      {str(self.level).zfill(3)}     {progress_from_percentage(self.progress_percent)}       {str(self.number_of_runs).zfill(3)}    {self.money_to_add:.1f}     {self.upgrade_price}        {self.delay:.1f}")

    def increase_level(self, output=False):
        self.level += 1
        self.upgrade_price = 10 * self.level
        if (output):
            logging.info(f"{self.name} increase to {self.level}")

    def reduce_delay(self, output=False):
        if self.delay * self.delay_reduction < self.minimum_delay:
            if output:
                logging.info(f"{self.delay} already at minimum delay")
            return
        self.delay *= self.delay_reduction
        if (output):
            logging.info(f"{self.name} decreasing delay to {self.delay}")

class count(Thread):
    def __init__(self, delay):
        self.delay = delay

    def run(self):
        sleep(self.delay)
        return

class run(Thread):
    runtime = 50 # in s
    update_type: UpgradeType = UpgradeType.delay # in s
    update_delay = 0.1

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
        logging.info(f"Name   Level                              reps   add     price    delay")
        for thread in self.threads:
            thread.outputValues()
    
    def checkInput(self):
        global money
        if len(self.inputs.currentMessage) == 0:
            return
        
        last_digit = self.inputs.currentMessage[-1]
        if last_digit == "g":
            self.inputs.currentMessage = ""
            self.update_type = self.update_type.next()
            return

        if not last_digit.isdigit():
            return
        
        last_digit = int(last_digit)
        
        if (last_digit >= 0 and last_digit < len(self.threads)):
            self.inputs.currentMessage = ""

            if (self.threads[last_digit].upgrade_price <= money):
                if self.update_type == UpgradeType.delay:
                    self.threads[last_digit].reduce_delay()

                elif self.update_type == UpgradeType.value:
                    self.threads[last_digit].increase_level()
                
                money -= self.threads[last_digit].upgrade_price

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    main = run()

    start_time = perf_counter()
    while ((perf_counter()-start_time) < main.runtime):
        os.system("clear")
        main.output()
        print(f"{money:.1f}")
        print(main.update_type)
        main.checkInput()
        sleep(main.update_delay)

    main.end()

    print(f"Ending Money: £{money:.1f}")
    input("E")