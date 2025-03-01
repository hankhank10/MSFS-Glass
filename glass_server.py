import configparser
import json
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, jsonify, render_template, request, abort, redirect

import subscribe_input_variables
import subscribe_variables
from SimConnect import *
from SimConnect import EventSet
from SimConnect.Enum import SIMCONNECT_PERIOD
from time import sleep
import logging
import socket
import datetime
import os

config = configparser.ConfigParser()
config_file = "config.ini"
config.read(config_file)

logging.basicConfig(
    format="%(asctime)s - %(filename)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s",
)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG if config['CONFIG']['loglevel'] == "debug" else logging.INFO)
LOG.info(socket.gethostbyname(socket.gethostname()))

logging.getLogger("SimConnect").setLevel(logging.DEBUG if config['CONFIG']['loglevel'] == "debug" else logging.INFO)

if "logfile" in config['CONFIG'].keys():
    fh = logging.FileHandler(config['CONFIG']['logfile'])
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    LOG.addHandler(fh)

ui_friendly_dictionary = {'created': True}
sm = None
selected_aircraft = ""
previous_aircraft = ""
aircraft_specific_def_id = None
aircraft_specific_req_id = None
manual_aircraft_selection = False

# list of kml files in program directroy
kml_list = []

cwd = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
files = os.listdir(cwd)
for file in files:
    if file.endswith("kml"):
        kml_list.append(file)

# Define Supported Aircraft
dir_aircraft = {
    "default": "Default",
    "default_gns430": "Default GNS430",
    "default_gns530": "Default GNS530",
    "default_g1000": "Default G1000",
    "asobo_c172sp_g1000": "Cessna 172 G1000",
    "asobo_c208b": "Cessna 208",
    "microsoft_c400_corvalis": "Cessna 400",
    "asobo_tbm930": "Daher TBM 930",
    "microsoft-a320neo": "A320neo",
    "microsoft-a321": "A321",
    "as_crj": "CRJ-550/700 (Aerosoft)",
    "pmdg_dc6": "DC-6 (PMDG)",
}


# Flask WebApp
def flask_thread_func(threadname):
    global ui_friendly_dictionary
    global sm
    global fltpln
    global selected_aircraft

    # Variable for dropdown menu
    aircraft_list = []
    for key, value in dir_aircraft.items():
        aircraft_list.append(value)

    # Variable to retrieve the dir name from the friendly name effectively
    aircraft_dir = {}
    for key, value in dir_aircraft.items():
        aircraft_dir[value] = key

    # Variable to populate the Navbar and templates
    aircraft_menu_dict = {
        "default": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["Panel", "panel"], ["Other", "other"]],
        "default_gns430": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["GPS", "gns430"], ["Panel", "panel"],
                           ["Other", "other"]],
        "default_gns530": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["GPS", "gns530"], ["Panel", "panel"],
                           ["Other", "other"]],
        "default_g1000": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g1000_pfd"], ["MFD", "g1000_mfd"],
                          ["Panel", "panel"], ["Other", "other"]],
        "asobo_c172sp_g1000": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g1000_pfd"], ["MFD", "g1000_mfd"],
                               ["Panel", "panel"], ["Other", "other"]],
        "microsoft_c400_corvalis": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g1000_pfd"], ["MFD", "g1000_mfd"],
                               ["Panel", "panel"], ["Other", "other"]],
        "asobo_c208b": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g1000_pfd"], ["MFD", "g1000_mfd"],
                        ["Panel", "panel"], ["Other", "other"]],
        "asobo_tbm930": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g3000_pfd"], ["MFD", "g3000_mfd"],
                               ["Panel", "panel"], ["Other", "other"]],
        "microsoft-a320neo": [["FCU", "ap"], ["EFIS", "efis"], ["COM", "com"], ["Panel", "panel"],
                              ["Other", "other"]],
        "microsoft-a321": [["FCU", "ap"], ["EFIS", "efis"], ["COM", "com"],
                           ["Panel", "panel"], ["Other", "other"]],
        "as_crj": [["FCP", "ap"], ["Side\xa0Panel", "side_panel"], ["NAV", "nav"],
                   ["COM", "com"], ["Other", "other"]],
        "pmdg_dc6": [["NAV", "nav"], ["COM", "com"], ["AFE", "afe"],
                     ["AP", "ap"], ["GPS", "gns430"], ["Other", "other"]],
    }

    selected_aircraft = "default"
    ui_friendly_dictionary["current_aircraft_ui_friendly"] = dir_aircraft[selected_aircraft]
    ui_friendly_dictionary["current_aircraft"] = selected_aircraft

    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)

    flask_log = logging.getLogger('werkzeug')
    flask_log.disabled = True

    @app.route('/ui')
    def output_ui_variables():
        # Initialise dictionary
        ui_friendly_dictionary["STATUS"] = "success"
        return jsonify(ui_friendly_dictionary)

    @app.route('/sync_aircraft')
    def sync_aircraft():
        if sm is not None:
            try:
                sm.load_selected_aircraft()
                sm.enumerate_input_events()
            except OSError as err:
                LOG.error(f"OS error: {err}. Connection to MSFS is probably not established.")
        referer = request.headers.get('Referer', '/')
        reload_url = f"{referer}?reload=true"
        return redirect(reload_url)


    @app.route('/', methods=["GET", "POST"])
    @app.route('/landscape', methods=["GET", "POST"])
    @app.route('/test', methods=["GET", "POST"])
    def index():
        global selected_aircraft
        global previous_aircraft
        global manual_aircraft_selection
        # We are getting friendly name from the FE
        ui_selected_aircraft = request.form.get("plane_selected")
        api_key_input = request.form.get("api_key")
        manual_aircraft_selection = True if request.form.get("manual_aircraft_selection",
                                                             "").lower() == "true" else False
        api_key = ''
        if api_key_input is not None:
            config['CONFIG']['openaipapikey'] = api_key_input
            save_config()
        try:
            api_key = config['CONFIG']['openaipapikey']
        except KeyError:
            LOG.warning("OpenAIP API key not set in config file")

        # If there is no implementation for aircraft, change to default and manual selection
        if selected_aircraft not in dir_aircraft.keys():
            previous_aircraft = selected_aircraft
            selected_aircraft = "default"
            manual_aircraft_selection = True

        if ui_selected_aircraft is not None:
            previous_aircraft = selected_aircraft
            selected_aircraft = aircraft_dir[ui_selected_aircraft]
            ui_friendly_dictionary["current_aircraft_ui_friendly"] = ui_selected_aircraft

        template = "index_landscape.html" if request.path == "/landscape" else "index.html"
        if request.path == "/test":
            template = "index-ml.html"
        LOG.debug(
            f"Loading template: {template}, selected_aircraft: {selected_aircraft}, manual_aircraft_selection: {manual_aircraft_selection}")
        return render_template(template,
                               aircraft_list=aircraft_list,  # these are friendly names for the dropdown
                               current_aircraft_ui_friendly=dir_aircraft[
                                   selected_aircraft] if dir_aircraft.keys().__contains__(
                                   selected_aircraft) else "Default",  # we need friendly name for UI
                               aircraft_menu_tabs=aircraft_menu_dict[selected_aircraft],
                               aircraft_dir=selected_aircraft,  # dir name for templates
                               api_key=api_key,  # OpenAIP api key
                               manual_aircraft_selection=manual_aircraft_selection)  # manual selection checkbox

    # returns the list of available KML files
    @app.route('/kml', methods=["GET"])
    def get_list_of_kmls():
        return jsonify(kml_list)

    # returns the requested KML file or 404 if the file is not found
    @app.route('/kml/<file>', methods=["GET"])
    def get_kml_file_content(file):
        try:
            return read_file(file)
        except:
            return abort(404)

    def trigger_event(event_name, value_to_use=None, event_type=None):
        # This function actually does the work of triggering the event
        LOG.debug(f"Triggering event: {event_name}: {value_to_use} {event_type}")
        if event_type == '' or event_type == "aircraft":
            if event_name in EventSet.valid_events:
                event = sm.map_to_sim_event(event_name)
                if value_to_use is None:
                    sm.send_event(event, DWORD(0))
                else:
                    if event_name == "NAV1_RADIO_SET" or event_name == "NAV2_RADIO_SET":
                        freq_hz = float(value_to_use) * 100
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit) * (16 ** (figure))
                        sm.send_event(event, DWORD(int(freq_hz_bcd)))
                    elif event_name == "ADF_COMPLETE_SET":
                        freq_hz = int(value_to_use) * 10000
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit) * (16 ** (figure))
                        sm.send_event(event, DWORD(int(freq_hz_bcd)))
                    elif event_name == "COM_RADIO_SET" or event_name == "COM2_RADIO_SET":
                        freq_hz = float(value_to_use) * 100
                        flag_3dec = int(freq_hz) != freq_hz
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit) * (16 ** (figure))
                        sm.send_event(event, DWORD(int(freq_hz_bcd)))
                        # Workaround for 3rd decimal
                        if flag_3dec is True and str(value_to_use)[-2:] != "25" and str(value_to_use)[-2:] != "75":
                            if event_name == "COM_RADIO_SET":
                                trigger_event("COM_STBY_RADIO_SWAP")
                                trigger_event("COM_RADIO_FRACT_INC")
                                trigger_event("COM_STBY_RADIO_SWAP")
                            else:
                                trigger_event("COM2_RADIO_SWAP")
                                trigger_event("COM2_RADIO_FRACT_INC")
                                trigger_event("COM2_RADIO_SWAP")
                    elif event_name == "XPNDR_SET":
                        freq_hz = int(value_to_use) * 1
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit) * (16 ** (figure))
                        sm.send_event(event, DWORD(int(freq_hz_bcd)))
                    else:
                        sm.send_event(event, DWORD(int(value_to_use)))
            status = "success"
        elif event_type == "input":
            # Range knows are working only unfortunately if we don't touch the in game knobs
            if event_name in (
                    "AS1000_RANGE_ZOOM_MFD", "AS1000_RANGE_ZOOM_PFD", "AS1000_FMS_UPPER_PFD", "AS1000_FMS_UPPER_MFD",
                    "AS1000_FMS_LOWER_PFD", "AS1000_FMS_LOWER_MFD"):
                sm.subscribed_data[event_name] += value_to_use
                sm.set_input_event(event_name, float(sm.subscribed_data[event_name]))
            elif event_name == "AS1000_RANGE_MFD" or event_name == "AS1000_RANGE_PFD":
                sm.set_input_event(event_name, value_to_use)
                sleep(0.5)
                sm.set_input_event(event_name, [0.0, 0.0, 0.0])
            else:
                sm.set_input_event(event_name, float(value_to_use))
                if event_name in sm.subscribed_data.keys():
                    sm.subscribed_data[event_name] = value_to_use
                LOG.debug(f"Triggered event: {event_name}, {value_to_use}, {event_type}")
            status = "success"
        elif event_type == "lvar":

            variable = {
                event_name.encode(): {
                    "DatumName": event_name.encode(),  # don't go crazy with the LVars :)
                    "UnitsName": b'Bool',
                    "Value": value_to_use
                }
            }

            sm.set_simobject_data(variable)

            status = "success"
        else:
            status = "Error: %s is not an Event" % event_name

        return status

    @app.route('/event/<event_name>/trigger', methods=["POST"])
    def trigger_event_endpoint(event_name):
        # This is the http endpoint wrapper for triggering an event
        ds = request.get_json() if request.is_json else request.form
        value_to_use = json.loads(ds.get('value_to_use'))
        event_type = ds.get('event_type')
        status = trigger_event(event_name, value_to_use, event_type)

        return jsonify(status)

    # Load Flight Plan
    fltpln = []

    @app.route('/fltpln', methods=["POST"])
    def load_fltpln():
        # Load Settings - MSFS Install Location
        try:
            base_dir = config['CONFIG']['msfsbasedir']
            try:
                # MS Store
                fltpln_dir_full = base_dir + '\\LocalState\\MISSIONS\\Custom\\CustomFlight\\CustomFlight.FLT'
                with open(fltpln_dir_full, 'r') as fltpln:
                    LOG.debug(f"Loading fltpln: {fltpln_dir_full}")
                    fltpln_lines = fltpln.readlines()
            except:
                # Steam
                fltpln_dir_full = base_dir + '\\MISSIONS\\Custom\\CustomFlight\\CustomFlight.FLT'
                with open(fltpln_dir_full, 'r') as fltpln:
                    LOG.debug(f"Loading fltpln: {fltpln_dir_full}")
                    fltpln_lines = fltpln.readlines()

            # Process Flight Plan Function
            def latlong_dec_convert(to_convert):
                """Function converts deg/min/sec to decimal"""
                elements = to_convert.split(" ")
                conversion = 0
                for element in elements:
                    # Degrees Conversion
                    if element[-1] == "°":
                        conversion = conversion + float(element[1:-1])
                        continue
                    # Minutes Conversion
                    if element[-1] == "'":
                        conversion = conversion + (float(element[0:-1]) / 60)
                        continue
                    # Seconds Conversion
                    if element[-1] == '"':
                        conversion = conversion + (float(element[0:-1]) / 3600)
                        continue

                # Degrees Conversion Negative/Positive
                if elements[0][0] in ["W", "S"]:
                    conversion = conversion * (-1)

                return conversion

            # Check if ATC_RequestedFlightPlan
            atc_reqfltpln = False
            for idx, line in enumerate(fltpln_lines):
                if line.find("[ATC_RequestedFlightPlan.0]") >= 0:
                    atc_reqfltpln = True
                    fltpln_lines = fltpln_lines[(idx + 1):]
                    break

            # Process FLT file
            if atc_reqfltpln == False:
                # For VFR Flights
                # Get No of Waypoints
                no_wpts = 0
                for line in fltpln_lines:
                    if line.find("NumberofWaypoints=") >= 0:
                        no_wpts = int(line.split("=")[1])
                        break

                # Get LatLong for Waypoitns
                fltpln_arr = []
                wpts_processed = 0
                for line in fltpln_lines:
                    if wpts_processed < no_wpts:
                        if line.find("Waypoint.") >= 0:
                            line_elements = line.split(",")
                            fltpln_wp = [latlong_dec_convert(
                                line_elements[5].strip()), latlong_dec_convert(line_elements[6].strip())]
                            fltpln_arr.append(fltpln_wp)
                            wpts_processed = wpts_processed + 1
                    else:
                        break

            else:
                # For IFR Flights
                fltpln_arr = []
                wpt_id = False
                for line in fltpln_lines:
                    if line.find("waypoint.") >= 0:
                        line_elements = line.split(",")
                        fltpln_wp = [latlong_dec_convert(
                            line_elements[5].strip()), latlong_dec_convert(line_elements[6].strip())]
                        fltpln_arr.append(fltpln_wp)
                        wpt_id = True
                    else:
                        if wpt_id == True:
                            break

            ui_friendly_dictionary["FLT_PLN"] = fltpln_arr

            success = "Flight plan loaded"

        except:
            LOG.warning(
                "Error loading flight plan. Make sure you have the correct MSFS installation path in config.ini.")
            success = "Error loading flight plan"

        return success

    app.run(host='0.0.0.0', port=4000, debug=False)


# SimConnect  App
def simconnect_thread_func(threadname):
    global ui_friendly_dictionary
    global event_name
    global sm

    ui_friendly_dictionary["connected"] = False

    try:
        # This call is blocking until the sim is ready
        sm = SimConnect(name="MSFS Glass")
        LOG.info("********* MSFS Glass *********")
        LOG.info(f"Local web server for MSFS Glass initialized.")
        LOG.info(
            f"Launch {socket.gethostbyname(socket.gethostname())}:4000 in your browser to access MSFS Glass.")
        LOG.info(
            f"Make sure your your mobile device is connected to the same local network (WIFI) as this PC.")
        LOG.info(
            f"Notice: If your computer has more than one active ethernet/WIFI adapter, please check ipconfig in command prompt.")
        LOG.info("**************************************************")
    except Exception as e:
        LOG.error(f"Something went wrong: {e}")

    radio_vars_def_id = sm.create_data_definition(subscribe_variables.radio_vars)
    radio_vars_req_id = sm.subscribe_to_data(radio_vars_def_id, period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_VISUAL_FRAME,
                                             interval=15)

    ui_vars_def_id = sm.create_data_definition(subscribe_variables.ui_vars)
    ui_vars_req_id = sm.subscribe_to_data(ui_vars_def_id, period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_VISUAL_FRAME,
                                          interval=15)

    landing_vars_def_id = sm.create_data_definition(subscribe_variables.landing_vars)
    landing_vars_req_id = sm.subscribe_to_data(landing_vars_def_id, period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_SECOND,
                                               interval=5)

    pos_vars_def_id = sm.create_data_definition(subscribe_variables.pos_vars)
    pos_vars_req_id = sm.subscribe_to_data(pos_vars_def_id, period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_VISUAL_FRAME,
                                           interval=5)

    # Wait a bit for the data subscriptions
    sleep(0.3)

    # Initialize previous altitude for code stability
    previous_alt = -400

    # Initialize vars for landing info
    ui_friendly_dictionary["LANDING_VS1"] = "N/A"
    ui_friendly_dictionary["LANDING_T1"] = 0
    ui_friendly_dictionary["LANDING_G1"] = "N/A"
    ui_friendly_dictionary["LANDING_VS2"] = "N/A"
    ui_friendly_dictionary["LANDING_T2"] = 0
    ui_friendly_dictionary["LANDING_G2"] = "N/A"
    ui_friendly_dictionary["LANDING_VS3"] = "N/A"
    ui_friendly_dictionary["LANDING_T3"] = 0
    ui_friendly_dictionary["LANDING_G3"] = "N/A"
    ui_friendly_dictionary["connected"] = True

    def thousandify(x):
        return f"{x:,}"

    def ui_dictionary():
        global ui_friendly_dictionary
        global sm
        global selected_aircraft
        global previous_aircraft

        if sm.selected_aircraft in dir_aircraft.keys():
            if manual_aircraft_selection is False:
                previous_aircraft = selected_aircraft
                selected_aircraft = sm.selected_aircraft
        else:
            if manual_aircraft_selection is False and selected_aircraft != "default":
                LOG.debug(f"Selected aircraft {selected_aircraft} is not implemented. Falling back to default.")
                previous_aircraft = selected_aircraft
                selected_aircraft = "default"

        if selected_aircraft != ui_friendly_dictionary["current_aircraft"]:
            LOG.debug(f"Changing to aircraft {selected_aircraft}")
            change_aircraft()
        ui_friendly_dictionary["current_aircraft"] = selected_aircraft


        for var in sm.subscribed_data.keys():
            if var in ("latitude", "longitude"):
                ui_friendly_dictionary[var.upper()] = round(sm.subscribed_data[var], 6)

            elif var in ("plane_heading_degrees_magnetic", "nav1_standby", "nav1_active", "nav2_standby", "nav2_active"):
                ui_friendly_dictionary[var.upper()] = round(sm.subscribed_data[var], 2)

            elif var in ("com1_standby", "com1_active", "com2_standby", "com2_active"):
                ui_friendly_dictionary[var.upper()] = round(sm.subscribed_data[var], 3)

            elif var in ("altitude", "heading", "total_weight", "nav1_obs", "nav2_obs", "adf_card", "airspeed_indicated", "ap_heading_lock_dir", "ap_altitude_lock_var", "ap_airspeed_hold_var"):
                ui_friendly_dictionary[var.upper()] = round(sm.subscribed_data[var])

            elif var in ("flaps_handle_percent"):
                ui_friendly_dictionary[var.upper()] = round(sm.subscribed_data[var] * 100)

            elif var == "xpndr":
                xpndr_digits = str(int(sm.subscribed_data[var]))
                ui_friendly_dictionary["XPNDR"] = int(xpndr_digits)

                if int(xpndr_digits) > 1000:
                    ui_friendly_dictionary["XPNDR_1000"] = xpndr_digits[0]
                    ui_friendly_dictionary["XPNDR_100"] = xpndr_digits[1]
                    ui_friendly_dictionary["XPNDR_10"] = xpndr_digits[2]
                    ui_friendly_dictionary["XPNDR_1"] = xpndr_digits[3]
                elif xpndr_digits != "0":
                    ui_friendly_dictionary["XPNDR_1000"] = "0"
                    ui_friendly_dictionary["XPNDR_100"] = xpndr_digits[0]
                    ui_friendly_dictionary["XPNDR_10"] = xpndr_digits[1]
                    ui_friendly_dictionary["XPNDR_1"] = xpndr_digits[2]

            elif var == "adf1_active":
                adf_active = int(sm.subscribed_data[var])
                adf_active_arr = str(adf_active)

                ui_friendly_dictionary["ADF_USE_1000"] = adf_active_arr[0]
                ui_friendly_dictionary["ADF_USE_100"] = adf_active_arr[1]
                ui_friendly_dictionary["ADF_USE_10"] = adf_active_arr[2]
                ui_friendly_dictionary["ADF_USE_1"] = adf_active_arr[3]
                ui_friendly_dictionary["ADF_USE"] = adf_active

            elif var == "adf1_standby":
                adf_stby = int(sm.subscribed_data[var])
                adf_stby_arr = str(adf_stby)

                if adf_stby >= 1000:
                    ui_friendly_dictionary["ADF_STBY_1000"] = adf_stby_arr[0]
                    ui_friendly_dictionary["ADF_STBY_100"] = adf_stby_arr[1]
                    ui_friendly_dictionary["ADF_STBY_10"] = adf_stby_arr[2]
                    ui_friendly_dictionary["ADF_STBY_1"] = adf_stby_arr[3]
                else:
                    ui_friendly_dictionary["ADF_STBY_1000"] = "0"
                    ui_friendly_dictionary["ADF_STBY_100"] = adf_stby_arr[0]
                    ui_friendly_dictionary["ADF_STBY_10"] = adf_stby_arr[1]
                    ui_friendly_dictionary["ADF_STBY_1"] = adf_stby_arr[2]
            else:
                ui_friendly_dictionary[var.upper()] = sm.subscribed_data[var]






        # LOC and APPR Mode

        if (ui_friendly_dictionary["AP_APPROACH_HOLD"] == 1 and ui_friendly_dictionary[
            "AP_GLIDESLOPE_HOLD"] == 1):
            ui_friendly_dictionary["AP_APPR_MODE"] = 1
        else:
            ui_friendly_dictionary["AP_APPR_MODE"] = 0
        if (ui_friendly_dictionary["AP_APPROACH_HOLD"] == 1 and ui_friendly_dictionary[
            "AP_GLIDESLOPE_HOLD"] == 0):
            ui_friendly_dictionary["AP_LOC_MODE"] = 1
        else:
            ui_friendly_dictionary["AP_LOC_MODE"] = 0

        # Other

        current_landing = round(sm.subscribed_data["plane_touchdown_normal_velocity"] * 60)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        # Calculate Custom G-Force based on vertical speed
        # Model uses Harvsine acceleration model for peak acceleration https://www.nhtsa.gov/sites/nhtsa.dot.gov/files/18esv-000501.pdf
        # For time a custom function is used that ranges from 0.25 for GA to 0.35 for airliners. This simulates the rigidness of suspention.
        try:
            aircraft_weight = sm.subscribed_data["total_weight"]
        except:
            aircraft_weight = 0
        aircraft_weight_adj = max(round(aircraft_weight * 0.45), 200)
        custom_g_force_impact_duration = 0.355 + (-0.103 / (1 + (aircraft_weight_adj / 15463) ** 1.28))

        if ui_friendly_dictionary["LANDING_VS1"] != current_landing:
            # Move 2nd to 3rd
            ui_friendly_dictionary["LANDING_T3"] = ui_friendly_dictionary["LANDING_T2"]
            ui_friendly_dictionary["LANDING_VS3"] = ui_friendly_dictionary["LANDING_VS2"]
            ui_friendly_dictionary["LANDING_G3"] = ui_friendly_dictionary["LANDING_G2"]
            # Move 1st to 2nd
            ui_friendly_dictionary["LANDING_T2"] = ui_friendly_dictionary["LANDING_T1"]
            ui_friendly_dictionary["LANDING_VS2"] = ui_friendly_dictionary["LANDING_VS1"]
            ui_friendly_dictionary["LANDING_G2"] = ui_friendly_dictionary["LANDING_G1"]
            # Assign new 1st
            ui_friendly_dictionary["LANDING_VS1"] = current_landing
            ui_friendly_dictionary["LANDING_T1"] = current_time
            ui_friendly_dictionary["LANDING_G1"] = round(
                1 + (((2 * (current_landing / (60 * 3.281))) / custom_g_force_impact_duration) / 9.80665), 2)



    while True:
        try:
            ui_dictionary()
        except KeyError as err:
            LOG.debug(
                f"Key not found in subscribed_data dictionary: {str(err)}. This is normal at the very beginning of the ui_dictionary loop.")
        except Exception as err:
            LOG.error(f"Exception occured: {str(err)}")
        sleep(0.25)


def read_file(filename, directory=cwd):
    path = os.path.join(directory, filename)
    contents = None
    with open(path, "rb") as file:
        contents = file.read()
    return contents


def change_aircraft():
    global selected_aircraft
    global previous_aircraft
    global sm
    global aircraft_specific_def_id
    global aircraft_specific_req_id

    LOG.debug(f"Changing aircraft to {selected_aircraft}")
    LOG.debug(aircraft_specific_def_id)
    LOG.debug(aircraft_specific_req_id)

    # Unsubscribe if the last plan had also aircraft specific vars
    if aircraft_specific_req_id is not None and aircraft_specific_def_id is not None:
        LOG.debug("Unsubscribing from aircraft specific vars")
        sm.unsubscribe_from_data(aircraft_specific_req_id, aircraft_specific_def_id.value)

    var_selected_aircraft = selected_aircraft.replace("-", "_").replace(" ", "_")
    var_previous_aircraft = previous_aircraft.replace("-", "_").replace(" ", "_")

    # If there are aircraft specific vars we want to subscribe to
    if getattr(subscribe_variables, var_selected_aircraft, None) is not None:
        LOG.debug("Subscribing to aircraft specific vars")
        aircraft_specific_def_id = sm.create_data_definition(getattr(subscribe_variables, var_selected_aircraft),
                                                             data_def_id=aircraft_specific_def_id)
        aircraft_specific_req_id = sm.subscribe_to_data(aircraft_specific_def_id,
                                                        request_id=aircraft_specific_req_id,
                                                        period=SIMCONNECT_PERIOD.SIMCONNECT_PERIOD_VISUAL_FRAME,
                                                        interval=15)
    else:
        LOG.debug("No aircraft specific vars")
        aircraft_specific_req_id = None
        aircraft_specific_def_id = None

    # unsub from input events
    if getattr(subscribe_input_variables, var_previous_aircraft, None) is not None:
        for var in getattr(subscribe_input_variables, var_previous_aircraft):
            sm.unsubscribe_input_event(var[0])
            del sm.subscribed_data[var[0]]

    # sub and initalize input events
    try:
        if getattr(subscribe_input_variables, var_selected_aircraft, None) is not None:
            for var in getattr(subscribe_input_variables, var_selected_aircraft):
                sm.subscribe_input_event(var[0])
                sm.subscribed_data[var[0]] = var[1]
    except Exception as err:
        LOG.error(f"Exception occurred, probably no InputEvent called {str(err)} for aircraft.")

    # Clumsy workaround for G1000 Range/FMS knob bug in MSFS
    if selected_aircraft in ["default_g1000", "asobo_c172sp_g1000", "asobo_208b", "microsoft_c400_corvalis"]:
        LOG.debug("G1000 detected, workaround for range knobs")
        sm.subscribed_data["AS1000_RANGE_ZOOM_PFD"] = 0
        sm.subscribed_data["AS1000_RANGE_ZOOM_MFD"] = 0

        # these should work but the input events are only returning 0s from these
        # sm.subscribe_input_event("AS1000_RANGE_ZOOM_PFD")
        # sm.subscribe_input_event("AS1000_RANGE_ZOOM_MFD")

    else:
        if "AS1000_RANGE_ZOOM_PFD" in sm.subscribed_data.keys():
            # sm.unsubscribe_input_event("AS1000_RANGE_ZOOM_PFD")
            # sleep(0.1)
            del sm.subscribed_data["AS1000_RANGE_ZOOM_PFD"]
        if "AS1000_RANGE_ZOOM_MFD" in sm.subscribed_data.keys():
            # sm.unsubscribe_input_event("AS1000_RANGE_ZOOM_MFD")
            # sleep(0.1)
            del sm.subscribed_data["AS1000_RANGE_ZOOM_MFD"]



def save_config():
    global config
    global config_file
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def signal_handler(sig, frame):
    LOG.info("Gracefully shutting down...")
    global sm
    sm.exit()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(simconnect_thread_func, 'Simconnect Client')
        executor.submit(flask_thread_func, 'Webserver')

    sleep(.5)
