import React from 'react';

import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import { Alert, AlertTitle } from '@material-ui/lab';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Input from '@material-ui/core/Input';
import LinearProgress from '@material-ui/core/LinearProgress';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import {
  DateTimePicker,
} from '@material-ui/pickers';

import DatasetSelect from './DatasetSelect';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import SignalTable from './SignalTable';
import BarChart from './BarChart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';

import DatasetTable from './DatasetTable';

import api from '../api';

export default class DatasetUploadPage extends React.Component {
  
  state = {
    isLoading: false,
    
    // Initially, no file is selected
    selectedFile: null,

    usesRelativeTime: false,
    startDate: null,
    dataset: null,

    error: null,
  };
  
  // On file select (from the pop up)
  onFileChange = event => {
    
    // Update the state
    this.setState({ selectedFile: event.target.files[0] });
    
  };
  
  // On file upload (click the upload button)
  onFileUpload = () => {
    // Create an object of formData
    const formData = new FormData();
    
    // Update the formData object
    formData.append(
      "file",
      this.state.selectedFile,
      this.state.selectedFile.name
    );

    formData.append(
      "dataset",
      this.state.dataset,
    );

    formData.append(
      "start_time",
      this.state.startDate,
    );

    formData.append(
      "uses_relative_time",
      this.state.usesRelativeTime,
    );

    this.setState({ isLoading: true });
    api.postFormData("upload", formData).then(() => {
      this.setState({ isLoading: false });
      window.history.back();                              
    }).catch(e => {
      if (typeof e.then === 'function') {
        e.then(error => {
          if (!error || JSON.stringify(error) === '{}') {
            error = 'An error occurred during the upload. Ensure your data complies with our CSV file format above and try again.';
          }
          this.setState({
            isLoading: false,
            error: error,
          });
        });
      } else {
        this.setState({
          isLoading: false,
          error: e.toString(),
        });
      }
    });
  };

  error = () => {
    if (this.state.error !== null) {
      return (<div style={{ marginBottom: '0.5em' }}>
                <Alert severity="error">
                  <AlertTitle>Error</AlertTitle>
                  {this.state.error.toString()}                                    
                </Alert>
              </div>);
    }
    return (<span></span>);
  }

  loader = () => {
    if (this.state.isLoading) {
      return (
        <div>
          <LinearProgress />
          Please wait while your file is being uploaded.
        </div>
      );
    }
    return (<span></span>);
  }
  
  // File content to be displayed after
  // file upload is complete
  fileData = () => {
    
    if (this.state.selectedFile) {
      
      return (
        <div>
          <p>File Name: {this.state.selectedFile.name}</p>
          <p>File Type: {this.state.selectedFile.type}</p>
          <p>
            Last Modified:{" "}
            {this.state.selectedFile.lastModifiedDate.toDateString()}
          </p>
        </div>
      );
    } else {
      return (
        <div>
        </div>
      );
    }
  };

  startTimeControl = () => {
    if (this.state.usesRelativeTime) {
      return (<Grid item xs={12}>
                            <InputLabel>Start Time</InputLabel>
                            <DateTimePicker value={this.state.startDate}
                                            onChange={date => this.setState({ startDate: date })
			                             }
                                            label="Start Time"
                                            style={{marginRight: '20px'}}
                            />
                          </Grid>);
    } else {
      return (<span></span>);
    }
  };

  render() {
    
    return (
      <div>
        {this.error()}
        <Box header={"Upload a File"}>
          <p>
            This form allows the upload of samples into a dataset via the CSV format. We impose our own rules in addition to the CSV format to ensure no ambiguity in the upload. The format of the CSV file is as follows:
          </p>

          <p>
            Your CSV must have a column named "Time" (doesn't matter which column index it is, it simply has to exist). Each value in the "Time" column must either contain an ISO-8601 formatted time which is the absolute time that the row was sampled at or an offset time in seconds. As an example of an aboslute ISO formatted time: 2020-06-20T00:55:31.820Z is a valid time that we accept. An example of an offset is: 0.0 and 0.000001 (meaning 0 seconds from the beginning of the sample collection and 0.000001 seconds from the beginning of the sample collection). If you use relative time, you must select a start time for the data by selecting the "Use Relative Time" checkbox.
          </p>

          <p>
            Each other column (other than "Time") must be the name of a signal you are sending data for. No whitespace characters are allowed in the signal names. For example, "Voltage Phase A" is invalid. But, "Va" and "VoltagePhaseA" is OK. All of the data in these columns must be formatted as a decimal or integer (will be parsed as a double percision floating point) value. As an example 123 or 1.23 or -1.23  are all valid.
          </p>

          <p>
            All rows must have every column value set (you cannot skip any values).
          </p>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <InputLabel>Select a file *</InputLabel>                         
              <input type="file" id="file-upload" hidden onChange={this.onFileChange} />
              <label htmlFor="file-upload">
                {this.fileData()}              
                <Button
                  variant="contained"                
                  component="span"
                  color="primary">
                  Select 
                </Button>
              </label>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Checkbox color="primary"
                                checked={this.state.usesRelativeTime}
                                onChange={() => this.setState({ usesRelativeTime: !this.state.usesRelativeTime }) } />}
                label="Uses Relative Time?"
              />
              <div style={{color: 'gray'}}>If using relative time, the units on the "Time" column must be in seconds.</div>
            </Grid>

            {this.startTimeControl()}

            <Grid item xs={12}>
              <InputLabel>Dataset *</InputLabel>             
              <DatasetSelect
                limit={20}
                value={{ value: this.state.dataset, label: this.state.dataset }}
                creatable={true}
                onChange={x => {
                  this.setState({ dataset: x.value });
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Button variant="contained"
                      color="primary"
                      onClick={this.onFileUpload}
                      disabled={this.state.isLoading}>
                Upload
              </Button>
            </Grid>
            <Grid item xs={12}>
              {this.loader()}
            </Grid>
          </Grid>
        </Box>

      </div>
    );
  }
}
