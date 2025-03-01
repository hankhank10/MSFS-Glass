from time import sleep
import logging
import os

import subscribe_variables
from SimConnect import SimConnect
from SimConnect.Enum import SIMCONNECT_PERIOD, SIMCONNECT_DATATYPE, SIMCONNECT_DATA_DEFINITION_ID

logging.getLogger("SimConnect").setLevel(logging.DEBUG)

sm = SimConnect()

# sm.dll.ClearDataDefinition(sm.hSimConnect, sm.new_def_id().value)
# sm.dll.DATA_DEFINITION_ID = SIMCONNECT_DATA_DEFINITION_ID


variables = {
   "FD_ON_LVAR": {
      "DatumName": b'(L:XMLVAR_AS1000_Course_PFD_Value)',
      "UnitsName": b'Number',
      "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64,
   },
   # "latitude": {
   #    "DatumName": b'AUTOPILOT VERTICAL HOLD VAR',
   #    "UnitsName": b'Feet/minute',
   #    "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64,
   # },
   # "speed": {
   #    "DatumName": b'AIRSPEED INDICATED',
   #    "UnitsName": b'Knots',
   #    "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64,
   #    "fEpsilon": 1.0,
   #    # optional fields not provided
   # }
}


data_definition_id = sm.create_data_definition(variables)
sm.subscribe_to_data(data_definition_id)

while True:
   sleep(1)
   print(sm.subscribed_data)


