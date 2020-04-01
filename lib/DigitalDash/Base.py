"""Abstract classes."""
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.stencilview import StencilView
from typing import NoReturn, List, TypeVar
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from etc import Config
from kivy.core.window import Window
from static import Constants
from kivy.logger import Logger
from lib.DigitalDash.Massager import Massager


massager = Massager()

constants = Constants.GetConstants()
Builder.load_string('''
<GaugeLayout>:
    pos_hint: {'x': 0, 'y': self.gauge_count }
''')
class GaugeLayout(RelativeLayout):
    gauge_count = NumericProperty(300)

    def __init__(self, gauge_count):
       super(GaugeLayout, self).__init__()

       if ( gauge_count == 1 ):
           self.gauge_count = 0.015
       elif ( gauge_count == 2 ):
           self.gauge_count = 0.030
       else:
           self.gauge_count = 0.1


class Base(object):
    def __init__(self, **kwargs):
        super(Base, self).__init__()
        # Optional values
        self.minObserved = 9999
        self.maxObserved = -9999


class AbstractWidget(Base):
    """
    Generic scaffolding for KE Widgets.
        :param object: 
    """
    def __init__(self, **kwargs):
        super(AbstractWidget, self).__init__()
        # Our required attributes
        self.liveWidgets = []
        self.dataIndex   = -1
        self.Layout      = GaugeLayout(kwargs.get('gauge_count', 0))
        self.container   = None

    def build(self,
                container=BoxLayout(),
                **ARGS
            ):
        """
        Create widgets for Dial.
            :param **ARGS:
        """
        args = {}

        self.container = container

        args['PID']  = ARGS['pids'][ARGS['dataIndex']]
        args['path'] = ARGS['path']

        # Import theme specifc Config
        themeConfig = Config.getThemeConfig(ARGS['module'] + '/' + str(ARGS['args']['themeConfig']))
        args['themeConfig'] = {**ARGS['args'], **themeConfig}

        self.face = Face(nocache=True, **args)
        self.needle = globals()['Needle' + ARGS['module']](**args)
        (self.needle.sizex, self.needle.sizey) = (512, 512)

        self.gauge = Gauge(Face=self.face, Needle=self.needle)

        self.Layout.add_widget(self.face)
        self.Layout.add_widget(self.needle)

        self.needle.dataIndex = ARGS['dataIndex']
        # Adding widgets that get updated with data
        self.liveWidgets.append(self.needle)

        # Create our labels
        for labelConfig in themeConfig['labels']:
            labelConfig['dataIndex'] = ARGS['dataIndex']
            labelConfig['PID'] = ARGS['pids'][ARGS['dataIndex']]

            # Create Label widget
            label = KELabel(**labelConfig, min=self.needle.min)
            self.gauge.labels.append(label)

            # Add to data recieving widgets
            if (labelConfig['data']):
                self.liveWidgets.append(label)
            self.Layout.add_widget(label)

        self.container.add_widget(self.Layout)

        return self.liveWidgets


G = TypeVar('G', bound='Gauge')
class Gauge(object):
    """
    Class for coupling Needle and Face instances.
    """
    def __init__(self, Face, Needle, nocache=True, **kwargs):
        """
        Initite Gauge Widget.
        """
        super(Gauge, self).__init__()
        self.face   = Face
        self.needle = Needle
        self.labels = []

        self.needle.setStep()
        self.needle.setData(self.needle.min)

        self.needle.ObjectType = 'Needle'
        self.face.ObjectType   = 'Face'

        # This normalizes our canvas needle sizes and label positions
        def _size(instance, size):
            self.needle._size(self)
            self._label_position()
        self.face.bind(size=_size)

    def _label_position(self):
        for label in self.labels:
            label.pos = (min(self.face.size) * label.new_pos[0], min(self.face.size) * label.new_pos[1])


F = TypeVar('F', bound='Face')
class Face(Base, AsyncImage):
    """
    Create Face widget.

    Face class will return Kivy Image for the face of
    the gauge. Requires one argument of a path to the
    image dir, where **gauge.png** should be stored.

        :param MetaWidget: <DigitalDash.Components.Face>
    """

    def __init__(self, **kwargs):
        """Initite Face Widget."""
        super(Face, self).__init__()
        self.source    = kwargs.get('path', '') + 'gauge.png'
        self.size_hint = (1, 1)
        self.pos       = (0, 0)
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Needle(Base):
    """
    Base class for Needle classes to inherit from.
    """
    def SetUp(self, **kwargs):
        self.SetAttrs(**kwargs)
        self.SetOffset()
        self.true_value = self.min

        self.setData(self.true_value)

    def _size(self, gauge):
        '''Helper method that runs when gauge face changes size.'''
        (self.sizex, self.sizey) = gauge.face.norm_image_size

    def SetOffset(self) -> NoReturn:
        if (self.min < 0):
            self.offset = self.degrees / 2 - ( abs(self.min) * self.step )
        else:
            self.offset = self.degrees / 2

    def setStep(self) -> NoReturn:
        """Method for setting the step size for rotation/moving widgets."""
        self.step = self.degrees / (abs(self.min) + abs(self.max))
        if ( self.step == 0 ):
            self.step = 1

    def SetAttrs(self, themeConfig={'degrees': 0, 'MinMax': [-9999, 9999]}, path='', **args) -> NoReturn:
        """Set basic attributes for widget."""
        for key in args:
            setattr(self, key, args[key])

        (self.source, self.degrees, self.min, self.max) = (
            path + 'needle.png',
            float(themeConfig.get('degrees', 0)),
            themeConfig['MinMax'][0],
            themeConfig['MinMax'][1]
        )
        self.setStep()

    def setData(self, value=0) -> NoReturn:
        """
        Abstract setData method most commonly used.
            :param self: Widget Object
            :param value: Update value for gauge needle
        """
        global massager
        value = float(value)
        self.true_value = value

        current = self.update

        if value > self.max:
            value = self.max
        elif value < self.min:
            value = self.min
        self.update = massager.Smooth( Old=current, New=value * self.step - self.offset )

KL = TypeVar('KL', bound='KELabel')
class KELabel(Base, Label):
    """
    Create Label widget.

    Send a default value that will stay with the Label
    at all times 'default'.

        :param MetaWidget: <DigitalDash.Components.KELabel>

    If default value of label is set to '__PID__' then that string will
    be replaced with the PID name for the data index the label is for.
    """

    def __init__(self, **args):
        """Intiate Label widget."""
        super(KELabel, self).__init__()
        global constants
        self.default         = args.get('default', '')
        self.ConfigColor     = args.get('color', (1, 1, 1 ,1)) # White
        self.color           = self.ConfigColor
        self.ConfigFontSize  = args.get('font_size', 25)
        self.font_size       = self.ConfigFontSize
        self.decimals        = str(constants.get(args.get('PID', ''), {}).get('decimals', 2))

        self.ObjectType   = 'Label'

        if ( self.default == '__PID__' ):
            try:
                self.default = str(constants[args['PID']]['shortName'])
            except Exception as e:
                self.default = args.get('PID', '')
                Logger.error( "Could not load shortName from Static.Constants for PID: "+self.default+" : "+str(e) )
        self.text = self.default

        # Set position dynamically
        self.new_pos = list(map( lambda x: x / 100, args.get('pos', (0, 0)) ))

        if ( args.get('data', False) ):
            self.dataIndex = args['dataIndex']
            self.setData(args.get('min', 0))

    def setData(self: KL, value='') -> NoReturn:
        """
        Send data to Label widget.
        Check for Min/Max key words to cache values with regex checks.
            :param self: LabelWidget object
            :param value='': Numeric value for label
        """
        value = float(value)

        if ( self.default == 'Min: ' ):
            if ( self.minObserved > value ):
                self.minObserved = value
                self.text = ("{0:.%sf}"%(self.decimals)).format(value)
        elif ( self.default == 'Max: ' ):
            if ( self.maxObserved < value ):
                self.maxObserved = value
                self.text = ("{0:.%sf}"%(self.decimals)).format(value)
        else:
            self.text = self.default + ("{0:.%sf}"%(self.decimals)).format(value)


Builder.load_string('''
<NeedleRadial>:
    canvas.before:
        PushMatrix
        Translate:
            xy: (self.x + self.width / 2, self.y + self.height / 2)
        Rotate:
            angle: -self.update
            axis: (0, 0, 1.0)
        Translate:
            xy: (-self.x - self.width / 2, - self.y - self.height / 2)
    canvas.after:
        PopMatrix
''')

class NeedleRadial(Needle, AsyncImage):
    """
    Create Needle widget.

    Needle class is used to generate the needle for
    gauges. This class also has the **setData()**
    method, which can be called and update the needles
    angle value.

        :param MetaWidget: <DigitalDash.Components.NeedleRadial>
    """

    update = NumericProperty()

    def __init__(self, **kwargs):
        """Initiate Needle widget."""
        super(NeedleRadial, self).__init__()
        self.SetUp(**kwargs)
        self.Type = 'Radial'


Builder.load_string('''
<NeedleLinear>:
    canvas:
        # Draw our stencil
        StencilPush
        Rectangle:
            pos: self.x, root.center_y - self.height / 8
            size: self.update, self.height / 2
        StencilUse
        # Now we want to draw our gauge and crop it
        Color:
            rgba: self.r, self.g, self.b, self.a
        Rectangle:
            pos: self.x, root.center_y - self.height / 8
            size: self.update, self.height / 2
            source: self.source
        StencilUnUse

        # Redraw our stencil to remove it
        Rectangle:
            pos: self.x, root.center_y - self.height / 8
            size: self.update, self.height / 2
        StencilPop
''')

class NeedleLinear(Needle, StencilView):
    """
    Create Needle widget.

    Needle class is used to generate the needle for
    gauges. This class also has the **setData()**
    method, which can be called and update the needles
    angle value.

        :param MetaWidget: <DigitalDash.Components.NeedleLinear>
    """
    update = NumericProperty()
    source = StringProperty()
    step   = NumericProperty()
    r = NumericProperty()
    g = NumericProperty()
    b = NumericProperty()
    a = NumericProperty()

    def __init__(self, **kwargs):
        super(NeedleLinear, self).__init__()
        self.SetUp(**kwargs)
        (self.r, self.g, self.b, self.a) = (1, 1, 1, 1)
        self.Type = 'Linear'

    def _size(self, gauge):
        '''Helper method that runs when gauge face changes size.'''

        if ( self.width == self.parent.width ):
            self.width = min(self.parent.size)
        else:
            self.size = gauge.face.norm_image_size

        self.setStep()
        self.setData(self.true_value)

    def setStep(self) -> NoReturn:
        """Method for setting the step size for Linear needles."""
        self.step = self.width / (abs(self.min) + abs(self.max))
        if ( self.step == 0 ):
            self.step = 1.

    def SetOffset(self) -> NoReturn:
        """Set offset for negative values"""
        if (self.min < 0):
            self.offset = self.min
        else:
            self.offset = 0


Builder.load_string('''
<NeedleEllipse>:
    canvas:
        # Draw our stencil
        StencilPush
        Ellipse:
            size: self.sizex, self.sizey
            pos: self.width / 2 - self.sizex / 2, self.height / 2 - self.sizey / 2
            angle_start: self.angle_start
            angle_end: self.update
        StencilUse

        # Now we want to draw our gauge and crop it
        Ellipse:
            size: self.sizex, self.sizey
            pos: self.width / 2 - self.sizex / 2, self.height / 2 - self.sizey / 2
            source: self.source
            angle_start: self.angle_start
            angle_end: self.update
        StencilUnUse

        # Redraw our stencil to remove it
        Ellipse:
            size: self.sizex, self.sizey
            pos: self.width / 2 - self.sizex / 2, self.height / 2 - self.sizey / 2
            angle_start: self.angle_start
            angle_end: self.update
        StencilPop
''')

class NeedleEllipse(Needle, Widget):
    """
    Create Ellipse widget.
    """
    update       = NumericProperty()
    source       = StringProperty()
    degrees      = NumericProperty()
    angle_start  = NumericProperty()
    sizex        = NumericProperty()
    sizey        = NumericProperty()

    def __init__(self, **kwargs):
        super(NeedleEllipse, self).__init__()

        self.SetUp(**kwargs)
        self.SetOffset()
        self.angle_start = -self.offset
        self.Type = 'Ellipse'

    def _size(self, gauge):
        '''Helper method that runs when gauge face changes size.'''

        if self.sizex == 512: return
        (self.sizex, self.sizey) = gauge.face.norm_image_size
