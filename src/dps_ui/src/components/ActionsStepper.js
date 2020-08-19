
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
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
    return ['Add a Database Connection',
            'Add a System',
            'Add a Dataset',
            'Run a Batch Process'            
           ];
}

function getStepContent(stepIndex) {
    const text = 'Do Step';
    const linkStyle = { textDecoration: 'none', color: 'white' };
  switch (stepIndex) {
    case 0:
      return <Link to="/data-connector" style={linkStyle}>{text}</Link>;
    case 1:
      return <Link to="/system" style={linkStyle}>{text}</Link>;
    case 2:
      return <Link to="/data-set" style={linkStyle}>{text}</Link>;
    default:
      return 'Unknown stepIndex';
  }
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

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

    const button = activeStep <= 2 ? (<Button variant="contained" color="primary">
                      {getStepContent(activeStep)}
                    </Button>
                                     ) : (<span></span>);

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
