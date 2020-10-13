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
    const nonFieldErrors = 'non_field_errors' in this.props.errors ? util.objectPop(this.props.errors, 'non_field_errors') : [];
    
    return (
      <Alert severity="error">
        <AlertTitle>Error</AlertTitle>
        <ul style={{ marginTop: 0, paddingTop: 0 }}>
          {nonFieldErrors.map((x, i) => {
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
