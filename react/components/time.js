import React from 'react';

const Time = ({time}) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.round(time % 60);
    return (
        <span>
            {minutes}:{(seconds < 10 ? '0' : '')}{seconds}
        </span>
    );
};

export default Time;
