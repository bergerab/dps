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
    };
  }

  render() {
    const name = this.props.match.params.name;
    if (name) {
      return (
        <Box header={"Ding"}
             loading={this.state.loading}>
          <SignalTable
            dataset={name} />
        </Box>);
    } else {
      return (
        <Box header={"Datasets"}
             loading={this.state.loading}>
          <DatasetTable />
        </Box>);
    }
  }
}
