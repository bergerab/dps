import React from 'react';

import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/idea.css';
import 'codemirror/addon/display/autorefresh.js';
import 'codemirror/mode/python/python.js';
import { Controlled as CodeMirror } from "react-codemirror2";

export default class KPIEditor extends React.Component {
  render() {
    let option = {
      mode: 'python',
      theme: 'idea',
      lineNumbers: true,
      autoRefresh: true,
    };
    
    const styles = { fontSize: '12pt' };

    Object.assign(styles, this.props.style || {});
    Object.assign(option, this.props.options || {});

    return (
      <div>
	<CodeMirror
	  {...this.props}
	  style={styles}
	  options={option}
        />
      </div>
    );
  }
}
