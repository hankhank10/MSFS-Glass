import logging
from time import sleep

from SimConnect import SimConnect

logging.getLogger("SimConnect").setLevel(logging.DEBUG)

sm = SimConnect()

sleep(0.5)
sm.load_selected_aircraft()
sleep(0.5)
sm.enumerate_input_events()
sleep(0.5)


sm.set_input_event("AS530_CLR", [1.0, 0.0, 2.0])


while True:
    sleep(1)