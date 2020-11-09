import React from 'react';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import BatchResultTable from './BatchResultTable';

export default class EndUserSystemPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };
  }
  
  render () {
    const tableRef = React.createRef();
    return (
      <Box header={this.props.system_name}
           loading={this.state.loading}>
        <BatchResultTable
          system_id={this.props.system_id}/>

        <Link to={'/system/' + this.props.system_id + '/batch-process'}> 
          <Button variant="contained" color="primary" style={{ marginTop: '15px' }}>
            Create Batch Process
          </Button>
        </Link>
      </Box>
    );
  }
}
