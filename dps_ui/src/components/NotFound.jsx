import React from 'react';

import Box from './Box';

export default class NotFound extends React.Component {
  render() {
    return (<Box header="Error">
               Page not found.
             </Box>);
  }
}
