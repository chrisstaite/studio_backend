import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSocket } from './socket.js';

const OutputStoreContext = createContext([]);

const OutputStore = ({children}) => {
    const socket = useSocket();
    const [outputs, setOutputs] = useState([]);

    const created = (data) => setOutputs(outputs => outputs.concat(data));
    const updated = (data) =>
        setOutputs(outputs => outputs.map(output => output.id == data.id ? Object.assign(output, data) : output));
    const remove = (data) => setOutputs(outputs => outputs.filter(x => x.id != data.id));

    useEffect(() => {
        socket.on('output_create', created);
        socket.on('output_update', updated);
        socket.on('output_remove', remove);
        return () => {
            socket.off('output_create', created);
            socket.off('output_update', updated);
            socket.off('output_remove', remove);
        };
    }, [socket]);

    // Get the initial state by requesting it
    useEffect(() => {
        fetch('/audio/output')
            .then(response => response.json())
            .then(outputs => setOutputs(outputs))
            .catch(e => console.error(e));
    }, []);

    return (
        <OutputStoreContext.Provider value={outputs}>
            {children}
        </OutputStoreContext.Provider>
    );
};

const useOutputs = () => {
    return useContext(OutputStoreContext);
};

export { OutputStore, useOutputs };