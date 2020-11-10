import React from 'react'
import { Chart } from 'react-charts'

import moment from 'moment';

import api from '../api';
import util from '../util';

class SignalChart extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
      data:    [],
    };
  }
  
  componentDidMount() {
    let startTime = this.props.startTime || moment().subtract('months', 1);
    let endTime = this.props.endTime || moment();
    const samples = this.props.samples || 10;
    api.post('get_chart_data', {
      series: this.props.signals.map(x => {
        let dataset = '';
        if (x.batch_process_id) { /* If a batch_process_id is provided, set the magic dataset name. */
          dataset = 'batch_process_' + x.batch_process_id;
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
          d[0] = Date.parse(d[0]);
        }
      }
      console.log(data);
      this.setState({
        loading: false,
        data:    data.series,
      })
    });
  }
  
  render() {
    let axes = this.props.axes || [
      {
        primary: true,
        type: 'linear',
        position: 'bottom'
      },
      {
        type: 'linear',
        position: 'left'
      }
    ];
    
    return (
      // A react-chart hyper-responsively and continuously fills the available
      // space of its parent element automatically
      <div
        style={{
          width: '400px',
          height: '300px'
        }}
      >
        <Chart data={this.state.data} axes={axes} />
      </div>
    );
  }
}

export default SignalChart;
