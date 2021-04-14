import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

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

  return (
    <FormControl {...props} className={classes.formControl}>
      <InputLabel id="demo-simple-select-label">{props.header}</InputLabel>
      <Select
	labelId="demo-simple-select-label"
	id="demo-simple-select"
	{...props}
      >
	{items.map(x => {
	  return (<MenuItem key={x['id']} value={x['id']}>{x['displayName']}</MenuItem>);
	})}
      </Select>
    </FormControl>
  );
}
