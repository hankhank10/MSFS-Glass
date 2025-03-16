let EFIS_MINS_1;
let EFIS_MINS_REF_1;
let EFIS_BARO_UNIT_1;

let FCC_AUTOTHROTTLE;

let LIGHTING_RUNWAY_TURNOFF_LIGHT_L;
let LIGHTING_RUNWAY_TURNOFF_LIGHT_R;
let LIGHTING_POSITION_LIGHT;
let LIGHTING_TAXI_LIGHT_WHEEL_WELL;
let LIGHTING_TAXI_LIGHT_GEAR;

let HUD_DISPLAY;
let WINDSHIELD_L_WIPER;
let AFT_OVHD_DOME_LIGHT;
let BEHIND_YOKE_BACKGROUND_LIGHT;
let ANTI_ICE_ENG_1;
let ANTI_ICE_ENG_2;
let ANTI_ICE_WING;
let PROBE_HEAT_A;
let PROBE_HEAT_B;
let WINDOW_HEAT_L_FWD;
let BEHIND_YOKE_MAP_LIGHT_1;



function getPlaneSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function (data) {
        connected = data.connected;

        if (connected) {
            EFIS_MINS_1 = data.EFIS_MINS_1;
            EFIS_MINS_REF_1 = data.EFIS_MINS_REF_1;
            EFIS_BARO_UNIT_1 = data.EFIS_BARO_UNIT_1;
            FCC_AUTOTHROTTLE = data.FCC_AUTOTHROTTLE;
            LIGHTING_POSITION_LIGHT = data.LIGHTING_POSITION_LIGHT;
            LIGHTING_TAXI_LIGHT_WHEEL_WELL = data.LIGHTING_TAXI_LIGHT_WHEEL_WELL;
            LIGHTING_RUNWAY_TURNOFF_LIGHT_L = data.LIGHTING_RUNWAY_TURNOFF_LIGHT_L;
            LIGHTING_RUNWAY_TURNOFF_LIGHT_R = data.LIGHTING_RUNWAY_TURNOFF_LIGHT_R;
            LIGHTING_TAXI_LIGHT_GEAR = data.LIGHTING_TAXI_LIGHT_GEAR;
            HUD_DISPLAY = data.HUD_DISPLAY;
            WINDSHIELD_L_WIPER = data.WINDSHIELD_L_WIPER;
            AFT_OVHD_DOME_LIGHT = data.AFT_OVHD_DOME_LIGHT;
            BEHIND_YOKE_BACKGROUND_LIGHT = data.BEHIND_YOKE_BACKGROUND_LIGHT;
            BEHIND_YOKE_MAP_LIGHT_1 = data.BEHIND_YOKE_MAP_LIGHT_1;
            ANTI_ICE_ENG_1 = data.ANTI_ICE_ENG_1;
            ANTI_ICE_ENG_2 = data.ANTI_ICE_ENG_2;
            ANTI_ICE_WING = data.ANTI_ICE_WING;
            PROBE_HEAT_A = data.PROBE_HEAT_A;
            PROBE_HEAT_B = data.PROBE_HEAT_B;
            WINDOW_HEAT_L_FWD = data.WINDOW_HEAT_L_FWD;
        }
    });
    return connected;
}

function displayPlaneData() {
    checkAndUpdateButton("#mins-ref", EFIS_MINS_REF_1 === 0 ? 1 : 0, "Radio", "Baro")
    checkAndUpdateButton("#baro-unit", EFIS_BARO_UNIT_1 === 0 ? 1 : 0, "IN", "HPA")
    checkAndUpdateButton("#b737-autopilot-autothrottle", FCC_AUTOTHROTTLE);
    checkAndUpdateButton("#light-rwy-l", LIGHTING_RUNWAY_TURNOFF_LIGHT_L === 0 ? 1 : 0);
    checkAndUpdateButton("#light-rwy-r", LIGHTING_RUNWAY_TURNOFF_LIGHT_R === 0 ? 1 : 0);
    checkAndUpdateButton("#b737-light-strobe", LIGHTING_POSITION_LIGHT === 1 ? 0 : 1, (LIGHTING_POSITION_LIGHT === 0 ? "Stdy" : "Puls"), "Off");
    checkAndUpdateButton("#light-dome", AFT_OVHD_DOME_LIGHT === 1 ? 0 : 1, (AFT_OVHD_DOME_LIGHT === 0 ? "Lo." : "Hi"), "Off");
    checkAndUpdateButton("#b737-light-nose", LIGHTING_TAXI_LIGHT_WHEEL_WELL === 0 ? 1 : 0);
    checkAndUpdateButton("#b737-light-taxi", LIGHTING_TAXI_LIGHT_GEAR === 0 ? 1 : 0);
    checkAndUpdateButton("#light-bckg", BEHIND_YOKE_BACKGROUND_LIGHT === 0 ? 0 : 1);
    checkAndUpdateButton("#light-map", BEHIND_YOKE_MAP_LIGHT_1 === 0 ? 0 : 1);
    checkAndUpdateButton("#hud", HUD_DISPLAY);
    checkAndUpdateButton("#b737-ice-wing", ANTI_ICE_WING === 0 ? 1 : 0, "Wing Anti Ice (On)", "Wing Anti Ice (Off)");
    checkAndUpdateButton("#b737-ice-eng1", ANTI_ICE_ENG_1, "ENG1 Anti Ice (On)", "ENG1 Anti Ice (Off)");
    checkAndUpdateButton("#b737-ice-eng2", ANTI_ICE_ENG_2, "ENG2 Anti Ice (On)", "ENG2 Anti Ice (Off)");
    checkAndUpdateButton("#b737-ice-window", WINDOW_HEAT_L_FWD === 0 ? 1 : 0, "Window Heat (On)", "Window Heat (Off)");
    checkAndUpdateButton("#b737-probe-heat", PROBE_HEAT_A === 0 ? 1 : 0, "Probe Heat (On)", "Probe Heat (Auto)");
    checkAndUpdateButton("#b737-cpt-wiper", WINDSHIELD_L_WIPER === 0 ? 0 : 1, "Wiper (" + (WINDSHIELD_L_WIPER === 1 ? "Int" : WINDSHIELD_L_WIPER === 2 ? "Lo" : "Hi") + ")", "Wiper (Off)");


}
function toggleWindowHeat() {
    let newValue = (WINDOW_HEAT_L_FWD === 0 ? 1 : 0);
    triggerSimEvent('WINDOW_HEAT_L_FWD', newValue,true,'input')
    triggerSimEvent('WINDOW_HEAT_L_SIDE', newValue,true,'input')
    triggerSimEvent('WINDOW_HEAT_R_FWD', newValue,true,'input')
    triggerSimEvent('WINDOW_HEAT_R_SIDE', newValue,true,'input')
}


function changeMinimums(number) {
    let newMinimum = EFIS_MINS_1;
    let positive = number > 0;

    for (let i = 0; i < Math.abs(number); i++) {
        if (positive) {
            newMinimum++;
        } else {
            newMinimum--;
        }
        triggerSimEvent("EFIS_MINS_1", newMinimum, true, 'input')
    }
}

function changeScreenBrightness(brightness) {
    triggerSimEvent("BEHIND_YOKE_OUTBD_DU_BRIGHT_1", brightness, true, 'input');
    triggerSimEvent("BEHIND_YOKE_INBD_DU_BRIGHT_1", brightness, true, 'input');
    triggerSimEvent("BEHIND_YOKE_INBD_DU_BRIGHT_2", brightness, true, 'input');
    triggerSimEvent("BEHIND_YOKE_OUTBD_DU_BRIGHT_2", brightness, true, 'input');
    triggerSimEvent("HUD_BRT", brightness, true, 'input');
}


window.setInterval(function () {
    let isConnected = getPlaneSimulatorData();
    if (isConnected) {
        displayPlaneData();
    }
}, 200);
