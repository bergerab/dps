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
import DialogTitle from '@material-ui/core/DialogTitle';

import util from '../util.js';
import KPIEditor from './KPIEditor';

export default class ParameterDialog extends React.Component {
  render() {
    let id = this.props.id;
    if (this.props.paramErrors !== null && this.props.id === -1) {
      id = this.props.paramErrors.length - 1;
    }

    const hasError =
          this.props.paramErrors !== null &&
          this.props.paramErrors !== undefined &&
          id in this.props.paramErrors &&
          !util.objectIsEmpty(this.props.paramErrors[id]);
    const hasNameError = hasError && 'name' in this.props.paramErrors[id];
    const hasDefaultError = hasError && 'default' in this.props.paramErrors[id];
    const hasIdentifierError = hasError && 'identifier' in this.props.paramErrors[id];    

    const identifier = util.getIdentifier(this.props.name, this.props.identifier);    
    const identifierField =
          (
            <Grid item xs={12}>
              <TextField
                id="identifier"
                label="Identifier"
                type="text"
                error={hasIdentifierError}
                helperText={this.props.paramErrors === null ? '' : this.props.paramErrors[id].identifier}               
                value={identifier === null ? '' : identifier}                    
                onChange={event => {
                  this.props.handleIdentifier(event.target.value);
                }}
                fullWidth
              />
            </Grid>);

    const addOrEdit = this.props.id > -1 ? 'Edit' : 'Add';
    const header = this.props.header || 'Parameter';

    return (
      <Dialog open={this.props.open} onClose={this.props.handleClose} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">{addOrEdit} {header}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                id="name"
                label="Name"
                value={this.props.name}
                error={hasNameError}
                helperText={this.props.paramErrors === null ? '' : this.props.paramErrors[id].name}               
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
                id="units"
                label="Units"
                type="text"
                value={this.props.units}
                fullWidth
                multiline
                onChange={event => {
                  this.props.handleUnits(event.target.value);
                }}
                rows={2}
                rowsMax={4}
              />
            </Grid>


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

            {this.props._default === undefined ? null : (<Grid item xs={12}>
              <FormLabel>Default</FormLabel>              
              <KPIEditor
              	value={this.props._default}
	        onBeforeChange={(editor, data, value) => {
                  this.props.handleDefault(value);
	        }}
              />
            </Grid>)}
            
            {this.props.hidden === undefined ? null : (<Grid item xs={12}>
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
            </Grid>)}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={this.props.handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={this.props.handleSave} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}
