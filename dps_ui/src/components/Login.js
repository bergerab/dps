import React from "react";
import { withStyles } from '@material-ui/core/styles';
import clsx from 'clsx';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import { Redirect } from 'react-router'

import {
  Button,
  TextField,
  Grid,
  Paper,
  AppBar,
  Typography,
  Toolbar,
  Link,
} from "@material-ui/core";
import CssBaseline from '@material-ui/core/CssBaseline';

import { login } from '../api';
import api from '../api';

const drawerWidth = 240;
const styles = theme => ({
  root: {
    display: 'flex',
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  hide: {
    display: 'none',
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
  },
  drawerOpen: {
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerClose: {
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: 'hidden',
    width: theme.spacing(7) + 1,
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9) + 1,
    },
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
});

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      error: false,
      errorMessage: '',
      success: false,      
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ username: event.state.username, password: event.state.password });
  }

  handleSubmit(event) {
    event.preventDefault();
    if (this.state.username == 'admin@littech.in' && this.state.password == 'secret') {
      this.props.history.push("/home");
    } else {
      alert('Invalid credentials');
    }
  }

  render() {
    const { classes } = this.props;
    if (this.state.success)
      return (<Redirect to="/home"/>);
    return (
      <div className={classes.root}>
        <CssBaseline />
        <AppBar
          position="fixed"
          className={clsx(classes.appBar, {
	    [classes.appBarShift]: this.state.open,
          })}
        >
          <Toolbar>
            <Typography variant="h4" noWrap style={{
              fontWeight: 'bold',
              fontStyle: 'italic',
            }} >
              DPS
            </Typography>
          </Toolbar>
        </AppBar>
      <Grid container spacing={0} justify="center" direction="row">
        <Grid item>
          <Grid
            container
            direction="column"
            justify="center"
            spacing={2}
            className="login-form"
          >
            <Paper
              variant="elevation"
              elevation={2}
              className="login-background"
            >
              <form onSubmit={e => {
                e.preventDefault();
                login(this.state.username, this.state.password).then(r => {
                  if (r.status === 403) {
                    this.setState({ error: true,
                                    errorMessage: 'Invalid credentials' });
                  } else {
                    r.json().then(x => {
                      api.setToken(x.token);
                      api.setTokenExpires(x.expires_at);                      
                      this.setState({ error: false, success: true });
                    });
                  }
                });
              }}>
                
                <Grid item>
                  <Typography component="h1" variant="h5">
                    Login
                  </Typography>
                </Grid>
                <Grid item>

                  <Grid container direction="column" spacing={2}>
                    <Grid item>
                      <TextField
                        type="username"
                        placeholder="Username"
                        fullWidth
                        name="username"
                        error={this.state.error}
                        helperText={this.state.error ? this.state.errorMessage : ''}                                                
                        variant="outlined"
                        value={this.state.username}
                        onChange={(event) =>
                                  this.setState({
                                    [event.target.name]: event.target.value,
                                  })
                                 }
                        required
                        autoFocus
                      />
                    </Grid>
                    <Grid item>
                      <TextField
                        type="password"
                        placeholder="Password"
                        fullWidth
                        name="password"
                        variant="outlined"
                        value={this.state.password}
                        error={this.state.error}
                        helperText={this.state.error ? this.state.errorMessage : ''}                                                                        
                        onChange={(event) =>
                                  this.setState({
                                    [event.target.name]: event.target.value,
                                  })
                                 }
                        required
                      />
                    </Grid>
                    <Grid item>
                      <Button
                        variant="contained"
                        color="primary"
                        type="submit"
                        className="button-block"
                      >
                        Submit
                      </Button>
                    </Grid>
                  </Grid>
                </Grid>
            </form>                          
          </Paper>
        </Grid>
      </Grid>
      </Grid>

      </div>
    );
  }
}

export default withStyles(styles)(Login);
