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

import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/python/python.js';
import { Controlled as CodeMirror } from "react-codemirror2";

export default class KPIDialog extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      open: true,
      name: '',
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

    const identifierField = util.nameNeedsIdentifier(this.name) ? (
      <Grid item xs={12}>
        <TextField
          id="identifier"
          label="Identifier"
          type="text"
          fullWidth
        />
      </Grid>) : (<span/>);
    
    return (
      <Dialog open={this.state.open}
              onClose={handleClose}
              aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Add KPI</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                id="name"
                label="Name"
                type="text"
                onChange={event => {
                  this.setState({ name: event.target.value.trim() });
                }}
                fullWidth
                required
              />
            </Grid>

            {identifierField}
            
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

            <Grid item xs={12}>
              <FormLabel>Computation *</FormLabel>
              <KPIEditor
              	value={this.state.code}
	        onBeforeChange={(editor, data, value) => {
		  this.setState({ code: value });
	        }}
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

class KPIEditor extends React.Component {
  render() {
    let option = {
      mode: 'python',
      theme: 'material',
      lineNumbers: true,
    };

    return (
      <div>
	<CodeMirror
	  {...this.props}
	  style={{ fontSize: '12pt' }}
	  options={option}
        />
      </div>
    );
  }
}
