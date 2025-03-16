import logging
from time import sleep

from SimConnect import SimConnect

logging.getLogger("SimConnect").setLevel(logging.DEBUG)

sm = SimConnect()

ICAO = 'IBUSE'.encode('utf-8')
Region = 'K7'.encode('utf-8')

data_def_id = sm.new_def_id()

sm.dll.AddToFacilityDefinition(sm.hSimConnect, data_def_id.value, 'OPEN WAYPOINT'.encode('utf-8'))
sm.dll.AddToFacilityDefinition(sm.hSimConnect, data_def_id.value, 'LATITUDE'.encode('utf-8'))
sm.dll.AddToFacilityDefinition(sm.hSimConnect, data_def_id.value, 'LONGITUDE'.encode('utf-8'))
sm.dll.AddToFacilityDefinition(sm.hSimConnect, data_def_id.value, 'CLOSE WAYPOINT'.encode('utf-8'))

sm.dll.RequestFacilityData(sm.hSimConnect,
                           data_def_id.value,
                           999,
                           ICAO,
                           Region
)


while True:
    sleep(1)
