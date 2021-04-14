import React from 'react'

import { Line } from 'react-chartjs-2';
import 'chartjs-plugin-zoom';

import LoadingOverlay from 'react-loading-overlay';

import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import RefreshIcon from '@material-ui/icons/Refresh';
import ZoomOutIcon from '@material-ui/icons/ZoomOut';

import moment from 'moment';

import api from '../api';
import util from '../util';

import debounce from 'lodash/debounce';

class SignalChart extends React.Component {
  constructor(props) {
    super(props);
    this.chartRef = React.createRef();
    this.state = {
      data: [],
      loading: true,
    };
  }

  componentDidMount() {
    // Infer time range for first chart load 
    // any subsequent loads should not be inferred (the user will pan/zoom)
    this.doFetch(undefined, undefined, true);
  }

  doFetch = debounce((startTime=this.props.startTime, endTime=this.props.endTime, infer=false, pad=false) => {
    this.setState({ loading: true });
    fetchData(this.getChartInstance(),
              this.props.signals, startTime,
              endTime, this.props.samples,
              this.props.batch_process_id,
              this.props.dataset,
              infer,
              pad
             ).then(series => {
               this.setState({ data: series });
               this.setState({ loading: false });                                
              });
  }, 500);

  getChartInstance = () => {
    if (this.chartRef.current === undefined || this.chartRef.current === null)
      return null;
    if (this.chartRef.current.chartInstance === undefined || this.chartRef.current.chartInstance === null)
      return null;
    return this.chartRef.current.chartInstance;
  }

  refresh = (chart, pad) => {
    const timeScales = chart.scales['x-axis-0'];
    const startTime = new Date(timeScales.min);
    const endTime = new Date(timeScales.max);
    this.setState({ loading: true });                                      
    this.doFetch(startTime, endTime, undefined, pad);
  };

  render() {
    const options = {
      animation: {
        duration: 0, // disable animations
      },
      scales: {
        xAxes: [{
          type: 'time',
          ticks: {
            /* The x axis ticks are problematic -- ChartJS uses too many and it pushes the chart upwards unless you configure them properly. */
            maxTicksLimit: 2, /* Only ever have 2 ticks */
            maxRotation: 0, /* Don't rotate the ticks. */
            minRotation: 0,            
          }
        }]
      },
      pan: {
        enabled: false,
        mode: 'x',
        onPan: ({chart}) => {
          this.refresh(chart, true);
        }
      },
      zoom: {
        drag: true,
        enabled: true,         
        mode: 'x',
        threshold: 10,
        onZoom: ({chart}) => {
          this.refresh(chart, true);
        }
      },
    };

    // Chart.JS titel. Currently commented out with "false &&" because i've added our own title
    if (false && this.props.title !== undefined) {
      options.title = {
        display: true,
        text: this.props.title,
        fontSize: 20
      }
    }

    if (this.props.showLegend === undefined || this.props.showLegend === false) {
      options.legend = {
        display: false,
      };
    }

    if (this.props.minimal) {
      options.legend = {
        display: false,
      };
    }
    
    return (
      // A react-chart hyper-responsively and continuously fills the available
      // space of its parent element automatically
      <Paper style={{  padding: '1em 1em 0 1em' }}>
        <h2 style={{ padding: '0 0 0.5em 0', margin: 0, textAlign: 'center' }}>{this.props.title}</h2>
        <LoadingOverlay
          active={this.state.loading}
          text="Loading chart..."
          spinner={<div><CircularProgress /></div>}
          styles={{
            overlay: (base) => ({
              ...base,
              background: 'rgba(255, 255, 255, 0.5)'
            }),
            content: (base) => ({
              ...base,
              color: '#AAAAAA',
              fontSize: '0.9em',
            }),
          }}
        >

          <Line
            data={this.state.data}
            options={options}
            ref={this.chartRef}
          />
        </LoadingOverlay>        
        <div>
          <Tooltip title="Zoom Out" aria-label="zoom out">
            <IconButton aria-label="zoom out"
                        onClick={() => {
                          this.doFetch(undefined, undefined, true); // Infer the time range to zoom out
                        }}>
              <ZoomOutIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh" aria-label="refresh">
            <IconButton aria-label="refresh"
                        onClick={() => {
                          this.refresh(this.getChartInstance(), false);
                        }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </div>
      </Paper>

    );
    }
}

const colors = [
  '#3f51b5',
  '#EBB07A',
  '#6AB890',
];

function fetchData(chart, signals, startTime, endTime, samples, batch_process_id, dataset, infer, pad) {
  return new Promise(resolve => {
    var gmtOffset = -(new Date().getTimezoneOffset()/60);    
    startTime = moment.utc(startTime || moment().subtract('months', 1)); // should be UTC
    endTime = moment.utc(endTime || moment());
    samples = samples || 10;
    api.post('get_chart_data', {
      infer: infer,
      pad: pad,      
      series: signals.map(x => {
        let ds = dataset;
        if (batch_process_id !== undefined) { /* If a batch_process_id is provided, set the magic dataset name. */
          ds = 'batch_process' + batch_process_id;
        }
        if (x.signal === undefined) throw Error('Charts require a signal name for each signal.');
        const o = {
          signal: x.signal,
          dataset: ds,
          aggregation: x.aggregation === undefined ? 'average' : x.aggregation,
        };
        return o;
      }),
      interval: {
        start: util.dateToString(startTime),
        end:   util.dateToString(endTime),
      },
      samples: samples,
      offset: gmtOffset,
    }).then(data => {
      // Convert the strings for each series data into times.
      // The server returns strings, but chartjs needs javascript date objects.
      let colorIndex = 0;      
      for (const s of data.datasets) {
        for (const d of s.data) {
          d.x = new Date(Date.parse(d.x + 'Z'));
        }
        s.backgroundColor = colors[colorIndex];
        colorIndex = (colorIndex + 1) % colorIndex;
      }

      // If the server inferred the time range, set the chart's time range to the one returned by the server
      if (infer && chart !== null && chart.$zoom !== undefined) { // $zoom -- I was getting a strange error from the chartjs zoom plugin unless I checked this (happened on navigating pages while chart was loading)
        chart.resetZoom();
      }
      
      resolve(data);
    });
  });
}

export default SignalChart;
