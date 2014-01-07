from mididings import Call
import mididings.engine as _engine
import mididings.setup as _setup
import mididings.misc as _misc

import mididings.extra.panic as _panic

import liblo as _liblo

class OSCCustomInterface(object):
    def __init__(self, port=56418):
        self.port = port

    def on_start(self):
        if self.port is not None:
            self.server = _liblo.ServerThread(self.port)
            self.server.register_methods(self)
            self.server.start()

    def on_exit(self):
        if self.port is not None:
            self.server.stop()
            del self.server

    @_liblo.make_method('/pedalBoard/button', 'i')
    def button_cb(self, path, args):
        if _engine.current_subscene() == 8:
         _engine.switch_scene(args[0])
         _engine.switch_subscene(1)
        if args[0] == 12 and _engine.current_subscene() != 8:
         _engine.switch_subscene(8)

