import random
import wsnsimpy.wsnsimpy_tk as wsp

class GossipNode(wsp.Node):

    def run(self):
        self.tx_range = self.sim.tx_range
        self.tx = 0
        self.rx = 0
        self.logging = False
        if self.id == self.sim.source:
            self.success = True
            yield self.timeout(1)
            self.log(f"Broadcast hello")
            self.send(wsp.BROADCAST_ADDR, msg="hello")
            self.tx += 1
            self.scene.nodewidth(self.id, 3)
        else:
            self.success = False
            self.scene.nodecolor(self.id, .7, .7, .7)

    def on_receive(self, sender, msg):
        self.rx += 1
        self.log(f"Receive {msg} from {sender}")
        if not self.success:
            self.scene.nodecolor(self.id, 1, 0, 0)
            self.success = True
            if random.uniform(0, 1) < self.sim.gossip_prob:
                yield self.timeout(random.uniform(0.1, 0.5))
                self.log(f"Broadcast {msg}")
                self.tx += 1
                self.send(wsp.BROADCAST_ADDR, msg=msg)
                self.scene.nodewidth(self.id, 3)


def runsim(seed, prob, source, tx_range):
    random.seed(seed)
    sim = wsp.Simulator(
            timescale=0,
            until=50,
            terrain_size=(600, 600),
            visual=True)
    # place 100 nodes on 10x10 grid space
    for x in range(10):
        for y in range(10):
            px = x*50 + 50
            py = y*50 + 50
            sim.add_node(GossipNode,  (px, py))
    sim.gossip_prob = prob
    sim.source = source
    sim.tx_range = tx_range
    sim.run()

    num_successes = sum([n.success for n in sim.nodes])
    num_tx = sum([n.tx for n in sim.nodes])
    num_rx = sum([n.rx for n in sim.nodes])
    return num_successes, num_tx, num_rx

import sys
if len(sys.argv) != 4:
    print("Usage: {} tx-range src prob".format(sys.argv[0]))
    sys.exit(1)

runsim(1, float(sys.argv[3]), int(sys.argv[2]), float(sys.argv[1]))
