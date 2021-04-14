import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

const useStyles = makeStyles({
  table: {
  },
});

export default function PrettyTable(props) {
  const classes = useStyles();

  const empty = (<TableRow>
                   <TableCell>
                     <i style={{whiteSpace: 'pre'}}>No data to display.</i>
                   </TableCell>
                 </TableRow>);

  const rows = props.rows.map((row, i) => (
    <TableRow key={i}>
      {row.map((item, j) => (
        <TableCell
          key={j}
          component="th"
          scope="row"
        >
          {item}
        </TableCell>
      ))}
    </TableRow>
  ));
  
  return (
    <TableContainer component={Paper}
                    style={props.style}
                    style={{ overflow: 'visible' }}
    >
      <Table className={classes.table} aria-label="simple table" >
        <TableHead>
          <TableRow>
            {props.header.map((header, i) => (
              <TableCell key={i}>{header}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {props.rows.length > 0 ? rows : empty}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
