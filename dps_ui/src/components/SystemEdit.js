import React from 'react';
import Grid from '@material-ui/core/Grid';

import ChipInput from 'material-ui-chip-input';
import FormLabel from '@material-ui/core/FormLabel';
import Button from '@material-ui/core/Button';

import EntityEdit from './EntityEdit';
import KeyValueInput from './KeyValueInput';
import TextField from './TextField';
import EntityMultiSelect from './EntityMultiSelect';
import KPIDialog from './KPIDialog';
import ParameterDialog from './ParameterDialog';
import PrettyTable from './PrettyTable';

import EditIcon from '@material-ui/icons/Edit';

import Link from './Link';
import ConfirmationDialog from './ConfirmationDialog';

export default class KPIEdit extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {
      // Defaults for System fields
      // (used before the onEntity GET request returns)
      name: '',
      kpis: [],
      parameters: [],

      // State controls for dialog boxes
      kpiDialogOpen: false,
      kpiToEdit: null,
      
      parameterDialogOpen: false,      
    };
  }

  handleCloseKPIDialog() {
    this.setState({ kpiDialogOpen: false });
  }

  handleSaveKPIDialog(kpi) {
    this.setState({
      kpiDialogOpen: false
    });
    
    const edit = kpi.edit;
    delete kpi.edit;

    if (!edit) {
      this.setState({
        kpis: this.state.kpis.concat([kpi]),
      });
    }

    console.log(kpi);
  }

  handleOpenKPIDialog() {
    this.setState({ kpiDialogOpen: true });
  }
  
  render () {
    const props = this.props;
    
    const onEntity = (entity) => {
      const name = entity.name;
      this.setState({
        name: entity.name,
        kpis: entity.kpis,
        parameters: entity.parameters,
      });
    };

    return (
      <EntityEdit
        {...props}
        edit={props.edit}
        entityName="System"
        entityUrl='system'
        onGETEntity={onEntity}
      >
        <Grid container spacing={2}>
          <Grid item xs={12}>            
            <TextField
              fullWidth={true}
              name="name"
              value={this.state.name}
              onChange={e => this.setState({ name: e.value })}
              label="Name"
            />
          </Grid>

          <Grid item xs={12}>
            <FormLabel>KPIs</FormLabel>
            <PrettyTable
              header={['Name', 'Identifier', 'Computation', 'Description', 'Hidden', '']}
              rows={this.state.kpis.map(kpi =>
                                        [kpi.name,
                                         kpi.identifier,
                                         kpi.computation,
                                         kpi.description,
                                         kpi.hidden ? 'Yes' : 'No',
                                         (<EditAndDeleteLocal
                                            onClickEdit={() => {
                                              this.setState({
                                                kpiDialogOpen: true,
                                                kpiToEdit: kpi,
                                              });
                                            }}
                                          />)])}
            />
            <Button variant="contained"
                    color="primary"
                    style={{ marginTop: '10px' }}
                    onClick={() => {
                      this.setState({ kpiDialogOpen: true })
                    }}>
              Add KPI
            </Button>
          </Grid>
          
          <Grid item xs={12}>
            <FormLabel>Parameters</FormLabel>
            <PrettyTable
              header={['Name']}
              rows={this.state.parameters.map(parameter => [parameter.name])}              
            />
            <Button variant="contained"
                    color="primary"
                    style={{ marginTop: '10px' }}
                    onClick={() => {
                      this.setState({ parameterDialogOpen: true })
                    }}>
              Add Parameter
            </Button>
          </Grid>

          <input name="kpis"
                 value={JSON.stringify(this.state.kpis)}
                 data-type="json"
                 type="hidden" />
          <KPIDialog
            open={this.state.kpiDialogOpen}
            handleClose={this.handleCloseKPIDialog.bind(this)}
            handleSave={this.handleSaveKPIDialog.bind(this)}
            kpiToEdit={this.state.kpiToEdit}                    
          />
          <ParameterDialog
            open={this.state.parameterDialogOpen}
          />          
          
        </Grid>
      </EntityEdit>
    );
    
  }
}

function EditAndDeleteLocal(props) {
  return (
    <div style={{ display: 'inline-flex' }}>
      <Button
        variant="outlined"
        color="primary"
        style={{ marginRight: '10px' }}
        onClick={props.onClickEdit}
      >
        <EditIcon/>
      </Button>
      <ConfirmationDialog
        deleteObj={() => {
          console.log("TODO: Delete KPI");
        }}
	header={`Delete "" ?`}
      >
	Are you sure you want to delete this? This action is irreversible.
      </ConfirmationDialog>
    </div>
  );
}
