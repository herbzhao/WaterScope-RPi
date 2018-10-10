// NOTE: use plotly and axios to plot data async
// NOTE: below is how we draw the graph


var trace = {
  x: [],
  y: [],
  type: 'line'
}

var plotting_element_ID = 'plotly_chart'
var API_url = '/parabolic_serial_monitor'

// generates a bare plot

setTimeout(() => {
  Plotly.newPlot(plotting_element_ID, data = [trace]);
}, 1000)

// update the value from axios
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises
// https://hashnode.com/post/how-can-i-use-the-data-of-axioss-response-outside-cj2yddlhx003kcfk8h8czfo7k
function get_data_and_plot() {
  axios.get(API_url).then(response => {

    x_value = response.data.x
    y_value = response.data.y
    // console.log(y_value)
    real_time_plotting(x_value, y_value)
  }).catch(error => console.log(error))
}


window_size = 200
var layout = {
  xaxis: {
    title: 'time (s)',
    range: [0, window_size]
  },
  yaxis: {
    title: 'temperature (°c)',
    range:[10,35]
  }
}

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
  if (x_value > window_size) {
    layout['xaxis']['range'] = [x_value - window_size, x_value]    
  }
  Plotly.relayout(plotting_element_ID, layout);
}

// plot with intervals
setTimeout(() => {
  setInterval(() => {
    get_data_and_plot()
  }, 500);
}, 2000)