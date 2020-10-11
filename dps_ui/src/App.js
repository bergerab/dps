import 'fontsource-roboto';
import './App.css';

import React from "react";

import AppNav from './components/AppNav';

import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import MomentUtils from '@date-io/moment';

export default function App() {
  return (
      <MuiPickersUtilsProvider utils={MomentUtils}>
      <AppNav/>
      </MuiPickersUtilsProvider>    
  );
}
