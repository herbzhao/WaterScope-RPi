Vue.options.delimiters = ["[[", "]]"];

var app = new Vue({
    el: '#app',
    data: () => ({
        serial_command: '',
        chosen_arduino_board: 'parabolic',
        arduino_boards: ['parabolic', 'waterscope', 'fergboard'],
        LED_switch: 'LED_on',
        recording_switch: null,
        config_update_switch: null,
        timelapse_switch: null,
        timelapse_interval: 10,
        message: 'test vue',
        stream_method: 'PiCamera',
        zoom: 1,
    }),

    // watch when data change 
    watch: {
        zoom: function (newzoom, oldzoom) {
            this.change_zoom()
        }
    },
    // DEBUG: why when vue is not running, plotly willl work
    mounted: function () {
        this.LED_on(),
        this.read_info()
    },

    methods: {
        toggle_LED: function () {
            setTimeout(() => {
                if (this.LED_switch == null) {
                    console.log('turn off LED')
                    axios.get("/ser/?value=led_off&board=parabolic");
                    //check whether we can put watescope here without connecting
                    // axios.get("/ser/?value=led_on&board=waterscope");

                } else if (this.LED_switch == "LED_on") {
                    console.log('turn on LED')
                    axios.get("/ser/?value=led_on&board=parabolic");
                }
            }, 50);
        },
        LED_on: function () {
            this.LED_switch = 'LED_on'
            this.toggle_LED()
        },
        LED_off: function () {
            this.LED_switch = null
            this.toggle_LED()
        },

        toggle_recording: function () {
            setTimeout(() => {
                if (this.recording_switch == null) {
                    console.log('video recording off')
                } else if (this.recording_switch == "recording") {
                    console.log('video recording on')
                }
            }, 10);
        },
        toggle_config_update: function () {
            setTimeout(() => {
                if (this.config_update_switch == "config_updating") {
                    console.log('start updating config')
                    config_loop = setInterval(() => {
                        axio.get("/config");
                    }, 200);
                } else if (this.config_update_switch == null) {
                    console.log('stop updating config')
                    clearInterval(config_loop)
                }
            }, 10);
        },
        toggle_timelapse: function () {
            setTimeout(() => {
                if (this.timelapse_switch == 'waterscope_timelapse') {
                    try {
                        clearInterval(timelapse_loop)
                    } finally {

                        console.log('Starting waterscope timelapse')
                        // NOTE: a safety precaution to set a interval not too low
                        if (this.timelapse_interval < 5) {
                            this.timelapse_interval = 5
                        }
                        timelapse_interval_ms = this.timelapse_interval * 1000

                        console.log('Starting timelapse')
                        this.LED_on()
                        setTimeout(() => {
                            this.snap()
                        }, 1000)
                        setTimeout(() => {
                            this.LED_off()
                        }, 3000)

                        // NOTE: arrow function very important!
                        timelapse_loop = setInterval(() => {
                            this.LED_on()
                            setTimeout(() => {
                                this.snap()
                            }, 1000)
                            setTimeout(() => {
                                this.LED_off()
                            }, 3000)

                        }, timelapse_interval_ms);
                    }

                } else if (this.timelapse_switch == 'timelapse') {
                    try {
                        clearInterval(timelapse_loop)
                    } finally {
                        if (this.timelapse_interval < 1.5) {
                            this.timelapse_interval = 1.5
                        }
                        timelapse_interval_ms = this.timelapse_interval * 1000

                        console.log('Starting timelapse')
                        // first take one image then start the loop
                        this.snap();
                        timelapse_loop = setInterval(() => {
                            this.snap();
                        }, timelapse_interval_ms);
                    }
                } else if (this.timelapse_switch == null) {
                    console.log('stop timelapse')
                    clearInterval(timelapse_loop)
                }
            }, 10);
        },
        send_serial_command: function () {
            console.log('sending serial command')
            axios.get('/ser/?value={0}&board={1}'.format(this.serial_command, this.chosen_arduino_board ))
        },
        toggle_stream: function () {
            // a tiny delay is required for the toggle buttons
            setTimeout(() => {
                if (this.stream_method == null) {
                    this.stream_method = 'PiCamera'
                } else if (this.stream_method == 'PiCamera') {
                    console.log(this.stream_method)
                    window.location = '/swap_stream/?stream=picamera'
                    axios.get('/swap_stream/?stream=picamera')
                } else if (this.stream_method == 'OpenCV') {
                    console.log(this.stream_method)
                    window.location = '/swap_stream/?stream=opencv'
                    axios.get('/swap_stream/?stream=opencv')
                }
            }, 10);
        },

        read_info: function () {
            axios
                .get('/info')
                .then(response => {
                    current_stream_method = response.data.stream_method
                    console.log(current_stream_method)
                    if (current_stream_method == 'pi') {
                        this.stream_method = 'PiCamera'
                    } else if (current_stream_method == 'opencv') {
                        this.stream_method = 'OpenCV'
                    }
                })
        },

        change_zoom: function () {
            console.log(this.zoom)
        },
        refresh: function () {
            window.location = "/"
        },
        stop_stream: function () {
            axios.get("/stop");
        },
        auto_focus: function () {
            window.location = "/auto_focus";
        },
        snap: function () {
            axios.get("/snap")
            console.log("taking image")
        },
        peltier_control: function () {
            if (peltier_control_command == 'stop') {
                axios.get("/ser/?value=stop&board=parabolic");
                console.log("Stop peltier cooling")
            } else if (peltier_control_command == 'start') {
                axios.get("/ser/?value=start&board=parabolic");
                console.log("Cool from current temp to T_fin")
            } else if (peltier_control_command == 'start') {
                axios.get("/ser/?value=start&board=parabolic");
                console.log("Restart the cooling process from T_start to T_fin")
            } else if (peltier_control_command == 'prepare') {
                axios.get("/ser/?value=prepare&board=parabolic");
                console.log("Cool/heat to phase transition point")
            } else if (peltier_control_command == 'hold') {
                axios.get("/ser/?value=hold&board=parabolic");
                console.log("Hold at current temperature")
            }
        },
    },



})

// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var a = this;
    for (var k in arguments) {
        a = a.replace(new RegExp("\\{" + k + "\\}", 'g'), arguments[k]);
    }
    return a
}