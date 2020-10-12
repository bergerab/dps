import React from 'react';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import EntityTable from './EntityTable';

export default class EntityPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
    };
  }
  
  render () {
    const props = this.props;
    
    // Router parameters
    const { match: { params } } = props;

    const add = params.action === 'add',
          edit = params.action === 'edit',
          view = !add && !edit;

    if (view) {
      return (
        <Box header={props.entityName + 's'}
             loading={this.state.loading}>
          <EntityTable
            entityUrl={props.entityUrl}
            entityName={props.entityName}
            header={props.fields}
            onLoad={() => {
              this.setState({ loading: false });
            }}
          />            
          <Row key>
            <Link to={props.entityUrl + '/add'} style={{ color: 'white' }}>              
              <Button variant="contained" color="primary">
                Add {props.entityName}
              </Button>
            </Link>          
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
