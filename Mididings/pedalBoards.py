# coding=utf8
from mididings import *
from mididings.extra.osc import OSCInterface
from mididings.extra.inotify import AutoRestart
from mididings.extra.osc import SendOSC
from customosc import OSCCustomInterface

import liblo


config(
	backend='jack',
	client_name='PedalBoardsRoutes',
	out_ports=['PBseq24', 'PBAMSBassSynth', 'PBAMSChordsSynth', 'PBAMSLeadSynth', 'PBAMSCtLeadSynth', 'PBAMSClassicalSynth', 'PBTapeutape', 'PBGuitarDag', 'PBGuitarORL', 'PBCtrlOut'],
	in_ports=['PBCtrlIn']
)

hook(
    OSCInterface(56422, 56423),
    OSCCustomInterface(56418),
    AutoRestart()
)


#### Ports OSC ################################################

klickport = 1234
slport = 9951
testport = 1111



#### Outputs ################################################
seq24=Output('PBseq24',1)
seq24once=Output('PBseq24',2)

abass=Output('PBAMSBassSynth',3)
achords=Output('PBAMSChordsSynth',4)
alead=Output('PBAMSLeadSynth',5)
actlead=Output('PBAMSCtLeadSynth',6)
aclass=Output('PBAMSClassicalSynth',7)

tapeutape=Output('PBTapeutape',10)

guitardag=Output('PBGuitarDag', 1)
guitarorl=Output('PBGuitarORL', 1)


#### Functions #############################################
#### Trigger seq24 ####
p_firstpart=[range(1,65)]
p_secondpart=[range(65,129)]

note2seq = ProgramFilter(p_firstpart) >> seq24 # mute-groups seq24
note2seqNplay = ProgramFilter(p_secondpart) >> [ # mute-groups + play
			NoteOn(EVENT_PROGRAM,127) >> Transpose(-62) >> Program('PBseq24',1,EVENT_NOTE) >> seq24,
			Program('PBseq24',1,1),
		]


seq24start = Program('PBseq24',1,1)

seqtrigger = Filter(PROGRAM) >> [
		ChannelFilter(1) >> [ 
             		note2seq,
			note2seqNplay,
		],
		ChannelFilter(2) >> [
			seq24once,
		]
	]

cseqtrigger = Channel(1) >> seqtrigger


#### Stop ####

stop = [
        Program(2) >> cseqtrigger,
#        vxfx_ohreland,
        SendOSC(slport, '/sl/-1/hit', 'pause_on') >> Discard(),
        SendOSC(klickport, '/klick/metro/stop') >> Discard(),

	Program(2) >> abass,
	Program(6) >> actlead
]

#### Synths ####
abass_mute = Program(2) >> abass
actlead_mute = Program(6) >> actlead


#### Guitars ####

# Dag
gtrdag_clean = Program(3) >> guitardag
gtrdag_disto = Program(2) >> guitardag
# gtrdagmute = SendOSC()

# ORL
gtrorl_clean = Program(4) >> guitarorl
gtrorl_disto = Program(1) >> guitarorl
# gtrdagmute = SendOSC()



#### Scenes ################################################

#### ACTE 0 ####
acte0 = PortFilter('PBCtrlIn') >> [
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Intro - Bouton 2
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(65) >> cseqtrigger,
        abass_mute,
        [
            NoteOn('c#-2',127),
            Program(3) 
            ] >> actlead,
        
        ],
    ProgramFilter(3) >> [ # Stop - Bouton 3
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(66) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        NoteOff('c#2', 0) >> actlead,
        
        ],
    ProgramFilter(4) >> [ # Every Machines - Bouton 4
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 14, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxxXxxxxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(67) >> cseqtrigger,
        [
            NoteOff('c#-2', 0),
            Program(3)
            ] >> actlead,
        Program(6) >> abass,
        
        ],
    ProgramFilter(5) >> [ # Every Machines Full - Bouton 5
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 14, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxxXxxxxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(6) >> cseqtrigger,
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        gtrdag_disto,
        ],
    ProgramFilter(6) >> [ # Lancement - Bouton 6
        stop,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        ],
    ProgramFilter(7) >> [ # Refrain - Bouton 7
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(69) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(16) >> alead,
        gtrorl_disto,
        ],
    ProgramFilter(8) >> [ # Couplet - Bouton 8
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(70) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(2) >> alead,
        gtrorl_clean,
        ],
    ProgramFilter(9) >> [ # Couplet - Bouton 9
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(70) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(9) >> alead,
        gtrorl_clean,
        ],
    ProgramFilter(10) >> [ # Couplet - Bouton 10
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(71) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(11) >> alead,
        gtrorl_clean,
        ],
    
    
    ]

#### ACTE 1 ####
acte1 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Intro - Bouton 2
        Program(65) >> cseqtrigger,
        Program(10) >> achords,
        abass_mute,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean
        ],
    ProgramFilter(3) >> [ # Intro Up - Bouton 3
        Program(6) >> Channel(2) >> seqtrigger,
        ],
    ProgramFilter(4) >> [ # Bustas - Bouton 4
        Program(66) >> cseqtrigger,
        Program(10) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean
        ],
    ProgramFilter(5) >> [ # Post Bustas - Bouton 5
        Program(67) >> cseqtrigger,
        
        Program(10) >> achords,
        Program(1) >> abass,
        Program(9) >> alead,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean
        ],
    ProgramFilter(6) >> [ # Final Couplet - Bouton 6
        [
            Program(19),
            Program(22)
            ] >> Channel(2) >> seqtrigger,
        ],
    ProgramFilter(7) >> [ # Debut Riff MathoMagma - Bouton 7
        Program(68) >> cseqtrigger,
        
        Program(10) >> achords,
        abass_mute,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_clean
        
        ],
    ProgramFilter(8) >> [ # MathoMag - Bouton 8
        Program(69) >> cseqtrigger,
        
        Program(10) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_clean
        ],
    ProgramFilter(9) >> [ # MathoMag II - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(9) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(10) >> [ # DeathoDeb - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(7) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_disto
        ],
    ProgramFilter(11) >> [ # Forain I - Bouton 10
        Program(72) >> cseqtrigger,
        
        Program(7) >> achords,
        Program(1) >> abass,
        Program(1) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    
    
    
    
    ]

#### ACTE 2 ####
acte2 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Pattern percus Had Gadya - Bouton 2
        Program(65) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        gtrdag_clean
        ],
    ProgramFilter(3) >> [ # Sample Had Gadya - Bouton 3
        Program(6) >> Channel(2) >> seqtrigger,
        ],
    ProgramFilter(4) >> [ # Tutti Had Gadya - Bouton 4
        Program(66) >> cseqtrigger,
        abass_mute,
        Program(1) >> alead,
        Program(1) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_disto
        ],
    ProgramFilter(5) >> [ # Pont Had Gadya - Bouton 5
        Program(65) >> cseqtrigger,        
        Program(6) >> Channel(2) >> seqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_disto
        ],
    ProgramFilter(6) >> [ # Filtre Pont Had Gadya & suite - Bouton 6
        Program(67) >> cseqtrigger,
        [
            Program(1),
            Ctrl(64,0),
            Ctrl(65,34),
            Ctrl(66,21),
            ] >> achords,
        Program(1) >> abass,
        Program(1) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_disto
        ],
    ProgramFilter(7) >> [ # Debut Couplet - Bouton 7
        Program(69) >> cseqtrigger,

        Program(8) >> achords,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_clean,
        gtrorl_clean
        
        ],
    ProgramFilter(8) >> [ # Pont ternaire - Bouton 8
        Program(72) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_clean
        ],
    ProgramFilter(9) >> [ # Break Couplet - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(10) >> [ # Couplet Part II - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(9) >> alead,
        Program(8) >> achords,
        abass_mute,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(11) >> [ # Switch to Forain Acte II - Bouton 11
        Program(115) >> seq24once,
        SceneSwitch(4)
        ],
    ]

forainacte2 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Forain Acte II - Bouton 2
        Program(65) >> cseqtrigger,
        
        abass_mute,
        Program(5) >> achords,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_clean
        ],
    ProgramFilter(3) >> [ # Forain Acte II Drums - Bouton 3
        Program(6) >> Channel(2) >> seqtrigger,
        seq24start,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        ],
    ProgramFilter(4) >> [ # Forain Acte II Classical - Bouton 4
        Program(13) >> Channel(2) >> seqtrigger
        ],
    ProgramFilter(5) >> [ # Forain Acte II Bîîîîm - Bouton 5
        Program(66) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(5) >> achords,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_clean        
        ],
    ProgramFilter(6) >> [ # Forain Léger Avant Baroque - Bouton 6
        Program(67) >> cseqtrigger,
        abass_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        ],
    ProgramFilter(7) >> [ # Barocko by MX - Bouton 7
        Program(71) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        Program(9) >> alead,
        Program(8) >> achords,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        ],
    ProgramFilter(8) >> [ # Forain Léger Après Baroque - Bouton 8
        Program(68) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> actlead,
        Program(1) >> alead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        ],
    ProgramFilter(9) >> [ # Forain Solo flûte - Bouton 9
        Program(69) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> actlead,
        Program(5) >> achords,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        ],
    ]



#### ACTE 3 ####
acte3 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Sortie solo flûte - Bouton 2
        stop,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        gtrdag_clean
        ],
    ProgramFilter(3) >> [ # Hell Entry - Bouton 3
        Program(65) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(9) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        gtrdag_clean
        ],
    ProgramFilter(4) >> [ # Couplet - Bouton 4
        Program(66) >> cseqtrigger,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_clean
        ],
    ProgramFilter(5) >> [ # Pont glauque - Bouton 5
        [
            Program(14),
            Program(15)
            ] >> Channel(2) >> seqtrigger,
        actlead_mute,
        gtrdag_clean
        ],
    ProgramFilter(6) >> [ # 6/8 Magasin - Bouton 6
        Program(67) >> cseqtrigger,
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 90),
            SendOSC(klickport, '/klick/simple/set_tempo', 90),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_disto
        ],
    ProgramFilter(7) >> [ # Couplet v2 - Bouton 7
        Program(68) >> cseqtrigger,

        Program(10) >> achords,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_clean,
        gtrorl_clean
        
        ],
    ProgramFilter(8) >> [ # Hell Entry Tutti - Bouton 8
        Program(69) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(9) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(9) >> [ # Hip Hop ?? - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(10) >> [ # Mises en place - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(1) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean,
        Program(117) >> seq24once,
        SceneSwitch(6)

        ],
    ]

acte3partII =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Acte III - Couplet II - Bouton 2
        Program(65) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 10),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        gtrdag_clean
        ],
    ProgramFilter(3) >> [ # Acte III - Couplet Alterno - Bouton 3
        [
            Program(6),
            Program(7)
            ] >> Channel(2) >> seqtrigger,
        ],
    ProgramFilter(4) >> [ # Acte III - Couplet Ternaire - Bouton 4
        Program(66) >> cseqtrigger,
        Program(1) >> abass,
        Program(7) >> achords,
        Program(8) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_clean
        ],
    ProgramFilter(5) >> [ # Acte III - Couplet II - Secondo - Bouton 5
        Program(67) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 10),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_clean,
        gtrdag_clean
        ],
    ProgramFilter(6) >> [ # Evil - Bouton 6
        Program(68) >> cseqtrigger,
        Program(1) >> achords,
        Program(1) >> abass,
        Program(9) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrorl_disto
        ],
    ProgramFilter(7) >> [ # Solo batterie - Bouton 7
        Program(69) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        gtrdag_clean,
        gtrorl_clean
        
        ],
    ProgramFilter(8) >> [ # 6/8 Safety Bourre - Bouton 8
        Program(70) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(10) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 90),
            SendOSC(klickport, '/klick/simple/set_tempo', 90),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        
        
        gtrdag_clean,
        gtrorl_clean
        ],
    ProgramFilter(9) >> [ # Hip Hop ?? - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean
        ],
    ProgramFilter(10) >> [ # Mises en place - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(1) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_disto,
        gtrorl_clean,
        Program(117) >> seq24once,
        SceneSwitch(6)

        ],
    ]




#### RUN ###################################################

run(
    scenes = {
        1: SceneGroup("Acte 0", [
  		Scene("Bass ORL",
                    acte0
		),
		Scene("Guitar ORL",
		    acte0
		),
		Scene("Voix ORL",
		    acte0
	        ),
		Scene("Bass Dag",
		    acte0
		),
		Scene("Guitar Dag",
		    acte0
		),
		Scene("Voix Dag",
		    acte0
		),
		Scene("Boucles",
		    acte0
		),
		Scene("Bank Select",
		    acte0
		),
		Scene("Tune Select",
		    acte0
		)

	    ]
        ),
        2: SceneGroup("Acte I", [
  		Scene("Bass ORL",
                    acte1		    
		),
		Scene("Guitar ORL",
		    acte1
		),
		Scene("Voix ORL",
		    acte1
	        ),
		Scene("Bass Dag",
		    acte1
		),
		Scene("Guitar Dag",
		    acte1
		),
		Scene("Voix Dag",
		    acte1
		),
		Scene("Boucles",
		    acte1
		),
		Scene("Bank Select",
		    acte1
		),
		Scene("Tune Select",
		    acte1
		)
	    ]
        ),
        3: SceneGroup("Acte II", [
  		Scene("Bass ORL",
                    acte2		    
		),
		Scene("Guitar ORL",
		    acte2
		),
		Scene("Voix ORL",
		    acte2
	        ),
		Scene("Bass Dag",
		    acte2
		),
		Scene("Guitar Dag",
		    acte2
		),
		Scene("Voix Dag",
		    acte2
		),
		Scene("Boucles",
		    acte2
		),
		Scene("Bank Select",
		    acte2
		),
		Scene("Tune Select",
		    acte2
		)
	    ]
        ),
        4: SceneGroup("Forain Acte II", [
  		Scene("Bass ORL",
                    forainacte2		    
		),
		Scene("Guitar ORL",
		    forainacte2
		),
		Scene("Voix ORL",
		    forainacte2
	        ),
		Scene("Bass Dag",
		    forainacte2
		),
		Scene("Guitar Dag",
		    forainacte2
		),
		Scene("Voix Dag",
		    forainacte2
		),
		Scene("Boucles",
		    forainacte2
		),
		Scene("Bank Select",
		    forainacte2
		),
		Scene("Tune Select",
		    forainacte2
		)
	    ]
        ),
        5: SceneGroup("Acte III", [
  		Scene("Bass ORL",
                    acte3		    
		),
		Scene("Guitar ORL",
		    acte3
		),
		Scene("Voix ORL",
		    acte3
	        ),
		Scene("Bass Dag",
		    acte3
		),
		Scene("Guitar Dag",
		    acte3
		),
		Scene("Voix Dag",
		    acte3
		),
		Scene("Boucles",
		    acte3
		),
		Scene("Bank Select",
		    acte3
		),
		Scene("Tune Select",
		    acte3
		)
	    ]
        ),
        6: SceneGroup("Acte III Part II", [
  		Scene("Bass ORL",
                    acte3partII		    
		),
		Scene("Guitar ORL",
		    acte3partII
		),
		Scene("Voix ORL",
		    acte3partII
	        ),
		Scene("Bass Dag",
		    acte3partII
		),
		Scene("Guitar Dag",
		    acte3partII
		),
		Scene("Voix Dag",
		    acte3partII
		),
		Scene("Boucles",
		    acte3partII
		),
		Scene("Bank Select",
		    acte3partII
		),
		Scene("Tune Select",
		    acte3partII
		)
	    ]
        ),

    },
)

