import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Link } from "react-router-dom";
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Input from '@material-ui/core/Input';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Breadcrumbs from '@material-ui/core/Breadcrumbs';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';


import Box from './Box';
import Row from './Row';
import { get, API_PREFIX } from '../api';

export default class EntityEdit extends React.Component {
    constructor(props) {
        super(props);
    }
    
    async componentDidMount() {
        if (this.props.edit) {
            const entity = await get(this.props.entityUrl, this.props.entityId).then(r => r.json());
            if (this.props.onGETEntity !== undefined) {
                this.props.onGETEntity(entity);
            }
        }
    }

    
    render () {
        const props = this.props;
        
    const headerText = (props.edit ? 'Edit' : 'Add') + ' ' + props.entityName;
    
        const onSubmit = e => {
            const jo = {};
            for (const el of e.target) {
                console.log('el', el);
                if (el.name) {
                    jo[el.name] = el.value;
                }
            }
            console.log(jo);
            
        if (props.edit) {
            fetch(API_PREFIX + props.entityUrl + props.entityId, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jo),
            }).then(r => {
                console.log(r);
		window.history.back();		
            });
            
        } else {

            fetch(API_PREFIX + props.entityUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jo),
            }).then(r => {
                console.log(r);
		window.history.back();
            });
            
        }
        e.preventDefault();
        return false;
    };

        let form = (<form onSubmit={onSubmit} noValidate autoComplete="off" style={{ width: '100%'}}>
                      {props.children}
                      <Row>
                  <Button type="submit" variant="contained" color="primary">
                    Save
                  </Button>          

                      </Row>
                </form>);


    return (
        <Box header={headerText}>
          <Grid container>
            {form}
          </Grid>
        </Box>
    );
        
    }
}
