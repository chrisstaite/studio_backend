import React from 'react';
import { InputStore } from './input-store.js';
import { OutputStore } from './output-store.js';
import { MixerStore } from './mixer-store.js';
import { PlayerStore } from './player-store.js';
import { Socket } from './socket.js';

const Contexts = ({children}) => (
    <Socket>
        <InputStore>
            <OutputStore>
                <MixerStore>
                    <PlayerStore>
                        {children}
                    </PlayerStore>
                </MixerStore>
            </OutputStore>
        </InputStore>
    </Socket>
);

export default Contexts;
