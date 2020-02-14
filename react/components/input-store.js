import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSocket } from './socket.js';
import { fetchGet } from './fetch-wrapper.js';

const InputStoreContext = createContext([]);

const InputStore = ({children}) => {
    const socket = useSocket();
    const [inputs, setInputs] = useState([]);

    const created = (data) => setInputs(inputs => inputs.concat(data));
    const updated = (data) =>
        setInputs(inputs => inputs.map(input => input.id == data.id ? Object.assign(input, data) : input));
    const remove = (data) => setInputs(inputs => inputs.filter(x => x.id != data.id));

    useEffect(() => {
        socket.on('input_create', created);
        socket.on('input_update', updated);
        socket.on('input_remove', remove);
        return () => {
            socket.off('input_create', created);
            socket.off('input_update', updated);
            socket.off('input_remove', remove);
        };
    }, [socket]);

    // Get the initial state by requesting it
    useEffect(() => {
        fetchGet('/audio/input')
            .then(inputs => setInputs(existing => existing.concat(inputs)))
            .catch(e => console.error(e));
    }, []);

    return (
        <InputStoreContext.Provider value={inputs}>
            {children}
        </InputStoreContext.Provider>
    );
};

const useInputs = () => {
    return useContext(InputStoreContext);
};

export { InputStore, useInputs };