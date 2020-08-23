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

import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import EditAndDelete from './EditAndDelete';
import KPIEdit from './KPIEdit';

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

export default function Systems(props) {
    const classes = useStyles();

    const [dataSource, setDataSource] = useState(0);

    function handleDataSource(e) {
        setDataSource(e.target.value);
    }

    // Router parameters
    const { match: { params } } = props;

    const add = params.action === 'add',
          edit = params.action === 'edit',
          view = !add && !edit;

    if (view) {

    return (
        <Box header="Systems">
	  <SystemsTable/>
          
          <Row>
            <Button variant="contained" color="primary">
              <Link to="/systems/add" style={{ color: 'white' }}>
                Add System
              </Link>
            </Button>          
          </Row>
        </Box>
    );
        
    } else {

        return (
            <KPIEdit edit={edit} />
        );
    }
}

function SystemsTable() {
    const classes = useStyles();

    const rows = [
        ['Efficiency', 'Va Vb Vc', 'None', 0],
    ];

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Display Name</TableCell>
            <TableCell>Input Signals</TableCell>
            <TableCell>Input Constants</TableCell>
            <TableCell></TableCell>                        
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row[0]}>
              <TableCell component="th" scope="row">
                {row[0]}
              </TableCell>
              <TableCell>{row[1]}</TableCell>
              <TableCell>{row[2]}</TableCell>
              <TableCell align="right">
                <EditAndDelete entityId={row[3]} entityUrl="/systems/"entityName="System"/>
              </TableCell>                                          
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
