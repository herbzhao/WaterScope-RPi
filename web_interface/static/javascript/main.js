var direction_key;

// Move fergboard
Mousetrap.bind('w', function () {
    console.log('pressed w');
    fetch('/ser/?type=jog&value=0,-1,0&board=ferg');
});
Mousetrap.bind('s', function () {
    console.log('pressed s');
    fetch('/ser/?type=jog&value=0,1,0&board=ferg');
});
Mousetrap.bind('a', function () {
    console.log('pressed a');
    fetch('/ser/?type=jog&value=-1,0,0&board=ferg');
});
Mousetrap.bind('d', function () {
    console.log('pressed d');
    fetch('/ser/?type=jog&value=1,0,0&board=ferg');
});
Mousetrap.bind('q', function () {
    console.log('pressed q');
    fetch('/ser/?type=jog&value=0,0,1&board=ferg');
});
Mousetrap.bind('e', function () {
    console.log('pressed e');
    fetch('/ser/?type=jog&value=0,0,-1&board=ferg');
});

// change fergboard speed
Mousetrap.bind(']', function () {
    fetch("/ser/?type=set_speed&value=increase&board=ferg");
} );
Mousetrap.bind('[', function () {
    fetch("/ser/?type=set_speed&value=decrease&board=ferg");
});

Mousetrap.bind('esc', function () {
    location.href = "/";
}, 'keyup');

// key combination to turn on/off LED
// TODO: incorporate waterscope as well?
Mousetrap.bind('o n', function () {
    fetch("/ser/?value=led_on&board=parabolic");
    fetch("/ser/?value=led_on&board=waterscope");
});
Mousetrap.bind('o f f', function () {
    fetch("/ser/?value=led_off&board=parabolic");
    fetch("/ser/?value=led_off&board=waterscope");
});