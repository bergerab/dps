import React from 'react';
import Paper from '@material-ui/core/Paper';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import CircularProgress from '@material-ui/core/CircularProgress';

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

  async componentDidMount() {
    console.log('did mount');
    list(this.props.entityUrl).then(entities => {
      this.setState({ entities, loading: false });
    });
  }

  render () {
    const props = this.props;
    const entities = this.state.entities.map(row => {
      const cells = props.header.map(h => {
        const value = typeof h[1] === 'function' ? h[1](row) : row[h[1]];        
	return(<TableCell
                       key={value}
             >
               {value}
             </TableCell>)
      });
      
      return (
        <TableRow key={row.id}>
	  {cells}
	  <TableCell align="right">
	    <EditAndDelete {...props}
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
      body = (
        <TableRow>
          <TableCell style={{ height: '200px' }}>
            <CircularProgress />
          </TableCell>

        </TableRow>
      );
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
