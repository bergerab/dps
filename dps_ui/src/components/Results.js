import React from 'react';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import BatchResultTable from './BatchResultTable';

export default class ResultsPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };
  }
  
  render () {
    const tableRef = React.createRef();
    return (
      <Box header={"Batch Processes"}
           loading={this.state.loading}>
        <BatchResultTable
          system_id={292}/>
      </Box>
    );
  }
}