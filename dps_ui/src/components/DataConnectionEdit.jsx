import React, { useState } from 'react';

import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Grid from '@material-ui/core/Grid';

import EntityEdit from './EntityEdit';

export default function DataConnectionEdit(props) {
  const [dataSource, setDataSource] = useState(0);
  const [displayName, setDisplayName] = useState('');
  const [username, setUserName] = useState('');
  const [password, setPassword] = useState('');    
  const [url, setURL] = useState('');        
  
  function handleDataSource(e) {
    setDataSource(e.target.value);
  }

  const onEntity = (entity) => {
    const displayName = entity['displayName'];
    setDisplayName(displayName);
    setURL(entity['url']);
    setPassword(entity['password']);
    setUserName(entity['username']);
    setDataSource(entity['database']);
  };

  return (
    <EntityEdit
      {...props}
      onGETEntity={onEntity}
      edit={props.edit}
      entityName="Data Connector"
      entityUrl="/data-connector/">
      <Grid container spacing={2}>

        <Grid item xs={12}>            
          <TextField
            fullWidth={true}
            name="displayName"            
            id="displayName"
            value={displayName}
            onChange={x => setDisplayName(x.target.value)}
            label="Name"
          />
        </Grid>
        
        <Grid item xs={12}>            
          
          <Select
            fullWidth={true}
            name="database"
            labelId="demo-simple-select-label"
            value={dataSource}
            onChange={handleDataSource}>
            <MenuItem value={0}>
              <img src="/influxdb.png" alt="InfluxDB" height="30px" />
              <span style={{ 'paddingLeft': '10px' }}>InfluxDB</span>
            </MenuItem>
            <MenuItem value={1} style={{}}>
              <img src="/timescale.png" alt="TimescaleDB" height="30px" />
              <span style={{ 'paddingLeft': '10px' }}>TimescaleDB</span>                
            </MenuItem>
          </Select>
        </Grid>

        <Grid item xs={12}>            
          <TextField
            fullWidth={true}
            name="url"            
            id="url"
            value={url}
            onChange={x => setURL(x.target.value)}
            label="URL"
          />
        </Grid>

        <Grid item xs={12} sm={6}>                        
          <TextField
            fullWidth={true}              
            name="username"            
            id="username"
            value={username}
            onChange={x => setUserName(x.target.value)}
            label="Username"
          />
        </Grid>

        <Grid item xs={12} sm={6}>                                    
          <TextField
            fullWidth={true}
            type="password"
            name="password"            
            id="password"
            value={password}
            onChange={x => setPassword(x.target.value)}              
            label="Password"
          />
        </Grid>
      </Grid>
    </EntityEdit>
  );
}
