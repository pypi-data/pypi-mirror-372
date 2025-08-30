import os

import numpy as np

from scuq import si,quantities
from mpylab.tools import util, mgraph
from mpylab.env.univers.AmplifierTest import dBm2W
from mpylab.env.Measure import Measure

class TestSusceptibiliy(Measure):
    def __init__(self, parent=None):
        Measure.__init__(self, parent)

    def Init(self, names=None,
             datafunc = None,
             pin=None,
             dwell_time=None,
             e_target=None,
             dotfile=None,
             SearchPath=None,
             leveler_par=None,
             adjust_to_setting=None):
        if names is None:
            self.names = {
                'sg': 'sg',
                'a1': 'amp1',
                'a2': 'amp2',
                'fp': 'prb',
                'tem': 'gtem'
            }
        else:
            self.names = names

        if adjust_to_setting == None:
            self.adjust_to_setting = 'auto'
        else:
            self.adjust_to_setting = adjust_to_setting

        self.main_e_component = None

        def __datafunc(data):
            if self.adjust_to_setting == 'x':
                return data[0]  # x-coordinate
            elif self.adjust_to_setting == 'y':
                return data[1]  # y-coordinate
            elif self.adjust_to_setting == 'z':
                return data[2]  # y-coordinate
            elif self.adjust_to_setting == 'largest':
                return max(data)
            elif self.adjust_to_setting == 'mag':
                return np.linalg.norm(data)
            else:   # auto
                if self.main_e_component in (0,1,2):
                    return data[self.main_e_component]
                else:
                    self.main_e_component = data.index(max(data))
                    return data[self.main_e_component]


        if datafunc is None:
            self.datafunc = __datafunc
        else:
            self.datafunc = datafunc
        if pin is None:
            self.pin = [quantities.Quantity(si.WATT, dBm2W(_dBm)) for _dBm in (-40, -30, -25)]
        else:
            self.pin = [quantities.Quantity(si.WATT, dBm2W(_dBm)) for _dBm in pin]

        if dwell_time is None:
            self.dwell_time = 1
        else:
            self.dwell_time = dwell_time

        if e_target is None:
            self.e_target = quantities.Quantity(si.VOLT / si.METER, 1)
        else:
            self.e_target = quantities.Quantity(si.VOLT / si.METER, e_target)

        if dotfile is None:
            self.dotfile = 'gtem.dot'
        else:
            self.dotfile = dotfile
        if SearchPath is None:
            self.SearchPath = ['.', os.path.abspath('conf')]
        else:
            self.SearchPath = SearchPath
        self.mg = mgraph.MGraph(self.dotfile, themap=self.names.copy(), SearchPaths=self.SearchPath)
        if leveler_par is None:
            self.leveler_par = {'mg': self.mg,
                        'actor': self.mg.name.sg,
                        'output': self.mg.name.tem,
                        'lpoint': self.mg.name.tem,
                        'observer': self.mg.name.fp,
                        'pin': self.pin,
                        'datafunc': self.datafunc,
                        'min_actor': None}
        else:
            self.leveler_par = leveler_par

        #self.ddict = self.mg.CreateDevices()
        return 0

    def init_measurement(self, am):
        err = self.mg.CreateDevices()
        err = self.mg.Init_Devices()
        stat = self.mg.Zero_Devices()
        #stat = self.mg.CmdDevices(True, 'ConfAM', {'source': 'INT1',
        #                                           'freq': 1e3,
        #                                           'depth': am,
        #                                           'waveform': 'SINE',
        #                                           'LFOut': 'OFF'})
        stat = self.mg.CmdDevices(True, 'ConfAM', 'INT1',1e3,am*1e-2,'SINE','OFF')
        stat = self.mg.RFOn_Devices()

    def rf_on(self):
        try:
            stat = self.mg.RFOn_Devices()
            if stat == 0:
                return True
            else:
                return False
        except AttributeError:
            return False

    def rf_off(self):
        try:
            stat = self.mg.RFOff_Devices()
            if stat == 0:
                return True
            else:
                return False
        except AttributeError:
            return False

    def am_on(self):
        try:
            stat = self.mg.CmdDevices(True, 'AMOn')
            if stat == 0:
                return True
            else:
                return False
        except AttributeError:
            return False

    def am_off(self):
        try:
            stat = self.mg.CmdDevices(True, 'AMOff')
            if stat == 0:
                return True
            else:
                return False
        except AttributeError:
            return False

    def adjust_level(self):
        leveler = mgraph.Leveler(**self.leveler_par)
        leveler.adjust_level(self.e_target)
        res = self.mg.Read([self.mg.name.fp])
        return res[self.mg.name.fp]

    def get_waveform(self):
        try:
            fp = self.mg.nodes['prb']['inst']
            # print(fp)
            err, ts, ex, ey, ez = getattr(fp, 'GetWaveform')()
            return err, ts, ex, ey, ez
        except AttributeError:
            return -1, None, None, None, None

    def do_measurement(self, f):
        minf, maxf = self.mg.SetFreq_Devices(f)
        self.mg.EvaluateConditions()
        res = self.adjust_level()
        # res = self.mg.Read([self.mg.name.fp])
        print(f, res[self.mg.name.fp][0])
        self.mg.CmdDevices(True, 'AMOn')
        # wait delay seconds
        #self.messenger(util.tstamp() + " Going to sleep for %d seconds ..." % (self.dwell_time), [])
        self.wait(self.dwell_time, locals(), self.__HandleUserInterrupt)
        #self.messenger(util.tstamp() + " ... back.", [])
        # time.sleep(self.dwell_time)
        self.mg.CmdDevices(True, 'AMOff')

    def quit_measurement(self):
        try:
            stat = self.mg.RFOff_Devices()
            stat = self.mg.Quit_Devices()
        except AttributeError:
            pass

    def __HandleUserInterrupt(self, dct, ignorelist='', handler=None):
        if callable(handler):
            return handler(dct, ignorelist=ignorelist)
        else:
            return self.stdUserInterruptHandler(dct, ignorelist=ignorelist)

    def stdUserInterruptHandler(self, dct, ignorelist=''):
        key = self.UserInterruptTester()
        if key and not chr(key) in ignorelist:
            # empty key buffer
            _k = self.UserInterruptTester()
            while _k is not None:
                _k = self.UserInterruptTester()

            mg = self.mg
            names = self.names
            dwell_time = self.dwell_time
            self.messenger(util.tstamp() + " RF Off...", [])
            stat = mg.RFOff_Devices()  # switch off after measure
            msg1 = """The measurement has been interrupted by the user.\nHow do you want to proceed?\n\nContinue: go ahead...\nSuspend: Quit devices, go ahead later after reinit...\nInteractive: Go to interactive mode...\nQuit: Quit measurement..."""
            but1 = ['Continue', 'Quit']
            answer = self.messenger(msg1, but1)
            # print answer
            if answer == but1.index('Quit'):
                self.messenger(util.tstamp() + " measurment terminated by user.", [])
                raise UserWarning  # to reach finally statement
            self.messenger(util.tstamp() + " RF On...", [])
            stat = mg.RFOn_Devices()  # switch on just before measure
