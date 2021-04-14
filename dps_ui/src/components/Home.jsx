import React, { useState } from 'react';

import Box from './Box';

import Grid from '@material-ui/core/Grid';
import ActionsTable from './ActionsTable';
import ActionsStepper from './ActionsStepper';

export default function Home(props) {
  return (
    <Grid container>
      <Grid item xs={12}>
        <Box header="System Setup">            
          <ActionsStepper />
        </Box>
      </Grid>
    </Grid>
  );
}
