import React, { useState, useEffect } from 'react';
import * as io from 'socket.io-client';

// This is basically the trade-off between latency and choppy-ness
// This value was guessed on localhost using the hard-coded 64-bit encoding
const MINIMUM_LENGTH = 4 * 1024;
// The length that something is clearly wrong and we need to reset
const ABORT_LENGTH = 20 * 1024;

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
    let startTime = null;
    const handleAudio = data => {
        if (existingBuffer != null) {
            data = concat(existingBuffer, data);
        }
        if (data.byteLength < MINIMUM_LENGTH) {
            existingBuffer = data;
            return;
        }
        if (data.byteLength > ABORT_LENGTH) {
            existingBuffer = null;
            startTime = null;
            return;
        }
        context.decodeAudioData(data.slice(0))
            .then(audioBuffer => {
                existingBuffer = null;
                const source = context.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(context.destination);
                if (startTime == null) {
                    startTime = context.currentTime;
                } else {
                    startTime += source.buffer.duration;
                }
                source.start(startTime);
            })
            .catch(() => {
                existingBuffer = data;
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
