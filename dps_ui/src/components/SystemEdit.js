import React from 'react';
import Grid from '@material-ui/core/Grid';

import ChipInput from 'material-ui-chip-input';

import EntityEdit from './EntityEdit';
import KeyValueInput from './KeyValueInput';
import TextField from './TextField';
import EntityMultiSelect from './EntityMultiSelect';

export default class KPIEdit extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {
      displayName: '',
      signals: [],
      constants: '[]',
      kpis: '[]',
    };
    }
    
  render () {
    const props = this.props;
    
    const signalsInput = (<input type="hidden" name="signals" value={this.state.signals} />);
    const constantsInput = (<input type="hidden" name="constants" value={this.state.constants} />);
    const kpisInput = (<input type="hidden" name="code" value={this.state.kpis} />);        

    const onEntity = (entity) => {
      let signals = entity['signals'].split(',');
      let constants = entity['constants'];
      let kpis = entity['kpis'] || '[]';
      signals = signals[0] === '' ? [] : signals;
      const displayName = entity['displayName'];
      this.setState({
        signals,
        constants,
        kpis,
        displayName,                
      });
    };
    
    return (
      <EntityEdit
        {...props}
        edit={props.edit}
        entityName="System"
        entityUrl='/system/'
        onGETEntity={onEntity}
        >
        <Grid container spacing={2}>
          <Grid item xs={12}>            
            <TextField
              fullWidth={true}
              name="displayName"
              value={this.state.displayName} // apparently this is wrong to do something about controlled vs uncontrolled
              onChange={e => this.setState({ displayName: e.value })}
              label="Name" />
          </Grid>

          <Grid item xs={12} sm={6}>
            <ChipInput
              fullWidth={true}
            label="Signals"
            value={this.state.signals} 
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
        </Grid>

            <Grid item xs={12} m={6}>
              <KeyValueInput header={[
                  'Constant', 'Value',
              ]}
                             defaultValue={JSON.parse(this.state.constants)}
                             onChange={x => {
                                 this.setState({ constants: JSON.stringify(x) });
                             }}/>
        {constantsInput}
            </Grid>

            <Grid item xs={12}>
              <EntityMultiSelect header="KPIs"
                            fullWidth={true}
                            name="kpi"
                                 value={JSON.parse(this.state.kpis)}
                                 onChange={x => this.setState({ kpis: JSON.stringify(x.target.value) })}
                            entityUrl={'/kpi/'}/>
        {kpisInput}
</Grid>
        </Grid>
        </EntityEdit>
    );
        
    }
}
