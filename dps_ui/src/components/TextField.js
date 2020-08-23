import React from 'react';
import TextField from '@material-ui/core/TextField';

export default function (props) {
    return (<TextField
              {...props}
	      floatingLabelFixed={true}
              InputLabelProps={{
                  shrink: true,
              }}	
              fullWidth={true}
              />);
}
