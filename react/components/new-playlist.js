import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import DialogTitle from '@material-ui/core/DialogTitle';
import Typography from '@material-ui/core/Typography';
import Input from '@material-ui/core/Input';
import Dialog from '@material-ui/core/Dialog';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';

const useStyles = makeStyles(theme => ({
    add_button: {
        position: 'absolute',
        right: '5px',
        bottom: '10px',
    },
}));

const NewPlaylistDialog = ({ onClose, open }) => {
    const classes = useStyles();
    const [ playlist, setPlaylist ] = useState('');

    const handleClose = () => onClose(null);
    const create = () => onClose(playlist);

    return (
        <Dialog fullWidth={true} onClose={handleClose} open={open}>
            <DialogTitle>New playlist</DialogTitle>
            <Input placeholder="Name" fullWidth={true} value={playlist} onChange={event => setPlaylist(event.target.value)}/>
            <Tooltip title="Create playlist">
                <Fab size="small" color="primary" onClick={create} className={classes.add_button}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </Dialog>
    );
}

NewPlaylistDialog.propTypes = {
    onClose: PropTypes.func.isRequired,
    open: PropTypes.bool.isRequired,
};

export default NewPlaylistDialog;