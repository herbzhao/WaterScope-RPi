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
Plotly.newPlot(plotting_element_ID, data = [trace]);

// update the value from axios
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises
// https://hashnode.com/post/how-can-i-use-the-data-of-axioss-response-outside-cj2yddlhx003kcfk8h8czfo7k
function getData() {
  axios.get(API_url).then(response => {

    x_value = response.data.x
    y_value = response.data.y
    console.log(y_value)
    real_time_plotting(x_value, y_value)
  })
}


window_size = 10
var layout = {
  xaxis: {
    title: 'time (s)',
    range: [0, window_size]
  },
  yaxis: {
    title: 'temperature (°c)',
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
    Plotly.relayout(plotting_element_ID, layout);
  }
}

// plot with intervals
setInterval(function () {
  getData()
}, 100);