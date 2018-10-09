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
    fetch('/ser/?value=reset&board=ferg');
});

// some delay for the key input as it is too fast!
function direction_key_loop () {           //  create a loop function
    setTimeout(function () {    
        if (direction_key == 'w') {
            fetch('/ser/?type=jog&value=0,-1,0&board=ferg');
        } else if (direction_key == 's') {
            fetch('/ser/?type=jog&value=0,1,0&board=ferg');
        } else if (direction_key == 'a'){
            fetch('/ser/?type=jog&value=-1,0,0&board=ferg');
        }
        else if (direction_key == 'd'){
            fetch('/ser/?type=jog&value=1,0,0&board=ferg');
        }
        else if (direction_key == 'q'){
            fetch('/ser/?type=jog&value=0,0,1&board=ferg');
        }
        else if (direction_key == 'e'){
            fetch('/ser/?type=jog&value=0,0,-1&board=ferg');
        }
        direction_key = '';
        direction_key_loop();             //  ..  again which will trigger another 
    }, 200)
 }
 
direction_key_loop();   



// change fergboard speed
Mousetrap.bind(']', function () {
    console.log('zoom in');
    app.zoom = (app.zoom +0.1) || 2

} );
Mousetrap.bind('[', function () {
    console.log('zoom out');
    app.zoom = (app.zoom -0.1) || 1
});

Mousetrap.bind('esc', function () {
    app.refresh()
}, 'keyup');

// key combination to turn on/off LED
// TODO: incorporate waterscope as well?
Mousetrap.bind('o n', function () {
    app.LED_on()
});
Mousetrap.bind('o f f', function () {
    app.LED_off()
});
Mousetrap.bind('l e d', function () {
    if (app.LED_switch == null){
        app.LED_switch = 'LED_on'
    }
    else if (app.LED_switch == 'LED_on'){
        app.LED_switch = null
    }
    app.toggle_LED()
});

Mousetrap.bind('s t a r t', function () {
    start_cooling();
});
Mousetrap.bind('s t o p', function () {
    stop_cooling();
});
Mousetrap.bind('h o l d', function () {
    hold_temperature();
});
Mousetrap.bind('p r e p', function () {
    prepare_cooling();
});

// 
Mousetrap.bind(['g'], function() {
    snap();
});


Mousetrap.bind(['r'], function() {
    console.log('reset the motor');
    fetch("/ser/?value=reset&board=ferg");
});