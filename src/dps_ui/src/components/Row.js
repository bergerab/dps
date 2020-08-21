import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    row: {
        marginTop: theme.spacing(2),        
    },
}));

export default function Row(props) {
    const classes = useStyles();
    
    return (
	    <div className={classes.row}>
	    {props.children}
	</div>
    );
}
