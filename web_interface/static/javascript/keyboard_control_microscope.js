// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var str = this;
    for (var i in arguments) {
        str = str.replace(new RegExp("\\{" + i + "\\}", 'g'), arguments[i]);
    }
    return str
}

Mousetrap.bind('esc', function () {
    app.alert_window = false
    console.log('close window')
});



// change zoom
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


Mousetrap.bind('shift+s', function () {
    // first focus on the text_field
    // NOTE: added a delay, maybe this will not cause S input
    setTimeout(() => {
        serial_command_field.focus()
    }, 100)
    setTimeout(() => {
        serial_command_field.select()
    }, 100)
});

Mousetrap.bind(',', function () {
    // change the textfield to offset=
    // NOTE: added a delay, maybe this will not cause S input
    setTimeout(() => {
        app.serial_command = 'offset='
    }, 50)

    setTimeout(() => {
        serial_command_field.focus()
    }, 50)
    // move the window focus to the top
    window.scrollTo(0, 0)
});

// image capture
Mousetrap.bind(['c'], function () {
    app.take_image(option='', filename = 'raspberry_pi_time')
});

Mousetrap.bind(['g'], function () {
    app.take_image(option='high_res', filename = 'raspberry_pi_time')
});
Mousetrap.bind(['h'], function () {
    app.take_high_res_image()
});
Mousetrap.bind(['j'], function () {
    app.take_image()
});

// video switch
Mousetrap.bind(['v'], function () {
    if (app.recording_switch == "true") {
        app.recording_switch = null
    } else if (this.recording_switch == null) {
        app.recording_switch = "true"
    }
});


var direction_key;
// Move fergboard
Mousetrap.bind('w', function () {
    console.log('pressed w');
    direction_key = 'w';
});
Mousetrap.bind('s', function () {
    console.log('pressed s');
    direction_key = 's';
});
Mousetrap.bind('a', function () {
    console.log('pressed a');
    direction_key = 'a';
});
Mousetrap.bind('d', function () {
    console.log('pressed d');
    direction_key = 'd';
});
Mousetrap.bind('q', function () {
    direction_key = 'q';
    console.log('pressed q');
});
Mousetrap.bind('e', function () {
    direction_key = 'e';
    console.log('pressed e');
});


function reset_direction_key() {
    fetch('/send_serial/?value=reset&board=fergboard');
}

Mousetrap.bind('r', function () {
    reset_direction_key()
});


// some delay for the key input as it is too fast!
function direction_key_loop() { //  create a loop function
    setTimeout(function () {
        if (direction_key == 'w') {
            fetch('/send_serial/?value=jog(0,-1,0)&board=fergboard');
        } else if (direction_key == 's') {
            fetch('/send_serial/?value=jog(0,1,0)&board=fergboard');
        } else if (direction_key == 'a') {
            fetch('/send_serial/?value=jog(-1,0,0)&board=fergboard');
        } else if (direction_key == 'd') {
            fetch('/send_serial/?type=jog&value=jog(1,0,0)&board=fergboard');
        } else if (direction_key == 'q') {
            fetch('/send_serial/?type=jog&value=jog(0,0,1)&board=fergboard');
        } else if (direction_key == 'e') {
            fetch('/send_serial/?type=jog&value=jog(0,0,-1)&board=fergboard');
        }
        direction_key = '';
        direction_key_loop(); //  ..  again which will trigger another 
    }, 50)
}

direction_key_loop();

