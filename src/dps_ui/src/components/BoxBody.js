import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    boxBody: {
        padding: theme.spacing(2),        
    },    
}));

export default function BoxHeader(props) {
    const classes = useStyles();
    
    return (
	<div className={classes.boxBody}>
          {props.children}
	</div>
    );
}
