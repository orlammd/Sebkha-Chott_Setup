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


#### Guitars ####

# Dag
gtrdagclean = Program(3) >> guitardag
gtrdagdisto = Program(2) >> guitardag
# gtrdagmute = SendOSC()

# ORL
gtrorlclean = Program(3) >> guitarorl
gtrorldisto = Program(2) >> guitarorl
# gtrdagmute = SendOSC()




#### Scenes ################################################

run(
    scenes = {
        1: SceneGroup("Dummy", [
  		Scene("Bass ORL",
		    PortFilter('PBCtrlIn') >> [ 
			ProgramFilter(1) >> stop, # !!!STOP!!! #
			ProgramFilter(2) >> [ # Intro - Bouton 2
			    Program(65) >> cseqtrigger,
			    Program(10) >> achords,
			    Program(2) >> abass,
			    Program(6) >> actlead,

			    SendOSC(slport, '/set', 'eight_per_cycle', 24),
			    SendOSC(slport, '/set', 'tempo', 120),

			    SendOSC(klickport, '/klick/simple/set_tempo', 120),
			    SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
			    SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
			    SendOSC(klickport, '/klick/metro/start'),

			    gtrdagclean
			],
		        ProgramFilter(3) >> [ # Intro Up - Bouton 3
			    Program(6) >> Channel(2) >> seqtrigger,
		        ],
			ProgramFilter(4) >> [ # Bustas - Bouton 4
			    Program(66) >> cseqtrigger,
			    Program(10) >> achords,
			    Program(1) >> abass,
			    Program(6) >> actlead,

			    SendOSC(slport, '/set', 'eight_per_cycle', 24),
			    SendOSC(slport, '/set', 'tempo', 120),

			    SendOSC(klickport, '/klick/simple/set_tempo', 120),
			    SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
			    SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
			    SendOSC(klickport, '/klick/metro/start'),

			    gtrdagclean
			],
			ProgramFilter(5) >> [ # Post Bustas - Bouton 5
			    Program(67) >> cseqtrigger,

			    Program(10) >> achords,
			    Program(1) >> abass,
			    Program(9) >> alead,
			    Program(6) >> actlead,

			    SendOSC(slport, '/set', 'eight_per_cycle', 24),
			    SendOSC(slport, '/set', 'tempo', 120),

			    SendOSC(klickport, '/klick/simple/set_tempo', 120),
			    SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
			    SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
			    SendOSC(klickport, '/klick/metro/start'),

			    gtrdagclean
			],
		        ProgramFilter(6) >> [ # Final Couplet - Bouton 6
			    [
				Program(19),
				Program(23)
			    ] >> Channel(2) >> seqtrigger,
		        ],
			ProgramFilter(7) >> [ # Debut Riff MathoMagma - Bouton 7
			    stop,

			    SendOSC(slport, '/set', 'eight_per_cycle', 16),
			    SendOSC(slport, '/set', 'tempo', 120),

			    SendOSC(slport, '/sl/2/hit', 'record'),

			    SendOSC(klickport, '/klick/simple/set_tempo', 120),
			    SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
			    SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
			    SendOSC(klickport, '/klick/metro/start'),

			    gtrdagclean,
			    gtrorlclean

			]



		    ]

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
        2: SceneGroup("Dummy", [
  		Scene("Bass ORL",
		    Discard()
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

    },
)

