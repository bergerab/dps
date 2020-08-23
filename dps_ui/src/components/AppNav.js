import React from 'react';
import clsx from 'clsx';
import {
  HashRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import { makeStyles, useTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Grid from '@material-ui/core/Grid';
import List from '@material-ui/core/List';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';

import FunctionsIcon from '@material-ui/icons/Functions';
import HomeIcon from '@material-ui/icons/Home';
import MemoryIcon from '@material-ui/icons/Memory';
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import InputIcon from '@material-ui/icons/Input';
import TableChartIcon from '@material-ui/icons/TableChart';

import DataConnectionEdit from './DataConnectionEdit';
import KPIEdit from './KPIEdit';
import SystemEdit from './SystemEdit';
import DataSetEdit from './DataSetEdit';
import BatchProcessPage from './BatchProcessPage';
import Home from './Home';

import EntitySelect from './EntitySelect';
import EntityMultiSelect from './EntityMultiSelect';

import EntityPage from './EntityPage';

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
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
}));

export default function MiniDrawer(props) {
  const classes = useStyles();
  const theme = useTheme();
  const [open, setOpen] = React.useState(false);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const linkStyle = { textDecoration: 'none', color: 'initial' };

  return (
    <Router>
      <div className={classes.root}>
	<CssBaseline />
	<AppBar
	  position="fixed"
	  className={clsx(classes.appBar, {
	    [classes.appBarShift]: open,
	  })}
	>
	  <Toolbar>
	    <IconButton
	      color="inherit"
	      aria-label="open drawer"
	      onClick={handleDrawerOpen}
	      edge="start"
	      className={clsx(classes.menuButton, {
		[classes.hide]: open,
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
	    [classes.drawerOpen]: open,
	    [classes.drawerClose]: !open,
	  })}
	  classes={{
	    paper: clsx({
	      [classes.drawerOpen]: open,
	      [classes.drawerClose]: !open,
	    }),
	  }}>
	  <div className={classes.toolbar}>
	    <IconButton onClick={handleDrawerClose}>
	      {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
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
	    <Link to="/data-connector" style={linkStyle}>
	      <ListItem button key="Data Connectors">
		<ListItemIcon><InputIcon/></ListItemIcon>
		<ListItemText primary="Data Connectors" />
	      </ListItem>
	    </Link>
	    <Link to="/system" style={linkStyle}>
	      <ListItem button key="Systems">
		<ListItemIcon><MemoryIcon/></ListItemIcon>
		<ListItemText primary="Systems" />
	      </ListItem>
	    </Link>
	    <Link to="/data-set" style={linkStyle}>
	      <ListItem button key="Data Sets">
		<ListItemIcon><InsertDriveFileIcon/></ListItemIcon>
		<ListItemText primary="Data Sets" />
	      </ListItem>
	    </Link>
	    <Link to="/kpi" style={linkStyle}>
	      <ListItem button key="Compute">
		<ListItemIcon><FunctionsIcon/></ListItemIcon>
		<ListItemText primary="Compute" />
	      </ListItem>
	    </Link>
	  </List>
	  <Divider />
	  <List>
	    <Link to="batch-process" style={linkStyle}>
	      <ListItem button key="Batch Process">
		<ListItemIcon><TableChartIcon /></ListItemIcon>
		<ListItemText primary="Batch Process" />
	      </ListItem>
	    </Link>
	  </List>
	</Drawer>
	<main className={classes.content}>
	  <div className={classes.toolbar} />
	  <Switch>
	    <Route path="/home">
	      <Home />
	    </Route>
	    <Route
	      path="/data-connector/:action?/:id?"
	      component={props =>
			 (<EntityPage
			    {...props}
			    fields={[['Name', 'displayName'],
				     ['URL', 'url']]}
			    entityUrl="/data-connector/"
			    entityName="Data Connector"
			    editComponent={DataConnectionEdit}
			  />)}
	    />
	    <Route
	      path="/system/:action?/:id?"
	      component={props =>
			 (<EntityPage
			    {...props}
			    fields={[['Name', 'displayName'],
				     ['Signals', 'signals'],
				     ['Constants', 'constants']]}
			    entityUrl="/system/"
			    entityName="System"
			    editComponent={SystemEdit}
			  />)}
	    />
	    <Route
	      path="/data-set/:action?/:id?"
	      component={props =>
			 (<EntityPage
			    {...props}
			    fields={[
			      ['Name', 'displayName'],
			      ['Table', 'table'],
			      ['Mappings', 'mappings'],
			    ]}
			    entityUrl="/data-set/"

			    entityName="Data Set"
			    editComponent={DataSetEdit}
			  />)}
	    />
	    <Route
	      path="/kpi/:action?/:id?"
	      component={props =>
			 (<EntityPage
			    {...props}
			    fields={[
			      ['Name', 'displayName'],
			      ['Input Signals', 'signals'],
			      ['Input Constants', 'constants'],
			    ]}
			    entityUrl="/kpi/"
			    entityName="KPI"
			    editComponent={KPIEdit}
			  />)}
	    />

	    <Route
	      path="/batch-process"
	      component={BatchProcessPage}
	    />
	  </Switch>
	</main>
      </div>
    </Router>
  );
}
