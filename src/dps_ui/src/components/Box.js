import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

import Paper from '@material-ui/core/Paper';

import BoxBody from './BoxBody';
import BoxHeader from './BoxHeader';

const useStyles = makeStyles((theme) => ({
    box: {
        marginBottom: theme.spacing(2),        
    },    
}));

export default function Box(props) {
    const classes = useStyles();
    
    return (
	<Paper className={classes.box}>
	  <BoxHeader>
            {props.header}
	  </BoxHeader>
	  <BoxBody>
	    {props.children}
	  </BoxBody>
	</Paper>
    );
}
