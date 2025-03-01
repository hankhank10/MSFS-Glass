import logging
from time import sleep

from SimConnect import SimConnect

logging.basicConfig(level="DEBUG")

sm = SimConnect()

sleep(2)
sm.load_selected_aircraft()
sleep(1)
sm.enumerate_input_events()
sleep(1)
with open(f"..\\input_events\\{sm.selected_aircraft}", "w+") as file:
    for ie in sm.input_event_hash:
        file.write(ie + "\n")
sm.exit()

