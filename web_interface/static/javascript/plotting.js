// NOTE: use plotly and axios to plot data async
// NOTE: below is how we draw the graph


var trace = {
  x: [],
  y: [],
  type: 'line'
}

var plotting_element_ID = 'plotly_chart'
var API_url = '/serial_time_temp'

// the size of x-range in minute
// https://codepen.io/etpinard/pen/BZLPqo?editors=0010
window_size = 1
var layout = {
  xaxis: {
    title: 'time',
    type: 'date',
    tickformat: '%H:%M:%S',
    range: ['0001-01-01 00:00:00', '0001-01-01 00:0{0}:00'.format(window_size)]
  },
  yaxis: {
    title: 'temperature (°c)',
    range: [10, 40]
  }
}


// generates a bare plot - responsive as well
Plotly.newPlot(plotting_element_ID, data = [trace], layout = layout, config = {
  responsive: true
});

// update the value from axios
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises
// https://hashnode.com/post/how-can-i-use-the-data-of-axioss-response-outside-cj2yddlhx003kcfk8h8czfo7k
function get_data_and_plot() {
  axios.get(API_url).then(response => {

    x_value = response.data.x
    incubator_temp_value = response.data.incubator_temp_value
    defogger_temp_value = response.data.defogger_temp_value
    // these are required to plot in HH:MM:SS format
    date = response.data.date
    hour = response.data.hour
    minute = response.data.minute
    second = response.data.second

    // console.log(y_value)
    // real_time_plotting(x_value, incubator_temp_value)
    // real_time_plotting(x_value, incubator_temp_value)
    real_time_plotting(x_value, defogger_temp_value)


  }).catch(error => console.log(error))
}


// extend multiple traces

// https://redstapler.co/javascript-realtime-chart-plotly/
// function real_time_plotting_multiple_traces(x_value, y_value_1, y_value_2) {
//   Plotly.extendTraces(plotting_element_ID, {x:[[x_value], [x_value]], y: [[y_value_1], [y_value_2]]}, [0, 1])
// }


// https://redstapler.co/javascript-realtime-chart-plotly/
function real_time_plotting(x_value, y_value) {
  Plotly.extendTraces(plotting_element_ID, {
    x: [
      [x_value]
    ],
    y: [
      [y_value]
    ]
  }, [0]);

  // automatically adjust the window range - scrolling
  // e.g. 09:32:00 - 09:34:00
  if (minute >= window_size) {
    layout.xaxis.range = ['{0} {1}:{2}:{3}'.format(date, format_two_digits(hour), format_two_digits(minute - window_size), format_two_digits(second)), x_value]
  }
  // e.g. 08:59:00 - 09:02:00
  // e.g. 08:58:00 - 09:01:00
  if (minute < window_size) {
    // to avoid after 00:59 --> 01:00 and the minute is smaller than window size
    layout.xaxis.range = ['{0} {1}:{2}:{3}'.format(date, format_two_digits(hour - 1), 60 - window_size + minute, format_two_digits(second)), x_value]
  }

  // automatically change temperature range
  if (y_value > 30) {
    layout.yaxis.range = [30, 40]
  } else if (y_value < 30 && y_value > 20) {
    layout.yaxis.range = [20, 30]
  } else if (y_value < 20) {
    layout.yaxis.range = [5, 20]
  }

  Plotly.relayout(plotting_element_ID, layout);
}

// plot with intervals
setTimeout(() => {
  setInterval(() => {
    get_data_and_plot()
  }, 1000 * 0.5);
}, 2000)


// a home-made function to ensure HH:MM:SS format when the value is single digit
function format_two_digits(input_number_string) {
  return ("0" + input_number_string).slice(-2)
}