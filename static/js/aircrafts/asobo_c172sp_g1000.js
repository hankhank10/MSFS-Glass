
let LIGHTING_PANEL_1;
let LIGHTING_PANEL_2;
let LIGHTING_PEDESTRAL_1;
let LIGHTING_POTENTIOMETER_5;
let LIGHTING_CABIN_1;
let LIGHTING_CABIN_2;

function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            LIGHTING_PANEL_1 = data.LIGHTING_PANEL_1;
            LIGHTING_PANEL_2 = data.LIGHTING_PANEL_2;
            LIGHTING_PEDESTRAL_1 = data.LIGHTING_PEDESTRAL_1
            LIGHTING_POTENTIOMETER_5 = data.LIGHTING_POTENTIOMETER_5;
            LIGHTING_CABIN_1 = data.LIGHTING_CABIN_1;
            LIGHTING_CABIN_2 = data.LIGHTING_CABIN_2;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#light-flood", Math.ceil(LIGHTING_CABIN_1 / 100))
    checkAndUpdateButton("#light-pedestal", Math.ceil(LIGHTING_PEDESTRAL_1 / 100))
    checkAndUpdateButton("#light-glareshield", Math.ceil(LIGHTING_PANEL_1 / 100))
    checkAndUpdateButton("#light-stby-ind-light", Math.ceil(LIGHTING_PANEL_2 / 100))
    checkAndUpdateButton("#light-g1000", Math.ceil(LIGHTING_POTENTIOMETER_5 / 100))
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);

function toggle_g1000_light() {
triggerSimEvent("LIGHTING_POTENTIOMETER_5", LIGHTING_POTENTIOMETER_5 === 0 ? 100 : 0, true, 'input');
}

function toggle_stdy_ind_light() {
triggerSimEvent("LIGHTING_PANEL_2", LIGHTING_PANEL_2 === 0 ? 100 : 0, true, 'input');
}

function toggle_pedestal_light() {
triggerSimEvent("LIGHTING_PEDESTRAL_1", LIGHTING_PEDESTRAL_1 === 0 ? 100 : 0, true, 'input');
}

function toggle_glareshield_light() {
triggerSimEvent("LIGHTING_PANEL_1", LIGHTING_PANEL_1 === 0 ? 100 : 0, true, 'input');
}


function toggle_glareshield_light() {
triggerSimEvent("LIGHTING_PANEL_1", LIGHTING_PANEL_1 === 0 ? 100 : 0, true, 'input');
}

function toggle_floodlights() {
    if (LIGHTING_CABIN_1 === 0) {
        triggerSimEvent("LIGHTING_CABIN_1", 100, true, 'input')
        triggerSimEvent("LIGHTING_CABIN_2", 100, true, 'input')
    } else {
        triggerSimEvent("LIGHTING_CABIN_1", 0, true, 'input')
        triggerSimEvent("LIGHTING_CABIN_2", 0, true, 'input')
    }
}