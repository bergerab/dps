// import React from 'react';
// import TextField from '@material-ui/core/TextField';
// import Autocomplete from '@material-ui/lab/Autocomplete';
// import CircularProgress from '@material-ui/core/CircularProgress';
// import debounce from "lodash/debounce";

// import api from '../api';

// export default function SignalSelect(props) {
//   const [open, setOpen] = React.useState(false);
//   const [options, setOptions] = React.useState([]);
//   const [text, setText] = React.useState('');
//   const setTextDebounced = debounce(setText, 500);
//   const loading = open && options.length === 0;

//   React.useEffect(() => {
//     let active = true;

//     if (!loading) {
//       return undefined;
//     }

//     (async () => {
//       console.log(text)      
//       const response = await api.post('get_signal_names', {
//         dataset: props.dataset,
//         query: text,
//         limit: props.limit,
//         offset: 0,
//       });

//       console.log(response.values, text)
      
//       if (active) {
//         setOptions(response.values);
//       }
//     })();

//     return () => {
//       active = false;
//     };
//   }, [loading]);

//   React.useEffect(() => {
//     if (!open) {
//       setOptions([]);
//     }
//   }, [open]);

//   return (
//     <Autocomplete
//       open={open}
//       onOpen={() => {
//         setOpen(true);
//       }}
//       onClose={() => {
//         setOpen(false);
//       }}
//       getOptionSelected={(option, value) => option === value}
//       getOptionLabel={(option) => option}
//       options={options}
//       loading={loading}
//       renderInput={(params) => (
//         <TextField
//           {...params}
//           label="Signal"
//           variant="outlined"
//           value={text}
//           onKeyUp={e => setTextDebounced(e.target.value)}
//           InputProps={{
//             ...params.InputProps,
//             endAdornment: (
//               <React.Fragment>
//                 {loading ? <CircularProgress color="inherit" size={20} /> : null}
//                 {params.InputProps.endAdornment}
//               </React.Fragment>
//             ),
//           }}
//         />
//       )}
//     />
//   );
// }

import React, { Component } from 'react';
import { withStyles } from '@material-ui/core/styles'; 
import api from '../api';

import AsyncSelect from 'react-select/async';


const customStyles = {
  menu: (provided, state) => ({
    ...provided,
    width: state.selectProps.width,
    borderBottom: '1px dotted pink',
    color: state.selectProps.menuColor,
    padding: 20,
  }),  
}

class SignalSelect extends Component {
  render() {
    return (
      <AsyncSelect
        styles={customStyles}        
        cacheOptions
        defaultOptions
        loadOptions={query => {
          return api.post('get_signal_names', {
            dataset: this.props.dataset,
            query: query,
            limit: this.props.limit,
            offset: 0,
          }).then(x => x.values.map(x => ({ label: x, value: x })));
        }} />
    );
  }
}

export default withStyles({}, { withTheme: true })(SignalSelect);
