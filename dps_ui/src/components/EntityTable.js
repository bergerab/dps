import React from 'react';
import Paper from '@material-ui/core/Paper';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import Skeleton from '@material-ui/lab/Skeleton';

import EditAndDelete from './EditAndDelete';

import { list } from '../api';

/*
 * A table with an edit and delete button.
 */
export default class extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      entities: [],
      loading: true,
    };
  }

  componentDidMount() {
    list(this.props.entityUrl).then(entities => {
      this.setState({
        entities,
        loading: false
      });
    });
  }

render () {
  let rowId = 0;
  const props = this.props;
  const entities = this.state.entities.map(row => {
    let cellId = 0;        
    const cells = props.header.map(h => {
      const value = typeof h[1] === 'function' ? h[1](row) : row[h[1]];
      
      return(<TableCell
                 key={'cell' + cellId++}
                >
                  {value}
                </TableCell>)
    });

    return (
      <TableRow key={rowId++}>
	{cells}
	<TableCell
          align="right"
          key={rowId}
        >
	  <EditAndDelete {...props}
                         key={rowId}
			 entity={row}
			 entityName={props.entityName}
			 entityUrl={props.entityUrl}
	  />
	</TableCell>
      </TableRow>);
  });

  const empty = (<TableRow>
                   <TableCell>
                     <i style={{whiteSpace: 'pre'}}>No data to display.</i>
                   </TableCell>
                 </TableRow>);

  let body = this.state.entities.length > 0 ? entities : empty;

    if (this.state.loading) {
      body = [1,2,3,4,5].map((v, i) => (
        <TableRow key={v}>
          {this.props.header.map((v, i) => (
            <TableCell key={i}>
              <Skeleton/>
            </TableCell>
          ))}
        </TableRow>
      ));
    }
    
    return (
      <TableContainer component={Paper}>
        <Table aria-label="simple table">
	  <TableHead>
	    <TableRow>
	      {props.header.map(data => (
	        <TableCell
                  key={data[0]}
                >
                  {data[0]}
                </TableCell>
	      ))}
	      <TableCell></TableCell>
	    </TableRow>
	  </TableHead>
	  <TableBody>
            {body}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }
}
