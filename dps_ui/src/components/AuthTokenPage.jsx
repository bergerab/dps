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

import NotFound from './NotFound';

import api from '../api';

const makeDefaultState = () => ({
  loading: false,

  object: {
    name: '',
    key: '',
  },

  errors: {
  }
});

function makeToken() {
  /* Create a secure random string. */
  /* This should really be done on the backend side, but this was way easier to program. */
  let r = new Uint8Array(512 / 8); // 2048 = number length in bits
  window.crypto.getRandomValues(r);
  r = btoa(String.fromCharCode.apply(null, r));
  return r;
}

export default class APIKeyPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = makeDefaultState();
  }

  async componentDidMount() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;
    this.setObject({ key: makeToken() });
    if (action === 'edit') {
      this.setState({ loading: true });
      api.get('api_key', id).then(token => {
        this.setState({
          object: {
            name: token.name,
            key: token.key,
          },
          loading: false,
        });
      }).catch(r => {
        console.log('Error', r);
      });
    }
  }

  setObject(o) {
    this.setState({ object: Object.assign({}, this.state.object, o) });
  }

  render() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id,
          add = action === 'add',
          edit = action === 'edit';

    if (add || edit) {
      return (
        <Loader
          loading={this.state.loading}
          text="Loading..."
        >
          <Box header={(add ? 'Add' : 'Edit') + " API Key"}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth={true}
                  name="name"
                  value={this.state.object.name}
                  required={true}
                  onChange={e => this.setObject({ name: e.target.value })}
                  label="Name"
                  helperText={this.state.errors.name}
                  error={this.state.errors.name !== undefined}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth={true}
                  InputProps={{
                    readOnly: true,
                  }}
                  name="key"
                  value={this.state.object.key}
                  label="Key"
                  helperText={this.state.errors.key}
                  error={this.state.errors.key !== undefined}
                />
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
                            api.post('api_key', this.state.object).then(r => {
                              window.history.back();
                              this.setState(makeDefaultState())
                            }).catch(handleError);
                          } else {
                            api.put('api_key', id, this.state.object).then(r => {
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

    } else if (action === undefined) {
      return (<Box header={"API Keys"}>
                <EntityTable
                  idName="api_key_id"
                  entityName="api_key"
                  entityDisplayName="API Key"
                  entityNameField="key"
                  columns={[
                    ['Name', x => (<span style={{ wordBreak: 'break-all' }}>{x.name}</span>)],
                  ]}/>
                <Grid container style={{ marginTop: '15px' }}>                
                  <Grid item>
                    <Link to={'/admin/api_key/add'} style={{ color: 'white' }}>              
                      <Button variant="contained"
                              color="primary">
                        Add API Key
                      </Button>
                    </Link>
                  </Grid>
                </Grid>
              </Box>);
    } else {
      return (<NotFound/>);
    }
  }
}
