let LIGHTING_GLARESHIELD_LIGHT_INTENSITY;
let LIGHTING_CABIN_LIGHT_INTENSITY;
let LIGHTING_SUB_PANEL_LIGHT_INTENSITY;
let LIGHTING_PANEL_LIGHT_INTENSITY;
let HANDLING_SPOILERS;
let DEICE_PROP_HEAT;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            LIGHTING_GLARESHIELD_LIGHT_INTENSITY = data.LIGHTING_GLARESHIELD_LIGHT_INTENSITY;
            LIGHTING_CABIN_LIGHT_INTENSITY = data.LIGHTING_CABIN_LIGHT_INTENSITY;
            LIGHTING_SUB_PANEL_LIGHT_INTENSITY = data.LIGHTING_SUB_PANEL_LIGHT_INTENSITY;
            LIGHTING_PANEL_LIGHT_INTENSITY = data.LIGHTING_PANEL_LIGHT_INTENSITY;
            HANDLING_SPOILERS = data.HANDLING_SPOILERS;
            DEICE_PROP_HEAT = data.DEICE_PROP_HEAT;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#light-cabin", Math.ceil(LIGHTING_CABIN_LIGHT_INTENSITY / 100));
    checkAndUpdateButton("#light-panel", Math.ceil(LIGHTING_PANEL_LIGHT_INTENSITY / 100));
    checkAndUpdateButton("#light-glareshield", Math.ceil(LIGHTING_GLARESHIELD_LIGHT_INTENSITY / 100));
    checkAndUpdateButton("#light-stby-ind-light", Math.ceil(LIGHTING_SUB_PANEL_LIGHT_INTENSITY / 100));
    checkAndUpdateButton("#speedbrake", HANDLING_SPOILERS, "Speedbrake (On)", "Speedbrake (Off)");
    checkAndUpdateButton("#prop-heat", DEICE_PROP_HEAT, "Prop Heat (On)", "Prop Heat (Off)");
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
