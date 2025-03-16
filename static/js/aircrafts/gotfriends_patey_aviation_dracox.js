let SWITCHFLIRCAMERA;
let SWITCHNOSELIGHTSELECTED;
let SWITCHTIPTAXILIGHTSELECTED;
let SWITCHDNTAXILIGHTSELECTED;
let SWITCHNAVLIGHTSELECTED;


function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            SWITCHFLIRCAMERA = data.SWITCHFLIRCAMERA;
            SWITCHNOSELIGHTSELECTED = data.SWITCHNOSELIGHTSELECTED;
            SWITCHTIPTAXILIGHTSELECTED = data.SWITCHTIPTAXILIGHTSELECTED;
            SWITCHDNTAXILIGHTSELECTED = data.SWITCHDNTAXILIGHTSELECTED;
            SWITCHNAVLIGHTSELECTED = data.SWITCHNAVLIGHTSELECTED;

        }
    });
    return connected;
}

function displayPlaneData() {

    checkAndUpdateButton("#draco-flir", SWITCHFLIRCAMERA, "FLIR Camera (On)", "FLIR Camera (Off)");
    checkAndUpdateButton("#draco-lights-nose", SWITCHNOSELIGHTSELECTED === 0 ? 0 : 1, (SWITCHNOSELIGHTSELECTED === 1 ? "On" : "Pulse"), "Off");
    checkAndUpdateButton("#draco-lights-tip", SWITCHTIPTAXILIGHTSELECTED === 0 ? 0 : 1, (SWITCHTIPTAXILIGHTSELECTED === 1 ? "Taxi." : "Pulse"), "Off");
    checkAndUpdateButton("#draco-lights-down", SWITCHDNTAXILIGHTSELECTED === 0 ? 0 : 1, (SWITCHDNTAXILIGHTSELECTED === 1 ? "Taxi" : "Pulse"), "Off");
    checkAndUpdateButton("#draco-lights-nav", SWITCHNAVLIGHTSELECTED === 0 ? 0 : 1, (SWITCHNAVLIGHTSELECTED === 1 ? "Bcn." : "Strb."), "Off");
}

window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
