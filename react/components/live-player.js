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
import TextField from '@material-ui/core/TextField';
import PlayIcon from '@material-ui/icons/PlayArrow';
import PauseIcon from '@material-ui/icons/Pause';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { useSocket } from './socket.js';
import { fetchGet, fetchPut } from './fetch-wrapper.js';
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

const PlaylistItem = ({ item }) => {
    return (
        <TableRow>
            <TableCell>
            </TableCell>
            <TableCell>
            </TableCell>
            <TableCell>
                {item.id}
            </TableCell>
            <TableCell>
            </TableCell>
            <TableCell>
                {item.type}
            </TableCell>
        </TableRow>
    );
};

// TODO: Add playlist too
const SearchBox = ({ addTrack }) => {
    const [ search, setSearch ] = useState('');
    const [ options, setOptions ] = useState([]);
    const [ loading, setLoading ] = useState(false);

    useEffect(() => {
        if (search == '') {
            setOptions([]);
            setLoading(false);
        } else {
            setLoading(true);
            fetchGet(`/library/track?results=10&page=0&query=${search}`)
                .then(({count, tracks}) => { setOptions(tracks); setLoading(false); })
                .catch(e => { console.error(e); setLoading(false); });
        }
    }, [search]);

    const inputChange = (event, value, reason) => {
        setSearch(reason == 'input' ? value : '');
    };

    return (
        <Autocomplete
            onInputChange={inputChange}
            onChange={(event, value) => {value && addTrack(value.id);}}
            inputValue={search}
            options={options}
            getOptionLabel={option => `${option.artist} - ${option.title}`}
            loading={loading}
            style={{ width: 300 }}
            renderInput={params => (
                <TextField {...params} label="Add track" variant="outlined" fullWidth />
            )}/>
    );
};

const LivePlayer = ({ player_id }) => {
    const classes = useStyles();
    const socket = useSocket();
    const [ name, setName ] = useState('Live Player ' + player_id);
    const [ tracks, setTracks ] = useState([]);
    const [ jingleCount, setJingleCount ] = useState(0);
    const [ state, setState ] = useState('paused');
    const [ jinglePlaylist, setJinglePlaylist ] = useState('');
    const [ currentTime, setCurrentTime ] = useState(0.0);

    useEffect(() => {
        fetchGet('/player/' + player_id)
            .then(player => setName(player.name))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/jingle_count')
            .then(count => setJingleCount(count))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/state')
            .then(state => setState(state))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/tracks')
            .then(tracks => setTracks(tracks))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/jingle_playlist')
            .then(playlist => setJinglePlaylist(playlist))
            .catch(e => console.error(e));
    }, [player_id]);

    const updatePlayer = ({id, name}) => {
        if (id == player_id) {
            setName(name);
        }
    };

    useEffect(() => {
        socket.on('player_update', updatePlayer);
        socket.on('player_jinglecount_' + player_id, setJingleCount);
        socket.on('player_jingles_' + player_id, setJinglePlaylist);
        socket.on('player_tracks_' + player_id, setTracks);
        socket.on('player_state_' + player_id, setState);
        socket.on('player_tracktime_' + player_id, setCurrentTime);
        return () => {
            socket.off('player_update', updatePlayer);
            socket.off('player_jinglecount_' + player_id, setJingleCount);
            socket.off('player_jingles_' + player_id, setJinglePlaylist);
            socket.off('player_tracks_' + player_id, setTracks);
            socket.off('player_state_' + player_id, setState);
            socket.off('player_tracktime_' + player_id, setCurrentTime);
        };
    }, [socket, player_id]);

    const addTrack = trackId => {
        let newTracks = tracks.slice(0);
        newTracks.splice(tracks.length > 0 ? 1 : 0, 0, {'id': trackId, 'type': 'play_next'});
        let allTracks = {'tracks': newTracks.map(x => x.id), 'types': newTracks.map(x => x.type)};
        fetchPut('/player/' + player_id + '/tracks', allTracks)
            .catch(e => console.error(e));
    };

    const play = () => {
        fetchPut('/player/' + player_id + '/state', {'state': 'playing'})
            .catch(e => console.error(e));
    };

    const pause = () => {
        fetchPut('/player/' + player_id + '/state', {'state': 'paused'})
            .catch(e => console.error(e));
    };

    return (
        <div className={classes.live_player}>
            <Typography component="h5" variant="h5">
                {name}
            </Typography>
            <Paper>
                <SearchBox addTrack={addTrack} />
                <TableContainer>
                    <Table size='medium'>
                        <TableHead>
                            <PlaylistHeader />
                        </TableHead>
                        <TableBody>
                            {tracks.map((track, index) => <PlaylistItem item={track} key={index} />)}
                        </TableBody>
                    </Table>
                </TableContainer>
                {state == 'paused' &&
                    <Tooltip title="Play">
                        <Fab color="primary" size="small" onClick={play}>
                            <PlayIcon />
                        </Fab>
                    </Tooltip>}
                {state == 'playing' &&
                    <Tooltip title="Pause">
                        <Fab color="primary" size="small" onClick={pause}>
                            <PauseIcon />
                        </Fab>
                    </Tooltip>}
            </Paper>
        </div>
    );
};

export default LivePlayer;
