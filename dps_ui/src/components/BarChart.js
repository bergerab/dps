import React from 'react';
import {Bar} from 'react-chartjs-2';

import Paper from '@material-ui/core/Paper';

export default class BarChart extends React.Component {
  render() {
    const data = {
      labels: this.props.labels,
      datasets: [
        {
          label: this.props.label,
          backgroundColor: '#3f51b5',
          borderWidth: 2,
          data: this.props.data,
        }
      ]
    }

    return (
      <Paper style={{  padding: '1em 1em 3.3em 1em' }}>  {/* Bottom padding matches size of icon buttons for line charts */}
        <h2 style={{ padding: '0 0 0.5em 0', margin: 0, textAlign: 'center' }}>{this.props.title}</h2>
        <Bar
          data={data}
          options={{
          }}
        />
      </Paper>
    );
  }
}
