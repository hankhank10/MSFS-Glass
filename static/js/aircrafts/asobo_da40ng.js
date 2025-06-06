let LIGHTING_GLARESHIELD_1;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            LIGHTING_GLARESHIELD_1 = data.LIGHTING_GLARESHIELD_1;
        }
    });
    return connected;
}

function displayPlaneData() {

    checkAndUpdateButton("#light-glr", LIGHTING_GLARESHIELD_1 === 0 ? 0 : 1, );
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
