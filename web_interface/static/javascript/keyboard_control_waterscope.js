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
Mousetrap.bind(['c'], function () {
    app.take_image(option='', filename = 'raspberry_pi_time')
});
Mousetrap.bind(['g'], function () {
    app.take_image(option='high_res', filename = 'raspberry_pi_time')
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
// use q, e to change step??
Mousetrap.bind('q', function () {
    direction_key = 'q';
    console.log('pressed q');
});
Mousetrap.bind('e', function () {
    direction_key = 'e';
    console.log('pressed e');
});



// some delay for the key input as it is too fast!
function direction_key_loop() { //  create a loop function
    setTimeout(function () {
        if (direction_key == 'w') {
            fetch('/send_serial/?value=move(-500)&board=waterscope');
        } else if (direction_key == 's') {
            fetch('/send_serial/?value=move(500)&board=waterscope');
        }
        direction_key = '';
        direction_key_loop(); //  ..  again which will trigger another 
    }, 50)
}

direction_key_loop();
