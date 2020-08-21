import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Chip from '@material-ui/core/Chip';

import { list } from '../api';

const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
}));

export default function (props) {
  const classes = useStyles();
  const [items, setItems] = React.useState([]);

  useEffect(() => {
    list(props.entityUrl).then(r => r.json()).then(jo => {
      setItems(jo);
    });
  }, []);

  function get(id) {
    for (const o of items) {
      if (o.id === id) {
	return o;
      }
    }
    return null;
  }

  return (
    <FormControl {...props} className={classes.formControl}>
      <InputLabel id="demo-simple-select-label">{props.header}</InputLabel>
      <Select
	labelId="demo-simple-select-label"
	id="demo-simple-select"
	multiple
	renderValue={(selected) => (
	  <div className={classes.chips}>
	    {selected.map((value) => (
	      <Chip
		key={value}
		label={get(value)['displayName']}
		className={classes.chip}
	      />
	    ))}
	  </div>
	)}
	{...props}
      >
	{items.map(x => {
	  return (<MenuItem
		    key={x['id']}
		    value={x['id']}
		  >
		    {x['displayName']}
		  </MenuItem>);
	})}
      </Select>
    </FormControl>
  );
}
