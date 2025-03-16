
let LIGHTING_CABIN_1;
let LIGHTING_CABIN_2;
let LIGHTING_CABIN_3;
let LIGHTING_CABIN_4;
let INSTRUMENT_SWITCH_COMPASS;
let INSTRUMENT_LIGHTING_UVGAUGE;
let DEICE_WINDSHIELD_1;
let INSTRUMENT_SWITCH_PILOTWIPER;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            DEICE_WINDSHIELD_1 = data.DEICE_WINDSHIELD_1;
            INSTRUMENT_SWITCH_PILOTWIPER = data.INSTRUMENT_SWITCH_PILOTWIPER;
            INSTRUMENT_LIGHTING_UVGAUGE = data.INSTRUMENT_LIGHTING_UVGAUGE
            INSTRUMENT_SWITCH_COMPASS = data.INSTRUMENT_SWITCH_COMPASS;
            LIGHTING_CABIN_1 = data.LIGHTING_CABIN_1;
            LIGHTING_CABIN_2 = data.LIGHTING_CABIN_2;
            LIGHTING_CABIN_3 = data.LIGHTING_CABIN_3;
            LIGHTING_CABIN_4 = data.LIGHTING_CABIN_4;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#light-rear-wall", LIGHTING_CABIN_1)
    checkAndUpdateButton("#light-fo-sidewall", LIGHTING_CABIN_2)
    checkAndUpdateButton("#light-cpt-sidewall", LIGHTING_CABIN_3)
    checkAndUpdateButton("#light-cockpit", LIGHTING_CABIN_4)
    checkAndUpdateButton("#light-compass", INSTRUMENT_SWITCH_COMPASS)
    checkAndUpdateButton("#light-panel", INSTRUMENT_LIGHTING_UVGAUGE)
    checkAndUpdateButton("#deice-windshield", DEICE_WINDSHIELD_1, "Windshield Deice (On)", "Windshield Deice (Off)")
    checkAndUpdateButton("#pilot-wiper", INSTRUMENT_SWITCH_PILOTWIPER, " Pilot Wiper (On)", "Pilot Wiper (Off)")
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
