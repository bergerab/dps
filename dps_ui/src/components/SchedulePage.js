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

import api from '../api';

export default class SchedulePage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      result: null,
      loading: true,
    };
  }

  async componentDidMount() {
    const id = this.props.match.params.id;
    api.get('get_batch_process_result', id).then(result => {
      this.setState({
        result,
        loading: false,
      });
    });
  }

  render() {
    return (<div/>);
  }
}
