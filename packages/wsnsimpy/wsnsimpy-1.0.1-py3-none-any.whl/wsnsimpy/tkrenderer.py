from .common import (
    INF,
    DEFAULT_PARAMETERS,
    compute_link_endpoints,
)
import tkinter
from .scene import Scene, AbstractRenderer

ARROW_MAP = {
    'head' : tkinter.LAST,
    'tail' : tkinter.FIRST,
    'both' : tkinter.BOTH,
    'none' : tkinter.NONE,
}

###############################################
def color2str(color):
    if color == None:
        return ''
    else:
        return '#%02x%02x%02x' % tuple(int(x*255) for x in color)

###############################################
class TkRenderer(AbstractRenderer):
    def __init__(self,
                 scene:Scene,
                 window_title="WSNSimPy",
                 terrain_size=(500, 500),
                 params=DEFAULT_PARAMETERS,
                 **kwargs):
        self.scene = scene
        self.window_title = window_title
        self.params = params
        self._last_shown_time = 0
        self._tk_nodes = {}
        self._tk_links = {}
        self._shapes = {}
        self._prepare_canvas(terrain_size)

    ###################
    def _prepare_canvas(self, terrain_size=None):
        if terrain_size is not None:
            tx, ty = terrain_size
        else:
            tx, ty = 700, 700
        self.tk = tkinter.Tk()
        self.tk.title(self.window_title)
        self.canvas = tkinter.Canvas(self.tk, width=tx, height=ty)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.timeText = self.canvas.create_text(0, 0, text="time=0.0", anchor=tkinter.NW)

    ###################
    def _update_node_pos_and_size(self, id):
        p = self.params
        c = self.canvas
        if id not in self._tk_nodes.keys():
            node_tag = c.create_oval(0, 0, 0, 0)
            label_tag = c.create_text(0, 0, text=str(id))
            self._tk_nodes[id] = (node_tag, label_tag)
        else:
            (node_tag, label_tag) = self._tk_nodes[id]

        node = self.scene.nodes[id]
        nodesize = node.scale*p.nodesize
        x1 = node.pos[0] - nodesize
        y1 = node.pos[1] - nodesize
        (x2, y2) = (x1 + nodesize*2, y1 + nodesize*2)
        c.coords(node_tag, x1, y1, x2, y2)
        c.coords(label_tag, node.pos)

        for l in self.scene.node_links[id]:
            self._update_link(*l)

    ###################
    def _config_line(self, tag_or_id, line):
        config = {
            'fill': color2str(line.color),
            'width': line.width,
            'arrow': ARROW_MAP[line.arrow],
            'dash': line.dash,
        }
        self.canvas.itemconfigure(tag_or_id, config)

    ###################
    def _config_polygon(self, tag_or_id, line, fill):
        config = {
            'outline': color2str(line.color),
            'width': line.width,
            'dash': line.dash,
            'fill': color2str(fill.color),
        }
        self.canvas.itemconfigure(tag_or_id, config)

    ###################
    def settime(self, time):
        if (time - self._last_shown_time > 0.05):
            self.canvas.itemconfigure(self.timeText, text='Time: %.2fS' % time)
            self._last_shown_time = time

    ###################
    def createlink(self, src, dst, style):
        if src is dst:
            raise('Source and destination are the same node')
        p = self.params
        c = self.canvas
        (x1, y1, x2, y2) = compute_link_endpoints(
                self.scene.nodes[src],
                self.scene.nodes[dst], 
                p.nodesize)
        link_obj = c.create_line(x1, y1, x2, y2, tags='link')
        self._config_line(link_obj, self.scene.linestyles[style])
        return link_obj

    ###################
    def _update_link(self, src, dst, style):
        p = self.params
        c = self.canvas
        link_obj = self._tk_links[(src, dst, style)]
        (x1, y1, x2, y2) = compute_link_endpoints(
                self.scene.nodes[src],
                self.scene.nodes[dst], 
                p.nodesize)
        c.coords(link_obj, x1, y1, x2, y2)


    ###################
    def node(self, id, x, y):
        self._update_node_pos_and_size(id)
        self.tk.update()

    ###################
    def nodemove(self, id, x, y):
        self._update_node_pos_and_size(id)
        self.tk.update()

    ###################
    def nodecolor(self, id, r, g, b):
        (node_tag, label_tag) = self._tk_nodes[id]
        self.canvas.itemconfig(node_tag, outline=color2str((r, g, b)))
        self.canvas.itemconfigure(label_tag, fill=color2str((r, g, b)))
        self.tk.update()

    ###################
    def nodewidth(self, id, width):
        (node_tag, label_tag) = self._tk_nodes[id]
        self.canvas.itemconfig(node_tag, width=width)
        self.tk.update()

    ###################
    def nodescale(self, id, scale):
        # scale attribute has been set by the parent class
        # just update the node
        self.update_node_pos_and_size(id)
        self.tk.update()

    ###################
    def nodelabel(self, id, label):
        (node_tag, label_tag) = self._tk_nodes[id]
        self.canvas.itemconfigure(label_tag, text=self.scene.nodes[id].label)
        self.tk.update()

    ###################
    def addlink(self, src, dst, style):
        self._tk_links[(src, dst, style)] = self.createlink(src, dst, style)
        self.tk.update()

    ###################
    def dellink(self, src, dst, style):
        self.canvas.delete(self._tk_links[(src, dst, style)])
        del self._tk_links[(src, dst, style)]
        self.tk.update()

    ###################
    def clearlinks(self):
        self.canvas.delete('link')
        self._tk_links.clear()
        self.tk.update()

    ###################
    def circle(self, x, y, r, id, line, fill):
        if id in self._shapes.keys():
            self.canvas.delete(self._shapes[id])
            del self._shapes[id]
        self._shapes[id] = self.canvas.create_oval(x-r, y-r, x+r, y+r)
        self._config_polygon(self._shapes[id], line, fill)
        self.tk.update()

    ###################
    def line(self, x1, y1, x2, y2, id, line):
        if id in self._shapes.keys():
            self.canvas.delete(self._shapes[id])
            del self._shapes[id]
        self._shapes[id] = self.canvas.create_line(x1, y1, x2, y2)
        self._config_line(self._shapes[id], line)
        self.tk.update()

    ###################
    def rect(self, x1, y1, x2, y2, id, line, fill):
        if id in self._shapes.keys():
            self.canvas.delete(self._shapes[id])
            del self._shapes[id]
        self._shapes[id] = self.canvas.create_rectangle(x1, y1, x2, y2)
        self._config_polygon(self._shapes[id], line, fill)
        self.tk.update()

    ###################
    def delshape(self, id):
        if id in self._shapes.keys():
            self.canvas.delete(self._shapes[id])
            self.tk.update()

    ###### Not used by TkRenderer ######
    def init(self, tx, ty): pass
    def show(self): pass
    def linestyle(self, id, **kwargs): pass
    def fillstyle(self, id, **kwargs): pass
    def textstyle(self, id, **kwargs): pass
