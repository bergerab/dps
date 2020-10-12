import React from 'react';

import TextField from '@material-ui/core/TextField';
import CheckBox from '@material-ui/core/CheckBox';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import FormLabel from '@material-ui/core/FormLabel';

import Skeleton from '@material-ui/lab/Skeleton';

import {
  DateTimePicker,
} from '@material-ui/pickers';

import Box from './Box';
import PrettyTable from './PrettyTable';
import InputLabel from './InputLabel';


import { get, get_required_mappings } from '../api';

export default class BatchProcessPage extends React.Component {
  constructor(props) {
    super(props);

    var defaultStartDate = new Date();
    defaultStartDate.setMonth(defaultStartDate.getMonth()-1);
    
    this.state = {
      system: {
        name: '',
        description: '',
        kpis: [],
        parameters: [],
      },

      loading: true,

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
      this.setState({
        system,
        loading: false,
      });
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
          <div dangerouslySetInnerHTML={{ __html: kpi.description }}></div>,
          '',
          '',
        ]
      });

      const name = this.state.loading ?
            (<Skeleton width="150pt"/>) :
            this.state.system.name;

      const makeKPITableHeader = loading => [loading ? <CheckBox color="primary"/> :
                                             <CheckBox color="primary"
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
                                             />, 'KPI', 'Description', 'Last Run', 'Result'];

    const kpiTable = this.state.loading ?
          (<PrettyTable
             header={makeKPITableHeader(true)}
             rows={[1,2,3,4,5].map((_, i) => [
               <CheckBox color="primary" key={'cb' + i} />,
               <Skeleton key={'s1' + i} />,
               <Skeleton key={'s2' + i} />,
               <Skeleton key={'s3' + i} />,
               <Skeleton key={'s4' + i} />,
             ])}/>) :
          (<PrettyTable
             header={makeKPITableHeader(false)}
             rows={rows}
           />);

    const description =
          this.state.system.description !== '' &&
          this.state.system.description !== null &&
          this.state.system.description !== undefined ?
          (<Grid item xs={12}>
             <div dangerouslySetInnerHTML={{ __html: this.state.system.description }}></div>
           </Grid>) :
          null;

    return (
          <Box
            header={name}
            loading={this.state.loading}
          >
            <Grid container spacing={2}
                  style={{maxWidth: '1500px'}}>
              {description}
              
              <Grid item xs={12}>
                <InputLabel>KPIs</InputLabel>
                {kpiTable}
              </Grid>

              <Grid item xs={6}>
                <InputLabel>Signals</InputLabel>
                <PrettyTable
                  header={['KPI Input', 'Signal Name']}
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
                <InputLabel>Parameters</InputLabel>
                <PrettyTable
                  header={['KPI Input', 'Signal Name']}
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

              <Grid item xs={12}>
                <InputLabel>Date Range</InputLabel>            
                <DateTimePicker value={this.state.startDate}
                                onChange={date => this.setState({ startDate: date })}
                                label="Start Time"
                                style={{marginRight: '20px'}}
                                required />
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
