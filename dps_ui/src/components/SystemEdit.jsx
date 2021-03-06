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
import Errors from './Errors';
import InputLabel from './InputLabel';
import ConfirmationDialog from './ConfirmationDialog';

import util from '../util';
import { put, post } from '../api';

export default class KPIEdit extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      errors: null, // leftover errors which have not been handled by inputs

      system_id: -1,

      // Defaults for System fields
      // (used before the onEntity GET request returns)
      name: '',
      nameErrors: null,

      description: '',

      kpis: [],
      kpiErrors: null,

      parameters: [],
      paramErrors: null,

      signals: [],
      signalErrors: null,

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
      kpiUnits: '',
    });
  }

  clearParam() {
    Object.assign(this.state, {
      paramId: -1,
      paramName: '',
      paramDescription: '',
      paramUnits: '',
      paramIdentifier: '',
      paramHidden: false,
      paramDefault: '',
    });
  }

  clearSignal() {
    Object.assign(this.state, {
      signalId: -1,
      signalName: '',
      signalDescription: '',
      signalUnits: '',
      signalIdentifier: '',
    });
  }


  handleCloseSignalDialog() {
    this.setState({ signalDialogOpen: false });
  }

  handleSaveSignalDialog() {
    const signal = {
      name: this.state.signalName,
      identifier: this.state.signalIdentifier,
      description: this.state.signalDescription,
      units: this.state.signalUnits,
    };

    // Add
    if (this.state.signalId === -1) {
      const newSignals = this.state.signals.concat([signal]);
      this.save({ signals: newSignals }).then(o => {
        this.setState({
          signalDialogOpen: false,
          signalId: newSignals.length,
          signals: newSignals,
        });
        this.clearSignal();
      }).catch(() => { });
    } else { // Edit
      const newSignals = [];
      let i = 0;
      for (const oldSignal of this.state.signals) {
        if (i === this.state.signalId) {
          newSignals[i] = signal;
        } else {
          newSignals[i] = oldSignal;
        }
        ++i;
      }
      this.setState({
        signals: newSignals,
      }, () => {
        this.save().then(o => {
          this.setState({
            signalDialogOpen: false,
          });
        }).catch(() => { });
      });
    }
  }

  handleCloseParamDialog() {
    this.setState({ paramDialogOpen: false });
  }

  handleSaveParamDialog() {
    const param = {
      name: this.state.paramName,
      identifier: this.state.paramIdentifier,
      description: this.state.paramDescription,
      units: this.state.paramUnits,
      hidden: this.state.paramHidden,
      default: this.state.paramDefault,
    };

    // Add
    if (this.state.paramId === -1) {
      const newParams = this.state.parameters.concat([param]);
      this.save({ parameters: newParams }).then(o => {
        this.setState({
          paramDialogOpen: false,
          paramId: newParams.length,
          parameters: newParams,
        });
        this.clearParam();
      }).catch(() => { });
    } else { // Edit
      const newParams = [];
      let i = 0;
      for (const oldParam of this.state.parameters) {
        if (i === this.state.paramId) {
          newParams[i] = param;
        } else {
          newParams[i] = oldParam;
        }
        ++i;
      }
      this.setState({
        parameters: newParams,
      }, () => {
        this.save().then(o => {
          this.setState({
            paramDialogOpen: false,
          });
        }).catch(() => { });
      });
    }
  }

  handleCloseKPIDialog() {
    this.setState({ kpiDialogOpen: false });
  }

  handleSaveKPIDialog() {
    const kpi = {
      name: this.state.kpiName,
      identifier: this.state.kpiIdentifier,
      description: this.state.kpiDescription,
      hidden: this.state.kpiHidden,
      computation: this.state.kpiComputation,
      units: this.state.kpiUnits,
    };

    // Add
    if (this.state.kpiId === -1) {
      const newKpis = this.state.kpis.concat([kpi]);
      this.save({ kpis: newKpis }).then(o => {
        this.setState({
          kpiDialogOpen: false,
          kpiId: newKpis.length,
          kpis: newKpis,
        });
        this.clearKpi();
      }).catch(() => { });
    } else { // Edit
      const newKpis = [];
      let i = 0;
      for (const oldKpi of this.state.kpis) {
        if (i === this.state.kpiId) {
          newKpis[i] = kpi;
        } else {
          newKpis[i] = oldKpi;
        }
        ++i;
      }
      this.setState({
        kpis: newKpis,
      }, () => {
        this.save().then(o => {
          this.setState({
            kpiDialogOpen: false,
          });
        }).catch(() => { });
      });
    }
  }

  save(overrides) {
    this.setState({
      nameErrors: null,
      kpiErrors: null,
      paramErrors: null,
      errors: null,
    });

    const o = Object.assign({
      name: this.state.name,
      description: this.state.description,
      kpis: this.state.kpis,
      parameters: this.state.parameters,
      signals: this.state.signals,
    }, overrides);

    if (this.state.system_id === -1) {
      /*
      return post('system', o).catch(error => {
        error.then(jo => {
          this.onError(jo);
        });
        throw error;
      });
      */
      return Promise.resolve(o);
    } else {
      return put('system', this.state.system_id, o).catch(error => {
        error.then(jo => {
          this.onError(jo);
        });
        throw error;
      });
    }
  }

  handleOpenKPIDialog() {
    this.setState({
      kpiDialogOpen: true
    });
  }

  onError(error) {
    this.setState({ nameErrors: util.objectPop(error, 'name') });
    this.setState({ kpiErrors: util.objectPop(error, 'kpis') });
    this.setState({ paramErrors: util.objectPop(error, 'parameters') });
    if (Object.keys(error).length > 0) {
      this.setState({ errors: error });
    } else {
      this.setState({ errors: null });
    }
  }

  render() {
    const props = this.props;

    const onEntity = entity => {
      const name = entity.name;
      this.setState({
        system_id: entity.system_id,
        name: entity.name,
        description: entity.description,
        kpis: entity.kpis,
        parameters: entity.parameters,
        signals: entity.signals,
      });
    };

    return (
      <Grid container>
        {this.state.errors !== null ?
          (<Grid item style={{ marginBottom: '2em', width: '100%' }}>
            <Errors
              errors={this.state.errors}
            />
          </Grid>) : null
        }
        <EntityEdit
          {...props}
          edit={props.edit}
          entityName="System"
          entityUrl='system'
          onGETEntity={onEntity}
          onError={this.onError.bind(this)}
        >
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth={true}
                name="name"
                value={this.state.name}
                onChange={e => this.setState({ nameErrors: null, name: e.target.value })}
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
              <InputLabel>Signals</InputLabel>
              <PrettyTable
                header={['Name', 'Identifier', 'Units', 'Description', '']}
                rows={this.state.signals.map((signal, i) => {
                  const hasError =
                    this.state.signalErrors !== null &&
                    i <= this.state.signalErrors.length &&
                    !util.objectIsEmpty(this.state.signalErrors[i]);
                  const hasNameError = hasError && 'name' in this.state.signalErrors[i];
                  const hasIdentifierError = hasError && 'identifier' in this.state.signalErrors[i];

                  return [
                    hasNameError ?
                      (<div>
                        <TextField
                          error={true}
                          helperText={this.state.signalErrors[i].name}
                          value={signal.name}
                        />
                      </div>) : signal.name,

                    hasIdentifierError ?
                      (<div>
                        <div className="editor-error-thick">
                          <KPIEditor
                            className="code"
                            options={{
                              lineNumbers: false,
                              readOnly: true,
                            }}
                            readonly={true}
                            value={signal.identifier} />,
                        </div>
                        <FormHelperText error={true}>
                          {this.state.signalErrors[i].identifier}
                        </FormHelperText>
                      </div>) :
                      (<KPIEditor
                        className="code"
                        options={{
                          lineNumbers: false,
                          readOnly: true,
                        }}
                        readonly={true}
                        value={signal.identifier} />),

                    signal.units,

                    signal.description,

                    (<EditAndDeleteLocal
                      entityName={signal.name}
                      entityType="signal"
                      onClickEdit={() => {
                        this.setState({
                          signalDialogOpen: true,

                          signalId: i,
                          signalName: signal.name,
                          signalIdentifier: signal.identifier,
                          signalDefault: signal.default,
                          signalDescription: signal.description,
                          signalUnits: signal.units,
                          signalHidden: signal.hidden,
                          signalComputation: signal.computation,
                        });
                      }}
                      onClickDelete={x => {
                        this.setState({
                          signals: this.state.signals.filter((x, j) => i !== j)
                        }, () => {
                          this.save();
                        });

                      }}
                    />)];
                })}
              />
              <Button variant="contained"
                color="primary"
                style={{ marginTop: '10px' }}
                onClick={() => {
                  this.clearSignal();
                  this.setState({ signalDialogOpen: true })
                }}>
                Add Signal
              </Button>
            </Grid>

            <Grid item xs={12}>
              <InputLabel>Parameters</InputLabel>
              <PrettyTable
                header={['Name', 'Identifier', 'Units', 'Default', 'Description', 'Hidden', '']}
                rows={this.state.parameters.map((parameter, i) => {
                  const hasError =
                    this.state.paramErrors !== null &&
                    i <= this.state.paramErrors.length &&
                    !util.objectIsEmpty(this.state.paramErrors[i]);
                  const hasNameError = hasError && 'name' in this.state.paramErrors[i];
                  const hasIdentifierError = hasError && 'identifier' in this.state.paramErrors[i];
                  const hasDefaultError = hasError && 'default' in this.state.paramErrors[i];

                  return [
                    hasNameError ?
                      (<div>
                        <TextField
                          error={true}
                          helperText={this.state.paramErrors[i].name}
                          value={parameter.name}
                        />
                      </div>) : parameter.name,

                    hasIdentifierError ?
                      (<div>
                        <div className="editor-error-thick">
                          <KPIEditor
                            className="code"
                            options={{
                              lineNumbers: false,
                              readOnly: true,
                            }}
                            readonly={true}
                            value={parameter.identifier} />,
                        </div>
                        <FormHelperText error={true}>
                          {this.state.paramErrors[i].identifier}
                        </FormHelperText>
                      </div>) :
                      (<KPIEditor
                        className="code"
                        options={{
                          lineNumbers: false,
                          readOnly: true,
                        }}
                        readonly={true}
                        value={parameter.identifier} />),

                    parameter.units,

                    hasDefaultError ?
                      (<div>
                        <div className="editor-error-thick">
                          <KPIEditor
                            className="code"
                            options={{
                              lineNumbers: false,
                              readOnly: true,
                            }}
                            readonly={true}
                            value={parameter.default} />,
                        </div>
                        <FormHelperText error={true}>
                          {this.state.paramErrors[i].default}
                        </FormHelperText>
                      </div>) :
                      (<KPIEditor
                        className="code"
                        options={{
                          lineNumbers: false,
                          readOnly: true,
                        }}
                        readonly={true}
                        value={parameter.default} />),

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
                          paramUnits: parameter.units,
                          paramHidden: parameter.hidden,
                          paramComputation: parameter.computation,
                        });
                      }}
                      onClickDelete={x => {
                        this.setState({
                          parameters: this.state.parameters.filter((x, j) => i !== j)
                        }, () => {
                          this.save();
                        });

                      }}
                    />)];
                })}
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


            <Grid item xs={12}>
              <InputLabel>KPIs</InputLabel>
              <PrettyTable
                header={['Name', 'Identifier', 'Units', 'Computation', 'Description', 'Hidden', '']}
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
                        autoRefresh: true,
                        lineNumbers: false,
                        readOnly: true,
                      }}
                      readonly={true}
                      value={util.getIdentifier(kpi.name, kpi.identifier)} />,

                    kpi.units,

                    hasComputationError ?
                      (<div>
                        <div className="editor-error-thick">
                          <KPIEditor
                            className="code"
                            options={{
                              lineNumbers: false,
                            }}
                            value={kpi.computation} />
                        </div>
                        <FormHelperText error={true}>
                          {this.state.kpiErrors[i].computation}
                        </FormHelperText>
                      </div>) :
                      (<KPIEditor
                        className="code"
                        options={{
                          lineNumbers: false,
                        }}
                        value={kpi.computation} />),

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
                          kpiUnits: kpi.units,
                        });
                      }}
                      onClickDelete={x => {
                        this.setState({ kpis: this.state.kpis.filter((x, j) => i !== j) }, () => {
                          this.save();
                        });
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
              handleUnits={units => this.setState({ kpiUnits: units })}
              units={this.state.kpiUnits}
            />

            <input name="parameters"
              value={JSON.stringify(this.state.parameters)}
              data-type="json"
              type="hidden" />
            <ParameterDialog
              open={this.state.paramDialogOpen}
              handleClose={this.handleCloseParamDialog.bind(this)}
              handleSave={this.handleSaveParamDialog.bind(this)}
              paramErrors={this.state.paramErrors}

              id={this.state.paramId}
              name={this.state.paramName}
              handleName={name => this.setState({ paramName: name })}
              identifier={this.state.paramIdentifier}
              handleIdentifier={identifier => this.setState({ paramIdentifier: identifier })}
              description={this.state.paramDescription}
              handleDescription={description => this.setState({ paramDescription: description })}
              units={this.state.paramUnits}
              handleUnits={units => this.setState({ paramUnits: units })}
              hidden={this.state.paramHidden}
              handleHidden={hidden => this.setState({ paramHidden: hidden })}
              _default={this.state.paramDefault}
              handleDefault={_default => this.setState({ paramDefault: _default })}
            />

            <input name="signals"
              value={JSON.stringify(this.state.signals)}
              data-type="json"
              type="hidden" />
            <ParameterDialog
              open={this.state.signalDialogOpen}
              header={"Signal"}
              handleClose={this.handleCloseSignalDialog.bind(this)}
              handleSave={this.handleSaveSignalDialog.bind(this)}
              paramErrors={this.state.signalErrors}

              id={this.state.signalId}
              name={this.state.signalName}
              handleName={name => this.setState({ signalName: name })}
              identifier={this.state.signalIdentifier}
              handleIdentifier={identifier => this.setState({ signalIdentifier: identifier })}
              description={this.state.signalDescription}
              handleDescription={description => this.setState({ signalDescription: description })}
              units={this.state.signalUnits}
              handleUnits={units => this.setState({ signalUnits: units })}
            />

          </Grid>
        </EntityEdit>
      </Grid>
    );

  }
}

function EditAndDeleteLocal(props) {
  return (
    <div style={{ textAlign: 'right' }}>
      <div style={{ display: 'inline-flex' }}>
        <Button
          variant="outlined"
          color="primary"
          style={{ marginRight: '10px' }}
          onClick={props.onClickEdit}
        >
          <EditIcon />
        </Button>
        <ConfirmationDialog
          deleteText='Remove'
          deleteObj={props.onClickDelete}
          header={`Remove "${props.entityName}" ${props.entityType}?`}
        >
          Are you sure you want to remove this {props.entityType}?
        </ConfirmationDialog>
      </div>

    </div>
  );
}
