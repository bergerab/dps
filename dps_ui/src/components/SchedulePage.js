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
import ScheduleTable from './ScheduleTable';
import DatasetSelect from './DatasetSelect';

import api from '../api';

export default class SchedulePage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,

      start: '8:00 PM',
      startErrors: null,
      end: new Date(),
      endErrors: null,
      type: 0,
      day: 1,
      dayError: null,
    };
  }

  render() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;

    const dayInput = (<Grid item xs={12}>
                        <TextField
                          name="day"
                          value={this.state.day}
                          type={'number'}
                          required={true}
                          onChange={e => this.setState({ day: e.target.value })}
                          label="Day of the Month"
                          helperText={this.state.dayError}
                          error={this.state.dayError !== null}
                        />
                      </Grid>);



    if (action === 'add') {
      return (<Box header={"Add Schedule"}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <InputLabel>Dataset *</InputLabel>                                
                    <DatasetSelect
                      limit={20}/>
                  </Grid>
                  <Grid item xs={12}>
                    <InputLabel>Interval *</InputLabel>                                
                    <Select
                      value={this.state.type}
                      onChange={e => {
                        this.setState({ type: e.target.value });
                      }}>
                      <MenuItem value={0}>Daily</MenuItem>
                      <MenuItem value={1}>Monthly</MenuItem>
                    </Select>
                  </Grid>

                  {this.state.type === 1 ? dayInput : null}
                  
                  <Grid item xs={12}>
                    <InputLabel>Time Range</InputLabel>            
                    <TimePicker value={this.state.start}
                                onChange={date => this.setState({ start: date })}
                                label="Start Time"
                                error={this.state.startErrors !== null}
                                helperText={this.state.startErrors}                                           
                                style={{marginRight: '20px'}}
                                required />
                    <TimePicker value={this.state.end}
                                onChange={date => this.setState({ end: date })}
                                error={this.state.endErrors !== null}
                                helperText={this.state.endErrors}
                                label="End Time"
                                required />
                  </Grid>

                    <Grid item>
                    <Button variant="contained" color="primary">
                      Save
                    </Button>
                  </Grid>
                </Grid>
              </Box>);

    } else {
      return (<Box header={"Schedules"}
              >
            <ScheduleTable />
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
