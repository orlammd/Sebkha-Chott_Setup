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
    OSCInterface(56422, "osc.udp://CtrlOrl:56423"),
    OSCCustomInterface(56418),
    AutoRestart()
)


#### Ports OSC ################################################

klickport = 1234
slport = 9951
testport = 1111
qlcport = ("192.168.0.13", 7770)
#qlcport = 7777
videoCport = ("192.168.0.110", 56418)
videoCseqport = 12346
qlcseqport = 12345 #("CtrlRegie", 12345)
#videoseqport = ("CtrlDag", 12346)
mainseqport = ("CtrlDag", 12343)
desktoporlport = ("CtrlOrl", 12345)

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
gtrdag_octaverdown = SendOSC(guitarsport, '/strip/FX_Gtr_Dag_2/AM%20pitchshifter/Pitch%20shift', 0.0655) >> Discard()
gtrdag_octavernull = SendOSC(guitarsport, '/strip/FX_Gtr_Dag_2/AM%20pitchshifter/Pitch%20shift', 0.2) >> Discard()

gtrdag_mute = SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 1.0) >> Discard()
gtrdag_on = [
    SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 0.0),
    gtrdag_octavernull
    ] >> Discard()
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
    SendOSC(guitarsport, '/strip/Scape_Gtr_Dag/Gain/Mute', 0.0),
    SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 1.0)
    ] >> Discard()
gtrdag_chromdelay_off = [
    SendOSC(guitarsport, '/strip/Scape_Gtr_Dag/Gain/Mute', 1.0),
    SendOSC(guitarsport, '/strip/Guitar_Dag/Gain/Mute', 0.0)
#    SendOSC(guitarsport, '/strip/Scape_Gtr_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 0.0),
#    SendOSC(guitarsport, '/strip/Scape_Gtr_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/dry', 1.0)
    ] >> Discard()

#### Bass ####

# Dag
bassdag_mute = [
    SendOSC(bassesport, '/strip/Bass_Dag/Gain/Mute', 1.0) >> Discard(),
    SendOSC(bassesport, '/strip/Octaver_Bass_Dag/Gain/Mute', 1.0) >> Discard(),
    SendOSC(bassesport, '/strip/FX_Bass_Dag/Gain/Mute', 1.0) >> Discard(),
    SendOSC(bassesport, '/strip/Disto_Bass_Dag/Gain/Mute', 1.0) >> Discard(),
    ]
bassdag_on = SendOSC(bassesport, '/strip/Bass_Dag/Gain/Mute', 0.0) >> Discard()
bassdag_octaver_on = [
    SendOSC(bassesport, '/strip/Oct_Bass_Dag/Gain/Mute', 0.0),
    ] >> Discard()
bassdag_octaver_off = [
    SendOSC(bassesport, '/strip/Oct_Bass_Dag/Gain/Mute', 1.0),
    ] >> Discard()
bassdag_fx_on = [
    SendOSC(bassesport, '/strip/FX_Bass_Dag/Gain/Mute', 0.0),
    ] >> Discard()
bassdag_fx_off = [
    SendOSC(bassesport, '/strip/FX_Bass_Dag/Gain/Mute', 1.0),
    ] >> Discard()
bassdag_disto_on = [
    SendOSC(bassesport, '/strip/Disto_Bass_Dag/Gain/Mute', 0.0),
    ] >> Discard()
bassdag_disto_off = [
    SendOSC(bassesport, '/strip/Disto_Bass_Dag/Gain/Mute', 1.0),
    ] >> Discard()

# ORL
bassorl_mute = [
    SendOSC(bassesport, '/strip/Bass_ORL/Gain/Mute', 1.0),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/Gain/Mute', 1.0),
    SendOSC(bassesport, '/strip/Oct_Bass_ORL/Gain/Mute', 1.0),
    SendOSC(bassesport, '/strip/Disto_Bass_ORL/Gain/Mute', 1.0)
    ] >> Discard()
bassorl_on = [
    SendOSC(bassesport, '/strip/Oct_Bass_ORL/Gain/Mute', 1.0),
    SendOSC(bassesport, '/strip/Bass_ORL/Gain/Mute', 0.0),
#    SendOSC(bassesport, '/strip/BassFX_ORL/Gain/Mute', 0.0)
    ] >> Discard()
bassorl_octaver_on = [
    SendOSC(bassesport, '/strip/Oct_Bass_ORL/Gain/Mute', 0.0),
    ] >> Discard()
bassorl_octaver_off = [
    SendOSC(bassesport, '/strip/Oct_Bass_ORL/Gain/Mute', 1.0),
    ] >> Discard()
bassorl_reverb_on = [
    SendOSC(bassesport, '/strip/FX_Bass_ORL/Gain/Mute', 0.0),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Delay/unscaled', 0.021),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Xover/unscaled', 350),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/RT-low/unscaled', 3.40),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/RT-mid/unscaled', 3.35),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Damping/unscaled', 4100),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F1-freq/unscaled', 160),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F1-gain/unscaled', 2.00),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F2-freq/unscaled', 950),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F2-gain/unscaled', 2.00),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Output%20mix/unscaled', 1.00),
    ] >> Discard()
bassorl_reverb_off = [
    SendOSC(bassesport, '/strip/FX_Bass_ORL/Gain/Mute', 1.0),
    ] >> Discard()
bassorl_disto_on = [
    SendOSC(bassesport, '/strip/Disto_Bass_ORL/Gain/Mute', 0.0),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/Gain/Mute', 0.0),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Delay/unscaled', 0.020),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Xover/unscaled', 500),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/RT-low/unscaled', 1.95),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/RT-mid/unscaled', 3.60),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Damping/unscaled', 1950),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F1-freq/unscaled', 160),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F1-gain/unscaled', 2.00),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F2-freq/unscaled', 800),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/F2-gain/unscaled', 3.50),
    SendOSC(bassesport, '/strip/FX_Bass_ORL/zita-reverb/Output%20mix/unscaled', 1.00),
    ] >> Discard()
bassorl_disto_off = [
    SendOSC(bassesport, '/strip/Disto_Bass_ORL/Gain/Mute', 1.0),
    ] >> Discard()
# TEMPORAIRE - TRANSITION PACKAGE
bassorl_fx_on = Discard()
bassorl_fx_off = Discard()
# TEMPORAIRE - TRANSITION PACKAGE


#### Vocals ####

#Dag
flutesolo_on = [
#    SendOSC(vocalsport, '/strip/Vx_Dag/Smooth%20Decimator/Resample%20rate', 4000.0),
#    SendOSC(vocalsport, '/strip/Vx_Dag/Ringmod%20with%20LFO/Modulation%20depth%20(0=none%2C%201=AM%2C%202=RM)', 1.0),
#    SendOSC(vocalsport, '/strip/Vx_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 1.0)
    SendOSC(vocalsport, '/strip/Scape_Vx_Dag/Gain/Mute', 0.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/Gain/Mute', 1.0),
    ] >> Discard()

flutesolo_off =[
#    SendOSC(vocalsport, '/strip/Vx_Dag/Smooth%20Decimator/Resample%20rate', 48000.0),
#    SendOSC(vocalsport, '/strip/Vx_Dag/Ringmod%20with%20LFO/Modulation%20depth%20(0=none%2C%201=AM%2C%202=RM)', 0.0),
#    SendOSC(vocalsport, '/strip/Vx_Dag/C%2A%20Scape%20-%20Stereo%20delay%20with%20chromatic%20resonances/blend', 0.0)
    SendOSC(vocalsport, '/strip/Scape_Vx_Dag/Gain/Mute', 1.0),
    SendOSC(vocalsport, '/strip/Vx_Dag/Gain/Mute', 0.0),
    ] >> Discard()


#### Stop ####

stop = [
        Program(2) >> cseqtrigger,
#        vxfx_ohreland,
        SendOSC(slport, '/sl/-1/hit', 'pause_on') >> Discard(),
        SendOSC(klickport, '/klick/metro/stop') >> Discard(),

	abass_mute,
	actlead_mute,

        flutesolo_off,

        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            ] >> Discard()
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
    ProgramFilter(20) >> bassorl_disto_on,
    ProgramFilter(21) >> bassorl_octaver_on,
    ProgramFilter(22) >> bassorl_reverb_on,
    ProgramFilter(23) >> [
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off
        ]
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
    ProgramFilter(17) >> SendOSC(slport, '/sl/1/hit', 'multiply') >> Discard(),
    ProgramFilter(18) >> SendOSC(slport, '/sl/1/hit', 'trigger') >> Discard(),

    ProgramFilter(20) >> bassdag_disto_on,
    ProgramFilter(21) >> bassdag_octaver_on,
    ProgramFilter(22) >> bassdag_fx_on,
    ProgramFilter(23) >> [
        bassdag_fx_off,
        bassdag_disto_off,
        bassdag_octaver_off
        ]
    ]
dag_gtrpedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(13) >> gtrdag_on,
    ProgramFilter(21) >> SendOSC(slport, '/sl/3/hit', 'record') >> Discard(),
    ProgramFilter(22) >> SendOSC(slport, '/sl/3/hit', 'pause_on') >> Discard(),
    ProgramFilter(23) >> SendOSC(slport, '/sl/3/hit', 'overdub') >> Discard(),
    ProgramFilter(17) >> SendOSC(slport, '/sl/3/hit', 'multiply') >> Discard(),
    ProgramFilter(18) >> SendOSC(slport, '/sl/3/hit', 'trigger') >> Discard(),

    ProgramFilter(23) >> gtrdag_clean,
    ProgramFilter(22) >> gtrdag_disto,
    ProgramFilter(21) >> gtrdag_chromdelay_on,
    ProgramFilter(20) >> gtrdag_chromdelay_off
    ]
dag_vxpedal = PortFilter('PBCtrlIn') >> [
    ProgramFilter(21) >> SendOSC(slport, '/sl/5/hit', 'record') >> Discard(),
    ProgramFilter(22) >> SendOSC(slport, '/sl/5/hit', 'pause_on') >> Discard(),
    ProgramFilter(23) >> SendOSC(slport, '/sl/5/hit', 'overdub') >> Discard(),
    ]

#### Scenes ################################################

#### ACTE 0 ####
acte0 = PortFilter('PBCtrlIn') >> [
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(127) >> [ # Intro - EXCEPTION
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        Program(2) >> achords,
        Program(2) >> alead,
        abass_mute,
        actlead_mute,
        NoteOff('c#2', 0) >> actlead,

        gtrorl_mute,
        gtrdag_mute,
        bassdag_mute,
        bassorl_mute,

        ],
    ProgramFilter(6) >> [ # Lancement - Bouton 6
        stop,
        [


            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),

            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcport, '/CC/Red/Segment/4', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/4', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CC/Red/Segment/5', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/5', 255),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/alpha', 99, 0.95),
            SendOSC(videoCport, '/pyta/slide/rgb', 99, 0, 0, 0),
            SendOSC(videoCport, '/pyta/slide/visible', 99, 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 480),
            SendOSC(videoCseqport, '/Sequencer/Trigger', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'CoffeeNoise', 1)
            ] >> Discard(),

        gtrdag_mute,
        gtrorl_clean,
        bassorl_mute,
        bassdag_on,
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off
        ],
    ProgramFilter(7) >> [ # Refrain - Bouton 7
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),


            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 0, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 1800),
            SendOSC(videoCseqport, '/Sequencer/Trigger', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A0 Refrain Alpha', 1)
            ] >> Discard(),
        Program(69) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(16) >> alead,

        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_on,
        bassdag_disto_on,
        bassdag_fx_off,
        bassdag_octaver_off,

        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            SendOSC(qlcport, '/CC/Blue/Segment/All', 0),
            SendOSC(qlcport, '/CJ/Blue/Segment/All', 0),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'Theme', 1),
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),
            ] >> Discard()
        ],
    ProgramFilter(8) >> [ # Couplet - Bouton 8
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'Theme', 0),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'Couplet', 1),
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 440),
            SendOSC(qlcport, '/BC/White/Segment/All', 0),
            SendOSC(qlcport, '/BJ/White/Segment/All', 0),
            SendOSC(qlcport, '/CC/Red/Segment/All', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 0),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 180),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 180),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 180),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 0.15, 0, 0.15), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 1800),
            SendOSC(videoCseqport, '/Sequencer/Trigger', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A0 Refrain Alpha', 1)
            
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
        bassdag_fx_off,
        bassdag_disto_off,
        bassorl_mute,

        [
            SendOSC(qlcport, '/stop', 1),
            SendOSC(qlcport, '/scene/36yulaViolet', 1),
            ] >> Discard() 
        ],
    ProgramFilter(9) >> [ # Say Hello - Bouton 9
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 8),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),

            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 180),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 180),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 180),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 960),
            SendOSC(videoCseqport, '/Sequencer/Trigger', 1),
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 1, 1),
            SendOSC(videoCport, '/pyta/slide/visible', 99, 1),
            SendOSC(videoCport, '/pyta/slide/rgb', 99, 0, 0, 0),
            SendOSC(videoCseqport, '/Sequencer/Scene/Play', 'A0 Say Hello'), 
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A0 Say Hello', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A0 Say Hello Alpha', 1)            
            ] >> Discard(),
#        SubSceneSwitch(2),
        Program(70) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(9) >> alead,

        gtrorl_mute,
        gtrdag_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_on,
        bassdag_on,
        bassdag_disto_off,
        bassdag_fx_off,

        [ #TODO : vérifier ce que ça fout là
            SendOSC(qlcport, '/stop', 1),
            SendOSC(qlcport, '/scene/36orlViolet', 1),
            SendOSC(qlcport, '/scene/36yulaViolet', 1)
            ]>> Discard(),
        ],
    ProgramFilter(10) >> [ # Tears Are Dropping - Bouton 10
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 8),
            SendOSC(slport, '/set', 'tempo', 120),

            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),

            SendOSC(qlcport, '/BC/Red/Segment/All', 70),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 70),


            ] >> Discard(),
        Program(71) >> cseqtrigger,
        actlead_mute,
        Program(6) >> abass,
        Program(1) >> achords,
        Program(1) >> aclass,
        Program(11) >> alead,

        gtrorl_disto,
        gtrdag_mute,
        bassorl_mute,
        bassdag_on,
        bassdag_disto_off,
        bassdag_fx_off,

        ],
    ProgramFilter(11) >> [ # Intro classique - Bouton 11
        stop,
        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 20),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 20),
            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 0.1, 0, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)

            ] >> Discard(),
    
    

        gtrorl_mute,
        gtrdag_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_on,
        bassorl_octaver_on,
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
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,

        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 150),

            SendOSC(qlcport, '/CC/Red/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 80),
            SendOSC(qlcport, '/CC/Red/Segment/3', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/3', 150),
            SendOSC(qlcport, '/CC/Green/Segment/3', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 80),
            SendOSC(qlcport, '/CC/Red/Segment/5', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 150),
            SendOSC(qlcport, '/CC/Green/Segment/5', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 80),
            SendOSC(qlcport, '/CC/Red/Segment/7', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/7', 150),
            SendOSC(qlcport, '/CC/Green/Segment/7', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 80),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 0, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)


            ] >> Discard()
        ],
    ProgramFilter(3) >> [ # Intro Up - Bouton 3
        Program(6) >> Channel(2) >> seqtrigger,
        [
            SendOSC(qlcport, '/scene/flip36yulaBlanc', 1),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A1 Gals Grouille', 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 960),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 0, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)

            ] >> Discard()
        ],
    ProgramFilter(4) >> [ # Couplet - Bouton 4
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

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 0.2, 0, 0),
	    SendOSC(videoCport, '/pyta/slide/scale', 79, 800, 800, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)

            ] >> Discard(),
        
        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on,
        bassorl_octaver_on,
        bassorl_reverb_off,
        bassorl_disto_off,

        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 150),

            SendOSC(qlcport, '/CC/Red/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 80),
            SendOSC(qlcport, '/CC/Red/Segment/3', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/3', 150),
            SendOSC(qlcport, '/CC/Green/Segment/3', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 80),
            SendOSC(qlcport, '/CC/Red/Segment/5', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 150),
            SendOSC(qlcport, '/CC/Green/Segment/5', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 80),
            SendOSC(qlcport, '/CC/Red/Segment/7', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/7', 150),
            SendOSC(qlcport, '/CC/Green/Segment/7', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 80),
            ] >> Discard()
        ],
    ProgramFilter(5) >> [ # Couplet Ternaire - Bouton 6 #TODO
        Program(69) >> cseqtrigger,
        
        Program(10) >> achords,
        Program(3) >> alead,

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

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 0.2, 0, 0),
	    SendOSC(videoCport, '/pyta/slide/scale', 79, 800, 800, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)


            ] >> Discard(),
        
        bassdag_mute,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_on,
        bassorl_reverb_off
        ],
    ProgramFilter(6) >> [ # Bustas - Bouton 6
        Program(66) >> cseqtrigger,
        Program(15) >> achords,
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

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 0.2, 0, 0),
	    SendOSC(videoCport, '/pyta/slide/scale', 79, 800, 800, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)

            ] >> Discard(),

        gtrorl_mute,
        gtrdag_clean,
        bassdag_mute,
        bassorl_on,
        bassorl_reverb_off,
        bassorl_disto_off,
        bassorl_octaver_on,

        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 150),

            SendOSC(qlcport, '/CC/Red/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 80),
            SendOSC(qlcport, '/CC/Red/Segment/3', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/3', 150),
            SendOSC(qlcport, '/CC/Green/Segment/3', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 80),
            SendOSC(qlcport, '/CC/Red/Segment/5', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 150),
            SendOSC(qlcport, '/CC/Green/Segment/5', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 80),
            SendOSC(qlcport, '/CC/Red/Segment/7', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/7', 150),
            SendOSC(qlcport, '/CC/Green/Segment/7', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 80),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AI Couplet', 1),
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),
            ] >> Discard()

        ],
    ProgramFilter(7) >> [ # Post Bustas - Bouton 7
        Program(67) >> cseqtrigger,
        
        Program(1) >> achords,
        Program(1) >> abass,
        Program(1) >> alead,
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
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,

        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),

            SendOSC(qlcport, '/CC/Red/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 80),
            SendOSC(qlcport, '/CC/Red/Segment/3', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/3', 150),
            SendOSC(qlcport, '/CC/Green/Segment/3', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 80),
            SendOSC(qlcport, '/CC/Red/Segment/5', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 150),
            SendOSC(qlcport, '/CC/Green/Segment/5', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 80),
            SendOSC(qlcport, '/CC/Red/Segment/7', 150),
            SendOSC(qlcport, '/CJ/Red/Segment/7', 150),
            SendOSC(qlcport, '/CC/Green/Segment/7', 80),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 80),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AI Couplet', 1),
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),
            

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 0, 0),
	    SendOSC(videoCport, '/pyta/slide/scale', 79, 800, 800, 0),
	    SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', "A1 StrangeWorld Sortie Reggae", 1), 
	    SendOSC(videoCseqport, '/Sequencer/Set_bpm', 960),
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)

            ] >> Discard()
        ],
    ProgramFilter(8) >> [ # MathoMag I - Bouton 8
        Program(68) >> cseqtrigger,
        
        Program(10) >> achords,
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
        
        gtrdag_mute,
        gtrorl_mute,
        bassdag_on,
        bassdag_fx_off,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,

        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AI Pont Guitare', 1),
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
	    SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 80, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 81, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 82, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 83, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 84, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 85, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 86, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 87, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 88, 0, 0.5, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 89, 0, 0.5, 0),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A1 Liba Libanese', 1),
            SendOSC(videoCseqport, '/Sequencer/Trigger', 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 480),

            SendOSC(qlcport, '/CC/Red/Segment/1', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/1', 0),
            SendOSC(qlcport, '/CC/Green/Segment/1', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 0),
            SendOSC(qlcport, '/CC/Red/Segment/3', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/3', 0),
            SendOSC(qlcport, '/CC/Green/Segment/3', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 0),
            SendOSC(qlcport, '/CC/Red/Segment/5', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 0),
            SendOSC(qlcport, '/CC/Green/Segment/5', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 0),
            SendOSC(qlcport, '/CC/Red/Segment/7', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/7', 0),
            SendOSC(qlcport, '/CC/Green/Segment/7', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 0),

            SendOSC(qlcport, '/BC/Red/Segment/1', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 120),
            SendOSC(qlcport, '/BC/Red/Segment/3', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 120),
            SendOSC(qlcport, '/BC/Red/Segment/5', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/5', 120),
            SendOSC(qlcport, '/BC/Red/Segment/7', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/7', 120),
            ] >> Discard()
        
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
            
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        bassdag_disto_on,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,

        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Scene/Play', 'AI MathoMag II'), 
            
            SendOSC(qlcport, '/CC/Green/Segment/1', 120),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 120),
            SendOSC(qlcport, '/CC/Green/Segment/3', 120),
            SendOSC(qlcport, '/CJ/Green/Segment/3', 120),
            SendOSC(qlcport, '/CC/Green/Segment/5', 120),
            SendOSC(qlcport, '/CJ/Green/Segment/5', 120),
            SendOSC(qlcport, '/CC/Green/Segment/7', 120),
            SendOSC(qlcport, '/CJ/Green/Segment/7', 120),

            SendOSC(qlcport, '/BC/Red/Segment/1', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 120),
            SendOSC(qlcport, '/BC/Red/Segment/3', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 120),
            SendOSC(qlcport, '/BC/Red/Segment/5', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/5', 120),
            SendOSC(qlcport, '/BC/Red/Segment/7', 120),
            SendOSC(qlcport, '/BJ/Red/Segment/7', 120),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
	    SendOSC(videoCport, '/pyta/slide/visible', -1, 0),

            ] >> Discard()
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
        
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_on,
        bassdag_disto_on,
        bassdag_octaver_off,

        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AI Metal',1),
            
            SendOSC(qlcport, '/CC/Blue/Segment/All', 200),
            SendOSC(qlcport, '/CJ/Blue/Segment/All', 200),
            SendOSC(qlcport, '/CC/Green/Segment/All', 200),
            SendOSC(qlcport, '/CJ/Green/Segment/All', 200),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),            
            ] >> Discard()
        ],
    ProgramFilter(11) >> [ # Forain I / Strange World - Bouton 11
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

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A1 Gals Grouille', 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 960),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/rgb', 79, 1, 0, 0), 
            SendOSC(videoCport, '/pyta/slide/visible', 79, 1)
            ] >> Discard(),

        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_disto_on,
        bassdag_octaver_off,
        [
            SendOSC(qlcport, '/AllStop', 1),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 480),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AI Forain',1),
            
            SendOSC(qlcport, '/BC/Red/Segment/All', 80),
            SendOSC(qlcport, '/BC/Green/Segment/All', 80),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 80),
            SendOSC(qlcport, '/BJ/Green/Segment/All', 80),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            
            ] >> Discard()
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
        bassorl_mute,

        [

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
                        
            SendOSC(qlcport, '/BC/Blue/Segment/1', 200),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 200),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 200),
            SendOSC(qlcport, '/CC/Blue/Segment/1', 200),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 200),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 200),
            SendOSC(qlcport, '/CJ/Blue/Segment/8', 200),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 200),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
     
            ] >> Discard()
        ],
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
        bassorl_on,
        bassorl_octaver_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        gtrdag_octaverdown,

        [
     
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
                        
            SendOSC(qlcport, '/BC/Blue/Segment/All', 210),
            SendOSC(qlcport, '/BJ/Blue/Segment/All', 210),
            SendOSC(qlcport, '/CJ/Blue/Segment/All', 210),
            SendOSC(qlcport, '/CC/Blue/Segment/All', 210),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),


            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A2 Had Gadya Grouille', 1),
            SendOSC(videoCseqport, '/Sequencer/Sequence/Enable', 'A2 Had Gadya Grouille Bis', 1),
            SendOSC(videoCseqport, '/Sequencer/Set_bpm', 480),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCport, '/pyta/slide/visible', 99, 1),
            SendOSC(videoCport, '/pyta/slide/alpha', 99, 0.85),
            SendOSC(videoCport, '/pyta/slide/visible', 70, 1),
            SendOSC(videoCport, '/pyta/slide/alpha', 70, 0.6),

            ] >> Discard()
        ],
    ProgramFilter(4) >> [ # Filtre Pont Had Gadya & suite - Bouton 4
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
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_on,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcseqport, '/Sequencer/Scene/Play', 'AII HG2'), 
            SendOSC(qlcport, '/BC/Blue/Segment/1', 200),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 200),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 200),
            SendOSC(qlcport, '/CC/Blue/Segment/1', 200),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 200),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 200),
            SendOSC(qlcport, '/CJ/Blue/Segment/8', 200),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 200),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),

            SendOSC(videoCseqport, '/Sequencer/DisableAll', 1),
            SendOSC(videoCport, '/pyta/slide/visible', -1, 0),
            SendOSC(videoCseqport, '/Sequencer/Scene/Play', 'AII HG2')

            ] >> Discard()
        ],
    ProgramFilter(5) >> [ # Lumières - bouton 5
        [
            ] >> Discard()
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
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255)
            ] >> Discard()
        
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
        gtrorl_mute,
        bassorl_on,
        bassorl_reverb_off,
        bassorl_disto_off,
        bassorl_octaver_off,

        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 150),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0)
            ] >> Discard()
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
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, 'Sequencer/Scene/Play', 'AII MEP')
            ] >> Discard()
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
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_octaver_off,
        bassorl_disto_off,
        bassorl_reverb_off,
        
        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255)
            ] >> Discard()
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
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_reverb_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255)
            ] >> Discard(),
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
        bassorl_mute,
        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 150),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase1',1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase2',1),
            ] >> Discard()
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
        Program(13) >> Channel(2) >> seqtrigger,
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
        bassdag_disto_on,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_on,
        bassorl_reverb_off,
        [
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 600),
            ] >> Discard()
        ],
    ProgramFilter(6) >> [ # Forain Léger Avant Baroque - Bouton 6
        Program(67) >> cseqtrigger,
        Program(1) >> actlead,
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
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,
        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 150),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 150),
            SendOSC(qlcport, '/CC/Green/Segment/1', 150),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 150),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255)
            ] >> Discard(),

        ],
    ProgramFilter(7) >> [ # Barocko by MX - Bouton 7
        Program(71) >> cseqtrigger,
        Program(1) >> abass,
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
        bassorl_mute,

        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 0),
            SendOSC(qlcport, '/CC/Green/Segment/1', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 150)
            ] >> Discard()
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
        bassorl_on,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 150),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase3',1),            
            ] >> Discard()
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
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_on,
        [
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Green/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 255),
            ] >> Discard()
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
        bassorl_on,
        bassorl_octaver_on,
        bassorl_disto_on,
        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 600),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase1',1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase2',1),
            ] >> Discard(),

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
        bassdag_disto_off,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrorl_clean,
        gtrdag_mute,
        bassorl_mute,
        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 150),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 150)
            ] >> Discard(),
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
        bassdag_disto_on,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_octaver_off,
        gtrorl_mute,
        gtrdag_mute,
        [
            SendOSC(qlcport, '/CC/Green/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 255),
            ] >> Discard(),
        
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
        bassorl_on,
        bassorl_reverb_on, # TENTATIVE !!!!!!
        bassorl_octaver_off,
        bassorl_disto_off,
        [
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/tail",0.85),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/damping",0.4),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/blend",0.4),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/Gain/Gain%20(dB)",0.945),
            SendOSC(vocalsport, "/strip/Vx_ORL/Gain/Gain%20(dB)",0.92),
            ] >> Discard(),
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            SendOSC(qlcport, '/CC/Green/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 255),
            ] >> Discard()
        
        ],
    ProgramFilter(5) >> [ # Pont glauque - Bouton 5
        [
            Program(14),
            Program(15)
            ] >> Channel(2) >> seqtrigger,
        [
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/tail",0.3),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/damping",0.62),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/blend",0.16),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/Gain/Gain%20(dB)",0.92),
            SendOSC(vocalsport, "/strip/Vx_ORL/Gain/Gain%20(dB)",0.945),
            ] >> Discard(),
        actlead_mute,
        [
            SendOSC(qlcport, '/stop', 1),
            SendOSC(qlcport, '/scene/36barresBleu', 1),
            ] >> Discard()
        ],
    ProgramFilter(6) >> [ # 6/8 Magasin - Bouton 6
        Program(67) >> cseqtrigger,
        Program(1) >> achords,
        Program(1) >> abass,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 12),
            SendOSC(slport, '/set', 'tempo', 90),
            SendOSC(klickport, '/klick/simple/set_tempo', 90),
            SendOSC(klickport, '/klick/simple/set_meter', 6, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        [
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/tail",0.3),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/damping",0.62),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/C%2A%20PlateX2%20-%20Versatile%20plate%20reverb%2C%20stereo%20inputs/blend",0.16),
            SendOSC(vocalsport, "/strip/FX_Vx_ORL/Gain/Gain%20(dB)",0.92),
            SendOSC(vocalsport, "/strip/Vx_ORL/Gain/Gain%20(dB)",0.945),
            ] >> Discard(),
        bassdag_mute,
        gtrdag_disto,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 180),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase4',1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase5',1),
            SendOSC(qlcport, '/CC/Green/Segment/1', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BC/Red/Segment/All', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 255),
            ] >> Discard()
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

        bassdag_on,
        gtrdag_clean,
        gtrorl_mute,
        bassorl_on,
        bassorl_octaver_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassdag_disto_off,
        bassdag_fx_off,
        [
            SendOSC(qlcport, '/BC/Red/Segment/All', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 0),
            SendOSC(qlcport, '/CC/Green/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 255),
            ] >> Discard()
        
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
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_disto_on,
        bassdag_octaver_off,
        [
            SendOSC(qlcport, '/CC/Green/Segment/1', 0),
            SendOSC(qlcport, '/CJ/Green/Segment/1', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 0),
            SendOSC(qlcport, '/CC/Blue/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/All', 255),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 120),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase3',1),
            ] >> Discard()
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
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/CC/Blue/Segment/All', 0),
            SendOSC(qlcport, '/CJ/Blue/Segment/All', 0),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 120),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase6',1),
            ] >> Discard()
        
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
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,
        flutesolo_on,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),

            SendOSC(qlcport, '/CC/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CC/Red/Segment/4', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/4', 200),
            SendOSC(qlcport, '/CC/Red/Segment/5', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 200),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            ] >> Discard(),

        Program(117) >> seq24once,
        SceneSwitch(6)

        ],
    ]

acte3partII =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Acte III - Couplet II - Bouton 2 - Solo Yom
        Program(65) >> cseqtrigger,
     #   Program(1) >> abass,
	abass_mute,
        Program(11) >> alead,
	Program(8) >> achords,
	Program(10) >> actlead,
#        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 10),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),

	    SendOSC(mxsynthport, '/strip/MxChords/Gain/Mute', 1.0),
	    SendOSC(mxsynthport, '/strip/MxCtLead/Gain/Mute', 1.0),

	    SendOSC(desktoporlport, '/Desktop', 1),

            ] >> Discard(),
        
        bassdag_on,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_on,
        bassorl_disto_off,
        bassdag_disto_off,
        bassorl_octaver_off,
        bassdag_octaver_off,
        bassorl_reverb_off,
        bassdag_fx_off,
        flutesolo_off,
        [
            SendOSC(qlcport, '/CC/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CC/Red/Segment/4', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/4', 200),
            SendOSC(qlcport, '/CC/Red/Segment/5', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 200),

            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 255),
            SendOSC(qlcport, '/BC/Red/Segment/1', 200),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 200),
            SendOSC(qlcport, '/BC/Red/Segment/8', 200),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 200),

            ] >> Discard()

        ],
    ProgramFilter(3) >> [ # Acte III - Thème Klezmer Guitare
        [
            stop,
            gtrorl_mute,
            gtrdag_clean,
            bassorl_on,
            bassorl_reverb_on,
            bassorl_disto_off,
            bassorl_octaver_off,
        [
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 5, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
            ]
        ],
    ProgramFilter(4) >> [ # Acte III - Klezmer Klub
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

        bassdag_on,
        bassdag_octaver_off,
        bassdag_disto_off,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,
        bassorl_fx_off,
        [
            SendOSC(qlcport, '/CC/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/4', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/5', 255),
            SendOSC(qlcport, '/CC/Red/Segment/4', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/4', 200),
            SendOSC(qlcport, '/CC/Red/Segment/5', 200),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 200),

	    SendOSC(mxsynthport, '/strip/MxChords/Gain/Mute', 0.0),
	    SendOSC(mxsynthport, '/strip/MxCtLead/Gain/Mute', 0.0),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 180),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase5',1),
            ] >> Discard()
        ],
    ProgramFilter(5) >> [ # Acte III - Couplet Ternaire - Bouton 5
        Program(67) >> cseqtrigger,
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

        bassdag_on,
        bassdag_disto_on,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 120),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase5',1),
            ] >> Discard()
        ],
    ProgramFilter(6) >> [ # Acte III - Klezmer Death - Bouton 6
        Program(71) >> cseqtrigger,
        Program(7) >> abass,
        Program(1) >> achords,
        Program(8) >> alead,
        actlead_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_disto_on,
        bassdag_on,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/AllStop', 1),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 180),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase3',1),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase4',1),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase5',1),
            ] >> Discard()
        ],
    ProgramFilter(7) >> [ # 6/8 Safety Bourre - Bouton 7
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
        bassdag_disto_on,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/CC/Blue/Segment/4', 0),
            SendOSC(qlcport, '/CJ/Blue/Segment/4', 0),
            SendOSC(qlcport, '/CC/Blue/Segment/5', 0),
            SendOSC(qlcport, '/CJ/Blue/Segment/5', 0),
            SendOSC(qlcport, '/CC/Red/Segment/4', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/4', 0),
            SendOSC(qlcport, '/CC/Red/Segment/5', 0),
            SendOSC(qlcport, '/CJ/Red/Segment/5', 0),

            SendOSC(qlcport, '/BC/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/1', 0),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Blue/Segment/8', 0),
            SendOSC(qlcport, '/BC/Red/Segment/1', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 0),
            SendOSC(qlcport, '/BC/Red/Segment/8', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 0),

            SendOSC(qlcport, '/BC/Red/Segment/All', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 255),
            ] >> Discard()
        ],
    ProgramFilter(8) >> [ # Solo guitare arpège - Bouton 8
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
        bassorl_mute,
        [
            SendOSC(qlcport, '/BC/Red/Segment/All', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 0),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            ] >> Discard()
        
        ],
    ProgramFilter(9) >> [ # Folk - Bouton 9
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
        bassorl_mute,
        [
            SendOSC(qlcport, '/BC/Red/Segment/All', 50),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 50),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            ] >> Discard()
        
        ],
    ProgramFilter(10) >> [ # Evil - Bouton 10
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
        bassdag_disto_on,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_disto,
        bassorl_mute,
        [
            SendOSC(qlcport, '/BC/Red/Segment/All', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            ] >> Discard()
        ],
    ProgramFilter(11) >> [ # Solo batterie - Bouton 11
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
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,
        [
            SendOSC(qlcport, '/BC/Red/Segment/All', 100),
            SendOSC(qlcport, '/BJ/Red/Segment/All', 100),
            SendOSC(qlcport, '/CC/Red/Segment/All', 100),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 100),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            ] >> Discard()
        
        
        ],
    ]
acte3partIII =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # 13/8 Ping - Bouton 2
        Program(72) >> cseqtrigger,
        abass_mute,
        actlead_mute,
        gtrdag_mute,
        gtrorl_mute,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 90),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 90),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', '---------Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            ] >> Discard()
        ],
    ProgramFilter(3) >> [ # 13/8 Prog - Bouton 3
        Program(65) >> cseqtrigger,
        
#        Program(1) >> abass,
        abass_mute,
        Program(10) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'X-x-x-x-x-x-x'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        bassdag_disto_off,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_off,
        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            ] >> Discard()

        ],
    ProgramFilter(4) >> [ # 13/8 Prog Jungle - Bouton 4
        Program(73) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(10) >> achords,
        actlead_mute,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxxxxxxxxxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        bassdag_disto_off,
        bassdag_fx_off,
        bassdag_octaver_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,
        [
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),

            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/BC/Green/Segment/1', 255),
            SendOSC(qlcport, '/BC/Green/Segment/1', 255),
            SendOSC(qlcport, '/BC/Green/Segment/8', 255),
            SendOSC(qlcport, '/BC/Green/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Green/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Green/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Green/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Green/Segment/8', 255),
 
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            ] >> Discard(),

        ],
    ProgramFilter(5) >> [ # 13/8 Organic Only - Bouton 5
        stop,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'X-x-x-x-x-x-x'),
            SendOSC(klickport, '/klick/metro/start'),

            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 200),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 200),

            ] >> Discard(),        

        bassdag_on,
        bassorl_on,
        bassdag_fx_off,
        bassdag_disto_off,
        bassdag_octaver_off,
        bassorl_disto_on,
        bassorl_reverb_on,
        bassorl_octaver_off,
        gtrorl_mute,
        gtrdag_mute
        ],
    ProgramFilter(6) >> [ # 13/8 Prog Thème - Bouton 6
        Program(70) >> cseqtrigger,

        Program(1) >> abass,
        Program(1) >> achords,
        Program(1) >> alead,
        Program(10) >> actlead,        
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 26),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 13, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'X-x-x-x-x-x-x'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_on,
        bassdag_disto_on,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/1', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/BC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            ] >> Discard()

        ],
    ProgramFilter(7) >> [ # 13/8 Prog bourrin - Bouton 7
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
            SendOSC(klickport, '/klick/simple/set_pattern', 'X-x-x-x-x-xxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_disto_on,
        bassdag_fx_off,
        bassdag_octaver_off,
        [
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 180),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase3',1),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase4',1),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase5',1),

            ] >> Discard()


        ],
    ProgramFilter(8) >> [ # 13/8 Prog en G - Bouton 8
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

        bassdag_on,
        bassorl_on,
        bassdag_fx_off,
        bassdag_disto_off,
        bassdag_octaver_off,
        bassorl_disto_off,
        bassorl_reverb_off,
        bassorl_octaver_off,        
        gtrdag_mute,
        gtrorl_mute,
        ],
    ProgramFilter(9) >> [ # Metal - Bouton 9
        Program(68) >> cseqtrigger,
        
        Program(1) >> abass,
        Program(10) >> achords,
        Program(10) >> actlead,
        
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 7),
            SendOSC(slport, '/set', 'tempo', 180),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxXxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_mute,
        gtrorl_mute,
        bassorl_on,
        bassorl_disto_on,
        bassdag_disto_on,
        bassorl_octaver_off,
        bassdag_octaver_off,
        bassdag_fx_off,
        [
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/6', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/3', 255),
            SendOSC(qlcport, '/BC/Red/Segment/3', 255),
            SendOSC(qlcport, '/BC/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            ] >> Discard()

        ],
    ProgramFilter(10) >> [ # Metal Bouclage basses - Bouton 10
        [
            SendOSC(slport, '/sl/0/hit', 'record'),
            SendOSC(slport, '/sl/1/hit', 'record'),
            ] >> Discard()
        ],

    ProgramFilter(11) >> [ # Metal Alterno - Bouton 11
        Program(69) >> cseqtrigger,

        Program(1) >> abass,
        Program(10) >> achords,
        Program(10) >> actlead,

        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 14),
            SendOSC(slport, '/set', 'tempo', 180),

            SendOSC(slport, '/sl/0/hit', 'trigger'),
            SendOSC(slport, '/sl/1/hit', 'trigger'),
            
            SendOSC(slport, '/sl/2/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 180),
            SendOSC(klickport, '/klick/simple/set_meter', 7, 8),
            SendOSC(klickport, '/klick/simple/set_pattern', 'XxXxXxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        [
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/6', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/3', 255),
            SendOSC(qlcport, '/BC/Red/Segment/3', 255),
            SendOSC(qlcport, '/BC/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/6', 255),
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CJ/Blue/Segment/1', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Blue/Segment/8', 255),
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),

            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 720),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase6',1),
            ] >> Discard(),
        
        bassdag_on,
        gtrdag_disto,
        gtrorl_disto,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        bassdag_disto_on,
        bassdag_octaver_off,
        bassdag_fx_off,
        [
            SendOSC(qlcport, '/stop', 1),
            SendOSC(qlcport, '/scene/introD', 1),
            ] >> Discard()

        ],
    ProgramFilter(11) >> [ # Vers Carmen - Bouton 11 -- !!! A VÉRIFIER EN RÉPÈTITION !!!

        Program(119) >> seq24once,
        SceneSwitch(8)        
        ],
 
    ]



#### ACTE 4 ####
acte4 =	PortFilter('PBCtrlIn') >> [ 
    ProgramFilter(1) >> stop, # !!!STOP!!! #
    ProgramFilter(2) >> [ # Première occurrence machines Carmeno Saoule - Bouton 2
        Program(65) >> cseqtrigger, 
        abass_mute,
        actlead_mute,
        Program(9) >> alead,
        Program(9) >> achords,
        [
            SendOSC(slport, '/set', 'eighth_per_cycle', 16),
            SendOSC(slport, '/set', 'tempo', 120),
            SendOSC(slport, '/sl/-1/hit', 'pause_on'),
            SendOSC(klickport, '/klick/simple/set_tempo', 120),
            SendOSC(klickport, '/klick/simple/set_meter', 4, 4),
            SendOSC(klickport, '/klick/simple/set_pattern', 'Xxxx'),
            SendOSC(klickport, '/klick/metro/start'),
            ] >> Discard(),

        bassdag_mute,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_mute,
        [
            SendOSC(qlcport, '/AllStop', 1),
            SendOSC(qlcseqport, '/DisableAll', 1),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            ] >> Discard()
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
        bassdag_disto_off,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrorl_mute,
        gtrdag_mute,
        bassorl_on,
        bassorl_disto_off,
        bassorl_octaver_off,
        bassorl_reverb_on,
        [
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 0),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 0),
            ] >> Discard()
        ],
    ProgramFilter(4) >> [ # Troisième occurrence machines Carmeno Saoule 2 - Bouton 4
        Program(67) >> cseqtrigger,
        Program(1) >> abass,
        Program(9) >> achords,
        Program(8) >> alead,
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
        bassorl_mute,
        [
            SendOSC(qlcport, '/CC/Red/Segment/All', 255),
            SendOSC(qlcport, '/CJ/Red/Segment/All', 255),
            SendOSC(qlcport, '/Decoupes/Jardin/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Cour/Dimmer', 255),
            SendOSC(qlcport, '/Decoupes/Jeannot/Dimmer', 255),
            ] >> Discard()
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
        bassdag_disto_on,
        bassdag_octaver_off,
        bassdag_fx_off,
        gtrdag_disto,
        gtrorl_disto,
        bassorl_on,
        bassorl_disto_on,
        bassorl_octaver_off,
        [
            SendOSC(qlcport, '/AllStop', 1),            
            SendOSC(qlcseqport, '/Sequencer/DisableAll', 1),
            
            SendOSC(qlcseqport, '/Sequencer/Trigger', 1),
            SendOSC(qlcseqport, '/Sequencer/Set_bpm', 120),

            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase6',1),
            SendOSC(qlcseqport, '/Sequencer/Sequence/Enable', 'AII Chase3',1),
            ] >> Discard()
        ],
    ProgramFilter(6) >> [ # Bouclage des basses - Bouton 6
        [
            SendOSC(slport, '/sl/0/hit', 'record'),
            SendOSC(slport, '/sl/1/hit', 'record')
            ] >> Discard(),
        [
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
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
            ] >> Discard(),
        [
            SendOSC(qlcport, '/BC/Red/Segment/1', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/1', 255),
            SendOSC(qlcport, '/BC/Red/Segment/8', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/8', 255),
            SendOSC(qlcport, '/BC/Red/Segment/3', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/3', 255),
            SendOSC(qlcport, '/BC/Red/Segment/5', 255),
            SendOSC(qlcport, '/BJ/Red/Segment/5', 255),
            ] >> Discard()
        ],
    ProgramFilter(10) >> [ # Overdub guitares - Bouton 10
        [
            SendOSC(slport, '/sl/2/hit', 'overdub'),
            SendOSC(slport, '/sl/3/hit', 'overdub')
            ] >> Discard()
        ],
    ProgramFilter(11) >> [ # Reverse All - Bouton 11
        [

            SendOSC(slport, '/sl/-1/set', 'dry', 0),
            SendOSC(slport, '/sl/4/set', 'dry', 1),
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

