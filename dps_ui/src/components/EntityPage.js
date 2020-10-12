import React from 'react';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import EntityTable from './EntityTable';

// import { API_PREFIX } from '../api';

export default class EntityPage extends React.Component {
  render () {
    const props = this.props;
    
    // const deleteAll = () => {
    //   fetch(API_PREFIX + props.entityUrl, {
    //     method: 'DELETE',
    //     headers: {
    //       'Content-Type': 'application/json'
    //     },
    //   }).then(r => {
    //     // TODO: how to make EntityTable refresh contents after?
    //     window.location.reload(); // goes against everything react stands for            
    //   });
    // };
    
    // Router parameters
    const { match: { params } } = props;

    const add = params.action === 'add',
          edit = params.action === 'edit',
          view = !add && !edit;

    if (view) {
	return (
          <Box header={props.entityName + 's'}>
            <EntityTable
              entityUrl={props.entityUrl}
              entityName={props.entityName}
              header={props.fields}
            />            
            <Row key>
              <Link to={props.entityUrl + '/add'} style={{ color: 'white' }}>              
                <Button variant="contained" color="primary">
                  Add {props.entityName}
                </Button>
              </Link>          

              {/* <Button variant="contained" */}
              {/*         color="primary" */}
              {/*         onClick={deleteAll} */}
              {/*         style={{ marginLeft: '20px' }}> */}
              {/*   Delete All {props.entityName}s */}
              {/* </Button>           */}
            </Row>
          </Box>
        );
    } else {
      return (
        <props.editComponent
          edit={edit}
          entityUrl={props.entityUrl}
          entityName={props.entityName}
          entityId={params.id}
        />
      );
    }
  }
}
