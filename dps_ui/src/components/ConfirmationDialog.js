import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

import DeleteIcon from '@material-ui/icons/Delete';

import { del } from '../api';

export default function AlertDialog(props) {
  const [open, setOpen] = React.useState(false);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const deleteEntity = () => {
        del(props.entityUrl, props.entity.id).then(() => {
            setOpen(false);
            window.location.reload(); // goes against everything react stands for
        });
    };

  return (
    <div>
      <Button variant="outlined" color="primary" onClick={handleClickOpen}>
        <DeleteIcon/>
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{props.header}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {props.children}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={deleteEntity} color="primary" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
