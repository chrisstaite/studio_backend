import React, { useState, useEffect } from 'react';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContentText from '@material-ui/core/DialogContentText';
import Dialog from '@material-ui/core/Dialog';
import { makeStyles } from '@material-ui/core/styles';
import TreeView from '@material-ui/lab/TreeView';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import TreeItem from '@material-ui/lab/TreeItem';
import CircularProgress from '@material-ui/core/CircularProgress';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import AddIcon from '@material-ui/icons/Add';
import { fetchGet } from './fetch-wrapper.js';

const useStyles = makeStyles({
    root: {
        height: 216,
        flexGrow: 1,
        maxWidth: 400,
    },
    fab: {
        position: 'absolute',
        right: 0,
        bottom: '5px',
    },
});

const DirectoryItem = ({ path, name, expandedList, setDirectory }) => {
    const [ expanded, setExpanded ] = useState(false);
    const [ hasChildren, setHasChildren ] = useState(true);

    useEffect(() => {
        if (expandedList.includes(path)) {
            setExpanded(true);
        }
    }, [expandedList]);

    if (hasChildren)
    {
        return (
            <TreeItem nodeId={path} label={name} onClick={() => setDirectory(path)}>
                <Directory path={path}
                           expandedList={expandedList}
                           expanded={expanded}
                           setHasChildren={setHasChildren}
                           setDirectory={setDirectory} />
            </TreeItem>
        );
    }

    return (<TreeItem nodeId={path} label={name} />);
};

const Directory = ({ path, expandedList, expanded, setDirectory, ...props }) => {
    const [ listing, setListing ] = useState([]);
    const [ loaded, setLoaded ] = useState(false);

    useEffect(() => {
        const abortController = new AbortController();
        if (!loaded && expanded)
        {
            fetchGet('/browse' + path, {signal: abortController.signal})
                .then(directories => {
                    if (Array.isArray(directories)) {
                        setListing(directories);
                    } else {
                        directories = [];
                    }
                    if (directories.length == 0 && props.hasOwnProperty('setHasChildren')) {
                        props.setHasChildren(false);
                    }
                })
                .catch(e => console.error(e));
            setLoaded(true);
        }
        return () => abortController.abort();
    }, [path, loaded, expanded]);

    if (!loaded && expanded) {
        return (<CircularProgress />);
    }

    return (
        <React.Fragment>
            {listing.map(directory =>
                <DirectoryItem name={directory}
                               path={path + "/" + directory}
                               expandedList={expandedList}
                               setDirectory={setDirectory}
                               key={directory} />)}
        </React.Fragment>
    );
};

const DirectoryPicker = ({ onClose, open }) => {
    const classes = useStyles();
    const [ expandedList, setExpandedList ] = useState([]);
    const [ directory, setDirectory ] = useState(null);

    const handleChange = (event, nodes) => setExpandedList(nodes);

    return (
        <Dialog fullWidth={true} onClose={() => onClose(null)} open={open}>
            <DialogTitle>Choose directory</DialogTitle>
            <DialogContent>
                <TreeView className={classes.root}
                          defaultCollapseIcon={<ExpandMoreIcon />}
                          defaultExpandIcon={<ChevronRightIcon />}
                          defaultEndIcon={<div style={{ width: 24 }} />}
                          expanded={expandedList}
                          onNodeToggle={handleChange}>
                    <Directory path=""
                               expandedList={expandedList}
                               expanded={true}
                               setDirectory={setDirectory} />
                </TreeView>
                <DialogActions className={classes.fab}>
                    <Tooltip title="Add root">
                        <Fab color="primary" size="small" onClick={_ => onClose(directory)}>
                            <AddIcon />
                        </Fab>
                    </Tooltip>
                </DialogActions>
            </DialogContent>
        </Dialog>
    );
};

export default DirectoryPicker;
