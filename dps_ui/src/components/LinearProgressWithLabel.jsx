import React from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';

export default function LinearProgressWithLabel(props) {
  const label = props.label || `${Math.round(
          props.value,
        )}%`;

  let progress = null;
  if (props.label) progress = (<LinearProgress {...props} />);
  else  progress = (<LinearProgress variant="determinate" {...props} />);

  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        {progress}
      </Box>
      <Box minWidth={35}>
        <Typography variant="body2" color="textSecondary">{
          label
        }</Typography>
      </Box>
    </Box>
  );
}

LinearProgressWithLabel.propTypes = {
  /**
   * The value of the progress indicator for the determinate and buffer variants.
   * Value between 0 and 100.
   */
  value: PropTypes.number.isRequired,
};
