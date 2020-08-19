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

import EditAndDelete from './EditAndDelete';

import { list } from '../api';

/*
 * A table with an edit and delete button.
 */
export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rows: [],
        };
    }
    
    async componentDidMount() {
        list(this.props.entityUrl).then(r => r.json())
            .then(rows => {
                this.setState({ rows });
            });

    }
    
    render () {
        const props = this.props;
        return (
        <TableContainer component={Paper}>
          <Table aria-label="simple table">
            <TableHead>
              <TableRow>
                {props.header.map(data => (
                    <TableCell key={data[0]}>{data[0]}</TableCell>                
                ))}
                <TableCell></TableCell>                        
              </TableRow>
            </TableHead>
            <TableBody>
              {this.state.rows.map((row) => (
                  <TableRow key={row.id}>
                    {props.header.map(h =>
                                      <TableCell key={row[h[1]]}>{row[h[1]]}</TableCell>                    
                                           )}
                    <TableCell align="right">
                      <EditAndDelete {...props}
                                     entity={row}
                                     entityName={props.entityName}
                                     entityUrl={props.entityUrl} />
                    </TableCell>                                          
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
    );
        
    }
}
