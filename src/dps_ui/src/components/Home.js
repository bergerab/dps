import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import Button from '@material-ui/core/Button';

import Box from './Box';

import ActionsTable from './ActionsTable';
import ActionsStepper from './ActionsStepper';

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
      width: '25ch',
    },
    paper: {
        padding: theme.spacing(2),        
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },    
  },
}));

export default function Home(props) {
    const classes = useStyles();

    const [dataSource, setDataSource] = useState(0);

    function handleDataSource(e) {
        setDataSource(e.target.value);
    }

    return (
        <div>
          <Box header="System Setup">            
            <ActionsStepper />              
          </Box>                

          <Box header="System Log">            
	    <ActionsTable />                        
          </Box>                
        </div>
    );
}
