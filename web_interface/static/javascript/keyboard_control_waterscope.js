// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var str = this;
    for (var i in arguments) {
        str = str.replace(new RegExp("\\{" + i + "\\}", 'g'), arguments[i]);
    }
    return str
}




// change speed
Mousetrap.bind(']', function () {
    app.zoom_in()
});
Mousetrap.bind('[', function () {
    app.zoom_out()
});


// key combination to turn on/off LED
// TODO: incorporate waterscope as well?
Mousetrap.bind('o n', function () {
    app.LED_switch = 'true'
});
Mousetrap.bind('o f f', function () {
    app.LED_switch = null
});

// auto focus
Mousetrap.bind('a f', function () {
    app.auto_focus()
});

// image capture
Mousetrap.bind(['g'], function () {
    app.take_image(option='', filename = 'raspberry_pi_time')
});
Mousetrap.bind(['h'], function () {
    app.take_image(option='high_res', filename = 'raspberry_pi_time')
});

var direction_key;
// a variable to store the focus movement size
var step_size = 150;
// Move fergboard
Mousetrap.bind('w', function () {
    console.log('pressed w');
    direction_key = 'w';
});
Mousetrap.bind('s', function () {
    console.log('pressed s');
    direction_key = 's';
});
// use q, e to change step??
Mousetrap.bind('e', function () {
    direction_key = 'e';
    step_size = step_size + 100;
    if (step_size >= 950) {
        step_size = 950
    }
    console.log('focus step size is: {0}'.format(step_size));
});
Mousetrap.bind('q', function () {
    direction_key = 'q';
    step_size = step_size - 100;
    if (step_size <= 50) {
        step_size = 50
    }
    console.log('focus step size is: {0}'.format(step_size));
});


var motor_idle;
// some delay for the key input as it is too fast!
function direction_key_loop() { //  create a loop function
    setTimeout(function () {
        axios.get('/waterscope_motor_status').then(response => {
            // disable the keyboard control of the motor when it is busy
            stepper_optics_busy = response.data.stepper_optics_busy
            // console.log(motor_idle)
        })
        if (stepper_optics_busy == false) {
            if (direction_key == 'w') {
                // NOTE: replace with axios
                axios.get('/send_serial/?value=move_opt(-{0})&board=waterscope'.format(step_size));
                // axios.get("/acquire_data/?option=stop_recording_video");
            } else if (direction_key == 's') {
                axios.get('/send_serial/?value=move_opt({0}})&board=waterscope'.format(step_size));
                // axios.get("/acquire_data/?option=stop_recording_video")
            }
        }
        direction_key = '';
        direction_key_loop(); //  ..  again which will trigger another 
    }, 200)
}

direction_key_loop();




// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var str = this;
    for (var i in arguments) {
        str = str.replace(new RegExp("\\{" + i + "\\}", 'g'), arguments[i]);
    }
    return str
}