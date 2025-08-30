import random
import wsnsimpy.wsnsimpy_tk as wsp


class MyNode(wsp.LayeredNode):

    def init(self):
        super().init()
        self.__ticks = 0

    def run(self):
        self.start_process(self.create_process(self.process_clock))

    def process_clock(self):
        while True:
            yield self.timeout(1)
            self.__ticks += 1
            self.log(f"Ticks = {self.__ticks}")


sim = wsp.Simulator(
        until=10,
        timescale=1,
        visual=False,
        terrain_size=(700,700),
        title="Clock Demo")

for x in range(3):
    for y in range(3):
        px = 50 + x*60 + random.uniform(-20,20)
        py = 50 + y*60 + random.uniform(-20,20)
        node = sim.add_node(MyNode, (px,py))
        node.tx_range = 75
        node.logging = True

sim.run()
