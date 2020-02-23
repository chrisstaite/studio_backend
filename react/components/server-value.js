import React, { useState, useEffect } from 'react';
import useDebouncedEffect from 'use-debounced-effect';

const useServerValue = (value, update, timeout=600) => {
    const [serverValue, setServerValue] = useState(value);
    const [localValue, setLocalValue] = useState(value);

    useDebouncedEffect(
        () => {
            if (serverValue != localValue) {
                return update(localValue);
            }
        },
        timeout,
        [localValue]
    );

    useEffect(() => {
        setServerValue(value);
        setLocalValue(value);
    }, [value]);

    return [localValue, setLocalValue];
};

export default useServerValue;