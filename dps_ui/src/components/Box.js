import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

import Paper from '@material-ui/core/Paper';
import Fade from '@material-ui/core/Fade';

import BoxBody from './BoxBody';
import BoxHeader from './BoxHeader';

const useStyles = makeStyles((theme) => ({
    box: {
        marginBottom: theme.spacing(2),        
    },    
}));

export default function Box(props) {
  const classes = useStyles();

  let style = props.style || {};
  if (props.loading) {
    style.display = 'none';
  }

  return (
    <Paper className={classes.box}
           style={style}>
      <BoxHeader>
        {props.header}
      </BoxHeader>
      <BoxBody>
        {props.children}
      </BoxBody>
    </Paper>
  );
}
