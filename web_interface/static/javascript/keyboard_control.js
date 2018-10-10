Mousetrap.bind('esc', function () {
    app.refresh()
}, 'keyup');


// change fergboard speed
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

Mousetrap.bind('s t a r t', function () {
    app.chosen_arduino_board = 'parabolic'
    app.serial_command = 'start'
    app.send_serial_command()
});
Mousetrap.bind('s t o p', function () {
    app.chosen_arduino_board = 'parabolic'
    app.serial_command = 'stop'
    app.send_serial_command()
});
Mousetrap.bind('h o l d', function () {
    app.chosen_arduino_board = 'parabolic'
    app.serial_command = 'hold'
    app.send_serial_command()
});
Mousetrap.bind('p r e p', function () {
    app.chosen_arduino_board = 'parabolic'
    app.serial_command = 'prepare'
    app.send_serial_command()
});


Mousetrap.bind(['g'], function () {
    app.take_image()
});
Mousetrap.bind(['h'], function () {
    app.take_image_high_res()
});



var direction_key;
// Move fergboard
Mousetrap.bind('w', function () {
    console.log('pressed w');
    direction_key = 'w';
    // fetch('/ser/?type=jog&value=0,-1,0&board=ferg');
});
Mousetrap.bind('s', function () {
    console.log('pressed s');
    direction_key = 's';
    // fetch('/ser/?type=jog&value=0,1,0&board=ferg');
});
Mousetrap.bind('a', function () {
    console.log('pressed a');
    direction_key = 'a';
    // fetch('/ser/?type=jog&value=-1,0,0&board=ferg');
});
Mousetrap.bind('d', function () {
    console.log('pressed d');
    direction_key = 'd';
    // fetch('/ser/?type=jog&value=1,0,0&board=ferg');
});
Mousetrap.bind('q', function () {
    direction_key = 'q';
    console.log('pressed q');
    // fetch('/ser/?type=jog&value=0,0,1&board=ferg');
});
Mousetrap.bind('e', function () {
    direction_key = 'e';
    console.log('pressed e');
    // fetch('/ser/?type=jog&value=0,0,-1&board=ferg');
});


Mousetrap.bind('r', function () {
    fetch('/ser/?value=reset&board=fergboard');
});

// some delay for the key input as it is too fast!
function direction_key_loop() { //  create a loop function
    setTimeout(function () {
        if (direction_key == 'w') {
            fetch('/ser/?value=jog(0,-1,0)&board=fergboard');
        } else if (direction_key == 's') {
            fetch('/ser/?value=jog(0,1,0)&board=fergboard');
        } else if (direction_key == 'a') {
            fetch('/ser/?value=jog(-1,0,0)&board=fergboard');
        } else if (direction_key == 'd') {
            fetch('/ser/?type=jog&value=jog(1,0,0)&board=fergboard');
        } else if (direction_key == 'q') {
            fetch('/ser/?type=jog&value=jog(0,0,1)&board=fergboard');
        } else if (direction_key == 'e') {
            fetch('/ser/?type=jog&value=jog(0,0,-1)&board=fergboard');
        }
        direction_key = '';
        direction_key_loop(); //  ..  again which will trigger another 
    }, 50)
}

direction_key_loop();