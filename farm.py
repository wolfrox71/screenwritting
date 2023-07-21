import logging
from time import sleep, perf_counter
from random import randint
from threading import Thread
import os
import math

global money
money = 0
running = True

def UP(number_of_lines: int) -> str:
    return f"\x1B[{number_of_lines}A"

class farm(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.value = None
        self.name = name
        self.level = randint(1,5)
        self.level_percent = 1.10
        self.delay = randint(1, 100) / 10 # in seconds
        self.number_of_runs = 10
        logging.info(f"{self.name} started with level: {self.level}, delay: {self.delay}")
    
    def run(self):
        global running
        while running:
            self.one_run()

            if (randint(1,10) == 2):
                self.increase_level()

    def one_run(self):
        global money
        self.money_to_add = self.level * self.level_percent
        self.startTime = perf_counter()
        self.endTime = self.startTime + self.delay
        sleep(self.delay) # wait the delay
        money += self.money_to_add
        
    
    def outputValues(self):
        self.progress_percent = (self.endTime - perf_counter())*100/self.delay
        self.progress_time = (self.endTime - perf_counter())
        logging.info(f"{self.name}      level: {self.level}         {self.progress_percent:.1f}% done        {self.progress_time:.1f} -> {self.delay:.1f}s")

    def increase_level(self):
        self.level += 1
        logging.info(f"{self.name} increase to {self.level}")

class count(Thread):
    def __init__(self, delay):
        self.delay = delay

    def run(self):
        sleep(self.delay)
        return

class run(Thread):
    def __init__(self):
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


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    main = run()

    for i in range(50):
        os.system("clear")
        main.output()
        sleep(0.1)

    
    main.end()

    print(money)
