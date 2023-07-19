from time import sleep, perf_counter

def progress(delay: int, minvalue: int = 0, maxvalue: int = 100) -> None:
    number_of_values = (maxvalue - minvalue)
    for loopCount in range(1,number_of_values+1):
        for displayCount in range(loopCount):
            print("#", end="")
        for toDisplayCount in range(number_of_values-loopCount):
            print("-", end="")

        print(f" {loopCount}/{maxvalue} ", end="")
        print("\r",end="")
        sleep(delay)
    print("") 

progress(0.1)