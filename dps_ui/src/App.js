import 'fontsource-roboto';
import './App.css';
import "react-datetime/css/react-datetime.css";

import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";


import AppNav from './components/AppNav';
import Login from './components/Login';

import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import MomentUtils from '@date-io/moment';

export default function App() {
  return (
      <MuiPickersUtilsProvider utils={MomentUtils}>
      <Router>
      <Switch>
      <Route path="/login" component={Login} />
      <Route path="/" component={AppNav}/>
      </Switch>
      </Router>
      </MuiPickersUtilsProvider>    
  );
}
