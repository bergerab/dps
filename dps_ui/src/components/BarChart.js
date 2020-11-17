import React from 'react';
import {Bar} from 'react-chartjs-2';

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
      <div>
        <Bar
          data={data}
          options={{
            title:{
              display:true,
              text:this.props.title,
              fontSize:20
            },
          }}
        />
      </div>
    );
  }
}
