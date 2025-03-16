let WTAP_GARMIN_NAV_MODE_ON;
let WTAP_GARMIN_APPROACH_MODE_ON;
let SF50_AUTOTHROTTLE_STATUS;
let SF50_LIGHTING_LANDING_LIGHTS;
let LIGHTING_WING_1;
let SF50_DEICE_WINDSHIELD;
let SF50_DEICE_WINDSHIELD_HIGH;
let SF50_LIGHTING_INSTRUMENT_LIGHTS;
let SF50_LIGHTING_PILOT_TASK_LIGHT;
let SF50_LIGHTING_COPILOT_TASK_LIGHT;

function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            WTAP_GARMIN_NAV_MODE_ON = data.WTAP_GARMIN_NAV_MODE_ON;
            WTAP_GARMIN_APPROACH_MODE_ON = data.WTAP_GARMIN_APPROACH_MODE_ON;
            SF50_AUTOTHROTTLE_STATUS = data.SF50_AUTOTHROTTLE_STATUS;
            SF50_LIGHTING_LANDING_LIGHTS = data.SF50_LIGHTING_LANDING_LIGHTS;
            LIGHTING_WING_1 = data.LIGHTING_WING_1;
            SF50_DEICE_WINDSHIELD = data.SF50_DEICE_WINDSHIELD;
            SF50_DEICE_WINDSHIELD_HIGH = data.SF50_DEICE_WINDSHIELD_HIGH;
            SF50_LIGHTING_INSTRUMENT_LIGHTS = data.SF50_LIGHTING_INSTRUMENT_LIGHTS;
            SF50_LIGHTING_PILOT_TASK_LIGHT = data.SF50_LIGHTING_PILOT_TASK_LIGHT;
            SF50_LIGHTING_COPILOT_TASK_LIGHT = data.SF50_LIGHTING_COPILOT_TASK_LIGHT;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#sf50-autopilot-autothrottle", SF50_AUTOTHROTTLE_STATUS)
    checkAndUpdateButton("#sf50-autopilot-approach-hold", WTAP_GARMIN_APPROACH_MODE_ON)
    checkAndUpdateButton("#sf50-autopilot-nav1-lock", WTAP_GARMIN_NAV_MODE_ON)
    checkAndUpdateButton("#sf50-light-landing", SF50_LIGHTING_LANDING_LIGHTS)
    checkAndUpdateButton("#light-wing", LIGHTING_WING_1)
    checkAndUpdateButton("#light-cpt", Math.ceil(SF50_LIGHTING_PILOT_TASK_LIGHT / 100))
    checkAndUpdateButton("#light-fo", Math.ceil(SF50_LIGHTING_COPILOT_TASK_LIGHT / 100))
    checkAndUpdateButton("#li", Math.ceil(SF50_LIGHTING_INSTRUMENT_LIGHTS / 100))
    checkAndUpdateButton("#deice-windshield", SF50_DEICE_WINDSHIELD, "Deice Windshield", "Deice Windshield")
    checkAndUpdateButton("#deice-windshield-high", SF50_DEICE_WINDSHIELD_HIGH, "Deice Windsh. High", "Deice Windsh. High")
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
