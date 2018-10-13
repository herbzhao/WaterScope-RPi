// NOTE: use plotly and axios to plot data async
// NOTE: below is how we draw the graph


var trace = {
    x: [],
    y: [],
    type: 'line'
  }
  
  var plotting_element_ID = 'plotly_chart'
  var API_url = '/parabolic_serial_monitor'
  
  // generates a bare plot - responsive as well
  Plotly.newPlot(plotting_element_ID, data = [trace], layout = {}, config = {responsive: true});
  
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
  
  // the size of x-range
  window_size = 200
  var layout = {
    xaxis: {
      title: 'time (s)',
      range: [0, window_size]
    },
    yaxis: {
      title: 'temperature (°c)',
      range: [15, 35]
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
      layout['xaxis']['range'] = [x_value - window_size/2, x_value+ window_size/2]
    }
    // automatically change temperature range
    if (y_value > 25) {
      layout['yaxis']['range'] = [20,35]
    }
    else if (y_value < 25 && y_value > 15) {
      layout['yaxis']['range'] = [15,25]
    }
    else if (y_value <15) {
      layout['yaxis']['range'] = [10,25]
    }

    Plotly.relayout(plotting_element_ID, layout);
  }
  
  // plot with intervals
  setTimeout(() => {
    setInterval(() => {
      get_data_and_plot()
    }, 500);
  }, 2000)