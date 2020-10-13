import React from 'react';
import Grid from '@material-ui/core/Grid';

import FormLabel from '@material-ui/core/FormLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import Button from '@material-ui/core/Button';

import EntityEdit from './EntityEdit';
import TextField from './TextField';
import KPIDialog from './KPIDialog';
import ParameterDialog from './ParameterDialog';
import PrettyTable from './PrettyTable';

import EditIcon from '@material-ui/icons/Edit';

import KPIEditor from './KPIEditor';
import HTMLEditor from './HTMLEditor';
import InputLabel from './InputLabel';
import ConfirmationDialog from './ConfirmationDialog';

import util from '../util';

export default class KPIEdit extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {
      errors: null, // leftover errors which have not been handled by inputs
      
      // Defaults for System fields
      // (used before the onEntity GET request returns)
      name: '',
      nameErrors: null,
      
      description: '',
      
      kpis: [],
      kpiErrors: null,
      
      parameters: [],

      // State controls for dialog boxes
      kpiDialogOpen: false,
      paramDialogOpen: false,
    };
    
    this.clearKpi();
    this.clearParam();
  }

  clearKpi() {
    Object.assign(this.state, {
      kpiId: -1,
      kpiName: '',
      kpiDescription: '',
      kpiIdentifier: '',
      kpiHidden: false,
      kpiComputation: '',                  
    });
  }    

  clearParam() {
    Object.assign(this.state, {
      paramId: -1,
      paramName: '',
      paramDescription: '',
      paramIdentifier: '',
      paramHidden: false,
      paramDefault: '',
    });
  }

  handleCloseParamDialog() {
    this.setState({ paramDialogOpen: false });
  }

  handleSaveParamDialog() {
    this.setState({
      paramDialogOpen: false
    });

    const param = {
      name: this.state.paramName,
      identifier: this.state.paramIdentifier,
      description: this.state.paramDescription,
      hidden: this.state.paramHidden,
      default: this.state.paramDefault,
    };

    // Add
    if (this.state.paramId === -1) {
      this.setState({
        parameters: this.state.parameters.concat([param]),
      });
      this.clearParam();      
    } else { // Edit
      this.state.parameters[this.state.paramId] = param;
    }
  }

  handleCloseKPIDialog() {
    this.setState({ kpiDialogOpen: false });
  }

  handleSaveKPIDialog() {
    this.setState({
      kpiDialogOpen: false
    });

    const kpi = {
      name: this.state.kpiName,
      identifier: this.state.kpiIdentifier,
      description: this.state.kpiDescription,
      hidden: this.state.kpiHidden,
      computation: this.state.kpiComputation,
    };

    // Add
    if (this.state.kpiId === -1) {
      this.setState({
        kpis: this.state.kpis.concat([kpi]),
      });
      this.clearKpi();      
    } else { // Edit
      this.state.kpis[this.state.kpiId] = kpi;
    }
  }

  handleOpenKPIDialog() {
    this.setState({
      kpiDialogOpen: true
    });
  }
  
  render () {
    const props = this.props;
    
    const onEntity = entity => {
      const name = entity.name;
      this.setState({
        name: entity.name,
        description: entity.description,
        kpis: entity.kpis,
        parameters: entity.parameters,
      });
    };

    const onError = error => {
      this.setState({ nameErrors: util.objectPop(error, 'name') });
      this.setState({ kpiErrors: util.objectPop(error, 'kpis') });      
      if (Object.keys(error).length > 0) {
        this.setState({ errors: error });
      } else {
        this.setState({ errors: null });
      }
    };

    return (
      <Grid container spacing={2}>
        {this.state.errors !== null ?
         (<Grid item>
            {JSON.stringify(this.state.errors)}
          </Grid>) : null
        }
        <EntityEdit
          {...props}
          edit={props.edit}
          entityName="System"
          entityUrl='system'
          onGETEntity={onEntity}
          onError={onError}        
        >
          <Grid container spacing={2}>
            <Grid item xs={12}>            
              <TextField
                fullWidth={true}
                name="name"
                value={this.state.name}
                onChange={e => this.setState({ nameErrors: null, name: e.value })}
                error={this.state.nameErrors !== null}
                helperText={this.state.nameErrors === null ? '' : this.state.nameErrors.join('\n')}
                label="Name"
              />
            </Grid>

            <Grid item xs={12}>
              <InputLabel>Description</InputLabel>
              <input name="description"
                     value={this.state.description}
                     type="hidden" />
              <HTMLEditor
                value={this.state.description}
                onChange={value => {
                  this.setState({ description: value });
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <InputLabel>KPIs</InputLabel>            
              <PrettyTable
                header={['Name', 'Identifier', 'Computation', 'Description', 'Hidden', '']}
                rows={this.state.kpis.map((kpi, i) => {
                  const hasError =
                        this.state.kpiErrors !== null &&
                        i <= this.state.kpiErrors.length &&
                        !util.objectIsEmpty(this.state.kpiErrors[i]);
                  const hasNameError = hasError && 'name' in this.state.kpiErrors[i];
                  const hasComputationError = hasError && 'computation' in this.state.kpiErrors[i];
                  
                  return [
                    hasNameError ?
                      (<div>
                         <TextField
                           error={true}
                           helperText={this.state.kpiErrors[i].name}
                           value={kpi.name}
                         />
                       </div>) : kpi.name,
                    <KPIEditor
                      className="code"
                      options={{
                        lineNumbers: false,
                        readOnly: true,
                      }}
                      readonly={true}
                      value={util.getIdentifier(kpi.name, kpi.identifier)}/>,
                    hasComputationError ?
                      (<div>
        <div class="editor-error-thick">
          <KPIEditor
            className="code"
            options={{
              lineNumbers: false,
              readOnly: true,
            }}
            readonly={true}
            value={kpi.computation}/>
        </div>
        <FormHelperText error={true}>
          {this.state.kpiErrors[i].computation}
        </FormHelperText>
      </div>) :
                      (<KPIEditor
                             className="code"
                             options={{
                               lineNumbers: false,
                               readOnly: true,
                             }}
                             readonly={true}
                             value={kpi.computation}/>),
                    <div dangerouslySetInnerHTML={{ __html: kpi.description }}></div>,
                    kpi.hidden ? 'Yes' : 'No',
                    (<EditAndDeleteLocal
                                           entityName={kpi.name}
                                             entityType="KPI"
                                 onClickEdit={() => {
                                   this.setState({
                                     kpiDialogOpen: true,
                                     
                                     kpiId: i,
                                     kpiName: kpi.name,
                                     kpiIdentifier: kpi.identifier,
                                     kpiDescription: kpi.description,
                                     kpiHidden: kpi.hidden,
                                     kpiComputation: kpi.computation,
                                   });
                                 }}
                                   onClickDelete={x => {
                                     this.setState({ kpis: this.state.kpis.filter((x, j) => i !== j) });                                              
                                   }}
          />)
                  ];
                                         })}
              />
              <Button variant="contained"
                      color="primary"
                      style={{ marginTop: '10px' }}
                      onClick={() => {
                        this.clearKpi();
                        this.setState({
                          kpiDialogOpen: true
                        })
                      }}>
                Add KPI
              </Button>
            </Grid>
            
            <Grid item xs={12}>
              <InputLabel>Parameters</InputLabel>                        
              <PrettyTable
                header={['Name', 'Identifier', 'Default', 'Description', 'Hidden', '']}
                rows={this.state.parameters.map((parameter, i) => [parameter.name,
                                                                   <KPIEditor
                                                                     className="code"
                                                                     options={{
                                                                       lineNumbers: false,
                                                                       readOnly: true,
                                                                     }}
                                                                     readonly={true}
                                                                     value={parameter.identifier}/>,
                                                                   <KPIEditor
                                                                     className="code"
                                                                     options={{
                                                                       lineNumbers: false,
                                                                       readOnly: true,
                                                                     }}
                                                                     readonly={true}
                                                                     value={parameter.default}/>,
                                                                   parameter.description,
                                                                   parameter.hidden ? 'Yes' : 'No',
                                                                   (<EditAndDeleteLocal
                                                                     entityName={parameter.name}
                                                                     entityType="parameter"
                                                                     onClickEdit={() => {
                                                                       this.setState({
                                                                         paramDialogOpen: true,
                                                                         
                                                                         paramId: i,
                                                                         paramName: parameter.name,
                                                                         paramIdentifier: parameter.identifier,
                                                                         paramDefault: parameter.default,                                                                        
                                                                         paramDescription: parameter.description,
                                                                         paramHidden: parameter.hidden,
                                                                         paramComputation: parameter.computation,
                                                                       });
                                                                     }}
                                                                     onClickDelete={x => {
                                                                       this.setState({ parameters: this.state.parameters.filter((x, j) => i !== j) });
                                                                     }}
                              />)])}              
              />
              <Button variant="contained"
                      color="primary"
                      style={{ marginTop: '10px' }}
                      onClick={() => {
                        this.clearParam();
                        this.setState({ paramDialogOpen: true })
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
            kpiErrors={this.state.kpiErrors}
            
            id={this.state.kpiId}
            name={this.state.kpiName}
            handleName={name => this.setState({ kpiName: name })}
            identifier={this.state.kpiIdentifier}
            handleIdentifier={identifier => this.setState({ kpiIdentifier: identifier })}
            description={this.state.kpiDescription}
            handleDescription={description => this.setState({ kpiDescription: description })}
            hidden={this.state.kpiHidden}
            handleHidden={hidden => this.setState({ kpiHidden: hidden })}
            computation={this.state.kpiComputation}
            handleComputation={computation => this.setState({ kpiComputation: computation })}
          />

          <input name="parameters"
                 value={JSON.stringify(this.state.parameters)}
                 data-type="json"
                 type="hidden" />
          <ParameterDialog
            open={this.state.paramDialogOpen}
            handleClose={this.handleCloseParamDialog.bind(this)}
            handleSave={this.handleSaveParamDialog.bind(this)}
            
            id={this.state.paramId}
            name={this.state.paramName}
            handleName={name => this.setState({ paramName: name })}
            identifier={this.state.paramIdentifier}
            handleIdentifier={identifier => this.setState({ paramIdentifier: identifier })}
            description={this.state.paramDescription}
            handleDescription={description => this.setState({ paramDescription: description })}
            hidden={this.state.paramHidden}
            handleHidden={hidden => this.setState({ paramHidden: hidden })}
            _default={this.state.paramDefault}
            handleDefault={_default => this.setState({ paramDefault: _default })}
          />          
          
        </Grid>
      </EntityEdit>
      </Grid>
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
        deleteText='Remove'
        deleteObj={props.onClickDelete}
	header={`Remove "${props.entityName}" ${props.entityType}?`}
      >
	Are you sure you want to remove this {props.entityType}?
      </ConfirmationDialog>
    </div>
  );
}
