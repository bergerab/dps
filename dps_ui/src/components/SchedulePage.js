import React from 'react';

import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';

import {
  TimePicker,
} from '@material-ui/pickers';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import SignalTable from './SignalTable';
import BarChart from './BarChart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';
import EntityTable from './EntityTable';
import DatasetSelect from './DatasetSelect';
import Loader from './Loader';

import api from '../api';

const makeDefaultState = () => ({
  loading: false,

  object: {
    /* The time picker uses whole dates. So we will cut off the date part and just use the time. 
      The default will just be to collect 5 minutes of data from 8:00 to 8:05 (local time). */ 
    start: '2020-12-08 08:00:00.000',
    end:   '2020-12-08 08:05:00.000',
    day: 1,
    type: 0,        
  },

  errors: {
  }
});

export default class SchedulePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = makeDefaultState();
  }

  async componentDidMount() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;
    if (action === 'edit') {
      this.setState({ loading: true });
      api.get('schedule', id).then(schedule => {
        this.setState({
          object: {
            dataset: schedule.dataset,
            start: schedule.start,
            end: schedule.end,
            type: schedule.type,
            day: schedule.day,
          },
          loading: false,          
        });
      });
    }
  }

  setObject(o) {
    this.setState({ object: Object.assign({}, this.state.object, o) });
  }

  render() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;

    const dayInput = (<Grid item xs={12}>
                        <TextField
                          name="day"
                          value={this.state.object.day}
                          type={'number'}
                          required={true}
                          onChange={e => this.setObject({ day: e.target.value })}
                          label="Day of the Month"
                          helperText={this.state.errors.day}
                          error={this.state.errors.day !== undefined}
                        />
                      </Grid>);

    const add = action === 'add',
          edit = action === 'edit';

    if (add || edit) {
      return (
        <Loader
          loading={this.state.loading}
          text="Loading..."
        >
          <Box header={(add ? 'Add' : 'Edit') + " Schedule"}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <InputLabel>Dataset *</InputLabel>                                
                <DatasetSelect
                  limit={20}
                  value={{ value: this.state.object.dataset, label: this.state.object.dataset }}
                  helperText={this.state.errors.dataset}
                  error={this.state.errors.dataset !== undefined}
                  onChange={x => {
                    this.setObject({ dataset: x.value });
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <InputLabel>Interval *</InputLabel>                                
                <Select
                  value={this.state.object.type}
                  onChange={e => {
                    this.setObject({ type: e.target.value });                        
                  }}>
                  <MenuItem value={0}>Daily</MenuItem>
                  <MenuItem value={1}>Monthly</MenuItem>
                </Select>
              </Grid>

              {this.state.object.type === 1 ? dayInput : null}
              
              <Grid item xs={12}>
                <InputLabel>Time Range</InputLabel>            
                <TimePicker value={this.state.object.start}
                            onChange={date => this.setObject({ start: date })}
                            label="Start Time"
                            error={this.state.errors.start !== undefined}
                            helperText={this.state.errors.start}                                           
                            style={{marginRight: '20px'}}
                            required />
                <TimePicker
                  value={this.state.object.end}
                  onChange={date =>
                            this.setObject({ end: date })
                           }
                  error={this.state.errors.end !== undefined}
                  helperText={this.state.errors.end}
                  label="End Time"
                  required />
              </Grid>

              <Grid item>
                <Button variant="contained"
                        color="primary"
                        onClick={() => {
                          const handleError = x => {
                            x.then(jo => {
                              this.setState({ errors: jo });
                            });
                          }
                          
                          if (add) {
                            api.post('schedule', this.state.object).then(r => {
                              console.log(r);
                              window.history.back();
                              this.setState(makeDefaultState())                              
                            }).catch(handleError);
                          } else {
                            api.put('schedule', id, this.state.object).then(r => {
                              window.history.back();
                              this.setState(makeDefaultState())                                                            
                            }).catch(handleError);
                          }
                        }}>
                  Save
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Loader>);

    } else {
      return (<Box header={"Schedules"}
    >
                <EntityTable
                  idName="schedule_id"
                  entityName="schedule"
                  entityDisplayName="Schedule"
                  entityNameField={'dataset'}
                  columns={[
                    ['Dataset', x => x.dataset],
                  ]}/>
              <Grid container style={{ marginTop: '15px' }}>                
                  <Grid item>
                    <Link to={'/admin/schedule/add'} style={{ color: 'white' }}>              
                      <Button variant="contained" color="primary">
                        Add Schedule
                      </Button>
                    </Link>
                  </Grid>
                </Grid>
   </Box>);
    }
  }
}
