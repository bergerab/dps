export const API_PREFIX = 'http://localhost:5000/api';

export function list(entityUrl) {
        return fetch(API_PREFIX + entityUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
	});
}

export function get(entityUrl, id) {
        return fetch(API_PREFIX + entityUrl + id, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
	});
}

export function del(entityUrl, id) {
        return fetch(API_PREFIX + entityUrl + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
	});
}
