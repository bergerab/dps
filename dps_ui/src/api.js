export const API_PREFIX = 'http://127.0.0.1:8000/api/v1/';

export function list(entityUrl) {
  return fetch(API_PREFIX + entityUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  }).then(r => {
    return r.json().then(data => {
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
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(entity),
  }).then(r => {
    const jo = r.json();
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
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(entity),
  }).then(r => {
    const jo = r.json();
    if (r.status >= 400 || r.status < 200) {
      throw jo;
    } else {
      return jo;
    }
  });
}

export function get(entityUrl, id) {
  return fetch(API_PREFIX + entityUrl + '/' + id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  }).then(r => r.json());
}

export function del(entityUrl, id) {
  return fetch(API_PREFIX + entityUrl + '/' + id, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
  });
}

export function get_required_mappings(system, kpi_names) {
  return fetch(API_PREFIX + 'get_required_mappings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      system: system,
      kpi_names: kpi_names,
    }),
  }).then(r => r.json());
}

export default {
  get, list,
  post, put,
};
