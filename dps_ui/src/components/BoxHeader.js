import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    boxHeader: {
      padding: theme.spacing(2),
      paddingBottom: 0,
      margin: 0,
    },    
}));

export default function BoxHeader(props) {
    const classes = useStyles();
    
    return (
	<h1 className={classes.boxHeader}>
          {props.children}
	</h1>
    );
}
