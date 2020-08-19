import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Link } from "react-router-dom";
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Input from '@material-ui/core/Input';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Breadcrumbs from '@material-ui/core/Breadcrumbs';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import ChipInput from 'material-ui-chip-input';

import TextField from './TextField';

// The following two imports is for the theme.
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';

// This import is for the language syntax highlighting.
import 'codemirror/mode/python/python.js';

import { Controlled as CodeMirror } from "react-codemirror2";

import EntityEdit from './EntityEdit';

const useStyles = makeStyles((theme) => ({
}));

export default class KPIEdit extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            displayName: '',
            signals: [],
            constants: [],
            code: '',
        };
    }
    
    render () {
        const props = this.props;
        
        const headerText = (props.edit ? 'Edit' : 'Add') + ' KPI';

        const signalsInput = (<input type="hidden" name="signals" value={this.state.signals} />);
        const constantsInput = (<input type="hidden" name="constants" value={this.state.constants} />);
        const codeInput = (<input type="hidden" name="code" value={this.state.code} />);        

        const onEntity = (entity) => {
            let signals = entity['signals'].split(',');
            let constants = entity['constants'].split(',');
            let code = entity['code'];
            signals = signals[0] === '' ? [] : signals;
            constants = constants[0] === '' ? [] : constants;
            const displayName = entity['displayName'];
            this.setState({
                signals,
                constants,
                displayName,
                code,                
            });
            console.log(entity, signals, constants);
    };
        
    return (
        <EntityEdit
          {...props}
          edit={props.edit}
          entityName="KPI"
          entityUrl='/kpi/'
          onGETEntity={onEntity}
        >
          <Grid container spacing={2}>
<Grid item xs={12}>            
            <TextField
	      floatingLabelFixed={true}
              InputLabelProps={{
                  shrink: true,
              }}	
              fullWidth={true}
              name="displayName"
              value={this.state.displayName} // apparently this is wrong to do something about controlled vs uncontrolled
          onChange={e => this.setState({ displayName: e.value })}
        label="Name" />
        </Grid>

          <Grid item xs={12} sm={6}>
            <ChipInput
              fullWidth={true}
            label="Input Signals"
            value={this.state.signals} // apparently this is wrong to do something about controlled vs uncontrolled
            onAdd={(e, b) => {
                this.setState({
                    signals: this.state.signals.concat([e]),
                });
            }}
            onDelete={(e, index) => {
                this.setState({
                    signals: this.state.signals.filter(x => x !== e),
                });
            }}        
          />
          {signalsInput}
            
          </Grid>
            
          <Grid item xs={12} sm={6}>  
            <ChipInput
              fullWidth={true}              
            label="Input Constants"
            value={this.state.constants} // apparently this is wrong to do something about controlled vs uncontrolled
            onAdd={(e, b) => {
                this.setState({
                    constants: this.state.constants.concat([e]),
                });
            }}
            onDelete={(e, index) => {
                this.setState({
                    constants: this.state.constants.filter(x => x !== e),
                });
            }}        
          />
        {constantsInput}
        </Grid>

<Grid item xs={12}>  
          <KPIEditor
            value={this.state.code}
            onBeforeChange={(editor, data, value) => {
                this.setState({ code: value });
            }}/>
        {codeInput}
</Grid>
        </Grid>
        </EntityEdit>
    );
        
    }
}

class KPIEditor extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let option = {
        mode: 'python',
        theme: 'material',
        lineNumbers: true,        
    };

    return (
      <div>
        <CodeMirror {...this.props}
          style={{ fontSize: '18pt' }}
          options={option}
//          onBeforeChange={(editor, data, value) => {
//            this.setState({ src: value });
//          }}
//          onChange={(editor, data, value) => {}}
        />
      </div>
    );
  }
}
