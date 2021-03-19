require('dotenv').config();
const HOST = process.env.DPS_HOST || 'localhost';

export const API_PREFIX = `http://${HOST}:8000/api/v1/`;

function handle(r) {
  if (r.status === 403) {
    window.location = '/login';
  }
  return r;
}

export function list(entityUrl) {
  return fetch(API_PREFIX + entityUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
  }).then(r => {
    return handle(r).json().then(data => {
      // The response should just have the entity name as one key,
      // and the value being the list of values.
      const entityName = Object.keys(data)[0];
      return data[entityName];
    })
  });
}

export function put(entityUrl, id, entity) {
  return fetch(API_PREFIX + entityUrl + '/' + id, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),
    },
    body: JSON.stringify(entity),
  }).then(r => {
    const jo = handle(r).json();
    if (r.status >= 400 || r.status < 200) {
      throw jo;
    } else {
      return jo;
    }
  });
}

export function post(entityUrl, entity) {
  return fetch(API_PREFIX + entityUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),      
    },
    body: JSON.stringify(entity),
  }).then(r => {
    const jo = handle(r).json();
    if (r.status >= 400 || r.status < 200) {
      throw jo;
    } else {
      return jo;
    }
  });
}

export function rawPost(entityUrl, entity) {
  return fetch(API_PREFIX + entityUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),      
    },
    body: JSON.stringify(entity),
  });
}

export function get(entityUrl, id) {
  let postfix;
  if (id === undefined) postfix = '';
  else postfix = '/' + id;
  
  return fetch(API_PREFIX + entityUrl + postfix, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
  }).then(r => {
    handle(r);
    if (r.status >= 400) throw r;
    return r.json();
  });
}

export function del(entityUrl, id) {
  return fetch(API_PREFIX + entityUrl + '/' + id, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
  });
}

export function delete_batch_process(id) {
  return fetch(API_PREFIX + 'delete_batch_process' + '/' + id, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
  });
}

export function delete_dataset(name) {
  return fetch(API_PREFIX + 'delete_dataset', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),
    },
    body: JSON.stringify({ dataset: name }),    
  });
}

export function add_dataset(name) {
  return fetch(API_PREFIX + 'add_dataset', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
    body: JSON.stringify({ name: name }),    
  });
}

export function get_required_mappings(system, kpi_names) {
  return fetch(API_PREFIX + 'get_required_mappings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
    body: JSON.stringify({
      system: system,
      kpi_names: kpi_names,
    }),
  }).then(r => handle(r).json());
}

export function login(username, password) {
  return fetch(API_PREFIX + 'login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': makeAuth(),            
    },
    body: JSON.stringify({ username: username,
			   password: password }),    
  });
}

export function isLoggedIn() {
  const token = localStorage.getItem('TOKEN');
  const expiration = new Date(Date.parse(getTokenExpires()));
  const expired = token === undefined || token === null || token === '' || new Date() > expiration;
  return !expired;
}

function getToken() {
  return localStorage.getItem('TOKEN');
}

function removeToken() {
  return localStorage.removeItem('TOKEN');
}

export function setToken(token) {
  localStorage.setItem('TOKEN', token);
}

export function setTokenExpires(token) {
  localStorage.setItem('TOKEN_EXPIRATION', token);
}

export function getTokenExpires(token) {
  return localStorage.getItem('TOKEN_EXPIRATION');
}

export function setIsAdmin(token) {
  localStorage.setItem('TOKEN_IS_ADMIN', token);
}

export function getIsAdmin(token) {
  return localStorage.getItem('TOKEN_IS_ADMIN') === 'true';
}

export function setUsername(token) {
  localStorage.setItem('TOKEN_USERNAME', token);
}

export function getUsername(token) {
  return localStorage.getItem('TOKEN_USERNAME');
}

function makeAuth() {
  return `Bearer ${getToken()}`;
}

export default {
  get, list,
  post, put,
  rawPost,
  delete_batch_process,
  del,
  get_required_mappings,
  delete_dataset,
  add_dataset,
  login,
  isLoggedIn,
  setToken,
  removeToken,
  setTokenExpires,
  setIsAdmin,
  getIsAdmin,
  setUsername,
  getUsername,
};
