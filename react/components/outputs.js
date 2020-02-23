import React, { useState } from 'react';
import Output from './output.js';
import { useOutputs } from './output-store.js';
import NewOutputDialog from './new-output.js'
import makeStyles from '@material-ui/core/styles/makeStyles';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import { fetchPost } from './fetch-wrapper.js';

const useStyles = makeStyles({
    output_list: {
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

const Outputs = () => {
    const classes = useStyles();
    const outputs = useOutputs();
    const [open, setOpen] = useState(false);

    const handleClose = (output) => {
        if (output != null) {
            fetchPost('/audio/output', output)
                .catch(e => console.error(e));
        }
        setOpen(false);
    };

    return (
        <div className={classes.output_list}>
            {outputs.map(output => <Output output={output} key={output.id} />)}
            <Tooltip title="Add an output device">
                <Fab size="small" color="primary" onClick={event => setOpen(true)} className={classes.add_button}>
                    <AddIcon />
                </Fab>
            </Tooltip>
            <NewOutputDialog open={open} onClose={handleClose} />
        </div>
    );
};

export default Outputs;