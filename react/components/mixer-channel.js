import React from 'react';
import Slider from '@material-ui/core/Slider';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import Fab from '@material-ui/core/Fab';
import RemoveIcon from '@material-ui/icons/Remove';
import Tooltip from '@material-ui/core/Tooltip';
import { useMixers } from './mixer-store.js';
import { useInputs } from './input-store.js';

const MixerChannel = ({mixer, channel}) => {
    const mixers = useMixers();
    const inputs = useInputs();

    const setVolume = volume => {
        // TODO: Debounce!
        const data = new FormData();
        data.append('volume', volume);
        fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'PUT', body: data});
    };
    const removeChannel = () => {
        fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'DELETE'});
    };
    const setInput = input => {
        const data = new FormData();
        data.append('input', input);
        fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'PUT', body: data});
    };

    return (
        <div>
            <Slider min={0} max={2} step={0.01} orientation="vertical" value={channel.volume}
                onChange={(event, value) => setVolume(value)} />
            <Select value={channel.input == null ? '' : channel.input} onChange={event => setInput(event.target.value)}>
                <MenuItem value="">None</MenuItem>
                {inputs.map(input => <MenuItem value={input.id} key={input.id}>{input.display_name}</MenuItem>)}
                {mixers.filter(x => x.id != mixer.id).map(
                        mixer => <MenuItem value={mixer.id} key={mixer.id}>{mixer.display_name}</MenuItem>
                    )}
            </Select>
            <Tooltip title="Remove channel">
                <Fab color="primary" size="small" onClick={removeChannel}>
                    <RemoveIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

export default MixerChannel;