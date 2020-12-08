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

export default class AuthTokenPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };
  }

  render() {
    return (<Box header={"Auth Tokens"}>
              <EntityTable
                idName="auth_token_id"
                entityName="auth_token"
                entityDisplayName="Auth Token"
                entityNameField="token"
                editDisabled={true}
                columns={[
                  ['Token', x => (<span style={{ wordBreak: 'break-all' }}>{x.token}</span>)],
                ]}/>
              <Grid container style={{ marginTop: '15px' }}>                
                <Grid item>
                  <Button variant="contained"
                          color="primary"
                          onClick={() => {
                            /* This should really be done on the backend side, but this was way easier to program. */
                            let r = new Uint8Array(512 / 8); // 2048 = number length in bits
                            window.crypto.getRandomValues(r);
                            r = btoa(String.fromCharCode.apply(null, r));
                            api.post('auth_token', {
                              token: r,
                            });
                          }
                                  }>
                    Create Auth Token
                  </Button>
                </Grid>
              </Grid>
              </Box>);
  }
}
