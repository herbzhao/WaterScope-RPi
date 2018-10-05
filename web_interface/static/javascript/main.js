function restart_stream() {
    window.location = "/"
}

function stop_stream() {
    fetch("/stop");
}

// refresh the config every 200 seconds
function update_config() {
    // TODO: make it a toggle to stop the config
    // clearInterval(config_loop);
    config_loop = setInterval(function () {
        fetch("/config");
        console.log("updating config")
    }, 200);
}


function swap_stream() {
    window.location = "/swap_stream";
    // window.location = "/";
}


function auto_focus() {
    window.location = "/auto_focus";
    // window.location = "/";
}


function snap() {
    fetch("/snap");
    console.log("taking image")
}

function start_timelapse() {
    // TODO: make it a toggle to stop the timelapse
    // clearInterval(timelapse_loop);
    let timelapse_delay = document.getElementById("timelapse_delay_form").value * 1000;
    timelapse_delay = parseFloat(timelapse_delay);
    console.log(timelapse_delay)
    // a safety precaution
    if (timelapse_delay < 1.5){
        timelapse_delay = 1.5
    }
    // first take one image then start the loop
    snap();
    timelapse_loop = setInterval(function () {
        snap();
    }, timelapse_delay);
}


function timelapse() {
    fetch("/snap");
}


function led_on() {
    console.log('led_on');
    fetch("/ser/?value=led_on&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}

function led_off() {
    console.log('led_off');
    fetch("/ser/?value=led_off&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}


function stop_cooling() {
    console.log('stop_cooling');
    fetch("/ser/?value=stop&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}

function start_cooling() {
    console.log('start_cooling');
    fetch("/ser/?value=start&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}

function prepare_cooling() {
    console.log('prepare_cooling');
    fetch("/ser/?value=prepare&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}

function hold_temperature() {
    console.log('hold_temperature');
    fetch("/ser/?value=hold&board=parabolic");
    // fetch("/ser/?value=led_on&board=waterscope");
}