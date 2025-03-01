let LIGHTING_PEDESTRAL_1;
let LIGHTING_POTENTIOMETER_30;
let LIGHTING_POTENTIOMETER_3;
let LIGHTING_CABIN_1;
let LIGHTING_CABIN_2;
let LIGHTING_CABIN_3;
let DEICE_ENGINE_1;
let LIGHTING_PANEL_1;

function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            LIGHTING_PEDESTRAL_1 = data.LIGHTING_PEDESTRAL_1;
            LIGHTING_POTENTIOMETER_30 = data.LIGHTING_POTENTIOMETER_30;
            LIGHTING_POTENTIOMETER_3 = data.LIGHTING_POTENTIOMETER_3;
            LIGHTING_CABIN_1 = data.LIGHTING_CABIN_1;
            LIGHTING_CABIN_2 = data.LIGHTING_CABIN_2;
            LIGHTING_CABIN_3 = data.LIGHTING_CABIN_3;
            DEICE_ENGINE_1 = data.DEICE_ENGINE_1;
            LIGHTING_PANEL_1 = data.LIGHTING_PANEL_1;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#light-cabin-pass", LIGHTING_CABIN_3)
    checkAndUpdateButton("#light-l-flood", Math.ceil(LIGHTING_CABIN_2 / 100))
    checkAndUpdateButton("#light-c-flood", Math.ceil(LIGHTING_PEDESTRAL_1 / 100))
    checkAndUpdateButton("#light-r-flood", Math.ceil(LIGHTING_CABIN_1 / 100))
    checkAndUpdateButton("#light-glareshield", Math.ceil(LIGHTING_POTENTIOMETER_3 / 100))
    checkAndUpdateButton("#light-stby-ind-light", Math.ceil(LIGHTING_PANEL_1 / 100))
    checkAndUpdateButton("#light-g1000", Math.ceil(LIGHTING_POTENTIOMETER_30 / 100))
    checkAndUpdateButton("#anti-ice-isd", DEICE_ENGINE_1, "Inertial Separator (On)", "Inertial Separator (Off)")
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
