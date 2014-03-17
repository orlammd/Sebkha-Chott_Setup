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
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
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
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(6) >> cseqtrigger,
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        gtrdag_disto,
        ],
    ProgramFilter(6) >> [ # Couplet - Bouton 6
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(69) >> cseqtrigger,
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(16) >> alead,
        gtrorl_disto,
        ],
    ProgramFilter(7) >> [ # Couplet - Bouton 7
        [
            SendOSC(slport, '/set', 'eight_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(70) >> cseqtrigger,
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(2) >> alead,
        gtrorl_clean,
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
        Program(71) >> cseqtrigger,
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(11) >> alead,
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
        Program(3) >> actlead,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(9) >> alead,
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


#### RUN ###################################################

run(
    scenes = {
        1: SceneGroup("Acte 0", [
  		Scene("Bass ORL",
                    acte0
		),
		Scene("Guitar ORL",
		    Discard()
		),
		Scene("Voix ORL",
		    Discard()
	        ),
		Scene("Bass Dag",
		    Discard()
		),
		Scene("Guitar Dag",
		    Discard()
		),
		Scene("Voix Dag",
		    Discard()
		),
		Scene("Boucles",
		    Discard()
		),
		Scene("Bank Select",
		    Discard()
		),
		Scene("Tune Select",
		    Discard()
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

    },
)

