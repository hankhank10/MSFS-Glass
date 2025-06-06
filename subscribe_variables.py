from subscribe_input_variables import microsoft_sf50

pos_vars = {
    "latitude": {
        "DatumName": b'PLANE LATITUDE',
        "UnitsName": b'Degrees',
        "fEpsilon": 0.001,
    },
    "longitude": {
        "DatumName": b'PLANE LONGITUDE',
        "UnitsName": b'Degrees',
        "fEpsilon": 0.001,
    },
    "altitude": {
        "DatumName": b'INDICATED ALTITUDE',
        "UnitsName": b'Feet',
        "fEpsilon": 1.0,
    },
    "heading": {
        "DatumName": b'PLANE HEADING DEGREES TRUE',
        "UnitsName": b'degrees',
        "fEpsilon": 0.1,
    },
    "plane_heading_degrees_magnetic": {
        "DatumName": b'PLANE HEADING DEGREES MAGNETIC',
        "UnitsName": b'degrees',
        "fEpsilon": 0.1,
    },
    "airspeed_indicated": {
        "DatumName": b'AIRSPEED INDICATED',
        "UnitsName": b'knots',
        "fEpsilon": 0.5,
    }
}

radio_vars = {
    "nav1_standby": {
        "DatumName": b'NAV STANDBY FREQUENCY:1',
        "UnitsName": b'MHz',
        "fEpsilon": 0.01,
    },
    "nav1_active": {
        "DatumName": b'NAV ACTIVE FREQUENCY:1',
        "UnitsName": b'MHz',
        "fEpsilon": 0.01,
    },
    "nav2_standby": {
        "DatumName": b'NAV STANDBY FREQUENCY:2',
        "UnitsName": b'MHz',
        "fEpsilon": 0.01,
    },
    "nav2_active": {
        "DatumName": b'NAV ACTIVE FREQUENCY:2',
        "UnitsName": b'MHz',
        "fEpsilon": 0.01,
    },
    "adf1_standby": {
        "DatumName": b'ADF STANDBY FREQUENCY:1',
        "UnitsName": b'Number',
        "fEpsilon": 0.9,
    },
    "adf1_active": {
        "DatumName": b'ADF ACTIVE FREQUENCY:1',
        "UnitsName": b'Number',
        "fEpsilon": 0.9,
    },
    "xpndr": {
        "DatumName": b'TRANSPONDER CODE:1',
        "UnitsName": b'Number',
        "fEpsilon": 0.9,
    },
    "com1_active": {
        "DatumName": b'COM ACTIVE FREQUENCY:1',
        "UnitsName": b'MHz',
        "fEpsilon": 0.001,
    },
    "com1_standby": {
        "DatumName": b'COM STANDBY FREQUENCY:1',
        "UnitsName": b'MHz',
        "fEpsilon": 0.001,
    },
    "com1_transmit": {
        "DatumName": b'COM TRANSMIT:1',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "com2_active": {
        "DatumName": b'COM ACTIVE FREQUENCY:2',
        "UnitsName": b'MHz',
        "fEpsilon": 0.001,
    },
    "com2_standby": {
        "DatumName": b'COM STANDBY FREQUENCY:2',
        "UnitsName": b'MHz',
        "fEpsilon": 0.001,
    },
    "com2_transmit": {
        "DatumName": b'COM TRANSMIT:2',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
}

landing_vars = {
    "plane_touchdown_normal_velocity": {
        "DatumName": b'PLANE TOUCHDOWN NORMAL VELOCITY',
        "UnitsName": b'feet/second',
        "fEpsilon": 0.01,
    },
    "total_weight": {
        "DatumName": b'TOTAL WEIGHT',
        "UnitsName": b'pounds',
        "fEpsilon": 1.0,
    },
}

ui_vars = {
    "brake_parking_position": {
        "DatumName": b'BRAKE PARKING POSITION',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "simulation_rate": {
        "DatumName": b'SIMULATION RATE',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    },
    "ap_master": {
        "DatumName": b'AUTOPILOT MASTER',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_nav1_lock": {
        "DatumName": b'AUTOPILOT NAV1 LOCK',
        "UnitsName": b'Radians',
        "fEpsilon": 1.0,
    },
    "ap_heading_lock": {
        "DatumName": b'AUTOPILOT HEADING LOCK',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_altitude_lock": {
        "DatumName": b'AUTOPILOT ALTITUDE LOCK',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_glideslope_hold": {
        "DatumName": b'AUTOPILOT GLIDESLOPE HOLD',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_approach_hold": {
        "DatumName": b'AUTOPILOT APPROACH HOLD',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_backcourse_hold": {
        "DatumName": b'AUTOPILOT BACKCOURSE HOLD',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_vertical_hold": {
        "DatumName": b'AUTOPILOT VERTICAL HOLD',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_flight_level_change": {
        "DatumName": b'AUTOPILOT FLIGHT LEVEL CHANGE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "autothrottle_active": {
        "DatumName": b'AUTOTHROTTLE ACTIVE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_yaw_damper": {
        "DatumName": b'AUTOPILOT YAW DAMPER',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_airspeed_hold": {
        "DatumName": b'AUTOPILOT AIRSPEED HOLD',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_flight_director_active": {
        "DatumName": b'AUTOPILOT FLIGHT DIRECTOR ACTIVE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_heading_lock_dir": {
        "DatumName": b'AUTOPILOT HEADING LOCK DIR',
        "UnitsName": b'Degrees',
    },
    "ap_altitude_lock_var": {
        "DatumName": b'AUTOPILOT ALTITUDE LOCK VAR',
        "UnitsName": b'feet',
        "fEpsilon": 1.0,
    },
    "ap_vertical_hold_var": {
        "DatumName": b'AUTOPILOT VERTICAL HOLD VAR',
        "UnitsName": b'feet/minute',
        "fEpsilon": 10.0,
    },
    "ap_airspeed_hold_var": {
        "DatumName": b'AUTOPILOT AIRSPEED HOLD VAR',
        "UnitsName": b'knots',
        "fEpsilon": 1.0,
    },
    "nav1_obs": {
        "DatumName": b'NAV OBS:1',
        "UnitsName": b'Degrees',
        "fEpsilon": 1.0,
    },
    "nav2_obs": {
        "DatumName": b'NAV OBS:2',
        "UnitsName": b'Degrees',
        "fEpsilon": 1.0,
    },
    "adf_card": {
        "DatumName": b'ADF CARD',
        "UnitsName": b'Degrees',
        "fEpsilon": 1.0,
    },
    "gps_wp_next_lat": {
        "DatumName": b'GPS WP NEXT LAT',
        "UnitsName": b'Degrees',
        "fEpsilon": 1.0,
    },
    "gps_wp_next_lon": {
        "DatumName": b'GPS WP NEXT LON',
        "UnitsName": b'Degrees',
        "fEpsilon": 1.0,
    },
    "gear_position": {
        "DatumName": b'GEAR POSITION:1',
        "UnitsName": b'Enum',
    },
    "flaps_handle_percent": {
        "DatumName": b'FLAPS HANDLE PERCENT',
        "UnitsName": b'Percent Over 100',
        "fEpsilon": 0.01,
    },
    "spoilers_handle_position": {
        "DatumName": b'SPOILERS HANDLE POSITION',
        "UnitsName": b'Percent over 100',
        "fEpsilon": 0.01,
    },

    "light_landing": {
        "DatumName": b'LIGHT LANDING',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_taxi": {
        "DatumName": b'LIGHT TAXI',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_strobe": {
        "DatumName": b'LIGHT STROBE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_nav": {
        "DatumName": b'LIGHT NAV',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_beacon": {
        "DatumName": b'LIGHT BEACON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_cabin": {
        "DatumName": b'LIGHT CABIN',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_panel": {
        "DatumName": b'LIGHT PANEL',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_logo": {
        "DatumName": b'LIGHT LOGO',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_wing": {
        "DatumName": b'LIGHT WING',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "light_recognition": {
        "DatumName": b'LIGHT RECOGNITION',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "pitot_heat": {
        "DatumName": b'PITOT HEAT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "eng_anti_ice": {
        "DatumName": b'ENG ANTI ICE:1',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "structural_deice_switch": {
        "DatumName": b'STRUCTURAL DEICE SWITCH',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },

}

##########################################################################
## Aircraft specific vars start here                                    ##
## Make sure that the variable name is the same as the directory name   ##
## Whitespaces and '-' (dashes) will be converted to _ (underscore)     ##
##########################################################################




asobo_b737max = {

    "XMLVAR_FCC_CMD_1_VALUE": {
        "DatumName": b'L:XMLVAR_FCC_CMD_1_VALUE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "XMLVAR_FCC_CMD_2_VALUE": {
        "DatumName": b'L:XMLVAR_FCC_CMD_2_VALUE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "XMLVAR_INDICATOR_INFO_FCC_CWS_1_ACTIVE": {
        "DatumName": b'L:XMLVAR_INDICATOR_INFO_FCC_CWS_1_ACTIVE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "XMLVAR_FCC_CWS_2_VALUE": {
        "DatumName": b'L:XMLVAR_FCC_CWS_2_VALUE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
}



microsoft_a320neo = {
    "ap_1": {
        "DatumName": b'L:INI_AP1_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_2": {
        "DatumName": b'L:INI_AP2_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_athr": {
        "DatumName": b'L:INI_ATHR_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_loc_mode": {
        "DatumName": b'L:INI_MCU_LOC_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_exped_mode": {
        "DatumName": b'L:A320_EXPEDITE_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_appr_mode": {
        "DatumName": b'L:INI_MCU_LAND_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "fd1_sel": {
        "DatumName": b'L:INI_FD1_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ls1_sel": {
        "DatumName": b'L:INI_LS_CAPTAIN',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_hdg": {
        "DatumName": b'L:INI_HEADING_DIAL',
        "UnitsName": b'Degrees',
        "fEpsilon": 0.5,
    },
    "ap_spd": {
        "DatumName": b'L:INI_Airspeed_Dial',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "ap_spd_mach": {
        "DatumName": b'L:INI_Airspeed_Dial_Mach_knots',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "ap_spd_is_mach": {
        "DatumName": b'L:INI_Airspeed_is_mach',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "eng1_anti_ice": {
        "DatumName": b'L:INI_ENG1_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "eng2_anti_ice": {
        "DatumName": b'L:INI_ENG2_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "wing_anti_ice": {
        "DatumName": b'L:INI_WING_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "probe_heat": {
        "DatumName": b'L:INI_PROBE_HEAT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
}

microsoft_a321 = {
    "ap_1": {
        "DatumName": b'L:INI_AP1_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_2": {
        "DatumName": b'L:INI_AP2_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_athr": {
        "DatumName": b'L:INI_ATHR_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_loc_mode": {
        "DatumName": b'L:INI_MCU_LOC_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_exped_mode": {
        "DatumName": b'L:A320_EXPEDITE_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_appr_mode": {
        "DatumName": b'L:INI_MCU_LAND_LIGHT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "fd1_sel": {
        "DatumName": b'L:INI_FD1_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ls1_sel": {
        "DatumName": b'L:INI_LS_CAPTAIN',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "ap_hdg": {
        "DatumName": b'L:INI_HEADING_DIAL',
        "UnitsName": b'Degrees',
        "fEpsilon": 0.5,
    },
    "ap_spd": {
        "DatumName": b'L:INI_Airspeed_Dial',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "ap_spd_mach": {
        "DatumName": b'L:INI_Airspeed_Dial_Mach_knots',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "ap_spd_is_mach": {
        "DatumName": b'L:INI_Airspeed_is_mach',
        "UnitsName": b'Knots',
        "fEpsilon": 0.5,
    },
    "eng1_anti_ice": {
        "DatumName": b'L:INI_ENG1_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "eng2_anti_ice": {
        "DatumName": b'L:INI_ENG2_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "wing_anti_ice": {
        "DatumName": b'L:INI_WING_ANTI_ICE',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "probe_heat": {
        "DatumName": b'L:INI_PROBE_HEAT',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
}

microsoft_sf50 = {
    "SF50_AUTOTHROTTLE_STATUS": {
        "DatumName": b'L:SF50_AUTOTHROTTLE_STATUS',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "WTAP_GARMIN_APPROACH_MODE_ON": {
        "DatumName": b'L:WTAP_GARMIN_APPROACH_MODE_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "WTAP_GARMIN_NAV_MODE_ON": {
        "DatumName": b'L:WTAP_GARMIN_NAV_MODE_ON',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },

}

asobo_tbm930 = {
    "LIGHTING_PANEL_LIGHT": {
        "DatumName": b'LIGHT POTENTIOMETER:14',
        "UnitsName": b'Percent',
        "fEpsilon": 1,
    },
    "DEICE_PROPELLER_1": {
        "DatumName": b'PROP DEICE SWITCH:1',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },

}

microsoft_pc12_ngx = {
    "DEICE_PROPELLER_1": {
        "DatumName": b'PROP DEICE SWITCH:1',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "DEICE_AIRFRAME_1": {
        "DatumName": b'L:DEICE_AIRFRAME_1',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    }
}
asobo_bonanza_g36 = {
    "DEICE_PROPELLER_1": {
        "DatumName": b'L:DEICE_PROPELLER_1',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    }
}

gotfriends_patey_aviation_dracox = {
    "SWITCHFLIRCAMERA": {
        "DatumName": b'L:SWITCHFLIRCAMERA',
        "UnitsName": b'Bool',
        "fEpsilon": 0.5,
    },
    "SWITCHNOSELIGHTSELECTED": {
        "DatumName": b'L:SWITCHNOSELIGHTSELECTED',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    },
    "SWITCHTIPTAXILIGHTSELECTED": {
        "DatumName": b'L:SWITCHTIPTAXILIGHTSELECTED',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    },
    "SWITCHDNTAXILIGHTSELECTED": {
        "DatumName": b'L:SWITCHDNTAXILIGHTSELECTED',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    },
    "SWITCHNAVLIGHTSELECTED": {
        "DatumName": b'L:SWITCHNAVLIGHTSELECTED',
        "UnitsName": b'Number',
        "fEpsilon": 0.5,
    }
}