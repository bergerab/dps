import React from 'react';

import Button from '@material-ui/core/Button';
import LinearProgress from '@material-ui/core/LinearProgress';
import MaterialTable from 'material-table';
import CircularProgress from '@material-ui/core/CircularProgress';

import LoadingOverlay from 'react-loading-overlay';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import api from '../api';

import ConfirmationDialog from './ConfirmationDialog';

import moment from 'moment';

import { forwardRef } from 'react';

import AddBox from '@material-ui/icons/AddBox';
import ArrowDownward from '@material-ui/icons/ArrowDownward';
import Refresh from '@material-ui/icons/Refresh';
import Check from '@material-ui/icons/Check';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Clear from '@material-ui/icons/Clear';
import DeleteOutline from '@material-ui/icons/DeleteOutline';
import Edit from '@material-ui/icons/Edit';
import FilterList from '@material-ui/icons/FilterList';
import FirstPage from '@material-ui/icons/FirstPage';
import LastPage from '@material-ui/icons/LastPage';
import Remove from '@material-ui/icons/Remove';
import SaveAlt from '@material-ui/icons/SaveAlt';
import Search from '@material-ui/icons/Search';
import ViewColumn from '@material-ui/icons/ViewColumn';
import EditIcon from '@material-ui/icons/Edit';

const tableIcons = {
  Add: forwardRef((props, ref) => <AddBox {...props} ref={ref} />),
  Check: forwardRef((props, ref) => <Check {...props} ref={ref} />),
  Clear: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
  Refresh: forwardRef((props, ref) => <Refresh {...props} ref={ref} />),  
  Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref} />),
  DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
  Edit: forwardRef((props, ref) => <Edit {...props} ref={ref} />),
  Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref} />),
  Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref} />),
  FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref} />),
  LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref} />),
  NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
  PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref} />),
  ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
  Search: forwardRef((props, ref) => <Search {...props} ref={ref} />),
  SortArrow: forwardRef((props, ref) => <ArrowDownward {...props} ref={ref} />),
  ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref} />),
  ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref} />)
};

export default class EntityTable extends React.Component {
  constructor(props) {
    super(props);
    this.tableRef = React.createRef();
  }

  render () {
    const columns = [];
    for (const x of this.props.columns) {
      columns.push({
        title: x[0],
        render: x[1],
      });
    }
    
    return (
      <MaterialTable
        icons={tableIcons}
        title=""
        tableRef={this.tableRef}
        options={{
          search: true,
          sorting: true,
          exportButton: false,
          pageSize: 5,
        }}          
        actions={[
          {
            icon: Refresh,
            tooltip: 'Refresh Data',
            isFreeAction: true,
            onClick: () => this.tableRef.current && this.tableRef.current.onQueryChange(),
          }
        ]}          
        columns={[
          ...columns,
          { title: '',
            field: '',
            render: data => {
              return (
                <div style={{ width: '100%', textAlign: 'right' }}>
                  <span style={{ display: 'inline-flex' }}>
                    {this.props.editDisabled ? null : 
                     (<Link to={"/admin/" + this.props.entityName + "/edit/" + encodeURI(data[this.props.idName])}>
                        <Button variant="outlined"
                                color="primary"
                                style={{ marginRight: '10px' }}>
                          <EditIcon/>
                        </Button>
                      </Link>)}

                    <ConfirmationDialog
	        /* header={`Delete "${data[this.props.entityNameField || 'name']}"?`} */
	              header={<span>Delete "<span style={{ wordBreak: 'break-all' }}>{data[this.props.entityNameField || 'name']}"</span>?</span>}                      
                      deleteObj={() => {
                        api.del(this.props.entityName, data[this.props.idName]).then(() => {
                          this.tableRef.current.onQueryChange();
                        });
                      }}
                    >
	              Are you sure you want to delete this {this.props.entityDisplayName}? This action is irreversible.
                    </ConfirmationDialog>

                  </span>
                </div>                
              );
                return data.dataset;
            },
            sorting: false
          },
        ]}
        data={query =>
              new Promise((resolve, reject) => {
                api.post(this.props.entityName + '/table', { 'page_size':       query.pageSize,
                                                             'page_number':     query.page,
                                                             'search':          query.search,
                                                             'order_direction': query.orderDirection,
                                                             'order_by':        (this.props.orderBy || 'name')
                                                           })
                  .then(result => {
                    resolve({
                      data: result.data,
                      page: result.page,
                      totalCount: result.total,
                    })
                  })
              })
             }
      />
    );
  }
}
