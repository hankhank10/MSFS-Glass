let TBM930_DEICE_INERT_SEP_SWITCH;
let TBM930_LIGHTING_TAXI_LANDING_LIGHT_SWITCH;
let TBM930_LIGHTING_PULSE_LIGHT_SWITCH;
let LIGHTING_PANEL_LIGHT;
let LIGHTING_DIMMER_LIGHT;
let TBM930_LIGHTING_CABIN_LIGHT;
let TBM930_LIGHTING_ACCESS_LIGHT;
let TBM930_LIGHTING_PILOT_LIGHT;
let TBM930_LIGHTING_COPILOT_LIGHT;
let DEICE_AIRFRAME_1;
let TBM930_DEICE_WINDSHIELD_SWITCH;

let DEICE_PROPELLER_1;

function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            TBM930_DEICE_INERT_SEP_SWITCH = data.TBM930_DEICE_INERT_SEP_SWITCH;
            TBM930_LIGHTING_TAXI_LANDING_LIGHT_SWITCH = data.TBM930_LIGHTING_TAXI_LANDING_LIGHT_SWITCH;
            TBM930_LIGHTING_PULSE_LIGHT_SWITCH = data.TBM930_LIGHTING_PULSE_LIGHT_SWITCH;
            LIGHTING_PANEL_LIGHT = data.LIGHTING_PANEL_LIGHT;
            LIGHTING_DIMMER_LIGHT = data.LIGHTING_DIMMER_LIGHT;
            TBM930_LIGHTING_CABIN_LIGHT = data.TBM930_LIGHTING_CABIN_LIGHT;
            TBM930_LIGHTING_ACCESS_LIGHT = data.TBM930_LIGHTING_ACCESS_LIGHT;
            TBM930_LIGHTING_PILOT_LIGHT = data.TBM930_LIGHTING_PILOT_LIGHT;
            TBM930_LIGHTING_COPILOT_LIGHT = data.TBM930_LIGHTING_COPILOT_LIGHT;
            DEICE_AIRFRAME_1 = data.DEICE_AIRFRAME_1;
            TBM930_DEICE_WINDSHIELD_SWITCH = data.TBM930_DEICE_WINDSHIELD_SWITCH;
            DEICE_PROPELLER_1 = data.DEICE_PROPELLER_1;
        }
    });
    return connected;
}

function displayPlaneData() {
checkAndUpdateButton("#anti-ice-isd", TBM930_DEICE_INERT_SEP_SWITCH, "Inertial Separator (On)", "Inertial Separator (Off)")
checkAndUpdateButton("#light-landing-taxi", TBM930_LIGHTING_TAXI_LANDING_LIGHT_SWITCH > 0 ? 1 : 0, (TBM930_LIGHTING_TAXI_LANDING_LIGHT_SWITCH === 1 ? "Taxi" : "Ldg"), "Off")
checkAndUpdateButton("#light-pulse", TBM930_LIGHTING_PULSE_LIGHT_SWITCH)
checkAndUpdateButton("#light-panel", LIGHTING_PANEL_LIGHT > 0 ? 1 : 0)
checkAndUpdateButton("#light-cabin", TBM930_LIGHTING_CABIN_LIGHT)
checkAndUpdateButton("#light-dimmer", LIGHTING_DIMMER_LIGHT)
checkAndUpdateButton("#light-access", TBM930_LIGHTING_ACCESS_LIGHT)
checkAndUpdateButton("#light-l-flood", TBM930_LIGHTING_PILOT_LIGHT)
checkAndUpdateButton("#light-r-flood", TBM930_LIGHTING_COPILOT_LIGHT)
checkAndUpdateButton("#airframe-deice", DEICE_AIRFRAME_1, "Airframe Deice (On)", "Airframe Deice (Off)")
checkAndUpdateButton("#windshield-deice", TBM930_DEICE_WINDSHIELD_SWITCH, "Windsh. Deice (On)", "Windsh. Deice (Off)")
checkAndUpdateButton("#prop-deice", DEICE_PROPELLER_1, "Prop Deice (On)", "Prop Deice (Off)")
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
