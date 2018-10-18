// NOTE: use plotly and axios to plot data async
// NOTE: below is how we draw the graph


var trace = {
  x: [],
  y: [],
  type: 'line'
}
 
var plotting_element_ID = 'plotly_chart'
var API_url = '/parabolic_serial_monitor'

// the size of x-range in minute
// https://codepen.io/etpinard/pen/BZLPqo?editors=0010
window_size = 2
var layout = {
  xaxis: {
    title: 'time',
    type: 'date',
    tickformat: '%M:%S',
    range: ['0001-01-01 00:00:00', '0001-01-01 00:0{0}:00'.format(window_size)]
  },
  yaxis: {
    title: 'temperature (°c)',
    range: [15, 35]
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
    y_value = response.data.y
    // these are required to plot in HH:MM:SS format
    date = response.data.date
    hour = response.data.hour
    minute = response.data.minute
    second = response.data.second

    // console.log(y_value)
    real_time_plotting(x_value, y_value)
  }).catch(error => console.log(error))
}


  
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
  if (minute >= window_size) {
    layout.xaxis.range = ['{0} {1}:{2}:{3}'.format(date, format_two_digits(hour), format_two_digits(minute - window_size), format_two_digits(second)),  x_value]
  } 
  if (hour > 0){
    layout.xaxis.tickformat = '%H:%M:%S'
    if (minute < window_size) {
      // to avoid after 00:59 --> 01:00 and the minute is smaller than window size
      layout.xaxis.range = ['{0} {1}:{2}:{3}'.format(date, format_two_digits(hour-1), 60-window_size, format_two_digits(second)),  x_value]      
    }
  }

    // automatically change temperature range
    if (y_value > 25) {
      layout.yaxis.range = [20,35]
    }
    else if (y_value < 25 && y_value > 15) {
      layout.yaxis.range = [15,25]
    }
    else if (y_value <15) {
      layout.yaxis.range = [10,25]
    }

    Plotly.relayout(plotting_element_ID, layout);
  }
  
  // plot with intervals
  setTimeout(() => {
    setInterval(() => {
      get_data_and_plot()
    }, 500);
  }, 2000)


  // a home-made function to ensure HH:MM:SS format when the value is single digit
  function format_two_digits(input_number_string) {
    return ("0" + input_number_string).slice(-2)  
  }
