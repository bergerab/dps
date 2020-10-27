import React from 'react';
import clsx from 'clsx';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import { withStyles } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Chip from '@material-ui/core/Chip';
import List from '@material-ui/core/List';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import WorkIcon from '@material-ui/icons/Work';
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
import Home from './Home';

import EntityPage from './EntityPage';

import { list } from '../api';
import util from '../util';

const drawerWidth = 240;

const indexToIcon = i => {
  return [
    <Filter1Icon/>, <Filter2Icon/>, <Filter3Icon/>,
    <Filter4Icon/>, <Filter5Icon/>, <Filter6Icon/>,
    <Filter7Icon/>, <Filter8Icon/>, <Filter9Icon/>,
  ][i % 9]
};

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
    };
  }
  
  async componentDidMount() {
    list('system').then(systems => {
      this.setState({ systems });
    });
  }

  render() {
    const { classes } = this.props;
    const handleDrawerOpen = () => {
      this.setState({ open: true });
    };

    const handleDrawerClose = () => {
      this.setState({ open: false });
    };

    const linkStyle = { textDecoration: 'none', color: 'initial' };

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
              <Typography variant="h6" noWrap>
                Data Processing System
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            className={clsx(classes.drawer, {
	      [classes.drawerOpen]: this.state.open,
	      [classes.drawerClose]: !this.state.open,
            })}
            classes={{
	      paper: clsx({
	        [classes.drawerOpen]: this.state.open,
	        [classes.drawerClose]: !this.state.open,
	      }),
            }}>
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
            <Divider />
            <List>
              <Link to="/system" style={linkStyle}>
                <ListItem button key="Systems">
                  <ListItemIcon><MemoryIcon/></ListItemIcon>
                  <ListItemText primary="Systems" />
                </ListItem>
              </Link>
              <Link to="/bp" style={linkStyle}>
                <ListItem button>
                  <ListItemIcon><TableChartIcon/></ListItemIcon>
                  <ListItemText primary="Batch Processes" />
                </ListItem>
              </Link>
              <Link to="/job" style={linkStyle}>
                <ListItem button>
                  <ListItemIcon><WorkIcon/></ListItemIcon>
                  <ListItemText primary="Jobs" />
                </ListItem>
              </Link>
            </List>
            <Divider />
            <List>
              {this.state.systems.map((system, i) => (
                <Link
                  key={system.system_id}
                  to={"/batch-process/" + system.system_id}
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
              <Route path="/home">
                <Home />
              </Route>
              <Route
                path="/system/:action?/:id?"
                render={props =>
		        (<EntityPage
                           key={'System'}
		           {...props}
		           fields={[['Name', 'name'],
			            ['KPIs', system => {
                                      return (<span>{system.kpis.filter(kpi => !kpi.hidden)
                                                     .map(kpi => <Chip
                                                                      key={kpi.name}
                                                                      label={kpi.name}
                                                                      style={{ margin: '5px' }}/>)}
                                                    </span>)
                                    }],
			            ['Parameters', system => {
                                      return (<span>{system.parameters.filter(param => !param.hidden)
                                                     .map(parameter => <Chip
                                                                            key={parameter.name}
                                                                            label={parameter.name}
                                                                            style={{ margin: '5px' }}/>)}
                                                             </span>)                                       
                                    }]]}
		              entityUrl="system"
		              entityName="System"
		              editComponent={SystemEdit}
      />)}
	      />
              <Route
                path="/bp"
                render={props =>
		        (<EntityPage
                         key={'Batch Process'}
                         readOnly={true}
		           {...props}
		           fields={[
                             ['Created At', bp => {
                               return util.dateToPrettyDate(new Date(bp.created_at));
                             }],
			     ['System', bp => {
                               return bp.system.name;
                             }],
                             ['KPIs', bp => {
                               return (<span>{bp.kpis
                                              .map(kpi => <Chip
                                                            key={kpi}
                                                            label={kpi}
                                                            style={{ margin: '5px' }}/>)}
                                       </span>)
                             }],
                             ['Start Time', bp => {
                               return util.dateToPrettyDate(util.stringToUTCDate(bp.interval.start));
                             }],
                             ['End Time', bp => {
                               return util.dateToPrettyDate(util.stringToUTCDate(bp.interval.end));
                             }],
                           ]}
		           entityUrl="batch_process"
		           entityName="Batch Process"
                         />)}
	      />

              <Route
                path="/job"
                render={props =>
		        (<EntityPage
                           key={'Job'}
                           readOnly={true}
		           {...props}
		           fields={[
                             ['Created At', j => {
                               return util.dateToPrettyDate(new Date(j.created_at));
                             }],
			     ['System', j => {
                               return j.batch_process.system.name;
                             }],
                             ['KPIs', j => {
                               return (<span>{j.batch_process.kpis
                                              .map(kpi => <Chip
                                                            key={kpi}
                                                            label={kpi}
                                                            style={{ margin: '5px' }}/>)}
                                       </span>)
                             }],
                             ['Start Time', j => {
                               return util.dateToPrettyDate(util.stringToUTCDate(j.batch_process.interval.start));
                             }],
                             ['End Time', j => {
                               return util.dateToPrettyDate(util.stringToUTCDate(j.batch_process.interval.end));
                             }],
                           ]}
		           entityUrl="job"
		           entityName="Job"
                         />)}
	      />
              
              {this.state.systems.map(system => (
                <Route
                  key={system.system_id}
                  path="/batch-process"

                /* Setting the key to Date.now forces a component remount when the same link is clicked more than once. */
                  
                  render={(props) => (<BatchProcessPage key={Date.now()} {...props} />)} />
              ))}
            </Switch>
          </main>
        </div>
      </Router>
    );
  }
                            }
export default withStyles(styles)(MiniDrawer);
