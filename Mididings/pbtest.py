# coding=utf8
from mididings import *
from mididings.extra.osc import OSCInterface
from mididings.extra.inotify import AutoRestart
from mididings.extra.osc import SendOSC
from customosc import OSCCustomInterface

import liblo


config(
	backend='alsa',
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

# Non Mixers
mainmixport = 6666
drumsport = 6667
bassesport = 6668
guitarsport = 6669
mxsynthport = 6670
mxdrumsport = 6671
vocalsport = 6672
tomsport = 6673
acousticsport = 6674
mondagport = 6675
monjeport = 6676
monorlport = 6677
mainsport = 6678



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



#### Synths ####
abass_mute = Program(2) >> abass
actlead_mute = Program(6) >> actlead


#### Guitars ####

# Dag
gtrdag_mute = SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 1.0) >> Discard()
gtrdag_on = SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 0.0) >> Discard()
gtrdag_clean = [
    Program(3) >> guitardag,
    gtrdag_on
    ]
gtrdag_disto = [
    Program(2) >> guitardag,
    gtrdag_on
    ]


# ORL
gtrorl_mute = SendOSC(guitarsport, '/strip/Guitar_ORL/Gain/Mute', 1.0) >> Discard()
gtrorl_on = SendOSC(guitarsport, '/strip/Guitar_ORL/Gain/Mute', 0.0) >> Discard()
gtrorl_clean = [
    Program(4) >> guitarorl,
    gtrorl_on
    ]
gtrorl_disto = [
    Program(1) >> guitarorl,
    gtrorl_on
    ]
gtrdag_chromdelay_on = [
    SendOSC(guitarsport, '/strip/Guitar_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 1.0),
    SendOSC(guitarsport, '/strip/Guitar_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/dry', 0.73)
    ] >> Discard()
gtrdag_chromdelay_off = [
    SendOSC(guitarsport, '/strip/Guitar_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 0.0),
    SendOSC(guitarsport, '/strip/Guitar_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/dry', 1.0)
    ] >> Discard()

#### Bass ####

# Dag
bassdag_mute = SendOSC(bassesport, '/strip/Bass_Dag/Gain/Mute', 1.0)
bassdag_on = SendOSC(bassesport, '/strip/Bass_Dag/Gain/Mute', 0.0)

# ORL
bassorl_mute = [
    SendOSC(bassesport, '/strip/Bass_ORL/Gain/Mute', 1.0),
    SendOSC(bassesport, '/strip/BassFX_ORL/Gain/Mute', 1.0)
    ]
bassorl_on = [
    SendOSC(bassesport, '/strip/Bass_ORL/Gain/Mute', 0.0),
    SendOSC(bassesport, '/strip/BassFX_ORL/Gain/Mute', 0.0)
    ]

#### Vocals ####

#Dag
flutesolo_on = [
    SendOSC(vocalsport, '/strip/Vx_Dag/Smooth%20Decimator/Resample%20rate', 4000.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/Ringmod%20with%20LFO/Modulation%20depth%20(0=none%2C%201=AM%2C%202=RM)', 1.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 1.0)
    ] >> Discard()

flutesolo_off =[
    SendOSC(vocalsport, '/strip/Vx_Dag/Smooth%20Decimator/Resample%20rate', 48000.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/Ringmod%20with%20LFO/Modulation%20depth%20(0=none%2C%201=AM%2C%202=RM)', 0.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 0.0)
        ] >> Discard()


#### Stop ####

stop = [
        Program(2) >> cseqtrigger,
#        vxfx_ohreland,
        SendOSC(slport, '/sl/-1/hit', 'pause_on') >> Discard(),
        SendOSC(klickport, '/klick/metro/stop') >> Discard(),

	abass_mute,
	actlead_mute,

        flutesolo_off
]



#### FX Pedals #############################################
# ORL
orl_basspedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(13) >> bassorl_on,
    ProgramFilter(14) >> SendOSC(slport, '/sl/0/hit', 'record') >> Discard(),
    ProgramFilter(15) >> SendOSC(slport, '/sl/0/hit', 'pause_on') >> Discard(),
    ProgramFilter(16) >> SendOSC(slport, '/sl/0/hit', 'overdub') >> Discard(),
    ProgramFilter(17) >> SendOSC(slport, '/sl/0/hit', 'multiply') >> Discard(),
    ProgramFilter(18) >> SendOSC(slport, '/sl/0/hit', 'trigger') >> Discard(),
#    ProgramFilter(18) >> bassfx_suboctaves,
#    ProgramFilter(19) >> bassfx_jazzdeluxe,
#    ProgramFilter(20) >> bassfx_sabra,
#    ProgramFilter(21) >> bassfx_revgav,
#    ProgramFilter(22) >> bassfx_mute,
    ]
orl_gtrpedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(13) >> gtrorl_on,
    ProgramFilter(14) >> SendOSC(slport, '/sl/2/hit', 'record') >> Discard(),
    ProgramFilter(15) >> SendOSC(slport, '/sl/2/hit', 'pause_on') >> Discard(),
    ProgramFilter(16) >> SendOSC(slport, '/sl/2/hit', 'overdub') >> Discard(),
    ProgramFilter(17) >> SendOSC(slport, '/sl/2/hit', 'multiply') >> Discard(),
    ProgramFilter(18) >> SendOSC(slport, '/sl/2/hit', 'trigger') >> Discard(),

    ProgramFilter(20) >> gtrorl_clean,
    ProgramFilter(19) >> gtrorl_disto
    ]
orl_vxpedal = PortFilter('PBCtrlIn') >> [
#    ProgramFilter(13) >> gtrorl_on,
    ProgramFilter(14) >> SendOSC(slport, '/sl/4/hit', 'record') >> Discard(),
    ProgramFilter(15) >> SendOSC(slport, '/sl/4/hit', 'pause_on') >> Discard(),
    ProgramFilter(16) >> SendOSC(slport, '/sl/4/hit', 'overdub') >> Discard(),
    ProgramFilter(17) >> SendOSC(slport, '/sl/4/hit', 'multiply') >> Discard(),
    ProgramFilter(18) >> SendOSC(slport, '/sl/4/hit', 'trigger') >> Discard(),
    ]


# DAG
dag_basspedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(13) >> bassdag_on,
    ProgramFilter(21) >> SendOSC(slport, '/sl/1/hit', 'record') >> Discard(),
    ProgramFilter(22) >> SendOSC(slport, '/sl/1/hit', 'pause_on') >> Discard(),
    ProgramFilter(23) >> SendOSC(slport, '/sl/1/hit', 'overdub') >> Discard(),
#    ProgramFilter(17) >> SendOSC(slport, '/sl/0/hit', 'multiply') >> Discard(),
#    ProgramFilter(18) >> SendOSC(slport, '/sl/0/hit', 'trigger') >> Discard(),
#    ProgramFilter(18) >> bassfx_suboctaves,
#    ProgramFilter(19) >> bassfx_jazzdeluxe,
#    ProgramFilter(20) >> bassfx_sabra,
#    ProgramFilter(21) >> bassfx_revgav,
#    ProgramFilter(22) >> bassfx_mute,
    ]
dag_gtrpedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(13) >> gtrdag_on,
    ProgramFilter(21) >> SendOSC(slport, '/sl/3/hit', 'record') >> Discard(),
    ProgramFilter(22) >> SendOSC(slport, '/sl/3/hit', 'pause_on') >> Discard(),
    ProgramFilter(23) >> SendOSC(slport, '/sl/3/hit', 'overdub') >> Discard(),
#    ProgramFilter(17) >> SendOSC(slport, '/sl/0/hit', 'multiply') >> Discard(),
#    ProgramFilter(18) >> SendOSC(slport, '/sl/0/hit', 'trigger') >> Discard(),

#    ProgramFilter(23) >> gtrdag_clean,
#    ProgramFilter(22) >> gtrdag_disto,
#    ProgramFilter(21) >> gtrdag_chromdelay_on,
#    ProgramFilter(20) >> gtrdag_chromdelay_off
    ]
dag_vxpedal = PortFilter('PBCtrlIn') >> [
#    ProgramFilter(13) >> gtrorl_on,
    ProgramFilter(21) >> SendOSC(slport, '/sl/5/hit', 'record') >> Discard(),
    ProgramFilter(22) >> SendOSC(slport, '/sl/5/hit', 'pause_on') >> Discard(),
    ProgramFilter(23) >> SendOSC(slport, '/sl/5/hit', 'overdub') >> Discard(),
#    ProgramFilter(17) >> SendOSC(slport, '/sl/0/hit', 'multiply') >> Discard(),
#    ProgramFilter(18) >> SendOSC(slport, '/sl/0/hit', 'trigger') >> Discard(),

#    ProgramFilter(21) >> flutesolo_on,
#    ProgramFilter(20) >> flutesolo_off
    ]

#### Scenes ################################################

#### ACTE 0 ####
acte0 = PortFilter('PBCtrlIn') >> [
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Intro - Bouton 2
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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

        gtrorl_mute,
        gtrdag_mute,
        bassdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(3) >> [ # Stop - Bouton 3
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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

        gtrorl_mute,
        gtrdag_mute,
        bassdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(4) >> [ # Every Machines - Bouton 4
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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

        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(5) >> [ # Every Machines Full - Bouton 5
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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
        gtrorl_mute,
        bassdag_mute,
        bassorl_on
        ],
    ProgramFilter(6) >> [ # Lancement - Bouton 6
        stop,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        gtrdag_disto,
        gtrorl_clean,
        bassorl_mute,
        bassdag_mute
        ],
    ProgramFilter(7) >> [ # Refrain - Bouton 7
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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

        gtrdag_mute,
        gtrorl_disto,
        bassorl_mute,
        bassdag_on
        ],
    ProgramFilter(8) >> [ # Couplet - Bouton 8
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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
        gtrdag_mute,
        bassdag_on,
        bassorl_mute
        ],
    ProgramFilter(9) >> [ # Couplet - Bouton 9
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
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
        gtrdag_mute,
        bassorl_mute,
        bassdag_on
        ],
    ProgramFilter(10) >> [ # Couplet - Bouton 10
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 110),

            SendOSC(klickport, '/klick/simple/set_tempo', 110),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(71) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(11) >> alead,

        gtrorl_clean,
        gtrdag_mute,
        bassorl_mute,
        bassdag_on
        ],
    ProgramFilter(11) >> [ # Intro classique - Bouton 11
        stop,
#        [
#            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
#            SendOSC(slport, '/set', 'tempo', 120),

#            SendOSC(klickport, '/klick/simple/set_tempo', 120),
#            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
#            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
#            SendOSC(klickport, '/klick/metro/start'),
#            ] >> Discard(),
        gtrorl_mute,
        gtrdag_mute,
        bassorl_mute,
        bassdag_mute,
        Program(113) >> seq24once,
        SceneSwitch(2),
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on
        ],
    ProgramFilter(5) >> [ # Post Bustas - Bouton 5
        Program(67) >> cseqtrigger,
        
        Program(10) >> achords,
        Program(1) >> abass,
        Program(9) >> alead,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrdag_clean,
        gtrorl_mute,
        bassdag_mute,
        bassorl_on
        
        ],
    ProgramFilter(8) >> [ # MathoMag - Bouton 8
        Program(69) >> cseqtrigger,
        
        Program(10) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(9) >> [ # MathoMag II - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(9) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(10) >> [ # DeathoDeb - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(7) >> achords,
        Program(1) >> abass,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 240),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_disto,
        bassorl_mute
        ],
    ProgramFilter(11) >> [ # Forain I - Bouton 11
        Program(72) >> cseqtrigger,
        
        Program(7) >> achords,
        Program(1) >> abass,
        Program(1) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            #			    SendOSC(slport, '/sl/2/hit', 'record'),
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    
    ]

#### ACTE 2 ####
acte2 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Pattern percus Had Gadya - Bouton 2
        Program(65) >> cseqtrigger,
        Program(6) >> Channel(2) >> seqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_mute
        ],
#    ProgramFilter(3) >> [ # Sample Had Gadya - Bouton 3
#        Program(6) >> Channel(2) >> seqtrigger,
#        ],
    ProgramFilter(3) >> [ # Tutti Had Gadya - Bouton 3
        Program(66) >> cseqtrigger,
        abass_mute,
        Program(1) >> alead,
        Program(1) >> actlead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(4) >> [ # Pont Had Gadya - Bouton 4
        Program(65) >> cseqtrigger,        
        Program(6) >> Channel(2) >> seqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(5) >> [ # Filtre Pont Had Gadya & suite - Bouton 5
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(6) >> [ # Debut Couplet - Bouton 6
        Program(69) >> cseqtrigger,

        Program(8) >> achords,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on
        
        ],
    ProgramFilter(7) >> [ # Pont ternaire - Bouton 7
        Program(72) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_clean,
        gtrorl_clean,
        bassorl_on
        ],
    ProgramFilter(8) >> [ # Break Couplet - Bouton 8
        Program(70) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        Program(11) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(9) >> [ # Couplet Part II - Bouton 9
        Program(71) >> cseqtrigger,
        
        Program(9) >> alead,
        Program(8) >> achords,
        abass_mute,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(10) >> [ # Solo Basse - Bouton 10
        stop,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        
        bassdag_mute,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_mute
        ],
    ProgramFilter(3) >> [ # Forain Acte II Drums - Bouton 3
        Program(6) >> Channel(2) >> seqtrigger,
        seq24start,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),


        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(6) >> [ # Forain Léger Avant Baroque - Bouton 6        
        Program(67) >> cseqtrigger,
        abass_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(7) >> [ # Barocko by MX - Bouton 7
        Program(71) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        Program(9) >> alead,
        Program(8) >> achords,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 100),
            SendOSC(klickport, '/klick/simple/set_tempo', 100),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(8) >> [ # Forain Léger Après Baroque sans machine - Bouton 8
        stop,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(9) >> [ # Forain Léger Après Baroque avec machines - Bouton 9
        Program(68) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> actlead,
        Program(1) >> alead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(10) >> [ # Forain Solo flûte - Bouton 10
        Program(69) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> actlead,
        Program(5) >> achords,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 150),
            SendOSC(klickport, '/klick/simple/set_tempo', 150),
            SendOSC(klickport, '/klick/simple/set_meter', 3, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        flutesolo_on,
        bassdag_mute,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on

        Program(116) >> seq24once,
        SceneSwitch(5)
        ],
    ]



#### ACTE 3 ####
acte3 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Sortie solo flûte - Bouton 2
        flutesolo_off,
        stop,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrorl_clean,
        gtrdag_mute,
        bassorl_mute
        ],
    ProgramFilter(3) >> [ # Hell Entry - Bouton 3
        Program(65) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(9) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrorl_clean,
        gtrdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(4) >> [ # Couplet - Bouton 4
        Program(66) >> cseqtrigger,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(5) >> [ # Pont glauque - Bouton 5
        [
            Program(14),
            Program(15)
            ] >> Channel(2) >> seqtrigger,
        actlead_mute,
        ],
    ProgramFilter(6) >> [ # 6/8 Magasin - Bouton 6
        Program(67) >> cseqtrigger,
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 90),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(7) >> [ # Couplet v2 - Bouton 7
        Program(68) >> cseqtrigger,

        Program(10) >> achords,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on
        
        ],
    ProgramFilter(8) >> [ # Hell Entry Tutti - Bouton 8
        Program(69) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(9) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(9) >> [ # Hip Hop ?? - Bouton 9
        Program(70) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        flutesolo_on,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_mute,
        gtrorl_clean,
        bassorl_on
        ],
    ProgramFilter(10) >> [ # Mises en place - Bouton 10
        Program(71) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(1) >> achords,
        actlead_mute,

        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on,
        flutesolo_on,

        Program(117) >> seq24once,
        SceneSwitch(6)

        ],
    ]

acte3partII =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Acte III - Couplet II - Bouton 2 - Surf
        Program(65) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 10),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrorl_clean,
        gtrdag_clean,
        bassorl_on,
        flutesolo_off
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
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(5) >> [ # Acte III - Couplet II - Secondo - Bouton 5
        Program(67) >> cseqtrigger,
        Program(1) >> abass,
        Program(8) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 10),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrorl_mute,
        gtrdag_disto,
        bassorl_on,
        ],
    ProgramFilter(6) >> [ # 6/8 Safety Bourre - Bouton 6
        Program(70) >> cseqtrigger,
        Program(1) >> abass,
        Program(1) >> achords,
        Program(10) >> alead,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 90),
            SendOSC(klickport, '/klick/simple/set_tempo', 90),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        
        
        bassdag_on,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(7) >> [ # Solo guitare arpège - Bouton 7
        stop,

        actlead_mute,
        abass_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        

        flutesolo_on,
        gtrorl_clean,
        gtrdag_clean,
        gtrdag_chromdelay_on,
        bassdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(8) >> [ # Folk - Bouton 8
        stop,

        actlead_mute,
        abass_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),        

        flutesolo_off,
        gtrorl_clean,
        gtrdag_clean,
        gtrdag_chromdelay_off,
        bassdag_mute,
        bassorl_mute
        
        ],
    ProgramFilter(9) >> [ # Evil - Bouton 9
        Program(68) >> cseqtrigger,
        Program(1) >> achords,
        Program(1) >> abass,
        Program(9) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrdag_mute,
        gtrorl_disto,
        bassorl_mute
        ],
    ProgramFilter(10) >> [ # Solo batterie - Bouton 10
        Program(69) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on
        
        ],

    ProgramFilter(11) >> [ # 12/8 Prog - Bouton 11
        stop,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on

        ],
    ]
acte3partIII =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # 13/8 Prog - Bouton 2
        Program(65) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(10) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxxXxxXxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on

        ],
    ProgramFilter(3) >> [ # 13/8 Prog bourrin - Bouton 3
        Program(66) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(1) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxxXxxXxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on
        ],
    ProgramFilter(4) >> [ # 13/8 Prog en G - Bouton 4
        Program(67) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(10) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxxXxxXxxXxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on

        ],
    ProgramFilter(5) >> [ # Metal - Bouton 5
        Program(68) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(10) >> achords,
        Program(10) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 14),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxXxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_disto,
        bassorl_mute

        ],
    ProgramFilter(6) >> [ # Metal Alterno - Bouton 6
        Program(69) >> cseqtrigger,

        Program(1) >> abass,
        Program(10) >> achords,
        Program(10) >> actlead,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 14),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxXxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_disto,
        gtrorl_disto,
        bassorl_mute

        ],
    ProgramFilter(7) >> [ # Vers Carmen - Bouton 7
        gtrorl_clean,

        Program(119) >> seq24once,
        SceneSwitch(8)        
        ]
    ]


#### ACTE 4 ####
acte4 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Première occurrence machines Carmeno Saoule - Bouton 2
        Program(65) >> cseqtrigger, 
        abass_mute,
        actlead_mute,
        Program(9) >> achords,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_mute
        ],
    ProgramFilter(3) >> [ # Seconde occurrence machines Mises en place - Bouton 3
        Program(66) >> cseqtrigger,
        Program(1) >> abass,
        Program(9) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_on
        ],
    ProgramFilter(4) >> [ # Troisième occurrence machines Carmeno Saoule 2 - Bouton 4
        Program(67) >> cseqtrigger,
        Program(1) >> abass,
        Program(9) >> achords,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrdag_disto,
        gtrorl_disto,
        bassorl_mute
        ],
    ProgramFilter(5) >> [ # Début basse Your Soul - Bouton 5
        Program(68) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),

            ] >> Discard(),

        bassdag_on,
        gtrdag_disto,
        gtrorl_disto,
        bassorl_on
        ],
    ProgramFilter(6) >> [ # Bouclage des basses - Bouton 6
        [
            SendOSC(slport, '/sl/0/hit', 'record'),
            SendOSC(slport, '/sl/1/hit', 'record')
            ] >> Discard()
        ],
    ProgramFilter(7) >> [ # Bouclage des voix - Bouton 7
        [
            SendOSC(slport, '/sl/4/hit', 'record'),
            SendOSC(slport, '/sl/5/hit', 'record'),
            SendOSC(slport, '/sl/6/hit', 'record'),
            ] >> Discard()
        ],
    ProgramFilter(8) >> [ # Overdub Voix - Bouton 8
#        Program(69) >> cseqtrigger,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/sl/4/hit', 'overdub'),
            SendOSC(slport, '/sl/5/hit', 'overdub'),
            SendOSC(slport, '/sl/6/hit', 'overdub'),

            ] >> Discard(),

        ],
    ProgramFilter(9) >> [ # Bouclage guitares - Bouton 9
        [
            SendOSC(slport, '/sl/2/hit', 'record'),
            SendOSC(slport, '/sl/3/hit', 'record')
            ] >> Discard()
        ],
    ProgramFilter(10) >> [ # Bouclage guitares - Bouton 10
        [
            SendOSC(slport, '/sl/2/hit', 'overdub'),
            SendOSC(slport, '/sl/3/hit', 'overdub')
            ] >> Discard()
        ],
    ProgramFilter(11) >> [ # Reverse All - Bouton 11
        [

            SendOSC(slport, '/sl/-1/set', 'dry', 0),
            SendOSC(slport, '/sl/-1/hit', 'reverse'),
            SendOSC(slport, '/sl/-1/set', 'rate', 0.5),

            SendOSC(klickport, '/klick/metro/stop')
            ] >> Discard()
        ]
    ]



#### RUN ###################################################

run(
    scenes = {
        1: SceneGroup("Acte 0", [
  		Scene("Bass ORL",
                      [
                        acte0,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte0,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte0,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte0,
                        dag_basspedal,
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte0,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte0,
                        dag_vxpedal
                        ]
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
                      [
                        acte1,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte1,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte1,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte1,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte1,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte1,
                        dag_vxpedal
                        ]
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
                      [
                        acte2,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte2,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte2,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte2,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte2,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte2,
                        dag_vxpedal
                        ]
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
                      [
                        forainacte2,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        forainacte2,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        forainacte2,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        forainacte2,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        forainacte2,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        forainacte2,
                        dag_vxpedal
                        ]
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
                      [
                        acte3,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte3,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte3,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte3,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte3,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte3,
                        dag_vxpedal
                        ]
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
                      [
                        acte3partII,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte3partII,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte3partII,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte3partII,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte3partII,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte3partII,
                        dag_vxpedal
                        ]
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
        7: SceneGroup("Acte III Part III", [
  		Scene("Bass ORL",
                      [
                        acte3partIII,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte3partIII,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte3partIII,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte3partIII,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte3partIII,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte3partIII,
                        dag_vxpedal
                        ]
		),
		Scene("Boucles",
                      acte3partIII,
		),
		Scene("Bank Select",
                      acte3partIII
		),
		Scene("Tune Select",
                      acte3partIII
		)
	    ]
        ),
        8: SceneGroup("Acte IV", [
  		Scene("Bass ORL",
                      [
                        acte4,
                        orl_basspedal
                        ]
		),
		Scene("Guitar ORL",
                      [
                        acte4,
                        orl_gtrpedal
                        ]
		),
		Scene("Voix ORL",
                      [
                        acte4,
                        orl_vxpedal
                        ]
	        ),
		Scene("Bass Dag",
                      [
                        acte4,
                        dag_basspedal
                        ]
		),
		Scene("Guitar Dag",
                      [
                        acte4,
                        dag_gtrpedal
                        ]
		),
		Scene("Voix Dag",
                      [
                        acte4,
                        dag_vxpedal
                        ]
		),
		Scene("Boucles",
		    acte4
		),
		Scene("Bank Select",
		    acte4
		),
		Scene("Tune Select",
		    acte4
		)
	    ]
        ),

    },
)

