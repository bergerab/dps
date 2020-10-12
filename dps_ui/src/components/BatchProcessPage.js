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


import { get, get_required_mappings } from '../api';

export default class BatchProcessPage extends React.Component {
  constructor(props) {
    super(props);


    var defaultStartDate = new Date();
    defaultStartDate.setMonth(defaultStartDate.getMonth()-1);
    
    this.state = {
      system: {
        name: '',
        kpis: [],
        parameters: [],
      },

      kpis: new Set(),
      parameters: [],
      parameterInputs: {},
      signals: [],
      signalInputs: {},

      startDate: defaultStartDate,
      endDate: new Date(),
    };
  }
  
  async componentDidMount() {
    const id = window.location.href.split('/').pop();
    get('system', id).then(system => {
      this.setState({ system });
    });
  }

  render () {
    const updateMappings = () => {
      get_required_mappings(this.state.system, Array.from(this.state.kpis))
        .then(resp => {
          for (const signal of resp.signals) {
            if (!(signal in this.state.signalInputs)) {
              this.state.signalInputs[signal] = '';
            }
          }

          this.setState({
            signals: resp.signals.sort(),
            parameters: resp.parameters.sort(),
          });
        });
    };

    const handleKPICheck = (kpi, checked) => {
      if (checked) {
        this.state.kpis.add(kpi.name);
      } else {
        this.state.kpis.delete(kpi.name);
      }

      // Force an update
      this.setState({ kpis: this.state.kpis });
      updateMappings();
    };

    const rows = this.state.system.kpis.filter(kpi => !kpi.hidden).map(kpi => {
      return [
        <CheckBox color="primary"
                  className="kpi-cb"
                  checked={this.state.kpis.has(kpi.name)}
                  onChange={e => {
                    const checked = e.target.checked
                    handleKPICheck(kpi, checked);
                  }}/>,
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
              header={[<CheckBox color="primary"
                                 checked={JSON.stringify(this.state.system.kpis.filter(x => !x.hidden).map(x => x.name).sort()) ===
                                          JSON.stringify(Array.from(this.state.kpis).sort())}
                                 onChange={e => {
                                   const checked = e.target.checked;
                                   if (checked) {
                                     const s = new Set();
                                     for (const kpi of this.state.system.kpis) {
                                       const name = kpi.name;
                                       s.add(name);
                                     }
                                     this.setState({ kpis: s }, () => {
                                       updateMappings();
                                     });
                                   } else {
                                     this.setState({ kpis: new Set() }, () => {
                                       updateMappings();
                                     });
                                   }
                                 }}
                       />, 'KPI', 'Description', 'Last Run', 'Result']}
              rows={rows}
            />
          </Grid>

          <Grid item xs={6}>
            <FormLabel>Signals</FormLabel>
            <PrettyTable
              header={['Name', 'Value']}
              rows={this.state.signals.map(signal => {
                return [
                  signal,
                  (<TextField
            fullWidth={true}
            name="name"
            value={signal in this.state.signalInputs ? this.state.signalInputs[signal] : ''}
            onChange={e => {
              this.state.signalInputs[signal] = e.target.value;
              // Force an update
              this.setState({ signals: this.state.signals });
            }}
                      />)
                ];
              })}
            />
          </Grid>
          
          <Grid item xs={6}>
            <FormLabel>Parameters</FormLabel>
            <PrettyTable
              header={['Name', 'Value']}
              rows={this.state.parameters.map(parameter => {
                return [
                  parameter,
                  (<TextField
                      fullWidth={true}
                      name="name"
                      value={parameter in this.state.parameterInputs ? this.state.parameterInputs[parameter] : ''}
                      onChange={e => {
                        this.state.parameterInputs[parameter] = e.target.value;
                        // Force an update
                        this.setState({ parameters: this.state.parameters });
                      }}
            />)
                ];
              })}
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


          <Grid container>
            <Grid item xs={12} sm={12} md={6}>
              <DateTimePicker value={this.state.startDate}
                              onChange={date => this.setState({ startDate: date })}
                              label="Start Time"
                              required />
              
            </Grid>

            <Grid item xs={12} sm={12} md={6}>
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
        </Grid>
      </Box>
    );
  }
}
