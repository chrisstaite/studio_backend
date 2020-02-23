import React, { useState, useEffect } from 'react';

const playWebAudio = uri => {
    const context = new AudioContext();

    const recursiveRead = reader => {
        reader.read()
            .then(({ done, value }) => {
                if (done) {
                    return;
                }
                context.decodeAudioData(value.buffer)
                    .then(audioBuffer => {
                        const source = context.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(context.destination);
                        source.start();
                    })
                    .catch(e => console.info(e));
            })
            .then(() => setTimeout(() => recursiveRead(reader), 0))
            .catch(e => console.error(e));
    };

    const abortController = new AbortController();
    fetch(uri, {signal: abortController.signal})
        .then(response => {
            if (!response.ok) {
                throw response;
            }
            return response;
        })
        .then(response => response.body.getReader())
        .then(recursiveRead)
        .catch(e => console.info(e));
    return () => abortController.abort();
};

const BrowserPlayer = () => {
    const [ uri, setUri ] = useState('/audio/output_stream/Browser');

    if (window.AudioContext !== undefined) {
        useEffect(() => playWebAudio(uri), [uri]);
        return ( <div /> );
    }
    return (
        <audio src='' autoPlay />
    );
};

export default BrowserPlayer;
