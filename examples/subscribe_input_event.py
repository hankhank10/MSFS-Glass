import logging
from time import sleep

from SimConnect import SimConnect

logging.getLogger("SimConnect").setLevel(logging.DEBUG)

sm = SimConnect()

sm.enumerate_input_events()
sleep(1)
sm.subscribe_input_event("AS1000_FMS_LOWER_PFD")
sm.subscribe_input_event("AS1000_FMS_LOWER_MFD")
sm.subscribe_input_event("AS1000_FMS_UPPER_PFD")
sm.subscribe_input_event("AS1000_RANGE_ZOOM_PFD")

print(sm.input_event_hash)

sleep(3)
while True:
    print(sm.subscribed_data)
    # sm.set_input_event(event_name, -1.0)
    sleep(1)

