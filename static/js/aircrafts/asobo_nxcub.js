let LIGHTING_LANDING_LIGHTS;
let LIGHTING_PULSE_LIGHTS;
let LIGHTING_PANEL_1;
let LIGHTING_GLARESHIELD_1;
let LANDING_SKIS;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            LIGHTING_LANDING_LIGHTS = data.LIGHTING_LANDING_LIGHTS;
            LIGHTING_PULSE_LIGHTS = data.LIGHTING_PULSE_LIGHTS;
            LIGHTING_PANEL_1 = data.LIGHTING_PANEL_1;
            LIGHTING_GLARESHIELD_1 = data.LIGHTING_GLARESHIELD_1;
            LANDING_SKIS = data.LANDING_SKIS;
        }
    });
    return connected;
}

function displayPlaneData() {

    checkAndUpdateButton("#skis", LANDING_SKIS === 0 ? 1 :0, "Skis (Down)", "Skis (Up)");
    checkAndUpdateButton("#xcub-lights-landing", LIGHTING_LANDING_LIGHTS);
    checkAndUpdateButton("#xcub-lights-pulse", LIGHTING_PULSE_LIGHTS);
    checkAndUpdateButton("#xcub-lights-placard", LIGHTING_PANEL_1 === 0 ? 0 : 1);
    checkAndUpdateButton("#xcub-lights-glareshield", LIGHTING_GLARESHIELD_1 === 0 ? 0 : 1);
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
