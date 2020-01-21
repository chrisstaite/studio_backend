import React, { useState, useEffect } from 'react';
import Input from './input.js';
import { useInputs } from './input-store.js';
import NewInputDialog from './new-input.js';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';

const useStyles = makeStyles({
    input_list: {
        position: 'relative',
        'min-height': '200px',
        'padding-bottom': '20px',
    },
    add_button: {
        position: 'absolute',
        right: '5px',
        bottom: '10px',
    },
});

const Inputs = () => {
    const classes = useStyles();
    const inputs = useInputs();
    const [open, setOpen] = useState(false);

    const handleClose = input => {
        if (input != null) {
            let new_device = { 'type': 'device', 'display_name': input, 'name': input };
            fetch('/audio/input', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(new_device)
                    })
                .then(response => response.json())
                .catch(e => console.error(e));
        }
        setOpen(false);
    };

    return (
        <div className={classes.input_list}>
            {inputs.map(input => <Input input={input} key={input.id} />)}
            <Tooltip title="Add an input device">
                <Fab size="small" color="primary" onClick={event => setOpen(true)} className={classes.add_button}>
                    <AddIcon />
                </Fab>
            </Tooltip>
            <NewInputDialog open={open} onClose={handleClose} />
        </div>
    );
};

export default Inputs;