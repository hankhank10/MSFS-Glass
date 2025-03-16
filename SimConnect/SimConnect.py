import logging
import os
import threading
from ctypes import cast, HRESULT, c_void_p
from ctypes.wintypes import LPCSTR
from enum import Enum
from time import sleep, time

from _ctypes import byref, sizeof, pointer, addressof, _SimpleCData

from SimConnect.Attributes import SimConnectDll
from SimConnect.Enum import *

_library_path = os.path.abspath(__file__).replace(".py", ".dll")

logging.basicConfig(
    format="%(asctime)s - %(filename)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s",

)
LOG = logging.getLogger(__name__)


def millis():
    return int(round(time() * 1000))
    pass


class SimConnect:

    def __init__(self, name="Python-Simconnect", auto_connect=True, library_path=_library_path,
                 subscribe_to_events=True):
        self.Requests = {}
        self.Name = name
        self.Facilities = []
        self.dll = SimConnectDll(library_path)
        self.hSimConnect = HANDLE()
        self.quit = 0
        self.ok = False
        self.running = False
        self.paused = False
        self.DEFINITION_POS = None
        self.DEFINITION_WAYPOINT = None
        self.my_dispatch_proc_rd = self.dll.DispatchProc(self.my_dispatch_proc)
        self.input_event_hash = {}
        self.selected_aircraft = None
        self.aircraft_changed = False
        self.subscribed_data = {}
        self.data_definitions = {}
        if auto_connect:
            self.connect(subscribe_to_events)

    def connect(self, subscribe_to_events):
        self.timerThread = threading.Thread(target=self._run, name="SimConnect", daemon=True)
        self.timerThread.start()

        err = None

        while not self.ok:
            try:
                err = self.dll.Open(
                    byref(self.hSimConnect), LPCSTR(self.Name.encode()), None, 0, 0, 0
                )
                sleep(1)
            except OSError:
                LOG.info("Did not find Flight Simulator running. Trying again in 5 seconds...")
                sleep(5)
        if self.IsHR(err, 0):
            LOG.info("Connected to Flight Simulator!")
            # Subscribe to events when the simulation starts
            if subscribe_to_events:
                LOG.debug("Subscribing to events")
                # The user is in control of the aircraft
                self.dll.SubscribeToSystemEvent(
                    self.hSimConnect, self.dll.EventID.EVENT_SIM_START, b"SimStart"
                )
                # The user is navigating the UI.
                self.dll.SubscribeToSystemEvent(
                    self.hSimConnect, self.dll.EventID.EVENT_SIM_STOP, b"SimStop"
                )
                # Request a notification when the flight is paused
                self.dll.SubscribeToSystemEvent(
                    self.hSimConnect, self.dll.EventID.EVENT_SIM_PAUSED, b"Paused"
                )
                # Request a notification when the flight is un-paused.
                self.dll.SubscribeToSystemEvent(
                    self.hSimConnect, self.dll.EventID.EVENT_SIM_UNPAUSED, b"Unpaused"
                )
                self.dll.SubscribeToSystemEvent(
                    self.hSimConnect, self.dll.EventID.EVENT_SIM_AIRCRAFT_LOADED, b"AircraftLoaded"
                )
                self.load_selected_aircraft()

    def _run(self):
        while self.quit == 0:
            try:
                self.dll.CallDispatch(self.hSimConnect, self.my_dispatch_proc_rd, None)
                sleep(.002)
            except OSError as err:
                if self.ok:
                    LOG.error(f"OS error: {err}")
                else:
                    sleep(4)
                    LOG.debug("Simconnect not connected yet, dispatch could not run. Trying again.")
                    sleep(1)

    def exit(self):
        self.quit = 1
        if self.timerThread.is_alive():
            self.timerThread.join()
        self.dll.Close(self.hSimConnect)

    def load_selected_aircraft(self):
        hr = self.dll.RequestSystemState(
            self.hSimConnect,
            self.new_request_id().value,
            b"AircraftLoaded"
        )

    def _get_aircraft_directory(self, cfg_location):
        # TODO: Community made planes probably residing elsewhere.
        path = cfg_location.decode('utf-8').lower()
        simobjects_index = path.find('simobjects')

        if simobjects_index == -1:
            raise ValueError("'simobjects' not found in the path.")

        # Strip everything before 'simobjects'
        stripped_path = path[simobjects_index:]

        # Normalize the path and split into parts
        path_parts = os.path.normpath(stripped_path).split(os.sep)

        # Ensure it starts with 'simobjects/airplanes' and extract the third directory
        if len(path_parts) >= 3 and path_parts[:2] == ['simobjects', 'airplanes']:
            LOG.debug(f"Getting aircraft directory: {path_parts[2]}")
            return path_parts[2]
        else:
            raise ValueError("Path must follow the structure: 'simobjects/airplanes/<aircraft_directory>'.")

    def IsHR(self, hr, value):
        _hr = HRESULT(hr)
        return c_ulong(_hr.value).value == value

    def handle_id_event(self, event):
        uEventID = event.uEventID
        if uEventID == self.dll.EventID.EVENT_SIM_START:
            LOG.info("SIM START")
            self.load_selected_aircraft()
            self.running = True
        if uEventID == self.dll.EventID.EVENT_SIM_STOP:
            LOG.info("SIM Stop")
            self.running = False
        # Unknown why not receiving
        if uEventID == self.dll.EventID.EVENT_SIM_PAUSED:
            LOG.info("SIM Paused")
            self.paused = True
        if uEventID == self.dll.EventID.EVENT_SIM_UNPAUSED:
            LOG.info("SIM Unpaused")
            self.paused = False

    def handle_simobject_event(self, ObjData):
        def_id = self.dll.DATA_DEFINITION_ID(ObjData.dwDefineID)
        if def_id.value in self.data_definitions.keys():
            data_ptr = addressof(ObjData.dwData)
            for key, var in self.data_definitions[def_id.value].items():
                ctype = SIMCONNECT_DATATYPE_MAP[var["DatumType"]]  # Get the corresponding ctype

                current_data = cast(data_ptr, POINTER(ctype)).contents.value

                if isinstance(current_data, bytes):
                    self.subscribed_data[key] = current_data.decode("utf-8")
                elif isinstance(current_data, (float, int)):
                    self.subscribed_data[key] = current_data
                else:
                    LOG.error(f"Unsupported data type for {str(type(current_data))}:{str(current_data)}")
                ctype_size = sizeof(ctype)  # Size of this data type

                data_ptr += ctype_size  # Move the pointer to the next data element

        else:
            LOG.warning(f"Data Definition ID {def_id} not found.")

    def handle_simobject_bytype_event(self, ObjData):
        dwRequestID = ObjData.dwRequestID

        if dwRequestID in self.Requests:
            _request = self.Requests[dwRequestID]
            rtype = _request.definitions[0][1].decode()
            if 'string' in rtype.lower():
                ctype = c_char * 265
            else:
                ctype = c_double
            data_ptr = addressof(ObjData.dwData)
            _request.outData = cast(
                data_ptr, POINTER(ctype)).contents.value

        else:
            LOG.warning(f"Event ID: {dwRequestID} Not Handled.")

    def handle_state_event(self, pData):
        LOG.debug(f"System state event received: I: {pData.dwInteger}, F: {pData.fFloat}, S: {pData.szString}")
        aircraft = self._get_aircraft_directory(pData.szString)
        if aircraft is not None:
            if aircraft != self.selected_aircraft:
                LOG.debug(f"Loading plane: {aircraft}")
                self.selected_aircraft = aircraft
                self.enumerate_input_events()
                self.aircraft_changed = True
                LOG.debug(f"Loaded plane: {self.selected_aircraft}")

    def handle_input_event_enum(self, pData):
        LOG.debug("Getting input event enumeration")
        event_descriptors = (SIMCONNECT_INPUT_EVENT_DESCRIPTOR * pData.dwArraySize).from_address(
            addressof(pData.rgData)
        )
        for i in range(pData.dwArraySize):
            data = event_descriptors[i]
            # LOG.trace(f"{data.Name}, {data.Hash}")
            try:
                self.input_event_hash[data.Name.decode()] = data.Hash
            except KeyError:
                LOG.debug(f"Key {data.Name.decode()} not found.")
        LOG.debug("Input event enumeration finished.")

    def handle_event_filename(self, pData):
        LOG.debug("Getting Event Filename")
        if pData.uEventID == self.dll.EventID.EVENT_SIM_AIRCRAFT_LOADED:
            aircraft = self._get_aircraft_directory(pData.zFileName)
            if aircraft is not None:
                if aircraft != self.selected_aircraft:
                    LOG.debug(f"Loading plane: {aircraft}")
                    self.selected_aircraft = aircraft
                    self.enumerate_input_events()
                    self.aircraft_changed = True
                    LOG.debug(f"Loaded plane: {self.selected_aircraft}")

    def handle_get_input_event(self, pData):
        req_id = int(pData.RequestID)
        input_event_value = ""
        if pData.eType == SIMCONNECT_INPUT_EVENT_TYPE.SIMCONNECT_INPUT_EVENT_TYPE_DOUBLE:
            input_event_value = pData.Value.flt_value

        elif pData.eType == SIMCONNECT_INPUT_EVENT_TYPE.SIMCONNECT_INPUT_EVENT_TYPE_STRING:
            input_event_value = pData.Value.str_value
        print(req_id, input_event_value)

    def handle_subscribe_input_event(self, pData):
        input_event_hash = int(pData.Hash)
        input_event_value = None

        data_ptr = addressof(pData.Value)
        if pData.eType == SIMCONNECT_INPUT_EVENT_TYPE.SIMCONNECT_INPUT_EVENT_TYPE_DOUBLE:
            input_event_value = cast(data_ptr, POINTER(c_double)).contents.value
        # Currently not used for anything in SimConnect per docs
        # elif pData.eType == SIMCONNECT_INPUT_EVENT_TYPE.SIMCONNECT_INPUT_EVENT_TYPE_STRING:
        #     input_event_value = str(pData.Value)
        else:
            LOG.error(f"Unsupported event type {pData.eType}")

        for name, hash in self.input_event_hash.items():
            if hash == input_event_hash:
                self.subscribed_data[name] = input_event_value
                break

    # TODO: update callbackfunction to expand functions.
    def my_dispatch_proc(self, pData, cbData, pContext):
        dwID = pData.contents.dwID
        match dwID:
            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_OPEN:
                LOG.info("SIM OPEN")
                self.ok = True

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_EVENT:
                self.handle_id_event(cast(pData, POINTER(SIMCONNECT_RECV_EVENT)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SYSTEM_STATE:
                self.handle_state_event(cast(pData, POINTER(SIMCONNECT_RECV_SYSTEM_STATE)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SIMOBJECT_DATA:
                self.handle_simobject_event(cast(pData, POINTER(SIMCONNECT_RECV_SIMOBJECT_DATA)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE:
                self.handle_simobject_bytype_event(cast(pData, POINTER(SIMCONNECT_RECV_SIMOBJECT_DATA_BYTYPE)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_ENUMERATE_INPUT_EVENTS:
                self.handle_input_event_enum(cast(pData, POINTER(SIMCONNECT_RECV_ENUMERATE_INPUT_EVENTS)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_GET_INPUT_EVENT:
                self.handle_get_input_event(cast(pData, POINTER(SIMCONNECT_RECV_GET_INPUT_EVENT)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_SUBSCRIBE_INPUT_EVENT:
                self.handle_subscribe_input_event(cast(pData, POINTER(SIMCONNECT_RECV_SUBSCRIBE_INPUT_EVENT)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_EXCEPTION:
                err = cast(pData, POINTER(SIMCONNECT_RECV_EXCEPTION)).contents
                LOG.error(f"Received exception: {SIMCONNECT_EXCEPTION(err.dwException).name}, parameter: {err.dwIndex}")

            case (
            SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_AIRPORT_LIST
            | SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_WAYPOINT_LIST
            | SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_NDB_LIST
            | SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_VOR_LIST
            ):
                pObjData = cast(
                    pData, POINTER(SIMCONNECT_RECV_FACILITIES_LIST)
                ).contents
                dwRequestID = pObjData.dwRequestID
                for _facilitie in self.Facilities:
                    if dwRequestID == _facilitie.REQUEST_ID.value:
                        _facilitie.parent.dump(pData)
                        _facilitie.dump(pData)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_EVENT_FILENAME:
                self.handle_event_filename(cast(pData, POINTER(SIMCONNECT_RECV_EVENT_FILENAME)).contents)

            case SIMCONNECT_RECV_ID.SIMCONNECT_RECV_ID_QUIT:
                self.quit = 1

            case _:
                LOG.error(f"Received event but not implemented: id:{dwID}, name {SIMCONNECT_RECV_ID(dwID).name}")
        return

    def map_to_sim_event(self, name):
        for m in self.dll.EventID:
            if name == m.name:
                LOG.debug(f"Already have event in SIMCONNECT_CLIENT_EVENT_ID enum: {m}")
                return m

        names = [m.name for m in self.dll.EventID] + [name]
        self.dll.EventID = Enum(self.dll.EventID.__name__, names)
        evnt = list(self.dll.EventID)[-1]
        err = self.dll.MapClientEventToSimEvent(self.hSimConnect, evnt.value, name.encode())
        if self.IsHR(err, 0):

            return evnt
        else:
            LOG.error("MapToSimEvent")
            return None

    def add_to_notification_group(self, group, evnt, bMaskable=False):
        self.dll.AddClientEventToNotificationGroup(
            self.hSimConnect, group, evnt, bMaskable
        )

    def request_data(self, _Request):
        _Request.outData = None
        self.dll.RequestDataOnSimObjectType(
            self.hSimConnect,
            _Request.DATA_REQUEST_ID.value,
            _Request.DATA_DEFINITION_ID.value,
            DWORD(0),
            SIMCONNECT_SIMOBJECT_TYPE.SIMCONNECT_SIMOBJECT_TYPE_USER,
        )
        temp = DWORD(0)
        self.dll.GetLastSentPacketID(self.hSimConnect, temp)
        _Request.LastID = temp.value

    def create_data_definition(self, variables, data_def_id=None):
        """
            Example usage with required dictionaries:
            https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/API_Reference/Events_And_Data/SimConnect_AddToDataDefinition.htm

            variables = {
                "altitude": {
                    "DatumName": b'PLANE ALTITUDE', # https://docs.flightsimulator.com/html/Programming_Tools/SimVars/Simulation_Variables.htm
                    "UnitsName": b'Feet', # https://docs.flightsimulator.com/html/Programming_Tools/SimVars/Simulation_Variable_Units.htm
                    "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64, # https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/API_Reference/Structures_And_Enumerations/SIMCONNECT_DATATYPE.htm
                    "fEpsilon": 0.1,
                    "DatumID": 1
                },
                "speed": {
                    "DatumName": b'AIRSPEED INDICATED',
                    "UnitsName": b'Knots'
                    # optional fields not provided
                }
            }

            data_definition_id = create_data_definition(variables)
            subscribe_to_data(data_definition_id, ...)
        """
        if data_def_id is None:
            data_def_id = self.new_def_id()
        self.data_definitions[data_def_id.value] = variables
        for name, var in variables.items():
            datum_name = var["DatumName"]
            units_name = var["UnitsName"]
            # Extract optional fields with default values
            var["DatumType"] = var.get("DatumType", SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64)  # Default to float
            datum_type = var["DatumType"]
            f_epsilon = var.get("fEpsilon", 0.0)  # Default to 0.0 if not provided
            datum_id = var.get("DatumID", SIMCONNECT_UNUSED)  # Default to 0 if not provided
            self.dll.AddToDataDefinition(
                self.hSimConnect,
                data_def_id.value,
                datum_name,
                units_name,
                datum_type,
                f_epsilon,
                datum_id
            )
        return data_def_id

    def subscribe_to_data(self, data_definition_id,
                          request_id=None,
                          flags=SIMCONNECT_DATA_REQUEST_FLAG.SIMCONNECT_DATA_REQUEST_FLAG_CHANGED,
                          object_id=SIMCONNECT_OBJECT_ID_USER_AIRCRAFT,
                          period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_SECOND,
                          origin=0, interval=0, limit=0):
        """https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/API_Reference/Events_And_Data/SimConnect_RequestDataOnSimObject.htm"""
        LOG.debug(
            f"Subscribing to data definition {data_definition_id.value}, period: {period.value}, interval: {interval}")
        if request_id is None:
            request_id = self.new_request_id()
        self.dll.RequestDataOnSimObject(
            self.hSimConnect,
            request_id.value,
            data_definition_id.value,
            object_id,
            period,
            flags,
            origin,
            interval,
            limit
        )
        return request_id.value

    def unsubscribe_from_data(self, request_id, data_definition_id,
                              object_id=SIMCONNECT_OBJECT_ID_USER_AIRCRAFT):
        LOG.debug(f"Unsubscribing from data: data_definition_id: {data_definition_id}, request_id: {request_id}")
        self.dll.RequestDataOnSimObject(
            self.hSimConnect,
            request_id,
            data_definition_id,
            object_id,
            SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_NEVER,
            SIMCONNECT_DATA_REQUEST_FLAG.SIMCONNECT_DATA_REQUEST_FLAG_DEFAULT,
            0,
            0,
            0
        )
        self.clear_data_definition(data_definition_id)

    def set_simobject_data(self, vars):
        """
            Example usage with required dictionaries:

            vars = {
                "altitude": {
                    "DatumName": b'PLANE ALTITUDE',
                    "UnitsName": b'Feet',  # make sure to pass the Unit you want to use
                    "DatumType": SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_FLOAT64,  # this will be the type in the struct
                    "Value": 1000.0  # this is the value to set
                },
                "speed": {
                    "DatumName": b'AIRSPEED INDICATED',
                    "UnitsName": b'Knots'
                    # optional fields not provided, default will be used (FLOAT64)
                    "Value": 1000.0
                }
            }
        """
        def_id = self.create_data_definition(vars)

        class data_struct(Struct1):
            _fields_ = [(v['DatumName'].decode('utf-8'), SIMCONNECT_DATATYPE_MAP[v['DatumType']]) for v in
                        vars.values()]

        data_values = {vars[key]['DatumName'].decode('utf-8'): vars[key]['Value'] for key in vars}

        struct_instance = data_struct(**data_values)

        # TODO: Passing arrays or as values
        err = self.dll.SetDataOnSimObject(
            self.hSimConnect,
            def_id.value,
            SIMCONNECT_SIMOBJECT_TYPE.SIMCONNECT_SIMOBJECT_TYPE_USER,
            0,  # Array size for passing multiple waypoints, etc
            0,  # Array element size in bytes
            sizeof(struct_instance),
            cast(byref(struct_instance), c_void_p)
        )

        self.clear_data_definition(def_id.value)

        if self.IsHR(err, 0):
            LOG.debug(f"Sim variable(s) set successfully:  {data_values}")
            return True
        else:
            return False

    def clear_data_definition(self, def_id):
        err = self.dll.ClearDataDefinition(self.hSimConnect, def_id)
        del self.data_definitions[def_id]
        if self.IsHR(err, 0):
            LOG.debug(f"Data Definition {def_id} cleared")
            return True
        else:
            return False

    def send_event(self, evnt, data=DWORD(0)):
        err = self.dll.TransmitClientEvent(
            self.hSimConnect,
            SIMCONNECT_OBJECT_ID_USER_AIRCRAFT,
            evnt.value,
            data,
            SIMCONNECT_GROUP_PRIORITY_HIGHEST,
            DWORD(16),
        )

        if self.IsHR(err, 0):
            LOG.debug(f"Event Sent: {evnt}")
            return True
        else:
            return False

    def enumerate_input_events(self):
        request_id = self.new_request_id().value
        self.dll.EnumerateInputEvents(self.hSimConnect, request_id)
        return request_id

    # TODO: No meaningful implementation for processing the received input event, use subscribe instead
    def get_input_event(self, event_hash):
        request_id = self.new_request_id()
        err = self.dll.GetInputEvent(self.hSimConnect, request_id.value, event_hash)
        if self.IsHR(err, 0):
            if LOG.level == logging.DEBUG:
                event_name = [name for name, val in self.input_event_hash.items() if val == event_hash]
                LOG.debug(f"Getting input event: hash: {event_hash}, name: {event_name}")
            return True
        else:
            return False

    def set_input_event(self, event_name, value=1.0):
        # Handle case where value is a float
        event_hash = self.input_event_hash[event_name]
        LOG.debug(f"Setting input event: hash:{event_hash}, name: {event_name}, value:{value}")
        if isinstance(value, float):
            value = c_double(value)
            cbUnitSize = sizeof(c_double)  # Size of the float
        if isinstance(value, list):
            cbUnitSize = sizeof(c_double) * len(value)
            value = (c_double * len(value))(*value)

        # TODO: Handle case where value is a string - MSFS devs said there are no events right now that expect String
        # elif isinstance(value, str):
        # 	# Encode string to bytes (UTF-8) and use c_char_p to represent it
        # 	value = ctypes.c_char_p(value.encode('utf-8'))
        # 	cbUnitSize = ctypes.sizeof(value)  # Size of the string (pointer size)
        elif not isinstance(value, _SimpleCData):
            raise TypeError(f"Unsupported type for input event value: {type(value)}")

        err = self.dll.SetInputEvent(self.hSimConnect, c_uint64(event_hash), cbUnitSize, byref(value))
        # Handle the error code returned by the API call
        if self.IsHR(err, 0):
            LOG.debug(f"Input event sent: {event_name}: {event_hash}")
            return True
        else:
            return False

    def subscribe_input_event(self, event_name):
        try:
            event_hash = self.input_event_hash[event_name]
        except KeyError:
            LOG.error(f"Input event not found in input_event_hash: {event_name}")
            return False
        err = self.dll.SubscribeInputEvent(self.hSimConnect, event_hash)
        if self.IsHR(err, 0):
            LOG.debug(f"Subscribed to input event: {event_name}: {event_hash}")
            return True
        else:
            return False

    def unsubscribe_input_event(self, event_name):
        try:
            event_hash = self.input_event_hash[event_name]
            return False
        except KeyError:
            LOG.error(f"Input event not found in input_event_hash: {event_name}")
        err = self.dll.UnsubscribeInputEvent(self.hSimConnect, event_hash)
        if self.IsHR(err, 0):
            LOG.debug(f"Unsubscribed from input event : {event_name}: {event_hash}")
            return True
        else:
            return False

    def new_def_id(self):
        _name = "DEFINITION_" + str(len(list(self.dll.DATA_DEFINITION_ID)))
        names = [m.name for m in self.dll.DATA_DEFINITION_ID] + [_name]
        self.dll.DATA_DEFINITION_ID = Enum(self.dll.DATA_DEFINITION_ID.__name__, names)
        DEFINITION_ID = list(self.dll.DATA_DEFINITION_ID)[-1]
        return DEFINITION_ID

    def new_request_id(self):
        name = "REQUEST_" + str(len(self.dll.DATA_REQUEST_ID))
        names = [m.name for m in self.dll.DATA_REQUEST_ID] + [name]
        self.dll.DATA_REQUEST_ID = Enum(self.dll.DATA_REQUEST_ID.__name__, names)
        REQUEST_ID = list(self.dll.DATA_REQUEST_ID)[-1]
        LOG.debug(f"New Request ID created:{REQUEST_ID}, total num: {len(self.dll.DATA_REQUEST_ID)}")
        return REQUEST_ID

    def add_waypoints(self, _waypointlist):
        if self.DEFINITION_WAYPOINT is None:
            self.DEFINITION_WAYPOINT = self.new_def_id()
            err = self.dll.AddToDataDefinition(
                self.hSimConnect,
                self.DEFINITION_WAYPOINT.value,
                b'AI WAYPOINT LIST',
                b'number',
                SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_WAYPOINT,
                0,
                SIMCONNECT_UNUSED,
            )
        pyarr = []
        for waypt in _waypointlist:
            for e in waypt._fields_:
                pyarr.append(getattr(waypt, e[0]))
        dataarray = (c_double * len(pyarr))(*pyarr)
        pObjData = cast(
            dataarray, c_void_p
        )
        sx = int(sizeof(c_double) * (len(pyarr) / len(_waypointlist)))
        return

    # hr = self.dll.SetDataOnSimObject(
    # 	self.hSimConnect,
    # 	self.DEFINITION_WAYPOINT.value,
    # 	SIMCONNECT_OBJECT_ID_USER_AIRCRAFT,
    # 	0,
    # 	len(_waypointlist),
    # 	sx,
    # 	pObjData
    # )
    # if self.IsHR(err, 0):
    # 	return True
    # else:
    # 	return False

    def set_pos(
            self,
            _Altitude,
            _Latitude,
            _Longitude,
            _Airspeed,
            _Pitch=0.0,
            _Bank=0.0,
            _Heading=0,
            _OnGround=0,
    ):
        Init = SIMCONNECT_DATA_INITPOSITION()
        Init.Altitude = _Altitude
        Init.Latitude = _Latitude
        Init.Longitude = _Longitude
        Init.Pitch = _Pitch
        Init.Bank = _Bank
        Init.Heading = _Heading
        Init.OnGround = _OnGround
        Init.Airspeed = _Airspeed

        if self.DEFINITION_POS is None:
            self.DEFINITION_POS = self.new_def_id()
            err = self.dll.AddToDataDefinition(
                self.hSimConnect,
                self.DEFINITION_POS.value,
                b'Initial Position',
                b'',
                SIMCONNECT_DATATYPE.SIMCONNECT_DATATYPE_INITPOSITION,
                0,
                SIMCONNECT_UNUSED,
            )

        hr = self.dll.SetDataOnSimObject(
            self.hSimConnect,
            self.DEFINITION_POS.value,
            SIMCONNECT_OBJECT_ID_USER_AIRCRAFT,
            0,
            0,
            sizeof(Init),
            pointer(Init)
        )
        if self.IsHR(hr, 0):
            return True
        else:
            return False

    def load_flight(self, flt_path):
        hr = self.dll.FlightLoad(self.hSimConnect, flt_path.encode())
        if self.IsHR(hr, 0):
            return True
        else:
            return False

    def load_flight_plan(self, pln_path):
        hr = self.dll.FlightPlanLoad(self.hSimConnect, pln_path.encode())
        if self.IsHR(hr, 0):
            return True
        else:
            return False

    def save_flight(
            self,
            flt_path,
            flt_title,
            flt_description,
            flt_mission_type='FreeFlight',
            flt_mission_location='Custom departure',
            flt_original_flight='',
            flt_flight_type='NORMAL'):
        hr = self.dll.FlightSave(self.hSimConnect, flt_path.encode(), flt_title.encode(), flt_description.encode(), 0)
        if not self.IsHR(hr, 0):
            return False

        dicp = self.flight_to_dic(flt_path)
        if 'MissionType' not in dicp['Main']:
            dicp['Main']['MissionType'] = flt_mission_type

        if 'MissionLocation' not in dicp['Main']:
            dicp['Main']['MissionLocation'] = flt_mission_location

        if 'FlightType' not in dicp['Main']:
            dicp['Main']['FlightType'] = flt_flight_type

        if 'OriginalFlight' not in dicp['Main']:
            dicp['Main']['OriginalFlight'] = flt_original_flight
        self.dic_to_flight(dicp, flt_path)

        return False

    def get_paused(self):
        hr = self.dll.RequestSystemState(
            self.hSimConnect,
            self.dll.EventID.EVENT_SIM_PAUSED,
            b"Sim"
        )

    def dic_to_flight(self, dic, fpath):
        with open(fpath, "w") as tempfile:
            for root in dic:
                tempfile.write("\n[%s]\n" % root)
                for member in dic[root]:
                    tempfile.write("%s=%s\n" % (member, dic[root][member]))

    def flight_to_dic(self, fpath):
        while not os.path.isfile(fpath):
            pass
        sleep(0.5)
        dic = {}
        index = ""
        with open(fpath, "r") as tempfile:
            for line in tempfile.readlines():
                if line[0] == '[':
                    index = line[1:-2]
                    dic[index] = {}
                else:
                    if index != "" and line != '\n':
                        temp = line.split("=")
                        dic[index][temp[0]] = temp[1].strip()
        return dic

    def sendText(self, text, timeSeconds=5, TEXT_TYPE=SIMCONNECT_TEXT_TYPE.SIMCONNECT_TEXT_TYPE_PRINT_WHITE):
        pyarr = bytearray(text.encode())
        dataarray = (c_char * len(pyarr))(*pyarr)
        pObjData = cast(dataarray, c_void_p)
        self.dll.Text(
            self.hSimConnect,
            TEXT_TYPE,
            timeSeconds,
            0,
            sizeof(c_double) * len(pyarr),
            pObjData
        )

    def createSimulatedObject(self, name, lat, lon, rqst, hdg=0, gnd=1, alt=0, pitch=0, bank=0, speed=0):
        simInitPos = SIMCONNECT_DATA_INITPOSITION()
        simInitPos.Altitude = alt
        simInitPos.Latitude = lat
        simInitPos.Longitude = lon
        simInitPos.Pitch = pitch
        simInitPos.Bank = bank
        simInitPos.Heading = hdg
        simInitPos.OnGround = gnd
        simInitPos.Airspeed = speed
        self.dll.AICreateSimulatedObject(
            self.hSimConnect,
            name.encode(),
            simInitPos,
            rqst.value
        )
