from time import sleep
import logging
import os

import subscribe_variables
from SimConnect import SimConnect
from SimConnect.Enum import SIMCONNECT_PERIOD, SIMCONNECT_DATATYPE, SIMCONNECT_DATA_DEFINITION_ID

logging.getLogger("SimConnect").setLevel(logging.DEBUG)

sm = SimConnect()

variables = {
   # "FD_ON_LVAR": {
   #    "DatumName": b'ATC ID',
   #    "UnitsName": b'', # String requires NULL as Unit
   #    "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_STRING64,
   #    "Value": b"Air Force 1"
   # },
   "latitude": {
      "DatumName": b'K:G1000_MFD_ZOOMIN_BUTTON', # don't go crazy with the LVars :)
      "UnitsName": b'Boold',
      "Value": 1
   }
}


sm.set_simobject_data(variables)

while True:
   sleep(1)



