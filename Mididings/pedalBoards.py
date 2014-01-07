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
	out_ports=['PBseq24', 'PBAMSBassSynth', 'PBAMSChordsSynth', 'PBAMSLeadSynth', 'PBAMSCtLeadSynth', 'PBTapeutape', 'PBCtrlOut'],
	in_ports=['PBCtrlIn']
)

hook(
    OSCInterface(56422, 56423),
    OSCCustomInterface(56418),
    AutoRestart()
)

klickport = 1234
slport = 9951
ardourport = 3819
testport = 1111



#### Outputs ################################################
seq24=Output('PBseq24',1)
seq24once=Output('PBseq24',2)

abass=Output('PBAMSBassSynth',3)
achords=Output('PBAMSChordsSynth',4)
alead=Output('PBAMSLeadSynth',5)
actlead=Output('PBAMSCtLeadSynth',6)

tapeutape=Output('PBTapeutape',10)



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




#### Scenes ################################################

run(
    scenes = {
        1: SceneGroup("Dummy", [
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

