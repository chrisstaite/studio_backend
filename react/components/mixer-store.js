import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSocket } from './socket.js';

const MixerStoreContext = createContext([]);

const MixerStore = ({children}) => {
    const socket = useSocket();
    const [mixers, setMixers] = useState([]);

    const created = (data) => setMixers(mixers => mixers.concat(data));
    const updated = (data) =>
        setMixers(mixers => mixers.map(mixer => mixer.id == data.id ? Object.assign(mixer, data) : mixer));
    const remove = (data) => setMixers(mixers => mixers.filter(x => x.id != data.id));

    const addChannel = (mixer, channelId) => {
        mixer.channels.push({id: channelId, volume: 1.0, input: null});
        return mixer;
    };
    const createChannel = (data) => setMixers(
        mixers => mixers.map(mixer => mixer.id == data.mixer ? addChannel(mixer, data.channel) : mixer)
    );
    const updateMixerChannel = (mixer, update) => {
        const {['mixer']: a, ['channel']: channelId, ...updateData} = update;
        mixer.channels.map(channel => channel.id == channelId ? Object.assign(channel, updateData) : channel );
        return mixer;
    };
    const updateChannel = (data) => setMixers(
        mixers => mixers.map(mixer => mixer.id == data.mixer ? updateMixerChannel(mixer, data) : mixer)
    );
    const removeMixerChannel = (mixer, channelId) => {
        let index = mixer.channels.findIndex(x => x.id == channelId);
        if (index != -1) {
            mixer.channels.splice(index, 1);
        }
        return mixer;
    };
    const removeChannel = (data) => setMixers(
        mixers => mixers.map(mixer => mixer.id == data.mixer ? removeMixerChannel(mixer, data.channel) : mixer)
    );

    useEffect(() => {
        socket.on('mixer_create', created);
        socket.on('mixer_update', updated);
        socket.on('mixer_remove', remove);
        socket.on('mixer_channel_create', createChannel);
        socket.on('mixer_channel_update', updateChannel);
        socket.on('mixer_channel_remove', removeChannel);
        return () => {
            socket.off('mixer_create', created);
            socket.off('mixer_update', updated);
            socket.off('mixer_remove', remove);
            socket.off('mixer_channel_create', createChannel);
            socket.off('mixer_channel_update', updateChannel);
            socket.off('mixer_channel_remove', removeChannel);
        };
    }, [socket]);

    const loadMixerChannels = mixers => {
        mixers.forEach(mixer => fetch('/audio/mixer/' + mixer.id)
            .then(response => response.json())
            .then(data => setMixers(mixers => mixers.concat([data])))
            .catch(e => console.error(e))
        );
    };

    // Get the initial state by requesting it
    useEffect(() => {
        fetch('/audio/mixer')
            .then(response => response.json())
            .then(mixers => loadMixerChannels(mixers))
            .catch(e => console.error(e));
    }, []);

    return (
        <MixerStoreContext.Provider value={mixers}>
            {children}
        </MixerStoreContext.Provider>
    );
};

const useMixers = () => {
    return useContext(MixerStoreContext);
};

export { MixerStore, useMixers };