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
import Errors from './Errors';

import util from '../util';
import api from '../api';

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

      errors: null,
      mappingErrors: null,      

      kpis: new Set(),
      parameters: [],
      parameterInputs: {},
      signals: [],
      signalInputs: {},

      intervalErrors: null,
      startDate: defaultStartDate,
      endDate: new Date(),
    };
  }

  makeObject() {
    const mappings = this.state.signals.map((x, i) => ({
      key: x,
      value: this.state.signalInputs[x]
    })).concat(
      this.state.parameters.map((x, i) => ({
        key: x,
        value: this.state.parameterInputs[x]
      }))
    );
    return {
      mappings: mappings,
      system_id: this.state.system.system_id,
      interval: {
        start: util.dateToString(this.state.startDate),
        end: util.dateToString(this.state.endDate),
      }
    };
  }

  localSave() {
    const o = {
      errors: this.state.errors,
      mappingErrors: this.state.mappingErrors,      
      kpis: Array.from(this.state.kpis),
      parameters: this.state.parameters,
      parameterInputs: this.state.parameterInputs,
      signals: this.state.signals,
      signalInputs: this.state.signalInputs,

      intervalErrors: this.state.intervalErrors,
      startDate: this.state.startDate.toJSON(),
      endDate: this.state.endDate.toJSON(),

      localLoaded: false,
    };
    localStorage.setItem(this.getLocalStorageItemName(), JSON.stringify(o));
  }

  getLocalStorageItemName() {
    // I don't think adding the name is necessary (introduces tiny memory leak when name changes)
    return 'batch-process;' + this.state.system.system_id + ';' + this.state.system.name;
  }

  localLoad() {
    const o = JSON.parse(localStorage.getItem(this.getLocalStorageItemName())) || {};
    if (o.kpis !== undefined) {
      o.kpis = new Set(o.kpis);
    }

    if (o.startDate !== undefined) {
      o.startDate = new Date(o.startDate);
    }

    if (o.kpis !== undefined) {
      o.endDate = new Date(o.endDate);
    }
    
    this.setState(Object.assign(o, { localLoaded: true }));
  }
  
  async componentDidMount() {
    const id = window.location.href.split('/').pop();
    get('system', id).then(system => {
      this.setState({
        system,
        loading: false,
      }, () => {
        this.localLoad();
      });
    });
  }

  render () {
    // If we attempted to load from localStorage already, save
    if (this.state.localLoaded) {
      this.localSave();
    }

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

    const allKpis = this.state.system.kpis.filter(x => !x.hidden).map(x => x.name).sort();
    const selectedKpis = Array.from(this.state.kpis).sort();
    const checked = util.arrayEqual(allKpis, selectedKpis);
    const indeterminate = selectedKpis.length > 0 && !util.arrayEqual(allKpis, selectedKpis);

    const makeKPITableHeader = loading => [loading ? <CheckBox checked={false}
                                                                            indeterminate={false}
                                                                            color="primary"/> :
                                           <CheckBox color="primary"
                                                     checked={checked}
                                                     indeterminate={indeterminate}                                             
                                                     onChange={e => {
                                                       const checked = e.target.checked;
                                                       if (checked) {
                                                         const s = new Set();
                                                         for (const kpi of this.state.system.kpis) {
                                                           const name = kpi.name;
                                                           if (!kpi.hidden) {
                                                             s.add(name);
                                                           }
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
             <CheckBox checked={false} color="primary" key={'cb' + i} />,
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
             <div className="system-description" dangerouslySetInnerHTML={{ __html: this.state.system.description }}></div>
           </Grid>) :
          null;

    const hasStartTimeError = this.state.intervalErrors !== null &&
          'start' in this.state.intervalErrors &&
          !util.objectIsEmpty(this.state.intervalErrors.start);
    const hasEndTimeError = this.state.intervalErrors !== null &&
          'end' in this.state.intervalErrors &&
          !util.objectIsEmpty(this.state.intervalErrors.end);

    return (
        <Grid container>
          {this.state.errors !== null && !util.objectIsEmpty(this.state.errors) ?
           (<Grid item style={{marginBottom: '2em', width: '100%' }}>
        <Errors
          errors={this.state.errors}
        />
      </Grid>) : null
          }

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
                  rows={this.state.signals.map((signal, i) => {
                    const hasError = this.state.mappingErrors !== null &&
                          i in this.state.mappingErrors &&
                          !util.objectIsEmpty(this.state.mappingErrors[i]);
                    
                    return [
                      signal,
                      (<TextField
                    fullWidth={true}
                    name="name"
                    error={hasError}
                    helperText={hasError ? this.state.mappingErrors[i].value : ''}
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
                  header={['Name', 'Value']}
                  rows={this.state.parameters.map((parameter, i) => {
                    const mappingIndex = i + this.state.signals.length;
                    
                    const hasError = this.state.mappingErrors !== null &&
                          mappingIndex in this.state.mappingErrors &&
                          !util.objectIsEmpty(this.state.mappingErrors[mappingIndex]);
                    
                    return [
                      parameter,
                      (<TextField
                                                                                fullWidth={true}
                  name="name"
                  error={hasError}
                       helperText={hasError ? this.state.mappingErrors[mappingIndex].value : ''}
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
                              error={hasStartTimeError}
                              helperText={hasStartTimeError ? this.state.intervalErrors.start : ''}                                           
                              style={{marginRight: '20px'}}
                              required />
              <DateTimePicker value={this.state.endDate}
                              onChange={date => this.setState({ endDate: date })}
                              error={hasEndTimeError}
                              helperText={hasEndTimeError ? this.state.intervalErrors.end : ''}                                           label="End Time"
                              required />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Button style={{'marginRight': '10px'}}
                      variant="contained"
                      color="primary"
                      onClick={e => {
                        const value = e.target.value;
                        const obj = this.makeObject();
                        api.post('batch_process', obj).then(() => {
                          
                          this.setState({
                            errors: null,
                            mappingErrors: null,
                            intervalErrors: null,
                          });
                        }).catch(e => {
                          e.then(errors => {
                            const mappingErrors = util.objectPop(errors, 'mappings');
                            const intervalErrors = util.objectPop(errors, 'interval');
                            this.setState({
                              errors,
                              mappingErrors,
                              intervalErrors,
                            });
                          });
                        });
                      }}
              >Run</Button>
              <Button variant="contained" color="primary">Export</Button>            
            </Grid>
          </Grid>
        </Box>
      </Grid>      
    );
  }
}
