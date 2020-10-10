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

import util from '../util.js';

export default class KPIDialog extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const identifierField = util.nameNeedsIdentifier(this.props.name) ? (
      <Grid item xs={12}>
        <TextField
          id="identifier"
          label="Identifier"
          type="text"
          value={this.props.identifier}                    
          onChange={event => {
            this.props.handleIdentifier(event.target.value);
          }}
          fullWidth
        />
      </Grid>) : (<span/>);

    const addOrEdit = this.props.id > -1 ? 'Edit' : 'Add';

    return (
      <Dialog open={this.props.open}
              onClose={() => {
                this.props.handleClose();
              }}
              aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">{addOrEdit} KPI</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                id="name"
                label="Name"
                value={this.props.name}                    
                type="text"
                  onChange={event => {
                  this.props.handleName(event.target.value);
                  }}
                fullWidth
                required
              />
            </Grid>

            {identifierField}
            
            <Grid item xs={12}>
              <TextField
                id="description"
                label="Description"
                type="text"
                value={this.props.description}
                fullWidth
                multiline
                onChange={event => {
                  this.props.handleDescription(event.target.value);
                }}
                rows={2}
                rowsMax={4}
              />
            </Grid>

            <Grid item xs={12}>
              <FormLabel>Computation *</FormLabel>
              <KPIEditor
              	value={this.props.computation}
	        onBeforeChange={(editor, data, value) => {
                  this.props.handleComputation(value);
	        }}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    color="primary"
                    checked={this.props.hidden}
                    onChange={event =>
                              this.props.handleHidden(event.target.checked)}
                    name="checkedF"
                  />
                }
                label="Hidden"
              />              
            </Grid>


          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.props.handleClose();
            }}
            color="primary">
            Cancel
          </Button>
          <Button
            onClick={() => {
              this.props.handleSave();
            }}
            color="primary"
          >
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
