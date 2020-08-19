import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import DeleteIcon from '@material-ui/icons/Delete';

import EditAndDelete from './EditAndDelete';
import Row from './Row';
import TextField from './TextField';

import { list } from '../api';

/*
 * A table with an edit and delete button.
 */
export default class extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            counter: [],
        };

        this.initialized = false;
    }

    forEach(f) {
        for (const k in this.state) {
            if (!isNaN(k)) {
                f(this.state[k], +k);
            }
        }
    }

    fromList(o) {
        if (o === undefined) return null;
        let i = 0;
        for (const row of o) {
            for (const val of row) {
                this.state[i++] = val;                    
            }
            this.state.counter.push(0);            
        }
    }

    toObject(f) {
        let key = null;
        const o = {};
        for (const k in this.state) {
            if (!isNaN(k)) {
                if (key === null) {
                    key = this.state[k];
                } else {
                    if (key === '' && this.state[k] === '') {
                        key = null; // skip
                    } else {
                        o[key] = this.state[k];
                        key = null;
                    }
                }
            }
        }
        return Object.entries(o);
    }
    
    render () {
        const props = this.props;

        // Hacky
        if (!this.initialized && this.props.defaultValue !== undefined && this.props.defaultValue.length > 0) {
            this.fromList(this.props.defaultValue); // only supports defaultValue
            this.initialized = true;
        }

        return (
            <div>
        <TableContainer component={Paper}>
          <Table aria-label="simple table">
            {/* <TableHead> */}
            {/*   <TableRow> */}
            {/*     {props.header.map(data => ( */}
            {/*         <TableCell key={data}>{data}</TableCell>                 */}
            {/*     ))} */}
            {/*     <TableCell></TableCell>                         */}
            {/*   </TableRow> */}
            {/* </TableHead> */}
            <TableBody>
              {this.state.counter.map((_, i) => (
                  <TableRow key={i}>
                    {props.header.map((h, j) =>
                                      <TableCell key={(2 * i) + j}>
                                        <TextField
                                          fullWidth={true}
                                          value={this.state[(2 * i) + j]}

                                          onChange={e => {
                                              const name  = (2 * i) + j;
                                              const o = {};
                                              o[name] = e.target.value;
                                              this.setState(o);
                                              
                                              if (typeof this.props.onChange === 'function') {
                                                  this.props.onChange(this.toObject());
                                              }
                                          }}
                                          label={h} />
                                      </TableCell>                    
                                           )}
                    <TableCell align="right">
                      <Button variant="outlined" color="primary" style={{ marginRight: '10px' }}>
                        <DeleteIcon />
                      </Button>                      
                    </TableCell>                                          
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
              <Row>
                <Button variant="contained" color="primary" onClick={e => {
                    this.setState({
                        counter: this.state.counter.concat([0]),
                    });
                }}>
                  Add Constant
                </Button>

              </Row>
            </div>
    );
        
    }
}
