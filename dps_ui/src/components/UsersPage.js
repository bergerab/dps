import React from 'react';

import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import Checkbox from '@material-ui/core/Checkbox';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';

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
import util from '../util';

import NotFound from './NotFound';

const makeDefaultState = () => ({
  loading: false,

  object: {
    /* The time picker uses whole dates. So we will cut off the date part and just use the time. 
      The default will just be to collect 5 minutes of data from 8:00 to 8:05 (local time). */
    username: '',
    email: '',
    password1: '',
    password2: '',
    password_was_set: false,
    is_admin: false,
  },

  errors: {
  }
});

export default class UsersPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = makeDefaultState();
  }

  async componentDidMount() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;
    if (action === 'edit') {
      this.setState({ loading: true });
      api.get('user', id).then(user => {
        this.setState({
          object: {
            username: user.username,            
            email: user.email,
            password1: '********', // A fake password (because the real password isn't sent)
            password2: '********',
            is_admin: user.is_admin,                        
          },
          loading: false,
          notFound: false,
        });
      }).catch(r => {
        if (r.status === 404) {
          this.setState({ notFound: true });
        }
      });
    }
  }

  setObject(o) {
    this.setState({ object: Object.assign({}, this.state.object, o) });
  }

  render() {
    const action = this.props.match.params.action,
          id = this.props.match.params.id;

    const add = action === 'add',
          edit = action === 'edit';

    if (add || edit) {
      if (this.state.notFound) {
        return (<NotFound/>);
      }

      return (
        <Loader
          loading={this.state.loading}
          text="Loading..."
        >
          <Box header={(add ? 'Add' : 'Edit') + " User"}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <InputLabel>Username</InputLabel>                
                <TextField
                  fullWidth={true}
                  label="Username"
                  value={this.state.object.username}
                  onChange={x => this.setObject({ username: x.target.value })}
                  error={this.state.errors.username !== undefined}
                  helperText={this.state.errors.username}                  
                />
              </Grid>

              <Grid item xs={12}>
                <InputLabel>Email</InputLabel>                
                <TextField
                  fullWidth={true}
                  label="Email"
                  value={this.state.object.email}
                  onChange={x => this.setObject({ email: x.target.value })}
                  error={this.state.errors.email !== undefined}
                  helperText={this.state.errors.email}                  
                />
              </Grid>

              <Grid item xs={12}>
                <InputLabel>Password</InputLabel>                                
                <TextField
                  fullWidth={true}                  
                  label="Password"
                  type="password"
                  onChange={e => this.setObject({ password1: e.target.value, password_was_set: true })}                  
                  value={this.state.object.password1}
                  error={this.state.errors.password1 !== undefined}
                  helperText={this.state.errors.password1}                  
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth={true}                  
                  label="Re-Enter Password"
                  type="password"
                  onChange={e => this.setObject({ password2: e.target.value, password_was_set: true, })}
                  value={this.state.object.password2}
                  error={this.state.errors.password2 !== undefined}
                  helperText={this.state.errors.password2}                  
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={this.state.object.is_admin}
                      onChange={e => {
                        this.setObject({ is_admin: e.target.checked })
                      }}
                      name="checkedB"
                      color="primary"

                    />
                  }
                  label="Is Admin"
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
                            api.post('user', this.state.object).then(r => {
                              window.history.back();
                              this.setState(makeDefaultState())                              
                            }).catch(handleError);
                          } else {
                            api.put('user', id, this.state.object).then(r => {
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
      return (<Box header={"Users"}
                                            >
                      <EntityTable
                        idName="user_id"
                        entityName="user"
                        entityDisplayName="User"
                        entityNameField={'username'}
                        orderBy={'username'}
                        columns={[
                          ['Username', x => x.username],
                          ['Email', x => x.email],                    
                          ['Is Admin', x => x.is_admin ? 'Yes' : 'No' ],                                                    
                          /* ['Last Login', x => x.last_login === null ? 'Never' : util.dateToPrettyDate(new Date(Date.parse(x.last_login)))], */
                          ['Created At', x => util.dateToPrettyDate(new Date(Date.parse(x.created_at)))],
                        ]}/>
                      <Grid container style={{ marginTop: '15px' }}>                
                        <Grid item>
                          <Link to={'/admin/user/add'} style={{ color: 'white' }}>              
                            <Button variant="contained" color="primary">
                              Add User
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
