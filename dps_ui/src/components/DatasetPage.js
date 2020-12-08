import React from 'react';

import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import SignalTable from './SignalTable';
import BarChart from './BarChart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';

import DatasetTable from './DatasetTable';

import api from '../api';

export default class DatasetPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,

      name: '',
      nameError: null,
    };
  }

  render() {
    const add = this.props.location.pathname.startsWith('/admin/dataset/add');
    if (add) {
      return (
        <Box header={"Add Dataset"} >
          <Grid container>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth={true}
                name="name"
                value={this.state.name}
                required={true}
                onChange={e => this.setState({ name: e.target.value })}
                label="Name"
                helperText={this.state.nameError}
                error={this.state.nameError !== null}
              />
            </Grid>
            <Grid item xs={12}>
              <Button variant="contained"
                      color="primary"
                      style={{ marginTop: '10px' }}
                      onClick={() => {
                        if (this.state.name === '') {
                          this.setState({ nameError: 'You must choose a non-empty name for the dataset.' });
                          return;
                        }
                        api.add_dataset(this.state.name);
                        window.history.back();                        
                      }}>
                Add
              </Button>
            </Grid>
          </Grid>
        </Box>
      );
    }
    
    let name = this.props.match.params.name;
    if (name) {
      name = decodeURIComponent(name);
      return (
        <Box header={"Datasets - " + name}
             loading={this.state.loading}>
          <SignalTable
            dataset={name} />
        </Box>);
    } else {
      return (
        <Box header={"Datasets"}
             loading={this.state.loading}>
          <DatasetTable />
          <Grid container style={{ marginTop: '15px' }}>
            <Grid item xs={12}>
              <Link to={'/admin/dataset/add'} style={{ color: 'white' }}>              
                <Button variant="contained" color="primary">
                  Add Dataset
                </Button>
              </Link>
            </Grid>
          </Grid>
        </Box>);
    }
  }
}
