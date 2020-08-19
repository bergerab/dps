import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';

import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';

import Button from '@material-ui/core/Button';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import ConfirmationDialog from './ConfirmationDialog';

export default function EditAndDelete(props) {
    //const classes = useStyles();

    return (
        <div style={{ display: 'inline-flex' }}>
          <Link to={props.entityUrl + 'edit/' + props.entity.id}>          
            <Button variant="outlined" color="primary" style={{ marginRight: '10px' }}>
              <EditIcon/>
            </Button>
          </Link>        
          <ConfirmationDialog {...props}
            header={`Delete "${props.entity.displayName}" ${props.entityName}?`}>
            Are you sure you want to delete this {props.entityName}? This action is irreversible.
          </ConfirmationDialog>
        </div>
  );
}

