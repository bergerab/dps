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

export default class SchedulePage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,

      object: {
        start: '8:00 PM',
        end: new Date(),
        day: 1,
        type: 0,        
      },

      errors: {
        start: null,
        end: null,
        day: null,
        dataset: null,
      }
    };
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
                          error={this.state.errors.day !== null}
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
                            error={this.state.errors.start !== null}
                            helperText={this.state.errors.start}                                           
                            style={{marginRight: '20px'}}
                            required />
                <TimePicker value={this.state.object.end}
                            onChange={date =>
                                      this.setObject({ end: date })
                                     }
                            error={this.state.errors.end !== null}
                            helperText={this.state.errors.end}
                            label="End Time"
                            required />
              </Grid>

              <Grid item>
                <Button variant="contained"
                        color="primary"
                        onClick={() => {
                          if (add) {
                            api.post('schedule', this.state.object).then(r => {
                              window.history.back();                        
                            });
                          } else {
                            api.put('schedule', id, this.state.object).then(r => {
                              window.history.back();                        
                            });
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
