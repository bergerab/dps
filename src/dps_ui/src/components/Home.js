import React from 'react';

import Box from './Box';

import ActionsTable from './ActionsTable';
import ActionsStepper from './ActionsStepper';

export default function Home(props) {
  return (
    <div>
      <Box header="System Setup">            
        <ActionsStepper />              
      </Box>                

      <Box header="System Log">            
	<ActionsTable />                        
      </Box>                
    </div>
  );
}
