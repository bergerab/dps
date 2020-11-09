import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import { list } from '../api';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  backButton: {
    marginRight: theme.spacing(1),
  },
  instructions: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
}));

function getSteps() {
  return [
    'Add a System',    
    'Send data',
    'Run a Batch Process',
  ];
}

export default function HorizontalLabelPositionBelowStepper() {
  const classes = useStyles();
  const [activeStep, setActiveStep] = React.useState(0);
  const steps = getSteps();

  useEffect(() => {
    list('/data-connector/').then(r => r.json()).then(jo => {
      if (jo.length > 0) {
	setActiveStep(1);
	list('/system/').then(r => r.json()).then(jo => {
	  if (jo.length > 0) {
	    setActiveStep(2);
	    list('/data-set/').then(r => r.json()).then(jo => {
	      if (jo.length > 0) {
		setActiveStep(3);
	      }
	    });
	  }
	});
      }
    });
  }, []);

  const handleReset = () => {
    setActiveStep(0);
  };

  return (
    <div className={classes.root}>
      <Stepper activeStep={activeStep} alternativeLabel>
	{steps.map((label) => (
	  <Step key={label}>
	    <StepLabel>{label}</StepLabel>
	  </Step>
	))}
      </Stepper>
      <div>
	{activeStep === steps.length ? (
	  <div>
	    <Typography className={classes.instructions}>All steps completed</Typography>
	    <Button onClick={handleReset}>Reset</Button>
	  </div>
	) : (
	  <div>
	    <Typography className={classes.instructions}>
	      {
	      }
	    </Typography>
	  </div>
	)}
      </div>
    </div>
  );
}
