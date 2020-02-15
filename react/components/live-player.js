import React, { useState, useEffect } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { useSocket } from './socket.js';
import { fetchGet } from './fetch-wrapper.js';
import { usePlayers } from './player-store.js';

const useStyles = makeStyles({
    live_player: {
        'min-height': '200px',
        'padding-bottom': '20px',
    },
});

const PlaylistHeader = () => (
    <TableRow>
        <TableCell>
            Start
        </TableCell>
        <TableCell>
            Artist
        </TableCell>
        <TableCell>
            Title
        </TableCell>
        <TableCell>
            Length
        </TableCell>
        <TableCell />
    </TableRow>
);

const LivePlayer = ({ player_id }) => {
    const classes = useStyles();
    const socket = useSocket();
    const [ name, setName ] = useState('Live Player ' + player_id)

    useEffect(() => {
        fetchGet('/player/' + player_id)
            .then(player => setName(player.name))
            .catch(e => console.error(e));
    }, [player_id]);

    return (
        <div className={classes.live_player}>
            <Typography component="h5" variant="h5">
                {name}
            </Typography>
            <Paper>
                <TableContainer>
                    <Table size='medium'>
                        <TableHead>
                            <PlaylistHeader />
                        </TableHead>
                    </Table>
                </TableContainer>
            </Paper>
        </div>
    );
};

export default LivePlayer;
