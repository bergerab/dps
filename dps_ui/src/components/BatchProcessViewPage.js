import React from 'react';

import moment from 'moment';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';

import api from '../api';

export default class BatchProcessViewPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      result: null,
      loading: true,
    };
  }

  async componentDidMount() {
    const id = this.props.match.params.id;
    api.get('get_batch_process_result', id).then(result => {
      this.setState({
        result,
        loading: false,
      });
    });
  }
  
  render () {
    if (this.state.loading) return (<div></div>);

    const bp = this.state.result.batch_process;
    const system = bp.system;

    console.log(bp, system)
    
    return (
      <Box header={'Batch Process #' + this.state.result.batch_process_id}
           loading={this.state.loading}>
        <Grid container spacing={2}
              style={{maxWidth: '1500px'}}>

          <Grid item xs={12}>
            <InputLabel>KPIs</InputLabel>
            <PrettyTable
              header={['KPI', 'Description', 'Value']}
              rows={[]}
            />
          </Grid>

          <Grid item xs={6}>
            <InputLabel>Signals</InputLabel>
            <PrettyTable
              header={['KPI Input', 'Signal Name']}
              rows={[]}
            />
          </Grid>

          <Grid item xs={6}>
            <InputLabel>Parameters</InputLabel>          
            <PrettyTable
              header={['Name', 'Value']}
              rows={[]}
            />
          </Grid>

          <Grid item xs={12}>
            <InputLabel>Date Range</InputLabel>
            {/* Hack to get moment to parse datetime as UTC: */}
            <TextField
              label="Start Time"
              InputProps={{
                readOnly: true,
              }}              
              value={moment(bp.interval.start + 'Z').format('LL LTS')}
              style={{ marginRight: '10px', width: '20em' }}/>
            <TextField
              InputProps={{
                readOnly: true,
              }}              
              label="End Time"
              value={moment(bp.interval.end + 'Z').format('LL LTS')}
              style={{ width: '20em' }}/>              
          </Grid>

        </Grid>
      </Box>
    );
  }
}
