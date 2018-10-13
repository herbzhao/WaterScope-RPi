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
        max_zoom: 5,
        alert_window: false,
        alert_window_timeout: 5000,
    }),

    // watch when data change 
    watch: {
        zoom: function () {
            this.change_zoom()
        },
        LED_switch: function () {
            if (this.LED_switch == "true") {
                this.led_on()
            } else if (this.LED_switch == null) {
                this.led_off()
            }
            this.alert_window = true
        },
        recording_switch: function () {
            if (this.recording_switch == "true") {
                this.start_recording()
            } else if (this.recording_switch == null) {
                this.stop_recording()
            }
            this.alert_window = true
        },
        config_update_switch: function () {
            if (this.config_update_switch == "true") {
                this.start_config_update()
            } else if (this.config_update_switch == null) {
                this.stop_config_update()
            }
            this.alert_window = true
        },
        timelapse_switch: function () {
            // always stop the timelapse first
            this.stop_timelapse()
            if (this.timelapse_switch == 'waterscope_timelapse') {
                this.start_waterscope_timelapse()
            } else if (this.timelapse_switch == 'timelapse') {
                this.start_timelapse()
            } else if (this.timelapse_switch == null) {
            }
            this.alert_window = true
        },
        stream_method: function () {
            if (this.stream_method == 'PiCamera') {
                this.start_PiCamera_stream()
            } else if (this.stream_method == 'OpenCV') {
                this.start_OpenCV_stream()
            } else if (this.stream_method == null) {
                this.stream_method = 'PiCamera'
                // DEBUG: is this necessary?
                this.start_PiCamera_stream()
            }
            this.alert_window = true
        },
    },
    
    computed: {
        alert_content: function () {
          alert_content = []
          if (this.LED_switch != null) {
            alert_content.push("LED")
          }
          if (this.config_update_switch != null) {
            alert_content.push('Updating config')
          }
          if (this.recording_switch != null) {
            alert_content.push('Recording')
          }
          if (this.timelapse_switch != null){
            alert_content.push('Timelapse')
          }
            return alert_content.join(', ')
        }
      },

      mounted: function () {
        this.read_server_info()
    },

    methods: {
        led_on: function () {
            console.log('turn on LED')
            axios.get("/ser/?value=led_on&board=parabolic");
        },
        led_off: function () {
            console.log('turn off LED')
            axios.get("/ser/?value=led_off&board=parabolic")
        },
        start_recording: function () {
            console.log('start recording..')
            axios.get("/take_image/?option=start_recording")
        },
        stop_recording: function () {
            console.log('stop recording')
            axios.get("/take_image/?option=stop_recording")
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

        start_waterscope_timelapse: function () {
            // NOTE: a safety precaution to set a interval not too low
            // TODO: Can move this into watch then we have no problem.
            if (this.timelapse_interval < 5) {
                this.timelapse_interval = 5
            }
            timelapse_interval_ms = this.timelapse_interval * 1000
            console.log('Starting waterscope timelapse')
            this.LED_on()
            setTimeout(() => {
                this.take_image()
            }, 1000)
            setTimeout(() => {
                this.LED_off()
            }, 3000)
            // NOTE: arrow function very important to prevent misunderstanding of this.
            this.timelapse_loop = setInterval(() => {
                this.LED_on()
                setTimeout(() => {
                    this.take_image()
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
            this.take_image();
            this.timelapse_loop = setInterval(() => {
                this.take_image();
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

        start_PiCamera_stream: function () {
            console.log('changing streaming: {}'.format(this.stream_method))
            axios.get('/settings/?stream_method=PiCamera')
            this.refresh()
            // TODO: maybe we can refresh the jpg elements
        },
        start_OpenCV_stream: function () {
            console.log('changing streaming: {}'.format(this.stream_method))
            axios.get('/settings/?stream_method=OpenCV')
            this.refresh()
        },

        send_serial_command: function () {
            console.log('Sending serial command {0}'.format(this.serial_command))
            axios.get('/ser/?value={0}&board={1}'.format(this.serial_command, this.chosen_arduino_board))
            // alert('Sending serial command \n {0}'.format(this.serial_command))
            // remove focus of the text field
            app.$refs.serial_command_field.blur()
            // show the pop up alert
            this.alert_window=true
        },

        read_server_info: function () {
            // Flask sending all the information through this page
            axios
                .get('/settings/')
                .then(response => {
                    this.stream_method = response.data.stream_method;
                    this.available_arduino_boards = response.data.available_arduino_boards;
                })
        },

        change_zoom: function () {
            axios.get('/settings/?zoom_value={0}'.format(this.zoom))
        },
        zoom_in: function () {
            console.log('zoom in');
            this.zoom = (this.zoom + 0.5) || this.max_zoom
        },
        zoom_out: function () {
            console.log('zoom out');
            this.zoom = (this.zoom - 0.5) || 1
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
        take_image: function () {
            axios.get("/take_image/")
            console.log("taking image")
        },
        take_image_with_arduino_time: function () {
            axios.get("/take_image/?option=high_res")
            console.log("taking image in high res")
        },
        take_image_high_res: function () {
            axios.get("/take_image/?option=high_res")
            console.log("taking image in high res")
        },
    }
})

// NOTE: python-like string format method https://coderwall.com/p/flonoa/simple-string-format-in-javascript
String.prototype.format = function () {
    var str = this;
    for (var i in arguments) {
        str = str.replace(new RegExp("\\{" + i + "\\}", 'g'), arguments[i]);
    }
    return str
}