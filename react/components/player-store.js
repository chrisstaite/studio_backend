import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSocket } from './socket.js';
import { fetchGet } from './fetch-wrapper.js';

const PlayerStoreContext = createContext([]);

const PlayerStore = ({children}) => {
    const socket = useSocket();
    const [players, setPlayers] = useState([]);

    const created = (data) => setPlayers(players => players.concat([data]));
    const updated = (data) =>
        setPlayers(players => players.map(player => player.id == data.id ? Object.assign(player, data) : player));
    const remove = (data) => setPlayers(players => players.filter(x => x.id != data.id));

    useEffect(() => {
        socket.on('player_create', created);
        socket.on('player_update', updated);
        socket.on('player_remove', remove);
        return () => {
            socket.off('player_create', created);
            socket.off('player_update', updated);
            socket.off('player_remove', remove);
        };
    }, [socket]);

    // Get the initial state by requesting it
    useEffect(() => {
        const abortController = new AbortController();
        fetchGet('/player', {signal: abortController.signal})
            .then(players => setPlayers(players))
            .catch(e => console.error(e));
        return () => abortController.abort();
    }, []);

    return (
        <PlayerStoreContext.Provider value={players}>
            {children}
        </PlayerStoreContext.Provider>
    );
};

const usePlayers = () => {
    return useContext(PlayerStoreContext);
};

export { PlayerStore, usePlayers };