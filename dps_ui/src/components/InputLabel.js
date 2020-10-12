import React from 'react';

export default class InputLabel extends React.Component {
  render() {
    return (
      <h3 style={{ marginTop: 0, color: 'gray' }}>{this.props.children}</h3>
    );
  }
}
