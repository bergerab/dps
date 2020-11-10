import React from 'react';

import Box from './Box';

import Grid from '@material-ui/core/Grid';
import ActionsTable from './ActionsTable';
import ActionsStepper from './ActionsStepper';
import SignalTable from './SignalTable';

export default function Home(props) {
  return (
    <Grid container>
      <Grid item xs={12}>
        <Box header="System Setup">            
          <ActionsStepper />              
        </Box>
      </Grid>
      
      <Grid item xs={12}>
        <Box header="Signals">
          <SignalTable />
        </Box>                
      </Grid>
    </Grid>
  );
}
