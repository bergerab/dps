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
import EntityTable from './EntityTable';

export default function DataSets(props) {
    const [dataSource, setDataSource] = useState(0);

    function handleDataSource(e) {
        setDataSource(e.target.value);
    }

    return (
        <Box header="Data Sets">
	  <EntityTable
            entityUrl="/data-sets/"
            entityName="Data Set"
            header={['One', 'Two', 'Three']}
            rows={[
                [0, 'a', 'b', 'c']
            ]}
          />
	<Row>
          <Button variant="contained" color="primary">
            Add Data Set
          </Button>
	</Row>
        </Box>
    );
}


