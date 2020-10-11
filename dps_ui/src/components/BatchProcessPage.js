import React from 'react';

import TextField from '@material-ui/core/TextField';
import CheckBox from '@material-ui/core/CheckBox';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import FormLabel from '@material-ui/core/FormLabel';

import {
  DateTimePicker,
} from '@material-ui/pickers';

import Box from './Box';
import PrettyTable from './PrettyTable';
import EntitySelect from './EntitySelect';

import { get, get_required_mappings } from '../api';

export default class BatchProcessPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      system: {
        name: '',
        kpis: [],
        parameters: [],
      },

      startDate: new Date(),
      endDate: new Date(),
    };
  }
  
  async componentDidMount() {
    const id = window.location.href.split('/').pop();
    get('system', id).then(system => {
      this.setState({ system });
      get_required_mappings(system, system.kpis.map(x => x.name)).then(x => console.log(x));
    });
  }

  render () {
    const props = this.props;

    const rows = this.state.system.kpis.filter(kpi => !kpi.hidden).map(kpi => {
      return [
        <CheckBox color="primary" />,
        kpi.name,
        kpi.description,
        '',
        '',
      ]
    });

    return (
      <Box
        header={this.state.system.name}
      >
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormLabel>KPIs</FormLabel>
            <PrettyTable
              header={['', 'Computation', 'Description', 'Last Run', 'Result']}
              rows={rows}
            />
          </Grid>

          {/*           <Grid item xs={12}> */}
          {/*             <TextField */}
          {/*               label="Warning Log" */}
          {/*               multiline={true} */}
          {/*               fullWidth={true} */}
          {/*               rows={10} */}
          {/*               variant="outlined" */}
          {/*               disabled={true} */}
          {/*               value={`8/20/2020 13:23:93.4234: THD Va above 10% */}
          {/* 8/21/2020 11:43:32.4353: Efficiency below 20% */}
          {/* `} */}
          {/*             > */}
          {/*             </TextField> */}
          {/*           </Grid> */}


          <Grid item xs={12}>
            <DateTimePicker value={this.state.startDate}
                            onChange={date => this.setState({ startDate: date })}
                            label="Start Time"
                            required />
            
          </Grid>

          <Grid item xs={12}>
            <DateTimePicker value={this.state.endDate}
                            onChange={date => this.setState({ endDate: date })}
                            label="End Time"
                            required />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Button style={{'marginRight': '10px'}} variant="contained" color="primary">Run</Button>
            <Button variant="contained" color="primary">Export</Button>            
	  </Grid>
        </Grid>
      </Box>
    );
  }
}
