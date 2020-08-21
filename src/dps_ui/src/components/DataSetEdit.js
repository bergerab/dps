import React from 'react';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';

import EntityEdit from './EntityEdit';
import EntitySelect from './EntitySelect';
import KeyValueInput from './KeyValueInput';

export default function SystemEdit(props) {
  const [mappings, setMappings] = React.useState('[]');
  const [table, setTable] = React.useState('');
  const [displayName, setDisplayName] = React.useState('');
  const [system, setSystem] = React.useState(0);
  const [connector, setConnector] = React.useState(0);                    

  const mappingsInput = (<input type="hidden" name="mappings" value={mappings} />);

  const onEntity = (entity) => {
    setDisplayName(entity['displayName']);
    setMappings(entity['mappings']);
    setTable(entity['table']);
    setSystem(entity['system']);
    setConnector(entity['data-connector']);                            
  };

  return (
    <EntityEdit
      {...props}
      edit={props.edit}
      entityName="Data Set"
      entityUrl='/data-set/'
      onGETEntity={onEntity}
    >
      <Grid item xs={12} s={6}>
        <TextField
          fullWidth={true}
          name="displayName"
          value={displayName} // apparently this is wrong to do something about controlled vs uncontrolled
          onChange={e => setDisplayName(e.target.value)}
          label="Name"
        />
      </Grid>
      
      <Grid container spacing={2}>
        <Grid item xs={12} s={6}>            
          <EntitySelect header="System"
                        fullWidth={true}
                        name="system"
                        value={system}
                        onChange={x => setSystem(x.target.value)}
                        entityUrl={'/system/'}
          />
	</Grid>
        
        <Grid item xs={12} s={6}>            
          <EntitySelect header="Data Connector"
                        fullWidth={true}
                        name="data-connector"
                        value={connector}
                        onChange={x => setConnector(x.target.value)}
                        entityUrl={'/data-connector/'}
          />
	</Grid>

        <Grid item xs={12} s={6}>
          <TextField
            fullWidth={true}
            name="table"
            value={table} // apparently this is wrong to do something about controlled vs uncontrolled
            onChange={e => setTable(e.target.value)}
            label="Table"
          />
          
	</Grid>
	
        <Grid item xs={12} m={6}>
          <KeyValueInput header={[
            'Data Set Signal Name', 'System Signal Name' ]}
                         defaultValue={JSON.parse(mappings)}
                         onChange={x => {
                           setMappings(JSON.stringify(x));
                         }}
          />
          {mappingsInput}
        </Grid>
      </Grid>
    </EntityEdit>
  );
}
