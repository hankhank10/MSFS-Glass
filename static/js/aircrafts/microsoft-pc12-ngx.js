let INSTRUMENT_LIGHTING_SWITCH_RECOG_PULSE;
let LIGHTING_GLARESHIELD_1;
let LIGHTING_POTENTIOMETER_20;
let LIGHTING_CABIN_1;
let LIGHTING_CABIN_2;
let DEICE_WINDSHIELD_1;
let DEICE_ENGINE_1;
let DEICE_AIRFRAME_1;
let DEICE_PROPELLER_1;
let AUTOPILOT_AUTOTHROTTLE;

function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            INSTRUMENT_LIGHTING_SWITCH_RECOG_PULSE = data.INSTRUMENT_LIGHTING_SWITCH_RECOG_PULSE;
            LIGHTING_GLARESHIELD_1 = data.LIGHTING_GLARESHIELD_1;
            LIGHTING_POTENTIOMETER_20 = data.LIGHTING_POTENTIOMETER_20;
            LIGHTING_CABIN_1 = data.LIGHTING_CABIN_1;
            LIGHTING_CABIN_2 = data.LIGHTING_CABIN_2;
            DEICE_WINDSHIELD_1 = data.DEICE_WINDSHIELD_1;
            DEICE_ENGINE_1 = data.DEICE_ENGINE_1;
            DEICE_AIRFRAME_1 = data.DEICE_AIRFRAME_1;
            DEICE_PROPELLER_1 = data.DEICE_PROPELLER_1;
            AUTOPILOT_AUTOTHROTTLE = data.AUTOPILOT_AUTOTHROTTLE;
        }
    });
    return connected;
}

function changeScreenBrightness(brightness) {
    triggerSimEvent("LIGHTING_POTENTIOMETER_10", brightness, true, 'input');
    triggerSimEvent("LIGHTING_POTENTIOMETER_7", brightness, true, 'input');
    triggerSimEvent("LIGHTING_POTENTIOMETER_9", brightness, true, 'input');
    triggerSimEvent("LIGHTING_POTENTIOMETER_15", brightness, true, 'input');
    triggerSimEvent("LIGHTING_POTENTIOMETER_8", brightness, true, 'input');
}

function displayPlaneData() {
    checkAndUpdateButton("#pc-12-light-recognition", INSTRUMENT_LIGHTING_SWITCH_RECOG_PULSE === 2 ? 0 : 1, (INSTRUMENT_LIGHTING_SWITCH_RECOG_PULSE === 1 ? "On" : "Pls"), "Off")
    checkAndUpdateButton("#light-panel", LIGHTING_POTENTIOMETER_20 <  1.0 ? 0 : 1)
    checkAndUpdateButton("#light-cabin", LIGHTING_CABIN_2 === 0 ? 0 : 1)
    checkAndUpdateButton("#light-glareshield", LIGHTING_GLARESHIELD_1 === 0 ? 0 : 1)
    checkAndUpdateButton("#light-flood", LIGHTING_CABIN_1 === 0 ? 0 : 1)
    checkAndUpdateButton("#pc-12-autopilot-autothrottle", AUTOPILOT_AUTOTHROTTLE)

    checkAndUpdateButton("#airframe-deice", DEICE_AIRFRAME_1, "Airframe Deice (On)", "Airframe Deice (Off)")
    checkAndUpdateButton("#prop-deice", DEICE_PROPELLER_1, "Prop Deice (On)", "Prop Deice (Off)")
    checkAndUpdateButton("#anti-ice-isd", DEICE_ENGINE_1, "Inertial Separator (On)" , "Inertial Separator (Off)")
    checkAndUpdateButton("#windshield-deice", DEICE_WINDSHIELD_1 === 2 ? 0 : 1, "Windsh. Deice (On)", "Windsh. Deice (Off)")
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
