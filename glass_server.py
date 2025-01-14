import json

from flask import Flask, jsonify, render_template, request, abort, redirect
from SimConnect import *
from SimConnect.simconnect_mobiflight import SimConnectMobiFlight
from SimConnect.mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep
import logging
import math
import socket
import asyncio
from threading import Thread
import datetime
import os

print(socket.gethostbyname(socket.gethostname()))

ui_friendly_dictionary = {}
event_name = None
value_to_use = None
sm = None
ae = None
selected_plane = ""

# list of kml files in program directroy
kml_list = []
LOG = logging.getLogger('SimConnect')
LOG.setLevel(logging.INFO)

cwd = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))
files = os.listdir(cwd)
for file in files:
    if(file.endswith("kml")):
        kml_list.append(file)

# Flask WebApp
def flask_thread_func(threadname):

    global ui_friendly_dictionary
    global event_name
    global value_to_use
    global sm
    global ae
    global fltpln
    global api_key

    # Define Supported Aircraft
    planes_list = [
        "Default",
        "Default GNS430",
        "Default GNS530",
        "Default G1000",
        "A320 (Asobo)",
        "A32NX (FlyByWire)",
        "CRJ-550/700 (Aerosoft)",
        "DC-6 (PMDG)",
        "FG-1D Corsair (MilViz)",
        "Ju-52 Classic (Asobo)",
        "Ju-52 Retrofit (Asobo)",
        "Long-EZ (IndiaFoxtEcho)",
        "MB-339 (IndiaFoxtEcho)",
        "PA-28R Arrow III GPS100 (Just Flight)",
        "PA-28R Arrow III GNS530 (Just Flight)",
        "PA-28R Arrow III GNS Dual (Just Flight)"
    ]
    planes_dict = {
        "Default": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["Panel", "panel"], ["Other", "other"]],
        "Default GNS430": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["GPS", "gns430"], ["Panel", "panel"], ["Other", "other"]],
        "Default GNS530": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["GPS", "gns530"], ["Panel", "panel"], ["Other", "other"]],
        "Default G1000": [["NAV", "nav"], ["COM", "com"], ["AP", "ap"], ["PFD", "g1000_pfd"], ["MFD", "g1000_mfd"], ["Panel", "panel"], ["Other", "other"]],
        "A320 (Asobo)": [["FCU", "ap_a320"], ["EFIS", "efis_a320"], ["COM", "com"], ["Panel", "panel_a320"], ["Other", "other_a32nx"]],
        "A32NX (FlyByWire)": [["FCU", "ap_a32nx_dev"], ["EFIS", "efis_a32nx_dev"], ["COM", "com"], ["Panel", "panel_a32nx_dev"], ["Other", "other_a32nx"]],
        "CRJ-550/700 (Aerosoft)": [["FCP", "ap_as_crj"], ["Side\xa0Panel", "side_panel_as_crj"], ["NAV", "nav_as_crj"], ["COM", "com_as_crj"], ["Other", "other_as_crj"]],
        "DC-6 (PMDG)": [["NAV", "nav_pmdg_dc6"], ["COM", "com_pmdg_dc6"], ["AFE", "afe_pmdg_dc6"], ["AP", "ap_pmdg_dc6"], ["GPS", "gns430"], ["Other", "other_pmdg_dc6"]],
        "FG-1D Corsair (MilViz)": [["NAV", "nav_milviz_corsair"], ["COM", "com_milviz_corsair"], ["Engine", "engine_milviz_corsair"], ["Panel", "panel_milviz_corsair"], ["Other", "other_milviz_corsair"]],
        "Ju-52 Classic (Asobo)": [["NAV", "nav_aso_ju52c"], ["COM", "com_aso_ju52c"], ["AP", "ap_aso_ju52c"], ["Panel", "panel_aso_ju52c"], ["Other", "other_aso_ju52"]],
        "Ju-52 Retrofit (Asobo)": [["NAV", "nav_aso_ju52"], ["COM", "com_aso_ju52"], ["Panel", "panel_aso_ju52"], ["Other", "other_aso_ju52"]],
        "Long-EZ (IndiaFoxtEcho)": [["COM", "com_ife_long_ez"], ["Panel", "panel_ife_long_ez"], ["Other", "other_ife_long_ez"]],
        "MB-339 (IndiaFoxtEcho)": [["NAV", "nav_ife_mb339"], ["COM", "com_ife_mb339"], ["FLT\xa0DIR", "flt_dir_ife_mb339"], ["AP", "ap_ife_mb339"], ["Panel", "panel_ife_mb339"], ["Other", "other"]],
        "PA-28R Arrow III GPS100 (Just Flight)": [["NAV", "nav_jf_arrow_gps100"], ["COM", "com_jf_arrow_gps100"], ["AP", "ap_jf_arrow"], ["GPS", "gps100_jf_arrow"], ["Panel", "panel_jf_arrow"], ["Other", "other_no_spd_ailr"]],
        "PA-28R Arrow III GNS530 (Just Flight)": [["NAV", "nav_jf_arrow_gns"], ["COM", "com_jf_arrow_gns"], ["AP", "ap_jf_arrow"], ["GPS", "gns530"], ["Panel", "panel_jf_arrow"], ["Other", "other_no_spd_ailr"]],
        "PA-28R Arrow III GNS Dual (Just Flight)": [["NAV", "nav_jf_arrow_gnsdual"], ["COM", "com_jf_arrow_gnsdual"], ["AP", "ap_jf_arrow"], ["GPS", "gnsdual_jf_arrow"], ["Panel", "panel_jf_arrow"], ["Other", "other_no_spd_ailr"]]
    }

    global selected_plane
    selected_plane = planes_list[0]
    ui_friendly_dictionary["selected_plane"] = selected_plane

    app = Flask(__name__)
    flask_log = logging.getLogger('werkzeug')
    flask_log.disabled = True


    @app.route('/ui')
    def output_ui_variables():
        # Initialise dictionaru
        ui_friendly_dictionary["STATUS"] = "success"
        return jsonify(ui_friendly_dictionary)

    @app.route('/sync_aircraft')
    def sync_aircraft():
        if sm is not None:
            sm.load_selected_plane()
        referer = request.headers.get('Referer', '/')
        reload_url = f"{referer}?reload=true"
        return redirect(reload_url)


    @app.route('/', methods=["GET", "POST"])
    def index():
        global selected_plane
        global api_key
        cur_plane_select = request.form.get("plane_selected")
        api_key = request.form.get("api_key")
        if cur_plane_select != None:
            selected_plane = cur_plane_select
            ui_friendly_dictionary["selected_plane"] = selected_plane
        return render_template('glass.html', planes_list=planes_list, selected_plane=selected_plane, curr_plane=planes_dict[selected_plane], api_key=api_key)

    @app.route('/landscape', methods=["GET", "POST"])
    def index_landscape():
        global selected_plane
        global api_key
        cur_plane_select = request.form.get("plane_selected")
        api_key = request.form.get("api_key")
        if cur_plane_select != None:
            selected_plane = cur_plane_select
            ui_friendly_dictionary["selected_plane"] = selected_plane
        return render_template('glass_landscape.html', planes_list=planes_list, selected_plane=selected_plane, curr_plane=planes_dict[selected_plane], api_key=api_key)

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
        LOG.debug(f"Triggered event: {event_name}: {value_to_use} {event_type}")
        if event_type == '' or event_type == "aircraft":
            EVENT_TO_TRIGGER = ae.find(event_name)
            if EVENT_TO_TRIGGER is not None:
                if value_to_use is None:
                    EVENT_TO_TRIGGER()
                else:
                    # Convert Hz BCD for NAV1_RADIO_SET, NAV2_RADIO_SET and AD_SET events
                    if event_name == "NAV1_RADIO_SET" or event_name == "NAV2_RADIO_SET":
                        freq_hz = float(value_to_use) * 100
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit)*(16**(figure))
                        EVENT_TO_TRIGGER(int(freq_hz_bcd))
                    elif event_name == "ADF_COMPLETE_SET":
                        freq_hz = int(value_to_use) * 10000
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit)*(16**(figure))
                        EVENT_TO_TRIGGER(int(freq_hz_bcd))
                    elif event_name == "COM_RADIO_SET" or event_name == "COM2_RADIO_SET":
                        freq_hz = float(value_to_use) * 100
                        flag_3dec = int(freq_hz) != freq_hz
                        freq_hz = str(int(freq_hz))
                        freq_hz_bcd = 0
                        for figure, digit in enumerate(reversed(freq_hz)):
                            freq_hz_bcd += int(digit)*(16**(figure))
                        EVENT_TO_TRIGGER(int(freq_hz_bcd))
                        # Workarouund for 3rd decimal
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
                            freq_hz_bcd += int(digit)*(16**(figure))
                        EVENT_TO_TRIGGER(int(freq_hz_bcd))
                    else:
                        EVENT_TO_TRIGGER(int(value_to_use))
            status = "success"
        elif event_type == "input":
            if event_name == "AS1000_RANGE_MFD" or event_name == "AS1000_RANGE_PFD":
                sm.set_input_event(sm.input_event_hash[event_name], value_to_use)
                sleep(0.5)
                sm.set_input_event(sm.input_event_hash[event_name], [0.0, 0.0, 0.0])
            else:
                print("triggering event: ", event_name, value_to_use, event_type)
                sm.set_input_event(sm.input_event_hash[event_name], float(value_to_use))

            status = "success"
        else:
            status = "Error: %s is not an Event" % (event_name)

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
            with open('settings.txt', 'r') as settings:
                lines = settings.readlines()

            # Get Flight Plan
            fltpln_dir = ""
            for line in lines:
                if len(line) > 0:
                    if line[0] != "#":
                        fltpln_dir = line
                        # Check to delete \ at the endswith
                        if fltpln_dir[-1] == "\\":
                            fltpln_dir = fltpln_dir[:-1]
                        break

            try:
                # MS Store
                fltpln_dir_full = fltpln_dir + '\LocalState\MISSIONS\Custom\CustomFlight\CUSTOMFLIGHT.FLT'
                with open(fltpln_dir_full, 'r') as fltpln:
                    fltpln_lines = fltpln.readlines()
            except:
                # Steam
                fltpln_dir_full = fltpln_dir + '\MISSIONS\Custom\CustomFlight\CUSTOMFLIGHT.FLT'
                with open(fltpln_dir_full, 'r') as fltpln:
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
                        conversion = conversion + (float(element[0:-1])/60)
                        continue
                    # Seconds Conversion
                    if element[-1] == '"':
                        conversion = conversion + (float(element[0:-1])/3600)
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
            print("Error loading flight plan. Make sure you have the correct MSFS installation path in settings.txt.")
            success = "Error loading flight plan"

        return success

    app.run(host='0.0.0.0', port=4000, debug=False)

# SimConnect  App
def simconnect_thread_func(threadname):

    global ui_friendly_dictionary
    global event_name
    global value_to_use
    global sm
    global ae

    while True:
        try:
            sm = SimConnect()
            print("\n********* MSFS 2024 Mobile Companion App *********\n")
            print(f"Local web server for MSFS 2024 Mobile Companion App initialized.\n")
            print(
                f"Launch {socket.gethostbyname(socket.gethostname())}:4000 in your browser to access MSFS 2024 Mobile Companion App.\n")
            print(
                f"Make sure your your mobile device is connected to the same local network (WIFI) as this PC.\n")
            print(f"Notice: If your computer has more than one active ethernet/WIFI adapter, please check ipconfig in command prompt.\n")
            print("**************************************************\n\n")
            break
        except:
            print("Could not find MSFS running. Please launch MSFS first and then restart the MSFS 2024 Mobile Companion App.")
            sleep(5)

    ae = AircraftEvents(sm)
    aq = AircraftRequests(sm)
    REQUEST_ID = sm.new_request_id()
    sm.dll.EnumerateInputEvents(sm.hSimConnect, REQUEST_ID.value)
    sleep(1)

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

    def thousandify(x):
        return f"{x:,}"

    async def ui_dictionary(ui_friendly_dictionary, previous_alt, landing_t1, landing_vs1, landing_t2, landing_vs2, landing_t3, landing_vs3, landing_g1, landing_g2, landing_g3):
        # Position
        try:
            ui_friendly_dictionary["LATITUDE"] = round(await aq.get("PLANE_LATITUDE"), 6)
            ui_friendly_dictionary["LONGITUDE"] = round(await aq.get("PLANE_LONGITUDE"), 6)
            ui_friendly_dictionary["MAGNETIC_COMPASS"] = round(round(await aq.get("PLANE_HEADING_DEGREES_TRUE"), 2) * 180/3.1416, 2)
            # ui_friendly_dictionary["MAGVAR"] = round(await aq.get("MAGVAR"))
        except:
            None

        # Radios
        ui_friendly_dictionary["NAV1_STANDBY"] = round(await aq.get("NAV_STANDBY_FREQUENCY:1"), 2)
        ui_friendly_dictionary["NAV1_ACTIVE"] = round(await aq.get("NAV_ACTIVE_FREQUENCY:1"), 2)

        ui_friendly_dictionary["NAV2_STANDBY"] = round(await aq.get("NAV_STANDBY_FREQUENCY:2"), 2)
        ui_friendly_dictionary["NAV2_ACTIVE"] = round(await aq.get("NAV_ACTIVE_FREQUENCY:2"), 2)

        # ADF Active
        adf_use_bcd = int(await aq.get("ADF_ACTIVE_FREQUENCY:1"))
        adf_use_digits = ""

        for i in reversed(range(4)):
            adf_use_digit = math.floor(adf_use_bcd / (65536*(16**i)))
            adf_use_digits = adf_use_digits + str(adf_use_digit)
            adf_use_bcd = adf_use_bcd - (65536*(16**i)) * adf_use_digit

        try:
            ui_friendly_dictionary["ADF_USE_1000"] = adf_use_digits[0]
            ui_friendly_dictionary["ADF_USE_100"] = adf_use_digits[1]
            ui_friendly_dictionary["ADF_USE_10"] = adf_use_digits[2]
            ui_friendly_dictionary["ADF_USE_1"] = adf_use_digits[3]
            ui_friendly_dictionary["ADF_USE"] = int(adf_use_digits)
        except:
            None

        # ADF Standby
        adf_stby = int(await aq.get("ADF_STANDBY_FREQUENCY:1"))/1000
        try:
            if adf_stby >= 1000:
                ui_friendly_dictionary["ADF_STBY_1000"] = str(adf_stby)[0]
                ui_friendly_dictionary["ADF_STBY_100"] = str(adf_stby)[1]
                ui_friendly_dictionary["ADF_STBY_10"] = str(adf_stby)[2]
                ui_friendly_dictionary["ADF_STBY_1"] = str(adf_stby)[3]
            else:
                ui_friendly_dictionary["ADF_STBY_1000"] = "0"
                ui_friendly_dictionary["ADF_STBY_100"] = str(adf_stby)[0]
                ui_friendly_dictionary["ADF_STBY_10"] = str(adf_stby)[1]
                ui_friendly_dictionary["ADF_STBY_1"] = str(adf_stby)[2]
        except:
            None

        # NAV/ADF Compass Settings
        # ui_friendly_dictionary["NAV1_OBS_DEG"] = round(await aq.get("NAV_OBS:1"),0)
        # ui_friendly_dictionary["ADF_CARD_DEG"] = round(await aq.get("ADF_CARD"),0)
        # ui_friendly_dictionary["NAV2_OBS_DEG"] = round(await aq.get("NAV_OBS:2"),0)

        # Comms
        ui_friendly_dictionary["COM1_STANDBY"] = round(await aq.get("COM_STANDBY_FREQUENCY:1"), 3)
        ui_friendly_dictionary["COM1_ACTIVE"] = round(await aq.get("COM_ACTIVE_FREQUENCY:1"), 3)
        ui_friendly_dictionary["COM1_TRANSMIT"] = await aq.get("COM_TRANSMIT:1")
        ui_friendly_dictionary["COM2_STANDBY"] = round(await aq.get("COM_STANDBY_FREQUENCY:2"), 3)
        ui_friendly_dictionary["COM2_ACTIVE"] = round(await aq.get("COM_ACTIVE_FREQUENCY:2"), 3)
        ui_friendly_dictionary["COM2_TRANSMIT"] = await aq.get("COM_TRANSMIT:2")

        # XPNDR
        xpndr_bcd = await aq.get("TRANSPONDER_CODE:1")
        xpndr_digits = ""

        # XPNDR Conversion from BCD to Decimal
        try:
            for i in reversed(range(4)):
                xpndr_digit = math.floor(xpndr_bcd / (16**i))
                xpndr_digits = xpndr_digits + str(xpndr_digit)
                xpndr_bcd = xpndr_bcd - (16**i) * xpndr_digit
        except:
            None

        try:
            ui_friendly_dictionary["XPNDR_1000"] = xpndr_digits[0]
            ui_friendly_dictionary["XPNDR_100"] = xpndr_digits[1]
            ui_friendly_dictionary["XPNDR_10"] = xpndr_digits[2]
            ui_friendly_dictionary["XPNDR_1"] = xpndr_digits[3]
            ui_friendly_dictionary["XPNDR"] = int(xpndr_digits)
        except:
            None

        # Autopilot
        ui_friendly_dictionary["AUTOPILOT_MASTER"] = await aq.get("AUTOPILOT_MASTER")
        ui_friendly_dictionary["AUTOPILOT_NAV1_LOCK"] = await aq.get("AUTOPILOT_NAV1_LOCK")
        ui_friendly_dictionary["AUTOPILOT_HEADING_LOCK"] = await aq.get("AUTOPILOT_HEADING_LOCK")
        ui_friendly_dictionary["AUTOPILOT_ALTITUDE_LOCK"] = await aq.get("AUTOPILOT_ALTITUDE_LOCK")
        ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] = await aq.get("AUTOPILOT_GLIDESLOPE_HOLD")
        ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] = await aq.get("AUTOPILOT_APPROACH_HOLD")
        ui_friendly_dictionary["AUTOPILOT_BACKCOURSE_HOLD"] = await aq.get("AUTOPILOT_BACKCOURSE_HOLD")
        ui_friendly_dictionary["AUTOPILOT_VERTICAL_HOLD"] = await aq.get("AUTOPILOT_VERTICAL_HOLD")
        ui_friendly_dictionary["AUTOPILOT_FLIGHT_LEVEL_CHANGE"] = await aq.get("AUTOPILOT_FLIGHT_LEVEL_CHANGE")
        ui_friendly_dictionary["AUTOPILOT_AUTOTHROTTLE"] = await aq.get("AUTOTHROTTLE_ACTIVE")
        ui_friendly_dictionary["AUTOPILOT_YAW_DAMPER"] = await aq.get("AUTOPILOT_YAW_DAMPER")
        ui_friendly_dictionary["AIRSPEED_INDICATED"] = round(await aq.get("AIRSPEED_INDICATED"))
        ui_friendly_dictionary["AUTOPILOT_AIRSPEED_HOLD"] = await aq.get("AUTOPILOT_AIRSPEED_HOLD")
        # ui_friendly_dictionary["AUTOPILOT_MACH_HOLD_VAR"] = round(await aq.get("AUTOPILOT_MACH_HOLD_VAR"),2)
        ui_friendly_dictionary["PLANE_HEADING_DEGREES"] = round(round(await aq.get("PLANE_HEADING_DEGREES_MAGNETIC"), 2) * 180/3.1416, 0)
        # Placeholders - Not Actively Used for stress testing
        # ui_friendly_dictionary["DA62_DEICE_PUMP"] = await aq.get("MobiFlight.DA62_DEICE_PUMP")
        # ui_friendly_dictionary["DA62_ICE_LIGHT_MAX_STATE_ENABLED"] = await aq.get("MobiFlight.DA62_ICE_LIGHT_MAX_STATE_ENABLED")
        # ui_friendly_dictionary["JFARROW_AP_HDG"] = await aq.get("MobiFlight.JFARROW_AP_HDG")
        # ui_friendly_dictionary["AUTOPILOT_WING_LEVELER"] = await aq.get("AUTOPILOT_WING_LEVELER")
        # ui_friendly_dictionary["AUTOPILOT_PITCH_HOLD"] = await aq.get("AUTOPILOT_PITCH_HOLD")
        # ui_friendly_dictionary["AUTOPILOT_PITCH_HOLD_REF"] = await aq.get("AUTOPILOT_PITCH_HOLD_REF")
        ui_friendly_dictionary["AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE"] = await aq.get("AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE")
        # Lights
        #ui_friendly_dictionary["LIGHT_LANDING"] = await aq.get("LIGHT_LANDING")
        #ui_friendly_dictionary["LIGHT_TAXI"] = await aq.get("LIGHT_TAXI")
        #ui_friendly_dictionary["LIGHT_STROBE"] = await aq.get("LIGHT_STROBE")
        #ui_friendly_dictionary["LIGHT_NAV"] = await aq.get("LIGHT_NAV")
        #ui_friendly_dictionary["LIGHT_BEACON"] = await aq.get("LIGHT_BEACON")
        #ui_friendly_dictionary["LIGHT_CABIN"] = await aq.get("LIGHT_CABIN")
        #ui_friendly_dictionary["LIGHT_LOGO"] = await aq.get("LIGHT_LOGO")
        #ui_friendly_dictionary["LIGHT_PANEL"] = await aq.get("LIGHT_PANEL")
        #ui_friendly_dictionary["LIGHT_WING"] = await aq.get("LIGHT_WING")
        #ui_friendly_dictionary["LIGHT_RECOGNITION"] = await aq.get("LIGHT_RECOGNITION")
        # Pitot Heat and Deice
        #ui_friendly_dictionary["PITOT_HEAT"] = await aq.get("PITOT_HEAT")
        # ui_friendly_dictionary["PROP_DEICE_SWITCH"] = await aq.get("PROP_DEICE_SWITCH:1")
        #ui_friendly_dictionary["ENG_ANTI_ICE"] = await aq.get("ENG_ANTI_ICE:1")
        # ui_friendly_dictionary["GEN_ENG_ANTI_ICE"] = await aq.get("GENERAL_ENG_ANTI_ICE_POSITION:1")
        #ui_friendly_dictionary["STRUCTURAL_DEICE_SWITCH"] = await aq.get("STRUCTURAL_DEICE_SWITCH")
        # ui_friendly_dictionary["PANEL_ANTI_ICE_SWITCH"] = await aq.get("PANEL_ANTI_ICE_SWITCH")
        # Sim Rate
        ui_friendly_dictionary["SIMULATION_RATE"] = await aq.get("SIMULATION_RATE")
        # GPS Next Waypoint
        ui_friendly_dictionary["NEXT_WP_LAT"] = await aq.get("GPS_WP_NEXT_LAT")
        ui_friendly_dictionary["NEXT_WP_LON"] = await aq.get("GPS_WP_NEXT_LON")
        # Other
        ui_friendly_dictionary["GEAR_POSITION"] = await aq.get("GEAR_POSITION:1")
        ui_friendly_dictionary["FLAPS_HANDLE_PERCENT"] = round(await aq.get("FLAPS_HANDLE_PERCENT")*100)
        ui_friendly_dictionary["SPOILERS_ARMED"] = await aq.get("SPOILERS_HANDLE_POSITION")

        # Current altitude
        current_alt = await aq.get("INDICATED_ALTITUDE")
        if current_alt > -300:
            ui_friendly_dictionary["INDICATED_ALTITUDE"] = round(current_alt)
            previous_alt = current_alt
        else:
            try:
                ui_friendly_dictionary["INDICATED_ALTITUDE"] = previous_alt
            except:
                pass

        # LOC and APPR Mode
        try:
            if (ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] == 1 and ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] == 1):
                ui_friendly_dictionary["AUTOPILOT_APPR_MODE"] = 1
            else:
                ui_friendly_dictionary["AUTOPILOT_APPR_MODE"] = 0
            if (ui_friendly_dictionary["AUTOPILOT_APPROACH_HOLD"] == 1 and ui_friendly_dictionary["AUTOPILOT_GLIDESLOPE_HOLD"] == 0):
                ui_friendly_dictionary["AUTOPILOT_LOC_MODE"] = 1
            else:
                ui_friendly_dictionary["AUTOPILOT_LOC_MODE"] = 0
        except:
            None

        # Other

        current_landing = round(await aq.get("PLANE_TOUCHDOWN_NORMAL_VELOCITY") * 60)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        # Calculate Custom G-Force based on vertical speed
        # Model uses Harvsine acceleration model for peak acceleration https://www.nhtsa.gov/sites/nhtsa.dot.gov/files/18esv-000501.pdf
        # For time a custom function is used that ranges from 0.25 for GA to 0.35 for airliners. This simulates the rigidness of suspention.
        try:
            plane_weight = await aq.get("TOTAL_WEIGHT")
        except:
            plane_weight = 0
        plane_weight_adj = max(round(plane_weight * 0.45), 200)
        custom_g_force_impact_duration = 0.355 + (-0.103/(1 + (plane_weight_adj/15463)**1.28))

        if landing_vs1 != current_landing:
            # Move 2nd to 3rd
            landing_t3 = landing_t2
            landing_vs3 = landing_vs2
            landing_g3 = landing_g2
            # Move 1st to 2nd
            landing_t2 = landing_t1
            landing_vs2 = landing_vs1
            landing_g2 = landing_g1
            # Assign new 1st
            landing_t1 = current_time
            landing_vs1 = current_landing
            landing_g1 = round(1 + (((2 * (current_landing / (60 * 3.281))) / custom_g_force_impact_duration) / 9.80665), 2)
            # Dictionary Output
            ui_friendly_dictionary["LANDING_VS1"] = landing_vs1
            ui_friendly_dictionary["LANDING_T1"] = landing_t1
            ui_friendly_dictionary["LANDING_G1"] = landing_g1
            ui_friendly_dictionary["LANDING_VS2"] = landing_vs2
            ui_friendly_dictionary["LANDING_T2"] = landing_t2
            ui_friendly_dictionary["LANDING_G2"] = landing_g2
            ui_friendly_dictionary["LANDING_VS3"] = landing_vs3
            ui_friendly_dictionary["LANDING_T3"] = landing_t3
            ui_friendly_dictionary["LANDING_G3"] = landing_g3

    while True:
        asyncio.run(ui_dictionary(ui_friendly_dictionary, previous_alt, ui_friendly_dictionary["LANDING_T1"], ui_friendly_dictionary["LANDING_VS1"], ui_friendly_dictionary["LANDING_T2"], ui_friendly_dictionary["LANDING_VS2"], ui_friendly_dictionary["LANDING_T3"], ui_friendly_dictionary["LANDING_VS3"], ui_friendly_dictionary["LANDING_G1"], ui_friendly_dictionary["LANDING_G2"], ui_friendly_dictionary["LANDING_G3"]))
        # sleep(0.3)

# SimConnect  App 2
def simconnect_thread_func2(threadname):

    global ui_friendly_dictionary

    while True:
        try:
            sm = SimConnect()
            break
        except:
            None

    ae = AircraftEvents(sm)
    aq = AircraftRequests(sm)


    def thousandify(x):
        return f"{x:,}"

    async def ui_dictionary(ui_friendly_dictionary):
        # Additional for performance
        ui_friendly_dictionary["LATITUDE"] = round(await aq.get("PLANE_LATITUDE"), 6)
        ui_friendly_dictionary["LONGITUDE"] = round(await aq.get("PLANE_LONGITUDE"), 6)
        ui_friendly_dictionary["AUTOPILOT_HEADING_LOCK_DIR"] = round(await aq.get("AUTOPILOT_HEADING_LOCK_DIR"))
        ui_friendly_dictionary["AUTOPILOT_ALTITUDE_LOCK_VAR"] = thousandify(round(await aq.get("AUTOPILOT_ALTITUDE_LOCK_VAR")))
        ui_friendly_dictionary["AUTOPILOT_VERTICAL_HOLD_VAR"] = await aq.get("AUTOPILOT_VERTICAL_HOLD_VAR")
        ui_friendly_dictionary["AUTOPILOT_AIRSPEED_HOLD_VAR"] = round(await aq.get("AUTOPILOT_AIRSPEED_HOLD_VAR"))
        # NAV/ADF Compass Settings
        ui_friendly_dictionary["NAV1_OBS_DEG"] = round(await aq.get("NAV_OBS:1"), 0)
        ui_friendly_dictionary["ADF_CARD_DEG"] = round(await aq.get("ADF_CARD"), 0)
        ui_friendly_dictionary["NAV2_OBS_DEG"] = round(await aq.get("NAV_OBS:2"), 0)
    while True:
        asyncio.run(ui_dictionary(ui_friendly_dictionary))

# SimConnect LVAR Reading
def simconnect_thread_func3(threadname):

    global ui_friendly_dictionary
    global selected_plane

    sm = SimConnectMobiFlight()
    vr = MobiFlightVariableRequests(sm)
    vr.clear_sim_variables()

    def thousandify(x):
        return f"{x:,}"

    while True:
        # Default/Generic
        ui_friendly_dictionary["LIGHT_LANDING"] = vr.get(
                "(A:LIGHT LANDING, Bool)")
        ui_friendly_dictionary["LIGHT_TAXI"] = vr.get(
                "(A:LIGHT TAXI, Bool)")
        ui_friendly_dictionary["LIGHT_STROBE"] = vr.get(
                "(A:LIGHT STROBE, Bool)")
        ui_friendly_dictionary["LIGHT_NAV"] = vr.get(
                "(A:LIGHT NAV, Bool)")
        ui_friendly_dictionary["LIGHT_BEACON"] = vr.get(
                "(A:LIGHT BEACON, Bool)")
        ui_friendly_dictionary["LIGHT_CABIN"] = vr.get(
                "(A:LIGHT CABIN, Bool)")
        ui_friendly_dictionary["LIGHT_LOGO"] = vr.get(
                "(A:LIGHT LOGO, Bool)")
        ui_friendly_dictionary["LIGHT_PANEL"] = vr.get(
                "(A:LIGHT PANEL, Bool)")
        ui_friendly_dictionary["LIGHT_WING"] = vr.get(
                "(A:LIGHT WING, Bool)")
        ui_friendly_dictionary["LIGHT_RECOGNITION"] = vr.get(
                "(A:LIGHT RECOGNITION, Bool)")
        ui_friendly_dictionary["PITOT_HEAT"] = vr.get(
                "(A:PITOT HEAT, Bool)")
        ui_friendly_dictionary["ENG_ANTI_ICE"] = vr.get(
                "(A:ENG ANTI ICE:1, Bool)")
        ui_friendly_dictionary["STRUCTURAL_DEICE_SWITCH"] = vr.get(
                "(A:STRUCTURAL DEICE SWITCH, Bool)")

        # PA-28R L-Vars
        if selected_plane[:6] == "PA-28R":
            ui_friendly_dictionary["JF_PA_28R_AP_HDG"] = vr.get(
                "(L:AUTOPILOT_hdg)")
            ui_friendly_dictionary["JF_PA_28R_AP_ROLL"] = vr.get(
                "(L:AUTOPILOT_roll)")
            ui_friendly_dictionary["JF_PA_28R_AP_MODE"] = vr.get(
                "(L:AUTOPILOT_mode)")
            ui_friendly_dictionary["JF_PA_28R_AP_NAV"] = vr.get(
                "(L:AUTOPILOT_nav)")
            ui_friendly_dictionary["JF_PA_28R_LIGHT_BCN"] = vr.get(
                "(L:CENTRE_LOWER_bcn_light)")
            ui_friendly_dictionary["JF_PA_28R_FUEL_SEL"] = vr.get(
                "(L:LEFT_MISC_fuel_sel)")
        # FG-1D L-Vars
        if selected_plane[:5] == "FG-1D":
            ui_friendly_dictionary["MILVIZ_CORSAIR_OIL_COOLER"] = vr.get(
                "(L:FG1D105)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_INTERCOOLER"] = vr.get(
                "(L:FG1D106)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_SUPERCHARGER"] = vr.get(
                "(L:FG1D021)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_FUEL_SELECT"] = vr.get(
                "(L:FG1D013)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_LOCK_TAILWHEEL"] = vr.get(
                "(L:FG1D005)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_GUN_LIGHT"] = vr.get(
                "(L:FG1D085)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_FUEL_PUMP"] = vr.get(
                "(L:FG1D118)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_EXT_LIGHTS"] = vr.get(
                "(L:FG1D124)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_WING_LIGHTS"] = vr.get(
                "(L:FG1D125)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_TAIL_LIGHTS"] = vr.get(
                "(L:FG1D126)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_FORM_LIGHTS"] = vr.get(
                "(L:FG1D127)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_SECTION_LIGHTS"] = vr.get(
                "(L:FG1D128)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_SECSEL_LIGHTS"] = vr.get(
                "(L:FG1D129)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_APP_LIGHTS"] = vr.get(
                "(L:FG1D130)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_COCKPIT_LIGHTS"] = vr.get(
                "(L:FG1D131)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_CHART_LIGHTS"] = vr.get(
                "(L:FG1D132)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_LPANEL_LIGHTS"] = vr.get(
                "(L:FG1D133)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_RPANEL_LIGHTS"] = vr.get(
                "(L:FG1D134)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_LINST_LIGHTS"] = vr.get(
                "(L:FG1D135)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_RINST_LIGHTS"] = vr.get(
                "(L:FG1D136)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_DEFROST"] = vr.get(
                "(L:FG1D137)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_PITOT_HEAT"] = vr.get(
                "(L:FG1D138)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_RECPT"] = vr.get(
                "(L:FG1D139)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_BNC_LIGHTS"] = vr.get(
                "(L:FG1D110)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_RECOGN_LIGHTS"] = vr.get(
                "(L:FG1D111)")
            ui_friendly_dictionary["MILVIZ_CORSAIR_LANDING_LIGHTS"] = vr.get(
                "(L:FG1D196)")
        # DC-6 L-Vars
        if selected_plane[:4] == "DC-6":
            ui_friendly_dictionary["PMDG_DC6_AFE_BEFORE_START"] = vr.get(
                "(L:AfeBeforeStart)")
            ui_friendly_dictionary["PMDG_DC6_AFE_AFTER_START"] = vr.get(
                "(L:AfeAfterStart)")
            ui_friendly_dictionary["PMDG_DC6_AFE_BEFORE_TAKEOFF"] = vr.get(
                "(L:AfeBeforeTakeoff)")
            ui_friendly_dictionary["PMDG_DC6_AFE_TAKEOFF_DRY"] = vr.get(
                "(L:AfeTakeoffDry)")
            ui_friendly_dictionary["PMDG_DC6_AFE_TAKEOFF_WET"] = vr.get(
                "(L:AfeTakeoffWet)")
            ui_friendly_dictionary["PMDG_DC6_AFE_CRUISE"] = vr.get(
                "(L:AfeCruise)")
            ui_friendly_dictionary["PMDG_DC6_AFE_DESCENT"] = vr.get(
                "(L:AfeDescent)")
            ui_friendly_dictionary["PMDG_DC6_AFE_INRANGE"] = vr.get(
                "(L:AfeInrange)")
            ui_friendly_dictionary["PMDG_DC6_AFE_BEFORE_LANDING"] = vr.get(
                "(L:AfeBeforeLanding)")
            ui_friendly_dictionary["PMDG_DC6_AFE_AFTER_LANDING"] = vr.get(
                "(L:AfeAfterLanding)")
            ui_friendly_dictionary["PMDG_DC6_AFE_PARKING"] = vr.get(
                "(L:AfeParking)")
            ui_friendly_dictionary["PMDG_DC6_ADF_ACTIVE"] = vr.get(
                "(L:ADFActiveFreq)")
            ui_friendly_dictionary["PMDG_DC6_ADF_STBY"] = vr.get(
                "(L:ADFStbyFreq)")
            ui_friendly_dictionary["PMDG_DC6_ADF2_ACTIVE"] = vr.get(
                "(L:ADF2ActiveFreq)")
            ui_friendly_dictionary["PMDG_DC6_ADF2_STBY"] = vr.get(
                "(L:ADF2StbyFreq)")
            ui_friendly_dictionary["PMDG_DC6_DME_MODE"] = vr.get(
                "(L:dc6_271_obj)")
            ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT"] = vr.get(
                "(L:dc6_434_obj)")
            ui_friendly_dictionary["PMDG_DC6_ALTITUDE_CONTROL"] = vr.get(
                "(L:dc6_436_obj)")
            ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] = vr.get(
                "(L:dc6_445_obj)")
            ui_friendly_dictionary["PMDG_DC6_AP_MECHANICAL"] = vr.get(
                "(L:dc6_404_obj)")
            ui_friendly_dictionary["PMDG_DC6_GUST_LOCK"] = vr.get(
                "(L:dc6_398_obj)")
            ui_friendly_dictionary["PMDG_DC6_COM1_SPACING"] = vr.get(
                "(A:COM SPACING MODE:1, Enum)")
            ui_friendly_dictionary["PMDG_DC6_COM2_SPACING"] = vr.get(
                "(A:COM SPACING MODE:2, Enum)")
            ui_friendly_dictionary["PMDG_DC6_ADF_MODE"] = vr.get(
                "(L:dc6_133_obj)")
            try:
                ui_friendly_dictionary["PMDG_DC6_COM1_STANDBY"] = round(
                    vr.get("(A:COM STANDBY FREQUENCY:1, Enum)")/1000000, 3)
                ui_friendly_dictionary["PMDG_DC6_COM1_ACTIVE"] = round(
                    vr.get("(A:COM ACTIVE FREQUENCY:1, Enum)")/1000000, 3)
                ui_friendly_dictionary["PMDG_DC6_COM2_STANDBY"] = round(
                    vr.get("(A:COM STANDBY FREQUENCY:2, Enum)")/1000000, 3)
                ui_friendly_dictionary["PMDG_DC6_COM2_ACTIVE"] = round(
                    vr.get("(A:COM ACTIVE FREQUENCY:2, Enum)")/1000000, 3)
            except:
                None
            # Gyropilot Settings
            try:
                ui_friendly_dictionary["PMDG_DC6_AP_TURN"] = int(
                    vr.get("(L:dc6_442_obj)")) - 20
                ui_friendly_dictionary["PMDG_DC6_AP_CLIMB_WHEEL"] = int(
                    vr.get("(L:dc6_440_obj)")) - 50
                ui_friendly_dictionary["PMDG_DC6_AP_AILERON_TRIM"] = int(
                    vr.get("(L:dc6_435_obj)")) - 50
            except:
                None
            # Gyro Pilot Mode Adjustments
            if ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] == 0:
                ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] = "GYROPILOT"
            if ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] == 1:
                ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] = "LOCALIZER"
            if ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] == 2:
                ui_friendly_dictionary["PMDG_DC6_GYRO_PILOT_MODE"] = "APPROACH"
            # COM Spacing
            if ui_friendly_dictionary["PMDG_DC6_COM1_SPACING"] == 0:
                ui_friendly_dictionary["PMDG_DC6_COM1_SPACING"] = "Toggle COM1 Spacing: 25KHz"
            else:
                ui_friendly_dictionary["PMDG_DC6_COM1_SPACING"] = "Toggle COM1 Spacing: 8.33KHz"
            if ui_friendly_dictionary["PMDG_DC6_COM2_SPACING"] == 0:
                ui_friendly_dictionary["PMDG_DC6_COM2_SPACING"] = "Toggle COM2 Spacing: 25KHz"
            else:
                ui_friendly_dictionary["PMDG_DC6_COM2_SPACING"] = "Toggle COM2 Spacing: 8.33KHz"
            # ADF Frequency Display
            if ui_friendly_dictionary["PMDG_DC6_ADF_MODE"] == 0:
                ui_friendly_dictionary["PMDG_DC6_ADF_ACTIVE"] = ui_friendly_dictionary["PMDG_DC6_ADF_ACTIVE"]
                ui_friendly_dictionary["PMDG_DC6_ADF_STBY"] = ui_friendly_dictionary["PMDG_DC6_ADF_STBY"]
            else:
                ui_friendly_dictionary["PMDG_DC6_ADF_ACTIVE"] = ui_friendly_dictionary["PMDG_DC6_ADF2_ACTIVE"]
                ui_friendly_dictionary["PMDG_DC6_ADF_STBY"] = ui_friendly_dictionary["PMDG_DC6_ADF2_STBY"]
        
        # FBW A32NX L-Vars
        if selected_plane[:5] == "A32NX":
            ui_friendly_dictionary["FBW_A32NX_EFIS_CSTR"] = vr.get(
                "(L:BTN_CSTR_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_WPT"] = vr.get(
                "(L:BTN_WPT_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_VORD"] = vr.get(
                "(L:BTN_VORD_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_NDB"] = vr.get(
                "(L:BTN_NDB_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_ARPT"] = vr.get(
                "(L:BTN_ARPT_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_NAV_MODE"] = vr.get(
                "(L:A320_Neo_MFD_NAV_MODE_1)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_RANGE"] = vr.get(
                "(L:A320_Neo_MFD_Range_1)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_NAV_AID_L1"] = vr.get(
                "(L:XMLVAR_NAV_AID_SWITCH_L1_State)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_NAV_AID_L2"] = vr.get(
                "(L:XMLVAR_NAV_AID_SWITCH_L2_State)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_LS"] = vr.get(
                "(L:BTN_LS_1_FILTER_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_EFIS_FD"] = vr.get(
                "(A:AUTOPILOT FLIGHT DIRECTOR ACTIVE, Bool)")
            ui_friendly_dictionary["FBW_A32NX_AP_ALT_INDICATOR"] = vr.get(
                "(A:AUTOPILOT ALTITUDE LOCK VAR:3, Feet)")
            ui_friendly_dictionary["FBW_A32NX_AP_FPA_INDICATOR"] = vr.get(
                "(L:A32NX_AUTOPILOT_FPA_SELECTED)")
            ui_friendly_dictionary["FBW_A32NX_AP_SPD_SLOT"] = vr.get(
                "(A:AUTOPILOT SPEED SLOT INDEX, Number)")
            ui_friendly_dictionary["FBW_A32NX_AP_HDG_SLOT"] = vr.get(
                "(A:AUTOPILOT HEADING SLOT INDEX, Number)")
            ui_friendly_dictionary["FBW_A32NX_AP_VS_SLOT"] = vr.get(
                "(A:AUTOPILOT VS SLOT INDEX, Number)")
            ui_friendly_dictionary["FBW_A32NX_AP_ALT_SLOT"] = vr.get(
                "(A:AUTOPILOT ALTITUDE SLOT INDEX, Number)")
            ui_friendly_dictionary["FBW_A32NX_AP_EXPED_MODE"] = vr.get(
                "(L:A32NX_FMA_EXPEDITE_MODE)")
            ui_friendly_dictionary["FBW_A32NX_AP_TRK_FPA_MODE"] = vr.get(
                "(L:A32NX_TRK_FPA_MODE_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_AP_ALT_INC_MODE"] = vr.get(
                "(L:XMLVAR_Autopilot_Altitude_Increment)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_ANTIICE_ENG1"] = vr.get(
                "(L:XMLVAR_Momentary_PUSH_OVHD_ANTIICE_ENG1_Pressed)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_ANTIICE_ENG2"] = vr.get(
                "(L:XMLVAR_Momentary_PUSH_OVHD_ANTIICE_ENG2_Pressed)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_ANTIICE_WING"] = vr.get(
                "(L:XMLVAR_Momentary_PUSH_OVHD_ANTIICE_WING_Pressed)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_PROBESWINDOW"] = vr.get(
                "(L:XMLVAR_Momentary_PUSH_OVHD_PROBESWINDOW_Pressed)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_NOSE"] = vr.get(
                "(L:LIGHTING_LANDING_1)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_RWY"] = vr.get(
                "(L:LIGHTING_TAXI_2)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_LAND"] = vr.get(
                "(L:LIGHTING_LANDING_2)")
            ui_friendly_dictionary["FBW_A32NX_OVHD_STROBE"] = vr.get(
                "(L:LIGHTING_STROBE_0)")
            ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] = vr.get(
                "(L:A32NX_AUTOPILOT_SPEED_SELECTED)")
            ui_friendly_dictionary["FBW_A32NX_AP_VS_INDICATOR"] = vr.get(
                "(L:A32NX_AUTOPILOT_VS_SELECTED)")
            ui_friendly_dictionary["FBW_A32NX_AP_ACTIVE"] = vr.get(
                "(L:A32NX_AUTOPILOT_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_AP_APPR_MODE"] = vr.get(
                "(L:A32NX_FCU_APPR_MODE_ACTIVE)")
            ui_friendly_dictionary["FBW_A32NX_AP_ATHR_MODE"] = vr.get(
                "(L:A32NX_AUTOTHRUST_STATUS)")
            ui_friendly_dictionary["FBW_A32NX_AP_LOC_MODE"] = vr.get(
                "(L:A32NX_FCU_LOC_MODE_ACTIVE)")
            try:
                ui_friendly_dictionary["FBW_A32NX_AP_HDG_INDICATOR"] = round(vr.get(
                    "(L:A32NX_AUTOPILOT_HEADING_SELECTED)"), 0)
            except:
                ui_friendly_dictionary["FBW_A32NX_AP_HDG_INDICATOR"] = vr.get(
                    "(L:A32NX_AUTOPILOT_HEADING_SELECTED)")
                    
            # Change VS/FPA for HTML output depending on mode selected
            try:
                if ui_friendly_dictionary["FBW_A32NX_AP_TRK_FPA_MODE"] == 1:
                    ui_friendly_dictionary["FBW_A32NX_AP_VS_FPA_INDICATOR"] = ui_friendly_dictionary["FBW_A32NX_AP_FPA_INDICATOR"]
                    ui_friendly_dictionary["FBW_A32NX_AP_HDG_UNIT"] = "TRK"
                    ui_friendly_dictionary["FBW_A32NX_AP_VS_UNIT"] = "FPA"
                else:
                    ui_friendly_dictionary["FBW_A32NX_AP_VS_FPA_INDICATOR"] = ui_friendly_dictionary["FBW_A32NX_AP_VS_INDICATOR"]
                    ui_friendly_dictionary["FBW_A32NX_AP_HDG_UNIT"] = "HDG"
                    ui_friendly_dictionary["FBW_A32NX_AP_VS_UNIT"] = "VS"

                # Change HDG Indicator for managed mode
                if ui_friendly_dictionary["FBW_A32NX_AP_HDG_SLOT"] == 2:
                    ui_friendly_dictionary["FBW_A32NX_AP_HDG_INDICATOR"] = "---"
                # Change SPD Indicator for managed mode
                if selected_plane[:7] == "A32NX D":
                    if ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] == -1:
                        ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] = "---"
                    if ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] == 0:
                        ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] = 100
                else:
                    if ui_friendly_dictionary["FBW_A32NX_AP_SPD_SLOT"] == 2:
                        ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] = "---"

                # Change Autothrust to 0/1
                if int(ui_friendly_dictionary["FBW_A32NX_AP_ATHR_MODE"]) > 1:
                    ui_friendly_dictionary["FBW_A32NX_AP_ATHR_MODE"] = 1
                
                # Set SPD unit based on indicator
                if ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] > 0 and ui_friendly_dictionary["FBW_A32NX_AP_SPD_INDICATOR"] < 2:
                    ui_friendly_dictionary["FBW_A32NX_AP_SPD_UNIT"] = "MACH"
                else:
                    ui_friendly_dictionary["FBW_A32NX_AP_SPD_UNIT"] = "KTS"
            except:
                None
                
        # Asobo Ju-52 L-Vars
        if selected_plane[:5] == "Ju-52":
            ui_friendly_dictionary["ASO_JU52_ADF_MODE"] = vr.get(
                "(L:XMLVAR_ADF_1_Power)")
            ui_friendly_dictionary["ASO_JU52_DMI"] = vr.get(
                "(L:DME_1_STATE)")
            ui_friendly_dictionary["ASO_JU52C_ALTIMETER_1"] = vr.get(
                "(A:KOHLSMAN SETTING HG:1, inHg)")
            ui_friendly_dictionary["ASO_JU52C_ALTIMETER_2"] = vr.get(
                "(A:KOHLSMAN SETTING HG:2, inHg)")
            ui_friendly_dictionary["ASO_JU52C_COM1"] = vr.get(
                "(A:COM ACTIVE FREQUENCY:1, MHz)")
            ui_friendly_dictionary["ASO_JU52C_AP"] = vr.get(
                "(L:XMLVAR_AUTOPILOT_ACTIVE)")
            ui_friendly_dictionary["ASO_JU52C_AP_DISENG"] = vr.get(
                "(L:XMLVAR_AP_DISENGAGED)")
            ui_friendly_dictionary["ASO_JU52C_AP_HEADING"] = vr.get(
                "(L:XMLVAR_AP_HEADING_HOLD)")
            ui_friendly_dictionary["ASO_JU52C_PITOT"] = vr.get(
                "(L:SWITCH_Vorwaermung)")

        # Set sleep to minimize performance impact
        sleep(0.15)


# Reads a file from the filesystem.
# @param filename the name of the file to read
# @param directory the directory where the file is located. Defaults to CWD
def read_file(filename, directory=cwd):
    path = os.path.join(directory, filename)
    contents = None
    with open(path, "rb") as file:
        contents = file.read()
        file.close()

    return contents


if __name__ == "__main__":
    thread1 = Thread(target=simconnect_thread_func, args=('Thread-1', ))
    thread2 = Thread(target=flask_thread_func, args=('Thread-2', ))
    thread3 = Thread(target=simconnect_thread_func2, args=('Thread-3', ))
    thread4 = Thread(target=simconnect_thread_func3, args=('Thread-4', ))
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    sleep(.5)
