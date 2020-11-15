import React from 'react';

import moment from 'moment';
import {CSVLink, CSVDownload} from 'react-csv';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';

import api from '../api';

export default class BatchProcessViewPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      result: null,
      loading: true,
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
    result.results.map(x => { kpiResults[x.key] = x.value });
    let kpiRows = system.kpis.filter(kpi => {
      return bp.kpis.includes(kpi.name);
    }).map(kpi => {
      return [kpi.name,
              (<div className="system-description" dangerouslySetInnerHTML={{ __html: kpi.description }}></div>),
              formatNumber(kpiResults[kpi.name])];
    });

    let parameterIdentifiersToNames = {};
    system.parameters.map(p => { parameterIdentifiersToNames[p.identifier === undefined || p.identifier === null ? p.name : p.identifier] = p.name });
      let parameterMappings = bp.mappings
          .filter(x => Object.keys(parameterIdentifiersToNames).includes(x.key))
          .map(x => [parameterIdentifiersToNames[x.key], formatNumber(x.value)]);
    let signalMappings = bp.mappings
        .filter(x => !Object.keys(parameterIdentifiersToNames).includes(x.key))
        .map(x => [x.key, x.value]);

    let charts;
    charts =
      kpiRows.map(x => x[0]).map(kpiName =>
                                 (<Grid item xs={6} key={kpiName}>
                                    <SignalChart
                                      signals={[{
                                        'signal': kpiName,
                                      }]}
                                      batch_process_id={result.batch_process_id}
                                      key={kpiName}
                                      startTime={moment(bp.interval.start + 'Z')}
                                      endTime={moment(bp.interval.end + 'Z')}
                                    />
                                  </Grid>))
    return (
      <div>
        <Box header={this.state.result.batch_process.name + " Results"}
             loading={this.state.loading}>
          <Grid container spacing={2}
                style={{maxWidth: '1500px'}}>
            <Grid item xs={12}>
              <InputLabel>KPIs</InputLabel>
              <PrettyTable
                header={kpiHeaders}
                rows={kpiRows}
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
                data={[kpiHeaders].concat(kpiRows.map(x => x.map(x => typeof(x) === 'object' ? removeTags(x.props.dangerouslySetInnerHTML.__html) : x )))}
                target="_blank"
                style={{ textDecoration: 'none' }}
                filename={this.state.result.batch_process.name + " Results.csv"}
              >
                <Button style={{ margin: '1em 0 0 0' }}
                        variant="contained"
                        color="primary">
                  Export
                </Button>
              </CSVLink>                      
            </Grid>

          </Grid>
        </Box>

            <Box
              header="Output">
              <Grid container>
                {charts}
              </Grid>
            </Box>
            
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
