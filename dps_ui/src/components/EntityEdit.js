import React from 'react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';

import Box from './Box';
import Row from './Row';
import { get, put, post, API_PREFIX } from '../api';

export default class EntityEdit extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
    };
  }
  
  async componentDidMount() {
    if (this.props.edit) {
      const entity = await get(this.props.entityUrl, this.props.entityId);
      if (this.props.onGETEntity !== undefined) {
        this.props.onGETEntity(entity);
      }
      this.setState({ loading: false });
    } else {
      this.setState({ loading: false });
    }
  }
  
  render () {
    const props = this.props;
    const headerText = (props.edit ? 'Edit' : 'Add') + ' ' + props.entityName;
    
    const onSubmit = e => {
      const jo = {};
      for (const el of e.target) {
        if (el.name) {
          if (el.dataset.type === 'json') {
            jo[el.name] = JSON.parse(el.value);            
          } else {
            jo[el.name] = el.value;
          }
        }
      }
      
      if (props.edit) {
        put(props.entityUrl, props.entityId, jo).then(o => {
	  window.history.back();		
        }).catch(error => {
          error.then(jo => {
            this.props.onError(jo);
          });
      });

  } else {
    post(props.entityUrl, jo).then(o => {
      window.history.back();
        }).catch(error => {
          error.then(jo => {
            this.props.onError(jo);
          });
        });
      }
      e.preventDefault();
      return false;
    };

    let form =
        (<form
           onSubmit={onSubmit}
           noValidate
           autoComplete="off"
           style={{ width: '100%'}}
         >
           {props.children}
           <Row>
             <Button
               type="submit"
               variant="contained"
               color="primary"
             >
               Save
             </Button>          
           </Row>
         </form>);

    return (
      <Grid container spacing={2}>
        <Grid item>
          <Box header={headerText}
               loading={this.state.loading}>
            <Grid container>
              {form}
            </Grid>
          </Box>
        </Grid>
      </Grid>
    );
  }
}
