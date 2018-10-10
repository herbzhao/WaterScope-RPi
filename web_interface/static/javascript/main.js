Vue.options.delimiters = ["[[", "]]"];

var app = new Vue({
    el: '#app',
    data: () => ({
        serial_command: '',
        peltier_control_command: '',
        chosen_arduino_board: 'parabolic',
        available_arduino_boards: ['parabolic', 'waterscope', 'fergboard'],
        LED_switch: 'true',
        stream_method: 'PiCamera',
        recording_switch: null,
        config_update_switch: null,
        timelapse_switch: null,
        timelapse_interval: 10,
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
                if (this.LED_switch == "true") {
                    this.LED_on()
                } else if (this.LED_switch == null) {
                    this.LED_off()
                }
            }, 10);
        },
        LED_on: function () {
            console.log('turn on LED')
            axios.get("/ser/?value=led_on&board=parabolic");
            this.LED_switch = "true"
        },
        LED_off: function () {
            console.log('turn off LED')
            axios.get("/ser/?value=led_off&board=parabolic")
            this.LED_switch = null
        },

        toggle_recording: function () {
            setTimeout(() => {
                if (this.recording_switch == "true") {
                    this.start_recording()
                } else if (this.recording_switch == null) {
                    this.stop_recording()
                }
            }, 10);
        },
        start_recording: function () {
            console.log('video recording on')
            axios.get('/')
            this.recording_switch = "true"
        },
        stop_recording: function () {
            console.log('video recording off')
            axios.get('/')
            this.recording_switch = null
        },

        toggle_config_update: function () {
            setTimeout(() => {
                if (this.config_update_switch == "true") {
                    this.start_config_update()
                } else if (this.config_update_switch == null) {
                    this.stop_config_update()
                }
            }, 10);
        },
        start_config_update: function () {
            console.log('start updating config')
            this.config_loop = setInterval(() => {
                axios.get("/settings/?config_update=true");
            }, 200)
        },
        stop_config_update: function () {
            console.log('stop updating config')
            clearInterval(this.config_loop)
        },

        toggle_timelapse: function () {
            setTimeout(() => {
                // always stop the timelapse first
                this.stop_timelapse()
                if (this.timelapse_switch == 'waterscope_timelapse') {
                    this.start_waterscope_timelapse()
                } else if (this.timelapse_switch == 'timelapse') {
                    this.start_timelapse()
                } else if (this.timelapse_switch == null) {
                    // do nothing
                }
            }, 10);
        },

        start_waterscope_timelapse: function () {
            // NOTE: a safety precaution to set a interval not too low
            if (this.timelapse_interval < 5) {
                this.timelapse_interval = 5
            }
            timelapse_interval_ms = this.timelapse_interval * 1000
            console.log('Starting waterscope timelapse')
            this.LED_on()
            setTimeout(() => {
                this.snap()
            }, 1000)
            setTimeout(() => {
                this.LED_off()
            }, 3000)
            // NOTE: arrow function very important to prevent misunderstanding of this.
            this.timelapse_loop = setInterval(() => {
                this.LED_on()
                setTimeout(() => {
                    this.snap()
                }, 1000)
                setTimeout(() => {
                    this.LED_off()
                }, 3000)
            }, timelapse_interval_ms);
        },

        start_timelapse: function () {
            if (this.timelapse_interval < 1.5) {
                this.timelapse_interval = 1.5
            }
            timelapse_interval_ms = this.timelapse_interval * 1000
            console.log('Starting timelapse')
            // first take one image then start the loop
            this.snap();
            this.timelapse_loop = setInterval(() => {
                this.snap();
            }, timelapse_interval_ms);
        },

        stop_timelapse: function () {
            try {
                clearInterval(this.timelapse_loop)
                setTimeout(() => {
                    console.log("stop exisiting timelapse...")
                }, 100)
            } finally {}
        },

        send_serial_command: function () {
            console.log('sending serial command')
            axios.get('/ser/?value={0}&board={1}'.format(this.serial_command, this.chosen_arduino_board))
        },

        toggle_stream: function () {
            // a tiny delay is required for the toggle buttons
            setTimeout(() => {
                if (this.stream_method == 'PiCamera') {
                    this.start_PiCamera_stream()
                } else if (this.stream_method == 'OpenCV') {
                    this.start_OpenCV_stream()
                } else if (this.stream_method == null) {
                    this.stream_method = 'PiCamera'
                    // DEBUG: is this necessary?
                    this.start_PiCamera_stream()
                }
            }, 10);
        },
        start_PiCamera_stream: function () {
            console.log('changing streaming: {}'.format(this.stream_method))
            window.location = '/settings/?stream_method=picamera'
            // axios.get('/swap_stream/?stream=picamera')
            // TODO: maybe we can refresh the jpg elements
        },
        start_OpenCV_stream: function () {
            console.log('changing streaming: {}'.format(this.stream_method))
            window.location = '/settings/?stream_method=opencv'
            // axios.get('/swap_stream/?stream=opencv')
        },

        read_server_info: function () {
            // Flask sending all the information through this page
            axios
                .get('/settings')
                .then(response => {
                    // string
                    this.stream_method = response.data.stream_method;
                    // should be a list
                    this.available_arduino_boards = response.data.available_arduino_boards;
                })
        }
    },

    change_zoom: function () {
        axios.get('/settings/?zoom={}'.format(this.zoom))
    },
    refresh: function () {
        window.location = "/"
    },
    stop_stream: function () {
        axios.get("/settings/?stop=true");
        this.stop_config_update()
        this.stop_timelapse()
        this.stop_recording()
    },
    auto_focus: function () {
        window.location = "/auto_focus";
    },
    snap: function () {
        axios.get("/snap")
        console.log("taking image")
    },
    peltier_control: function () {
        if (this.peltier_control_command == 'stop') {
            axios.get("/ser/?value=stop&board=parabolic");
            console.log("Stop peltier cooling")
        } else if (this.peltier_control_command == 'start') {
            axios.get("/ser/?value=start&board=parabolic");
            console.log("Cool from current temp to T_fin")
        } else if (this.peltier_control_command == 'start') {
            axios.get("/ser/?value=start&board=parabolic");
            console.log("Restart the cooling process from T_start to T_fin")
        } else if (this.peltier_control_command == 'prepare') {
            axios.get("/ser/?value=prepare&board=parabolic");
            console.log("Cool/heat to phase transition point")
        } else if (this.peltier_control_command == 'hold') {
            axios.get("/ser/?value=hold&board=parabolic");
            console.log("Hold at current temperature")
        }
    },
})

// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var str = this;
    for (var i in arguments) {
        str = str.replace(new RegExp("\\{" + i + "\\}", 'g'), arguments[i]);
    }
    return str
}