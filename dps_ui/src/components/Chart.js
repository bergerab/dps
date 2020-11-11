import React from 'react'
import { Chart } from 'react-charts'

import { Line } from 'react-chartjs-2';

import moment from 'moment';

import api from '../api';
import util from '../util';



function SignalChart(props) {
  const axes = React.useMemo(
    () => [
      { primary: true, type: 'linear', position: 'bottom' },
      { type: 'linear', position: 'left' },
    ],
    []
  );

  // const [data, setData] = React.useState([]);
  // React.useEffect(() => {
  //   const series = fetchData(props.signals, props.startTime,
  //                            props.endTime, props.samples,
  //                            props.batch_process_id).then(series => {
  //                              setData(series);
  //                            });
  // }, []);

  const [data, setData] = React.useState([]);
  const fetchData = React.useCallback(async () => {
    await  fetchData(props.signals, props.startTime,
                     props.endTime, props.samples,
                     props.batch_process_id).then(series => {
                       setData(series);
                     });
  }, []);
  

  const myData = React.useMemo(
    () => [
      {
        label: 'Series 1',
        data: [
          { primary: 1, secondary: 10 },
          { primary: 2, secondary: 10 },
          { primary: 3, secondary: 10 },
        ],
      },
    ],
    []
  )  
  
  return (
    // A react-chart hyper-responsively and continuously fills the available
    // space of its parent element automatically
    <div
      style={{
        width: '800px',
        height: '200px'
      }}
    >
      <Chart data={fetchData}
             series={{
               showPoints: true,
             }}
             axes={axes}
             tooltip />
    </div>
  );
}

function fetchData(signals, startTime, endTime, samples, batch_process_id) {
  return new Promise(resolve => {
    startTime = startTime || moment().subtract('months', 1);
    endTime = endTime || moment();
    samples = samples || 10;
    api.post('get_chart_data', {
      series: signals.map(x => {
        let dataset = '';
        if (batch_process_id) { /* If a batch_process_id is provided, set the magic dataset name. */
          dataset = 'batch_process_' + batch_process_id;
        }
        if (x.signal === undefined) throw Error('Charts require a signal name for each signal.');
        const o = {
          signal: x.signal,
          dataset,
          aggregation: x.aggregation === undefined ? 'average' : x.aggregation,
        };
        console.log(o);
        return o;
      }),
      interval: {
        start: util.dateToString(startTime),
        end:   util.dateToString(endTime),
      },
      samples: samples,
    }).then(data => {
      // Convert the strings for each series data into times.
      // The server returns strings, but react-charts needs javascript date objects.
      for (const s of data.series) {
        for (const d of s.data) {
          d[0] = new Date(Date.parse(d[0]));
          d[1] = d[1] === null ? 0 : d[1]; //sets any null values to 0
        }
      }

      resolve(data.series);
    });
  });
}

export default SignalChart;
