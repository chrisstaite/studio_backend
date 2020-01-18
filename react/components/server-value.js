import React, { useState, useEffect } from 'react';
import useDebouncedEffect from 'use-debounced-effect';

const useServerValue = (value, update) => {
    const [serverValue, setServerValue] = useState(value);
    const [localValue, setLocalValue] = useState(value);

    useDebouncedEffect(
        () => {
            if (serverValue != localValue) {
                update(localValue);
            }
        },
        600,
        [localValue]
    );

    useEffect(() => {
        setServerValue(value);
        setLocalValue(value);
    }, [value]);

    return [localValue, setLocalValue];
};

export default useServerValue;