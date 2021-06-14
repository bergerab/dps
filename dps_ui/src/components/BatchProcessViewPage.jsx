import React from 'react';

import {
  Redirect
} from "react-router-dom";
import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import download from 'downloadjs';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import SignalTable from './SignalTable';
import BarChart from './BarChart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';
import Loader from './Loader';

import api from '../api';

export default class BatchProcessViewPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      result: null,
      loading: true,
      loadingExport: false,
    };
  }

  async componentDidMount() {
    const id = this.props.match.params.id;
    api.get('get_batch_process_result', id).then(result => {
      this.setState({
        result,
        loading: false,
      });
    });
  }
  
  render () {
    if (this.state.loading) return (<div></div>);

    const result = this.state.result;
    const bp = result.batch_process;
    const system = bp.system;

    const startTime = moment(bp.interval.start + 'Z')
    const endTime = moment(bp.interval.end + 'Z')

    let percentComplete = '0%';
    if (result.total_samples !== 0)
      percentComplete = ((result.processed_samples / result.total_samples) * 100).toFixed(2) + '%';

    let processStats;
    if (result.status === 0) { // If process errored
      processStats = (<div>
                      <Grid item xs={12}>            
                          <TextField
                            label="Status"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={"Failed"}
                          />
                      </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Error Message"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={result.message}
                            multiline={true}
                            rows={5}
                            fullWidth={true}
                            variant="outlined"
                            style={{ color: 'red' }}
                          />
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Started At"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={moment(result.batch_process_time).format('LL LTS')}
                            style={{ width: '20em' }}/>
                        </Grid>
                      </div>)
    } else if (result.status === 1) { // If process is running
      processStats = (<div>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Status"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={"Running"}
                          />
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Started At"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={moment(result.batch_process_time).format('LL LTS')}
                            style={{ width: '20em' }}/>
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Total Samples"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={result.total_samples.toLocaleString()}
                            style={{ paddingRight: '1em' }}
                          />
                          <TextField
                            label="Samples Processed"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={result.processed_samples.toLocaleString()}/>
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Percent Complete"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={percentComplete}
                            style={{ paddingRight: '1em' }}
                          />
                        </Grid>
                      </div>)
    } else if (result.status === 2) { // If process has completed
      processStats = (<div>
                         <Grid item xs={12}>            
                           <TextField
                             label="Status"
                             InputProps={{
                               readOnly: true,
                             }}              
                             value={"Complete"}
                           />
                         </Grid>
                         <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                           <TextField
                             label="Started At"
                             InputProps={{
                               readOnly: true,
                            }}              
                            value={moment(result.batch_process_time).format('LL LTS')}
                            style={{ width: '20em' }}/>
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Samples Processed"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={result.processed_samples.toLocaleString()}/>
                        </Grid>
                       </div>)
    } else if (result.status === 3) { // If process has been queued
      processStats = (<div>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Status"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={"Queued"}
                          />
                        </Grid>
                        <Grid item xs={12} style={{ paddingTop: '1em' }}>            
                          <TextField
                            label="Started At"
                            InputProps={{
                              readOnly: true,
                            }}              
                            value={moment(result.batch_process_time).format('LL LTS')}
                            style={{ width: '20em' }}/>
                        </Grid>
                      </div>)
    }

    let kpiHeaders = ['KPI', 'Description', 'Value'];
    let kpiResults = {};
    result.results.map(x => { kpiResults[x.key] = x; });
    let kpiRows = system.kpis.filter(kpi => {
      return bp.kpis.includes(kpi.name);
    }).map(kpi => {
      return [kpi.name,
              kpi.description,
              kpiResults[kpi.name]];
                });

    // Filter out any KPIs that have no values. 
    let formattedKpiRows = kpiRows.filter(x => x[2] !== undefined ).map(row => {
      return [
        row[0],
        (<div className="system-description" dangerouslySetInnerHTML={{ __html: row[1] }}></div>),
        (<div style={{whiteSpace: 'pre'}} >{resultToString(row[2])}</div>)
      ];
    });

    let parameterIdentifiersToNames = {};
    system.parameters.map(p => { parameterIdentifiersToNames[(p.identifier === undefined || p.identifier === null || p.identifier === '') ? p.name : p.identifier] = p.name });
    let parameterMappings = bp.mappings
        .filter(x => Object.keys(parameterIdentifiersToNames).includes(x.key))
        .map(x => [parameterIdentifiersToNames[x.key], formatNumber(x.value)]);
    let signalMappings = bp.mappings
        .filter(x => !Object.keys(parameterIdentifiersToNames).includes(x.key))
        .map(x => [x.key, x.value]);

    let charts;
    charts =
      kpiRows.map(([kpiName, kpiDescription, kpiResults]) => {
	// Don't check the show_chart flag.
	      
        // if (resultDontChart(kpiResults) || kpiResults === undefined) {
        //   return (<span key={kpiName}/>);
        // }
        
        if (resultHasObject(kpiResults)) {
          const o = JSON.parse(kpiResults.object_value);
          return (<Grid item sm={12} md={6} xl={3} key={kpiName}>
                        <BarChart
                          label="THD (Percent)"
                          data={Object.values(o)}
                          labels={Object.keys(o)}
                          title={kpiName}
                        />
                      </Grid>);
        } else {
          return (<Grid item sm={12} md={6} xl={3} key={kpiName}>
   <SignalChart
     dataset={bp.dataset}
     signals={[{
       'signal': kpiName,
     }]}
     batch_process_id={result.batch_process_id}
     key={kpiName}
     title={kpiName}                      
     startTime={startTime}
     endTime={endTime}
   />
 </Grid>);
        }
      })

    if (window.location.href.endsWith('input')) {
      return (<Box
                header={`Input Signals for Batch Process "${this.state.result.batch_process.name}"`}>
                <SignalTable
                  dataset={bp.dataset}
	          startTime={startTime}
	          endTime={endTime}
                />
                <Link to={`/batch-process/${this.state.result.batch_process_id}`}>
                  <Button style={{ margin: '1em 0 0 0' }}
                          variant="contained"
                          color="primary">
                    Back
                  </Button>
                </Link>
              </Box>);
  }
  return (
    <div>
      <Box header={this.state.result.batch_process.name + " Results"}
           loading={this.state.loading}>
        <Grid container spacing={2}
              style={{maxWidth: '1500px'}}>
          <Grid item xs={12}>
            <TextField
              label="Dataset"
              InputProps={{
                readOnly: true,
              }}              
              value={bp.dataset}
            />
          </Grid>
          
          <Grid item xs={12}>
            <InputLabel>KPIs</InputLabel>
            <PrettyTable
              header={kpiHeaders}
              rows={formattedKpiRows}
            />
          </Grid>

          <Grid item xs={6}>
            <InputLabel>Signals</InputLabel>
            <PrettyTable
              header={['KPI Input', 'Signal Name']}
              rows={signalMappings}
            />
          </Grid>

          <Grid item xs={6}>
            <InputLabel>Parameters</InputLabel>          
            <PrettyTable
              header={['Name', 'Value']}
              rows={parameterMappings}
            />
          </Grid>

          <Grid item xs={12}>
            <InputLabel>Date Range</InputLabel>
            {/* Hack to get moment to parse datetime as UTC: */}
            <TextField
              label="Start Time"
              InputProps={{
                readOnly: true,
              }}              
              value={moment(bp.interval.start + 'Z').format('LL LTS')}
              style={{ marginRight: '10px', width: '20em' }}/>
            <TextField
              InputProps={{
                readOnly: true,
              }}              
              label="End Time"
              value={moment(bp.interval.end + 'Z').format('LL LTS')}
              style={{ width: '20em' }}/>              
          </Grid>

          <Grid item xs={12}>
            <CSVLink
              data={[kpiHeaders].concat(kpiRows.map(x => [x[0], x[1],
                                                          x[2] === undefined ? '' :
                                                          (x[2].value === undefined ? x[2].object_value : x[2].value)]))}
              target="_blank"
              style={{ textDecoration: 'none' }}
              filename={this.state.result.batch_process.name + " Results.csv"}
            >
              <Button style={{ margin: '1em 0 0 0' }}
                      variant="contained"
                      color="primary">
                Download Summary
              </Button>
            </CSVLink>
            
            <Link style={{ paddingLeft: '1em', }} to={`${this.state.result.batch_process_id}/input`}>
              <Button style={{ margin: '1em 0 0 0' }}
                      variant="contained"
                      color="primary">
                View Input Signals
              </Button>
            </Link>
          </Grid>
        </Grid>
      </Box>

      <Loader
        text="Exporting data..."
        loading={this.state.loadingExport}>
        
        <Box
          header="KPI Signals">
          <Grid container spacing={2}>
            {charts}
            <Grid item xs={12}>
              <Button style={{ margin: '1em 0 0 0' }}
                      variant="contained"
                      color="primary"
                      onClick={() => {
                        this.setState({ loadingExport: true });
                        api.rawPost('export_dataset', {
                          'dataset': 'batch_process' + result.batch_process_id,
                          /* Only export signals that are line charts */
                          'signals': kpiRows.filter(x => !resultHasObject(x[2])).map(x => x[0]),                              
                          'start':   bp.interval.start,
                          'end':     bp.interval.end,                              
                        }).then(resp => {
                          resp.blob().then(blob => {
                            download(blob, bp.name + '.csv', 'application/octet-stream');
                            this.setState({ loadingExport: false });
                          });
                        });
                      }}>
                Export
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Loader>
      <Box
        header="Stats">
        <Grid item xs={12}>
          {processStats}
        </Grid>
      </Box>
    </div>
  );
  }
}

 function removeTags(str) {
      if ((str===null) || (str===''))
      return false;
      else
      str = str.toString();
      return str.replace( /(<([^>]+)>)/ig, '');
 }

function formatNumber(s) {
  const n = +s
  if (Number.isNaN(n)) return s;
  return n.toLocaleString();
}

function formatObjectValue(s) {
  const o = JSON.parse(s);
  const lines = [];
  for (const key of Object.keys(o)) {
    lines.push(key + ': ' + (o[key] === null ? 'No Data' : formatNumber(o[key])));
  }
  return lines.join('\n');
}

function resultToString(x) {
  if (x === undefined) return '';  
  return resultHasObject(x) ? formatObjectValue(x.object_value) : formatNumber(x.value);
}

function resultHasObject(x) {
  if (x === undefined) return false;
  return x.value === undefined;
}

function resultDontChart(x) {
  if (x === undefined) return false;
  return x.show_chart !== true;
}
