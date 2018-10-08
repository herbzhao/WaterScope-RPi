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
    }, 25)
 }
 
direction_key_loop();   



// change fergboard speed
Mousetrap.bind(']', function () {
    console.log('increase speed');
    fetch("/ser/?type=set_speed&value=increase&board=ferg");
} );
Mousetrap.bind('[', function () {
    console.log('decrease speed');
    fetch("/ser/?type=set_speed&value=decrease&board=ferg");
});

Mousetrap.bind('esc', function () {
    location.href = "/";
}, 'keyup');

// key combination to turn on/off LED
// TODO: incorporate waterscope as well?
Mousetrap.bind('o n', function () {
    led_on();
});
Mousetrap.bind('o f f', function () {
    led_off();
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