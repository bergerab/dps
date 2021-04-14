import React from 'react';
import clsx from 'clsx';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect
} from "react-router-dom";

import { withStyles } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Chip from '@material-ui/core/Chip';
import List from '@material-ui/core/List';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import MenuIcon from '@material-ui/icons/Menu';
import WorkIcon from '@material-ui/icons/Work';
import PeopleIcon from '@material-ui/icons/People';
import VpnKeyIcon from '@material-ui/icons/VpnKey';
import ScheduleIcon from '@material-ui/icons/Schedule';
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';

import Filter1Icon from '@material-ui/icons/Filter1';
import Filter2Icon from '@material-ui/icons/Filter2';
import Filter3Icon from '@material-ui/icons/Filter3';
import Filter4Icon from '@material-ui/icons/Filter4';
import Filter5Icon from '@material-ui/icons/Filter5';
import Filter6Icon from '@material-ui/icons/Filter6';
import Filter7Icon from '@material-ui/icons/Filter7';
import Filter8Icon from '@material-ui/icons/Filter8';
import Filter9Icon from '@material-ui/icons/Filter9';

import HomeIcon from '@material-ui/icons/Home';
import MemoryIcon from '@material-ui/icons/Memory';
import TableChartIcon from '@material-ui/icons/TableChart';

import SystemEdit from './SystemEdit';
import BatchProcessPage from './BatchProcessPage';
import DatasetPage from './DatasetPage';
import SchedulePage from './SchedulePage';
import UsersPage from './UsersPage';
import AuthTokenPage from './AuthTokenPage';
import Home from './Home';
import NotFound from './NotFound';
import Login from './Login';

import EntityPage from './EntityPage';
import EndUserSystemPage from './EndUserSystemPage';
import BatchProcessViewPage from './BatchProcessViewPage';

import { list } from '../api';
import api from '../api';
import util from '../util';

const indexToIcon = i => {
  return [
    <Filter1Icon/>, <Filter2Icon/>, <Filter3Icon/>,
    <Filter4Icon/>, <Filter5Icon/>, <Filter6Icon/>,
    <Filter7Icon/>, <Filter8Icon/>, <Filter9Icon/>,
  ][i % 9]
};

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

class MiniDrawer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      systems: [],
      loadingSystems: true,
      anchorEl: null,
    };
  }
  
  async componentDidMount() {
    list('system').then(systems => {
      this.setState({ systems, loadingSystems: false });
    });
  }

  render() {
    if (!api.isLoggedIn()) {
      return (<Redirect to="/login"/>);
    }
    
    const { classes } = this.props;
    const handleDrawerOpen = () => {
      this.setState({ open: true });
    };

    const handleDrawerClose = () => {
      this.setState({ open: false });
    };

    const linkStyle = { textDecoration: 'none', color: 'initial' };

    const handleMenuClick = (event) => {
      this.setState({ anchorEl: event.currentTarget });
    };

    const handleMenuClose = () => {
      this.setState({ anchorEl: null });      
    };
 
    // redirect direct access of URL for non-admin users 
    const userRedirect = component => !api.getIsAdmin() ? (<Redirect to="/home"/>) : component; 

    return (
      <Router>
        <div className={classes.root}>
          <CssBaseline />
          <AppBar
            position="fixed"
            className={clsx(classes.appBar, {
	      [classes.appBarShift]: this.state.open,
            })}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerOpen}
                edge="start"
                className={clsx(classes.menuButton, {
	          [classes.hide]: this.state.open,
                })}>
                <MenuIcon />
              </IconButton>
              <Typography variant="h4" noWrap style={{
                fontWeight: 'bold',
                fontStyle: 'italic',
              }} >
                DPS
              </Typography>
              <div style={{ marginLeft: 'auto' }}>
                <IconButton aria-label="profile" style={{ color: 'white' }} onClick={handleMenuClick}>
                  <AccountCircleIcon fontSize={'large'} />
                </IconButton>
                <Menu
                  id="simple-menu"
                  anchorEl={this.state.anchorEl}
                  keepMounted
                  open={Boolean(this.state.anchorEl)}
                  getContentAnchorEl={null}
                  anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
                  transformOrigin={{vertical: 'top', horizontal: 'center'}}                  
                  onClose={handleMenuClose}
                >
                  <MenuItem disabled={true}>Logged in as {api.getUsername()} ({api.getIsAdmin() ? 'Admin': 'End-User'})</MenuItem>
                  <MenuItem onClick={() => { api.removeToken(); window.location = '/login'; }}>Logout</MenuItem>
                </Menu>
              </div>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            className={clsx(classes.drawer, {
	                  [classes.drawerOpen]: this.state.open,
	                  [classes.drawerClose]: !this.state.open,
                      })}
            classes={{paper: clsx({
	                  [classes.drawerOpen]: this.state.open,
	                  [classes.drawerClose]: !this.state.open,
	            }), }}
	  >
          <div className={classes.toolbar}>
             <IconButton onClick={handleDrawerClose}>
                 {/* {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />} */}
                 {<ChevronLeftIcon/>}
             </IconButton>
          </div>
          <Divider />
             <List>
               <Link to="/home" style={linkStyle}>
                 <ListItem button key="Home">
                   <ListItemIcon><HomeIcon/></ListItemIcon>
                   <ListItemText primary="Home" />
                 </ListItem>
               </Link>
             </List>
             { !api.getIsAdmin() ? null :
               (<span>
                  <Divider />
                    <List>
                      <Link to="/admin/system" style={linkStyle}>
                        <ListItem button>
                          <ListItemIcon><MemoryIcon/></ListItemIcon>
                          <ListItemText primary="Systems" />
                        </ListItem>
                      </Link>
                      <Link to="/admin/dataset" style={linkStyle}>
                        <ListItem button>
                          <ListItemIcon><InsertDriveFileIcon/></ListItemIcon>
                          <ListItemText primary="Datasets" />
                        </ListItem>
                      </Link>
                      <Link to="/admin/schedule" style={linkStyle}>
                        <ListItem button>
                          <ListItemIcon><ScheduleIcon/></ListItemIcon>
                          <ListItemText primary="Schedules" />
                        </ListItem>
                      </Link>
                      <Link to="/admin/user" style={linkStyle}>
                        <ListItem button>
                          <ListItemIcon><PeopleIcon/></ListItemIcon>
                          <ListItemText primary="Users" />
                        </ListItem>
                      </Link>
                      <Link to="/admin/api_key" style={linkStyle}>
                        <ListItem button>
                          <ListItemIcon><VpnKeyIcon/></ListItemIcon>
                          <ListItemText primary="API Key" />
                        </ListItem>
                      </Link>
                    </List>
                  </span>
	       )
             }
                  <Divider />
                     <List>
                        {this.state.systems.map((system, i) => (
                          <Link
                            key={system.system_id}
                            to={"/system/" + system.system_id}
                            style={linkStyle}>
                            <ListItem button key={system.name}>
                              <ListItemIcon>{indexToIcon(i)}</ListItemIcon>
                              <ListItemText primary={system.name} />
                            </ListItem>
                          </Link>
                        ))}
                     </List>
          </Drawer>
          <main className={classes.content}>
            <div className={classes.toolbar} />
            <Switch>
              <Route exact path="/home" > <Home/> </Route>
              <Route exact path="/" > <Home/> </Route>
              <Route exact path="/batch-process/:id" 		component={BatchProcessViewPage}/>
              <Route exact path="/admin/dataset" 		component={props => userRedirect( (<DatasetPage {...props}/>) )}/>
              <Route exact path="/admin/view-dataset/:name" 	component={props => userRedirect( (<DatasetPage {...props}/>) )}/>
              <Route exact path="/admin/dataset/add" 		component={props => userRedirect( (<DatasetPage add={true} {...props}/>) )}/> 
              <Route exact path="/admin/schedule/:action?/:id?"
                            component={props => {
                              const action = props.match.params.action;
                              return userRedirect( (<SchedulePage key={action} {...props}/>) );
                            }}   
	      />
              <Route exact path="/admin/user/:action?/:id?"
                            component={props => {
                              const action = props.match.params.action;                  
		              return userRedirect( (<UsersPage key={action} {...props} />) );
                            }}
	      />
              <Route exact path="/admin/api_key/:action?/:id?"                
                            component={props => {
                              const action = props.match.params.action;
                              return userRedirect( (<AuthTokenPage key={action} {...props}/>) );
                  }}
	      />
              <Route exact path="/admin/system/:action?/:id?" 
	                    render={props => userRedirect( (
			     <EntityPage key={'System'}
		                         {...props}
		                         fields={[['Name', x => x.name],
			                          ['KPIs', system => {
                                                    return (<span>{
							    system.kpis.filter(kpi => !kpi.hidden).map(kpi => 
								    <Chip key={kpi.name} label={kpi.name} style={{ margin: '5px' }}/>
							    )}</span>)
                                       
						  }],
			               
						  ['Parameters', system => { 
						    return (<span>{
							    system.parameters.filter(param => !param.hidden).map(parameter => 
								    <Chip key={parameter.name} label={parameter.name} style={{ margin: '5px' }}/>
							    )}</span>)                                       
                                       
						  }]
					 ]}
		              		 entityUrl="system"
		              		 entityName="System"
		             		 editComponent={SystemEdit}
                   	     />
			    ) )}
	      />
              /* Add batch process pages. */
              {this.state.systems.map(system => (
                <Route
                  exact
                  key={system.system_id}
                  path={"/system/" + system.system_id + "/batch-process"}
                /* Setting the key to Date.now forces a component remount when the same link is clicked more than once. */
                  render={(props) => (<BatchProcessPage key={Date.now()} system_id={system.system_id} {...props} />)} />
              ))}

              /* Add system pages. */
              {this.state.systems.map(system => (
                <Route
                  exact
                  key={system.system_id}
                  path={"/system/" + system.system_id}
                /* Setting the key to Date.now forces a component remount when the same link is clicked more than once. */
                  render={(props) => (<EndUserSystemPage
                                        system_id={system.system_id}
                                        system_name={system.name}                                        
                                        key={Date.now()} {...props} />)} />
              ))}
              {this.state.loadingSystems ? null : (<Route component={NotFound}/>)}
            </Switch>
          </main>
        </div>
      </Router>
    );
  }
}


export default withStyles(styles)(MiniDrawer);
