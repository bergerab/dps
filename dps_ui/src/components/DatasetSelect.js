import React, { Component } from 'react';
import { withStyles } from '@material-ui/core/styles'; 
import api from '../api';

import AsyncSelect from 'react-select/async';
import AsyncSelectCreatable from 'react-select/async-creatable';
import FormHelperText from '@material-ui/core/FormHelperText';

const customStyles = {
  menu: (provided, state) => ({
    ...provided,
    width: state.selectProps.width,
    borderBottom: '1px dotted pink',
    color: state.selectProps.menuColor,
    padding: 0,
  }),
}

class DatasetSelect extends Component {
  render() {
    const styles = Object.assign({}, customStyles);
    if (this.props.error) {
      styles.control = (base, state) => ({
        ...base,
        borderColor: 'red',
        // You can also use state.isFocused to conditionally style based on the focus state
      })
    }
    let Select = this.props.creatable ? AsyncSelectCreatable : AsyncSelect;
    return (
      <div>

        <Select
          styles={styles}
          onChange={this.props.onChange}
          value={this.props.value}        
          cacheOptions
          defaultOptions
          loadOptions={query => {
            return api.post('get_dataset_names', {
              query: query,
              limit: this.props.limit,
              offset: 0,
            }).then(x => x.values.map(x => ({ label: x, value: x })));
          }} />
        {this.props.error ? (<FormHelperText style={{ color: 'red' }}>{this.props.helperText}</FormHelperText>) : null}
      </div>
    );
  }
}

export default withStyles({}, { withTheme: true })(DatasetSelect);
