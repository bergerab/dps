import React from 'react';

import Paper from '@material-ui/core/Paper';
import { Alert, AlertTitle } from '@material-ui/lab';
import Box from './Box';

import util from '../util';

export default class Errors extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let errors = [];
    for (const key in this.props.errors) {
      if (key === 'non_field_errors')
          errors = errors.concat(`${this.props.errors[key]}`);
        else if (Array.isArray(this.props.errors[key]))
          errors = errors.concat(`${key}: ${this.props.errors[key]}`);
    }
    let intervalErrors = 'interval' in this.props.errors ? util.objectPop(this.props.errors, 'interval') : [];
    if (intervalErrors.start) {
      errors.push(intervalErrors.start);
    }
    if (intervalErrors.end) {
      errors.push(intervalErrors.end);
    }
    
    return (
      <Alert severity="error">
        <AlertTitle>Error</AlertTitle>
        <ul style={{ marginTop: 0, paddingTop: 0 }}>
          {errors.map((x, i) => {
            return (
              <li key={i}>
                {x}
              </li>
            );
          })}
        </ul>       
      </Alert>
    );
  }
}
