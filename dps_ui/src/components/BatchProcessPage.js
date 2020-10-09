import React from 'react';

import TextField from '@material-ui/core/TextField';
import CheckBox from '@material-ui/core/CheckBox';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';

import Box from './Box';
import PrettyTable from './PrettyTable';
import EntitySelect from './EntitySelect';

export default class BatchProcessPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      displayName: '',
      signals: [],
      constants: [],
      code: '',

      test: '[]',
    };
  }

  render () {
    const props = this.props;

    const signalsInput = (<input type="hidden" name="signals" value={this.state.signals} />);
    const constantsInput = (<input type="hidden" name="constants" value={this.state.constants} />);
    const codeInput = (<input type="hidden" name="code" value={this.state.code} />);

    const descriptionMock = 'Collect DC input and AC output power over varius power levels (10%, 20%, 30%, 50%, 75% and 100% of rated output AC power)';

    return (
      <Box
        header="Batch Analysis"
      >
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <PrettyTable
              header={['', 'Computation', 'Description', 'Last Run', 'Result']}
              rows={[
                [<CheckBox color="primary" />, 'Efficiency', descriptionMock, '8/20/2020', '99%'],
                [<CheckBox color="primary" />, 'Power', descriptionMock, '8/21/2020', '10K'],
                [<CheckBox color="primary" />, 'THD Voltage', descriptionMock, '8/20/2020', '2%'],                                
              ]}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Warning Log"
              multiline={true}
              fullWidth={true}
              rows={10}
              variant="outlined"
              disabled={true}
              value={`8/20/2020 13:23:93.4234: THD Va above 10%
8/21/2020 11:43:32.4353: Efficiency below 20%
`}
            >
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Button style={{'marginRight': '10px'}} variant="contained" color="primary">Run</Button>
            <Button variant="contained" color="primary">Export</Button>            
	  </Grid>
        </Grid>
      </Box>
    );
  }
}
