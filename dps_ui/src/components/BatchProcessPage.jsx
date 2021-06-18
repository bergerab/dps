import React from 'react';

import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import FormLabel from '@material-ui/core/FormLabel';
import { useHistory } from "react-router-dom";
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';

import Skeleton from '@material-ui/lab/Skeleton';

import {
  DateTimePicker,
} from '@material-ui/pickers';

import Box from './Box';
import PrettyTable from './PrettyTable';
import InputLabel from './InputLabel';
import Errors from './Errors';
import SignalSelect from './SignalSelect';
import DatasetSelect from './DatasetSelect';

import util from '../util';
import api from '../api';

import moment from 'moment';

import { get, post, get_required_mappings } from '../api';

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

      dataset: { value: '' },

      errors: null,
      mappingErrors: null,      

      kpis: new Set(),
      parameters: [],
      parameterInputs: {},
      signals: [],
      signalInputs: {},

      name: '',
      nameErrors: null,

      intervalErrors: null,
      useDateRange: false,
      startDate: defaultStartDate,
      endDate: new Date(),

      kpiResults: {},
    };
  }

  getParameterIdentifier(name) {
    for (const parameter of this.state.system.parameters) {
      if (parameter.name === name) {
        // console.log(parameter.name, name, parameter.identifier);
        return typeof parameter.identifier === 'string' &&
          parameter.identifier !== '' ? parameter.identifier : parameter.name;
      }
    }
    return name;
  }

  makeObject() {
    const mappings = this.state.signals.map((x, i) => ({
      key: x,
      value: this.state.signalInputs[x].value
    })).concat(
      this.state.parameters.map((x, i) => {
	let value = this.state.parameterInputs[x];
	let re = new RegExp(/^(\d+(\.\d+)?)(ms|s|m|h|d)$/)

	// if value is a time duration without quotes, then add quotes to make it a string literal.
	if (re.test(value)) {
		value = '"' + value + '"';
	}
	      
      	return {
        	key: this.getParameterIdentifier(x),
        	value: value
      	};
      })
    );
   
    // If date is chosen by DateTimePicker, it becomes the Moment object
    // and we have to call 'toDate' to get the date.
    let startDate = this.state.startDate, endDate = this.state.endDate;
    if(startDate.toDate) startDate = startDate.toDate();
    if(endDate.toDate) endDate = endDate.toDate();
    startDate = util.dateToString(util.dateToUTCDate(startDate));
    endDate = util.dateToString(util.dateToUTCDate(endDate));
    return {
      name: this.state.name,
      dataset: this.state.dataset.value,
      mappings: mappings,
      system: this.state.system,
      system_id: this.state.system.system_id,
      kpis: Array.from(this.state.kpis),            
      interval: {
        start: startDate,
        end: endDate,
      },
      use_date_range: this.state.useDateRange,
    };
  }

  localSave() {
    const o = {
      dataset: this.state.dataset,            
      kpis: Array.from(this.state.kpis),
      parameterInputs: this.state.parameterInputs,
      signalInputs: this.state.signalInputs,
      name: this.state.name,

      // Don't save the dates (let it use default of one month in the past)
      // startDate: this.state.startDate.toJSON(),
      // endDate: this.state.endDate.toJSON(),

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
      // console.log(o.kpis);
      const s = new Set();
      // Only add KPIs which exist in the system (for the case where a kpi name has changed since the last load)
      const allKpis = this.state.system.kpis.map(x => x.name);
      for (const kpi of o.kpis) {
        if (allKpis.includes(kpi)) {
          s.add(kpi);
        }
      }
      o.kpis = s;
    }

    if (o.startDate !== undefined) {
      o.startDate = new Date(o.startDate);
    }

    if (o.endDate !== undefined) {
      o.endDate = new Date(o.endDate);
    }
    
    this.setState(Object.assign(o, { localLoaded: true }), () => {
      this.updateMappings();
    });
  }

  getKPIResultByName(kpi_name) {
    return this.state.kpiResults[kpi_name];
  }
  
  async componentDidMount() {
    get('system', this.props.system_id).then(system => {
      this.setState({
        system,
        loading: false,
      }, () => {
        this.localLoad();
      });
      });
    
    this.updateKPIResults(this.props.system_id);
    // this.intervalId = setInterval(() => {
    //   this.updateKPIResults(this.props.system_id);
    // }, 1000);
  }

  // componentWillUnmount() {
  //   clearInterval(this.intervalId);
  // }  

  updateKPIResults(system_id) {
    api.post('get_kpis', {
      system_id: system_id,
    }).then(resp => {
      const results = {};
      for (const kpi of resp.kpis) {
        results[kpi.name] = kpi;
      }
      this.setState({ kpiResults: results });
      // console.log(results);
    });
  }

  getParameterDefault(name) {
    for (const parameter of this.state.system.parameters) {
      if (parameter.name === name) {
        return parameter.default;
      }
    }
    return undefined;
  }

  updateMappings() {
    return get_required_mappings(this.state.system, Array.from(this.state.kpis))
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

	this.state.parameters.map(name => {
		if (! this.state.parameterInputs[name]) { 
			this.state.parameterInputs[name] = this.getParameterDefault(name); 
		}
	});

	// force the UI to update the parameter values
	this.setState({parameterInputs: this.state.parameterInputs});
      });
  }

  render () {
    // If we attempted to load from localStorage already, save
    if (this.state.localLoaded) {
      this.localSave();
    }

    const handleKPICheck = (kpi, checked) => {
      if (checked) {
        this.state.kpis.add(kpi.name);
      } else {
        this.state.kpis.delete(kpi.name);
      }

      // Force an update
      this.setState({ kpis: this.state.kpis });
      this.updateMappings();
    };

    const rows = this.state.system.kpis.filter(kpi => !kpi.hidden).map(kpi => {
      return [
        <Checkbox color="primary"
        className="kpi-cb"
        checked={this.state.kpis.has(kpi.name)}
        onChange={e => {
                    const checked = e.target.checked
                    handleKPICheck(kpi, checked);
                  }}/>,
        kpi.name,
        <div dangerouslySetInnerHTML={{ __html: kpi.description }}></div>,
      ]
    });

    const name = this.state.loading ?
          (<Skeleton width="150pt"/>) :
          this.state.system.name;

    const allKpis = this.state.system.kpis.filter(x => !x.hidden).map(x => x.name).sort();
    const selectedKpis = Array.from(this.state.kpis).sort();
    const checked = util.arrayEqual(allKpis, selectedKpis);
    const indeterminate = selectedKpis.length > 0 && !util.arrayEqual(allKpis, selectedKpis);

	const makeKPITableHeader = loading => [loading ? <Checkbox checked={false}
        indeterminate={false}
        color="primary"/> :
        <Checkbox color="primary"
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
        this.updateMappings();
        });
        } else {
        this.setState({ kpis: new Set() }, () => {
        this.updateMappings();
        });
        }
        }}
                                           />, 'KPI', 'Description'];

    const kpiTable = this.state.loading ?
          (<PrettyTable
             header={makeKPITableHeader(true)}
             rows={[1,2,3,4,5].map((_, i) => [
               <Checkbox checked={false} color="primary" key={'cb' + i} />,
               <Skeleton key={'s1' + i} />,
               <Skeleton key={'s2' + i} />,
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
          header={name + ' - Batch Process'}
          loading={this.state.loading}
        >
          <Grid container spacing={2}
                style={{maxWidth: '1500px'}}>
            {description}

            <Grid item xs={12} s={6}>
              <InputLabel>Identifier</InputLabel>              
              <TextField
                label="Name"
                fullWidth={true}                
                value={this.state.name}
                onChange={e => this.setState({ name: e.target.value })}
                error={this.state.nameErrors !== null}
                helperText={this.state.nameErrors}/>
            </Grid>

            <Grid item xs={12} s={6}>
              <InputLabel>Dataset</InputLabel>
              <DatasetSelect
                limit={20}
                value={this.state.dataset}
                onChange={e => {
                  const inputs = {};
                  for (const key in this.state.signalInputs) {
                    inputs[key] = '';
                  }
                  this.setState({
                    dataset: e,
                    signalInputs: inputs,
                  });
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <InputLabel>KPIs</InputLabel>
              {kpiTable}
            </Grid>

            <Grid item xs={6}>
              <InputLabel>Signals</InputLabel>
              <PrettyTable
                key={this.state.dataset.value}
                header={['KPI Input', 'Signal Name']}
                rows={this.state.signals.map((signal, i) => {
                  const hasError = this.state.mappingErrors !== null &&
                        i in this.state.mappingErrors &&
                        !util.objectIsEmpty(this.state.mappingErrors[i]);
                  const signalValue = signal in this.state.signalInputs ? this.state.signalInputs[signal] : '';
                  return [
                    signal,
                    (<SignalSelect
                       dataset={this.state.dataset.value}
                       value={signalValue}
                       onChange={e => {
                         this.state.signalInputs[signal] = e;
                         // Force an update
                         this.setState({ signals: this.state.signals });
                       }}
                       error={hasError}
                       helperText={hasError ? this.state.mappingErrors[i].value : ''}
                       limit={20}
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
              <label>Use Date Range</label>
              <Checkbox
                color="primary"
                checked={this.state.useDateRange}
                onChange={e => this.setState({ useDateRange: e.target.checked })}
              />
            </Grid>

            {!this.state.useDateRange ? null :
             <Grid item xs={12} >
               <InputLabel>Date Range</InputLabel>            
               <DateTimePicker value={this.state.startDate}
                               onChange={date => this.setState({ startDate: date })             }
                               label="Start Time"
                               error={hasStartTimeError}
                               helperText={hasStartTimeError ? this.state.intervalErrors.start : ''}                                           
                               style={{marginRight: '20px'}}
                               required />
               <DateTimePicker value={this.state.endDate}
                              onChange={date => this.setState({ endDate: date })}
                              error={hasEndTimeError}
                              helperText={hasEndTimeError ? this.state.intervalErrors.end : ''}
                              label="End Time"
                              required />
             </Grid>}

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
                            nameErrors: null,                            
                          });
                          this.props.history.push('/system/' + this.props.system_id);
                        }).catch(e => {
                          console.log(e);
                          e.then(errors => {
                            const mappingErrors = util.objectPop(errors, 'mappings');
                            const intervalErrors = util.objectPop(errors, 'interval');
                            const nameErrors = util.objectPop(errors, 'name');                            
                            this.setState({
                              errors,
                              mappingErrors,
                              intervalErrors,
                              nameErrors,
                            });
                          });
                        });
                      }}
              >Run</Button>
            </Grid>
          </Grid>
        </Box>
      </Grid>      
    );
  }
}
