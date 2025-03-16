let DEICE_AIRFRAME;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            DEICE_AIRFRAME = data.DEICE_AIRFRAME;
        }
    });
    return connected;
}

function displayPlaneData() {

    checkAndUpdateButton("#deice-struct", DEICE_AIRFRAME === 0 ? 0 : 1, "Structural Deice (" + (DEICE_AIRFRAME === 1 ? "Norm" : "High") +")", "Structural Deice (Off)");
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
