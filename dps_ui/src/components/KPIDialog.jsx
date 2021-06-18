import React from 'react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormLabel from '@material-ui/core/FormLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';

import util from '../util.js';
import KPIEditor from './KPIEditor';
import HTMLEditor from './HTMLEditor';

export default class KPIDialog extends React.Component {
  render() {
    const addOrEdit = this.props.id > -1 ? 'Edit' : 'Add';

    let id = this.props.id;
    if (this.props.kpiErrors !== null && this.props.id === -1) {
      id = this.props.kpiErrors.length - 1;
    }
    
    const hasError =
          this.props.kpiErrors !== null &&
          this.props.kpiErrors !== undefined &&
          id in this.props.kpiErrors &&
          !util.objectIsEmpty(this.props.kpiErrors[id]);
    const hasNameError = hasError && 'name' in this.props.kpiErrors[id];
    const hasComputationError = hasError && 'computation' in this.props.kpiErrors[id];
    const hasIdentifierError = hasError && 'identifier' in this.props.kpiErrors[id];    

    const identifier = util.getIdentifier(this.props.name, this.props.identifier);
    const identifierField =
          (<Grid item xs={12}>
             <TextField
               id="identifier"
               label="Identifier"
               type="text"
               error={hasIdentifierError}
               helperText={this.props.kpiErrors === null ? '' : this.props.kpiErrors[id].identifier}               
               value={identifier === null ? '' : identifier}                    
               onChange={event => {
                 this.props.handleIdentifier(event.target.value);
               }}
               fullWidth
             />
           </Grid>);

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
                error={hasNameError}
                helperText={this.props.kpiErrors === null ? '' : this.props.kpiErrors[id].name}
                fullWidth
                required
              />
            </Grid>

            {identifierField}
            
            <Grid item xs={12}>
              <FormLabel>Description</FormLabel>              
              <HTMLEditor
                value={this.props.description}
                onChange={value => {
                  this.props.handleDescription(value);                  
                }}/>
            </Grid>

            <Grid item xs={12}>
              <FormLabel
                error={hasComputationError}
              >Computation *</FormLabel>
              {hasComputationError ?
               (<div>
                  <div className="editor-error">
                    <KPIEditor
              	      value={this.props.computation}
	              onBeforeChange={(editor, data, value) => {
                        this.props.handleComputation(value);
	              }}
                    />
                  </div>
                  <FormHelperText error={true}>
                    {this.props.kpiErrors[id].computation}
                  </FormHelperText>
                </div>) :
               (<KPIEditor
              	  value={this.props.computation}
	          onBeforeChange={(editor, data, value) => {
                    this.props.handleComputation(value);
	          }}
                />
               )}
            </Grid>

            <Grid item xs={12}>
              <TextField
                id="units"
                label="Units"
                type="text"
                value={this.props.units}                    
                onChange={event => {
                  this.props.handleUnits(event.target.value);
                }}
                fullWidth
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
