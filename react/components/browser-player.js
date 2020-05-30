import React, { useState, useEffect } from 'react';
import * as io from 'socket.io-client';

const concat = (buffer1, buffer2) => {
  var tmp = new Uint8Array(buffer1.byteLength + buffer2.byteLength);
  tmp.set(new Uint8Array(buffer1), 0);
  tmp.set(new Uint8Array(buffer2), buffer1.byteLength);
  return tmp.buffer;
};

const playWebAudio = () => {
    const socket = io('/audio');
    const context = new AudioContext();

    let existingBuffer = null;
    const handleAudio = data => {
        if (existingBuffer != null) {
            data = concat(existingBuffer, data);
        }
        const errorData = data.slice(0);
        context.decodeAudioData(data)
            .then(audioBuffer => {
                existingBuffer = null;
                const source = context.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(context.destination);
                source.start();
            })
            .catch(() => {
                existingBuffer = errorData;
            });
    };

    socket.emit('start_output', 'Browser');
    socket.on('output', handleAudio);

    return () => socket.disconnect();
};

const BrowserPlayer = () => {
    useEffect(playWebAudio, []);
    return ( <div /> );
};

export default BrowserPlayer;
