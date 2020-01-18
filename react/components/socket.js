import React, { createContext, useContext } from 'react';
import * as io from 'socket.io-client';

const SocketContext = createContext();

const socket = io();

const Socket = ({children}) => (
    <SocketContext.Provider value={socket}>
        {children}
    </SocketContext.Provider>
);

const useSocket = () => useContext(SocketContext);

export { Socket, useSocket };