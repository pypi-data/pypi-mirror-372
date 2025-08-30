from abc import ABC, abstractmethod
from time import sleep, time as systime
from threading import Timer
from heapq import heappush, heappop
import inspect

from .common import (
    INF,
    DEFAULT_PARAMETERS,
    DEFAULT_LINESTYLE,
    DEFAULT_FILLSTYLE,
    DEFAULT_TEXTSTYLE,
    LineStyle,
    FillStyle,
)

###############################################
class Node:
    """
    Define a dummy node structure to keep track of arbitrary node attributes
    """
    pass

###############################################
class AbstractRenderer(ABC):
    """
    Declare an interface for scene renderer
    """
    @abstractmethod
    def init(self, tx, ty):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def node(self, id, x, y):
        pass

    @abstractmethod
    def nodemove(self, id, x, y):
        pass

    @abstractmethod
    def nodecolor(self, id, r, g, b):
        pass

    @abstractmethod
    def nodewidth(self, id, width):
        pass

    @abstractmethod
    def nodescale(self, id, scale):
        pass

    @abstractmethod
    def nodelabel(self, id, label):
        pass

    @abstractmethod
    def addlink(self, src, dst, style):
        pass

    @abstractmethod
    def dellink(self, src, dst, style):
        pass

    @abstractmethod
    def clearlinks(self):
        pass

    @abstractmethod
    def circle(self, x, y, r, id):
        pass

    @abstractmethod
    def line(self, x1, y1, x2, y2, id):
        pass

    @abstractmethod
    def rect(self, x1, y1, x2, y2, id):
        pass

    @abstractmethod
    def delshape(self, id):
        pass

    @abstractmethod
    def linestyle(self, id, **kwargs):
        pass

    @abstractmethod
    def fillstyle(self, id, **kwargs):
        pass

    @abstractmethod
    def textstyle(self, id, **kwargs):
        pass


###############################################
class Scene:
    """
    Define a generic scene that keeps track of every object in the simulation
    model.  This class does not implement actual visualization, but only
    maintains abstraction of visualization operations.
    """

    ###################
    def __init__(self, timescale=1, realtime=False, params=None):
        """
        Instantiate a Scene object.  The timescale parameter indicates how
        the scene should adjust time delay as specified with a scene scripting
        command.  When the realtime parameter is True, the timescale parameter
        is ignored and each scene scripting command will take effect
        immediately once invoked.
        """
        self.params = params or DEFAULT_PARAMETERS
        self.time = 0.0
        self.initialized = False
        self.timescale = timescale
        self.realtime = realtime
        self.evq = []        # Event queue
        self.unique_id = 0   # Counter for generating unique IDs

        self.dim = (0, 0)      # Terrain dimension
        self.nodes = {}        # Nodes' information
        self.links = set()     # Set of links between nodes
        self.node_links = {}   # Map node -> links from node
        self.linestyles = {}   # List of defined line styles
        self.fillstyles = {}   # List of defined fill styles
        self.textstyles = {}   # List of defined text styles

        self.renderer: AbstractRenderer = None

        if realtime:
            self.startTime = systime()

    ###################
    def set_renderer(self, renderer: AbstractRenderer):
        self.renderer = renderer

    ###################
    def set_timing(self, scale=1, realtime=False):
        self.timescale = scale
        self.realtime = realtime
        if realtime:
            self.startTime = systime() - self.time

    ###################
    def _get_unique_id(self):
        """
        Create and return a unique integer everytime it gets called
        """
        self.unique_id = self.unique_id + 1
        return "_" + str(self.unique_id)

    ###################
    def execute(self, time, cmd, *args, **kwargs):
        """
        Execute the scene scripting command, cmd, with specified
        variable-length and keyword arguments
        """
        if self.realtime:
            self.settime(systime()-self.startTime)
        else:
            # examine the event queue and execute everything prior to
            # the 'current time'
            while len(self.evq) > 0 and self.evq[0][0] < time:
                (t, proc, a, kw) = heappop(self.evq)
                self.settime(t)
                proc(*a, **kw)
            self.settime(time)
        if type(cmd) is str:
            #exec 'self.' + cmd    # Python2
            exec('self.' + cmd)  # Python3
        else:
            cmd(*args, **kwargs)

    ###################
    def _execute_after(self, delay, cmd, *args, **kwargs):
        """
        Wait until the specified delay, then executed the given command
        """
        if delay is INF:
            # no need to scedule any execution at time infinity
            return
        if self.realtime:
            def execfn():
                self.execute(0, cmd, *args, **kwargs)
            Timer(delay, execfn).start()
        else:
            heappush(self.evq, (self.time+delay, cmd, args, kwargs))

    ###################
    def settime(self, time):
        """
        Set the current time being tracked by the scene to the specified time.
        A corresponding amount of delay will be applied unless the scene
        was instantiated to run in real-time.
        """
        if time < self.time:
            raise Exception(
                    'Time cannot flow backward: current = %.3f, new = %.3f'
                    % (self.time, time)
                    )
        if not self.realtime:
            sleep((time-self.time)*self.timescale)
            self.time = time
        if self.renderer:
            self.renderer.settime(time)

    ###################
    def init(self, tx, ty):
        """
        (Scene scripting command) Intialize the scene.  This command should
        be called before any other scripting commands.
        """
        if (self.initialized):
            raise Exception('init() has already been called')
        self.dim = (tx, ty)
        self.initialized = True
        if self.renderer:
            self.renderer.init(tx, ty)

    ###################
    def node(self, id, x, y):
        """
        (Scene scripting command)
        Define a node with the specified ID and location (x, y)
        """
        if id in self.nodes:
            raise Exception(f"Node with id={id} already exists")
        self.nodes[id] = Node()
        self.nodes[id].id = id
        self.nodes[id].pos = (x, y)
        self.nodes[id].scale = 1.0
        self.nodes[id].label = str(id)
        self.nodes[id].hollow = self.params.hollow
        self.nodes[id].double = self.params.double
        self.nodes[id].width = self.params.nodewidth
        self.nodes[id].color = self.params.nodecolor
        self.node_links[id] = []
        if self.renderer:
            self.renderer.node(id, x, y)

    ###################
    def nodemove(self, id, x, y):
        """
        (Scene scripting command)
        Move a node whose ID is id to a new location (x, y)
        """
        self.nodes[id].pos = (x, y)
        if self.renderer:
            self.renderer.nodemove(id, x, y)

    ###################
    def nodecolor(self, id, r, g, b):
        """
        (Scene scripting command)
        Set color (in rgb format, 0 <= r, g, b <= 1) of the node, specified by
        id
        """
        self.nodes[id].color = (r, g, b)
        if self.renderer:
            self.renderer.nodecolor(id, r, g, b)

    ###################
    def nodelabel(self, id, label):
        """
        (Scene scripting command)
        Set string label for the node, specified by id
        """
        self.nodes[id].label = label
        if self.renderer:
            self.renderer.nodelabel(id, label)

    ###################
    def nodescale(self, id, scale):
        """
        (Scene scripting command)
        Set node scaling factor.  By default, nodes are visualized with
        scale=1
        """
        self.nodes[id].scale = scale
        if self.renderer:
            self.renderer.nodescale(id, scale)

    ###################
    def nodehollow(self, id, flag):
        """
        (Scene scripting command)
        Set node's hollow display
        """
        self.nodes[id].hollow = flag
        if self.renderer:
            self.renderer.nodehollow(id, flag)

    ###################
    def nodedouble(self, id, flag):
        """
        (Scene scripting command)
        Set node's double-outline display
        """
        self.nodes[id].double = flag
        if self.renderer:
            self.renderer.nodedouble(id, flag)

    ###################
    def nodewidth(self, id, width):
        """
        (Scene scripting command)
        Set node's outline width
        """
        self.nodes[id].width = width
        if self.renderer:
            self.renderer.nodewidth(id, width)

    ###################
    def addlink(self, src, dst, style):
        """
        (Scene scripting command)
        Add a link with the specified style, which is an instance of
        LineStyle, between a pair of nodes
        """
        self.links.add((src, dst, style))
        self.node_links[src].append((src, dst, style))
        self.node_links[dst].append((src, dst, style))
        if self.renderer:
            self.renderer.addlink(src, dst, style)

    ###################
    def dellink(self, src, dst, style):
        """
        (Scene scripting command)
        Remove a link with the specified style from a pair of nodes
        """
        self.links.remove((src, dst, style))
        self.node_links[src].remove((src, dst, style))
        self.node_links[dst].remove((src, dst, style))
        if self.renderer:
            self.renderer.dellink(src, dst, style)

    ###################
    def clearlinks(self):
        """
        (Scene scripting command)
        Delete all links previously added
        """
        self.links.clear()
        for n in self.nodes.keys():
            self.node_links[n] = []
        if self.renderer:
            self.renderer.clearlinks()

    ###################
    def show(self):
        """
        (Scene scripting command)
        Force update of topology view
        """
        if self.renderer:
            self.renderer.show()

    ###################
    def circle(self, x, y, r, id=None,
               line=DEFAULT_LINESTYLE, fill=DEFAULT_FILLSTYLE, delay=INF):
        """
        (Scene scripting command)
        Draw/update a circle centered at (x, y) with radius r.  line and fill
        are applied to the drawn object.  The object will remain on the scene
        for the specified delay.  The shape id is returned.
        """
        if id == None:
            id = self._get_unique_id()

        if not isinstance(line, LineStyle):
            line = self.linestyles[line]

        if not isinstance(fill, FillStyle):
            fill = self.fillstyles[fill]

        if delay != INF:
            self._execute_after(delay, self.delshape, id)

        if self.renderer:
            self.renderer.circle(x, y, r, id, line, fill)

        return id


    ###################
    def line(self, x1, y1, x2, y2, id=None, line=None, delay=INF):
        """
        (Scene scripting command)
        Draw/update a line from (x1, y1) to (x2, y2).  The styles given by
        line and fill are applied to the drawn object.  The object will remain
        on the scene for the specified delay  The shape id is returned..
        """
        if id == None:
            id = self._get_unique_id()

        if line is None:
            line = LineStyle()
        elif not isinstance(line, LineStyle):
            line = self.linestyles[line]

        if delay != INF:
            self._execute_after(delay, self.delshape, id)

        if self.renderer:
            self.renderer.line(x1, y1, x2, y2, id, line)

        return id

    ###################
    def rect(self, x1, y1, x2, y2, id=None, line=None, fill=None, delay=INF):
        """
        (Scene scripting command)
        Draw/update a rectangle from (x1, y1) to (x2, y2).  line and fill
        are applied to the drawn object.  The object will remain on the scene
        for the specified delay.  The shape id is returned.
        """
        if id == None:
            id = self._get_unique_id()

        if line is None:
            line = LineStyle()
        elif not isinstance(line, LineStyle):
            line = self.linestyles[line]

        if fill is None:
            fill = FillStyle()
        elif not isinstance(fill, FillStyle):
            fill = self.fillstyles[fill]

        if delay != INF:
            self._execute_after(delay, self.delshape, id)

        if self.renderer:
            self.renderer.rect(x1, y1, x2, y2, id, line)

        return id

    ###################
    def delshape(self, id):
        """
        (Scene scripting command)
        Delete an animated shape (e.g., line, circle) previously created with ID id
        """
        if self.renderer:
            self.renderer.delshape(id)


    ###################
    def linestyle(self, id, **kwargs):
        """
        (Scene scripting command)
        Define or redefine a line style.
        """
        self.linestyles[id] = LineStyle(**kwargs)
        if self.renderer:
            self.renderer.linestyle(id, **kwargs)

    ###################
    def fillstyle(self, id, **kwargs):
        """
        (Scene scripting command)
        Define or redefine a fill style
        """
        self.fillstyles[id] = FillStyle(**kwargs)
        if self.renderer:
            self.renderer.fillstyle(id, **kwargs)

    ###################
    def textstyle(self, id, **kwargs):
        """
        (Scene scripting command)
        Define or redefine a text style
        """
        self.textstyles[id] = FillStyle(**kwargs)
        if self.renderer:
            self.renderer.textstyle(id, **kwargs)
