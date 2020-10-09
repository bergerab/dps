import React from 'react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormLabel from '@material-ui/core/FormLabel';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

export default class ParameterDialog extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      open: props.open,
      code: '',
      hidden: false, 
    }
  }
  
  render() {
    const handleClickOpen = () => {
      this.setState({ open: true });
    };

    const handleClose = () => {
      this.setState({ open: false });
    };
    
    return (
      <Dialog open={this.props.open} onClose={handleClose} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Add Parameter</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                id="name"
                label="Name"
                type="text"
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                id="identifier"
                label="Identifier"
                type="text"
                fullWidth
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                id="default"
                label="Default Value"
                type="text"
                fullWidth                
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    color="primary"
                    checked={this.state.hidden}
                    onChange={event => this.setState({ hidden: event.target.checked })}
                    name="checkedF"
                  />
                }
                label="Hidden"
              />              
            </Grid>

            <Grid item xs={12}>
              <TextField
                id="description"
                label="Description"
                type="text"
                fullWidth
                multiline
                rows={2}
                rowsMax={4}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleClose} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}
