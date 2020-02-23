import React from 'react';

const handleErrors = response => {
    if (!response.ok) {
        throw response;
    }
    return response;
};

const fetchWrap = (url, data, method) => {
    let headers = {'method': method};
    if (data !== undefined) {
        headers['headers'] = {'Content-Type': 'application/json'};
        headers['body'] = JSON.stringify(data);
    }
    return fetch(url, headers)
        .then(handleErrors)
        .then(response => response.json());
};

const fetchPut = (url, data) => fetchWrap(url, data, 'PUT');
const fetchPost = (url, data) => fetchWrap(url, data, 'POST');
const fetchDelete = (url, data) => fetchWrap(url, data, 'DELETE');

const fetchGet = (url, init) => fetch(url, init)
    .then(handleErrors)
    .then(response => response.json());

export { fetchPut, fetchPost, fetchGet, fetchDelete };
