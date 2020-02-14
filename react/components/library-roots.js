import React, { useState, useEffect } from 'react';
import DialogTitle from '@material-ui/core/DialogTitle';
import Dialog from '@material-ui/core/Dialog';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import LibraryAddIcon from '@material-ui/icons/LibraryAdd';
import FolderIcon from '@material-ui/icons/Folder';
import RemoveIcon from '@material-ui/icons/Remove';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';
import './library-roots.css';
import DirectoryPicker from './directory-picker.js';
import { fetchPost, fetchGet, fetchDelete } from './fetch-wrapper.js';

const Root = ({ root, deleteRoot }) => {
    return (
        <ListItem>
            <ListItemIcon><FolderIcon /></ListItemIcon>
            <ListItemText primary={root}/>
            <RemoveIcon onClick={() => deleteRoot(root)} />
        </ListItem>
    );
};

const LibraryRoots = ({ onClose, open }) => {
    const [ roots, setRoots ] = useState([]);
    const [ newRootOpen, setNewRootOpen ] = useState(false);

    useEffect(() => {
        if (open) {
            fetchGet('/library')
                .then(response => setRoots(response))
                .catch(e => console.error(e));
        }
    }, [open]);

    const addRootDirectory = directory => {
        if (directory != null) {
            fetchPost('/library', { 'directory': directory })
                .catch(e => console.error(e));
            setRoots(roots => roots.concat([directory]));
        }
        setNewRootOpen(false);
    };

    const deleteRoot = root => {
        confirmAlert({
            title: 'Remove library root',
            message: 'Are you sure you want to remove this directory?',
            buttons: [
                {
                    label: 'Yes',
                    onClick: () => {
                        fetchDelete('/library', { 'directory': root })
                            .catch(e => console.error(e));
                        setRoots(roots => roots.filter(x => x != root));
                    },
                },
                {
                    label: 'No',
                }
            ]
        })
    };

    return (
        <Dialog fullWidth={true} onClose={() => onClose()} open={open}>
            <DialogTitle>Library root directories</DialogTitle>

            <List>
                {roots.map(root => <Root root={root} key={root} deleteRoot={deleteRoot} />)}
            </List>

            <Tooltip title="Add a root">
                <Fab color="primary" size="small" onClick={_ => setNewRootOpen(true)}>
                    <LibraryAddIcon />
                </Fab>
            </Tooltip>
            <DirectoryPicker open={newRootOpen} onClose={addRootDirectory} />
        </Dialog>
    );
};

export default LibraryRoots;
