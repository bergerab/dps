import React from 'react'

import { Line } from 'react-chartjs-2';
import 'chartjs-plugin-zoom';

import moment from 'moment';

import api from '../api';
import util from '../util';

import debounce from 'lodash/debounce';

function SignalChart(props) {

  const [data, setData] = React.useState([]);
  React.useEffect(() => {
    doFetch();
  }, []);

  const doFetch = debounce((startTime=props.startTime, endTime=props.endTime) => {
    fetchData(props.signals, startTime,
              endTime, props.samples,
              props.batch_process_id,
              props.dataset).then(series => {
                setData(series);
              });
  }, 500);

  const options = {
    animation: {
      duration: 0, // disable animations
    },
    scales: {
      xAxes: [{
        type: 'time'
      }]
    },
    pan: {
      enabled: false,
      mode: 'x',
      onPan: function({chart}) {
        const timeScales = chart.scales['x-axis-0'];
        const startTime = new Date(timeScales.min);
        const endTime = new Date(timeScales.max);            
        doFetch(startTime, endTime);
      }
    },
    zoom: {
                               drag: true,
                               enabled: true,         
                               mode: 'x',
                               threshold: 10,
                               onZoom: function({chart}) {
                                 const timeScales = chart.scales['x-axis-0'];
                                 const startTime = new Date(timeScales.min);
                                 const endTime = new Date(timeScales.max);            
                                 doFetch(startTime, endTime);            
                               }
                             },
                           };

                           if (props.title !== undefined) {
                             options.title = {
                               display: true,
                               text: props.title,
                               fontSize: 20
                             }
                           }

                           if (props.minimal) {
                             options.legend = {
                               display: false,
                             };
                           }
                           
                           return (
                             // A react-chart hyper-responsively and continuously fills the available
                             // space of its parent element automatically
                             <Line
                               data={data}
                               options={options}
                             />
                           );
}

const colors = [
  '#3f51b5',
  '#EBB07A',
  '#6AB890',
];

function fetchData(signals, startTime, endTime, samples, batch_process_id, dataset) {
  return new Promise(resolve => {
    var gmtOffset = -(new Date().getTimezoneOffset()/60);    
    startTime = moment.utc(startTime || moment().subtract('months', 1)); // should be UTC
    endTime = moment.utc(endTime || moment());
    samples = samples || 10;
    api.post('get_chart_data', {
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
          // d[1] = d[1] === null ? 0 : d[1]; //sets any null values to 0
        }
        s.backgroundColor = colors[colorIndex];
        colorIndex = (colorIndex + 1) % colorIndex;
      }

      resolve(data);
    });
  });
}

export default SignalChart;
