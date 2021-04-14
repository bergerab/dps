import React from 'react';

import LoadingOverlay from 'react-loading-overlay';
import CircularProgress from '@material-ui/core/CircularProgress';

export default class Loader extends React.Component {
  render() {
    return (
      <LoadingOverlay
        active={this.props.loading}
        text={this.props.text}
        spinner={<div><CircularProgress /></div>}
        styles={{
          overlay: (base) => ({
            ...base,
            background: 'rgba(255, 255, 255, 0.5)'
          }),
          content: (base) => ({
            ...base,
            color: '#AAAAAA',
            fontSize: '0.9em',
          }),
        }}
      >
        {this.props.children}
      </LoadingOverlay>
    );
  }
}
