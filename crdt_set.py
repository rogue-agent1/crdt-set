#!/usr/bin/env python3
"""Conflict-free Replicated Data Types (CRDTs) — G-Set, OR-Set, G-Counter."""
import sys, uuid

class GSet:
    def __init__(self): self.elements = set()
    def add(self, e): self.elements.add(e)
    def lookup(self, e): return e in self.elements
    def merge(self, other): return GSet._from(self.elements | other.elements)
    @staticmethod
    def _from(s): g = GSet(); g.elements = s; return g

class GCounter:
    def __init__(self, node_id): self.id, self.counts = node_id, {}
    def increment(self, n=1): self.counts[self.id] = self.counts.get(self.id, 0) + n
    def value(self): return sum(self.counts.values())
    def merge(self, other):
        r = GCounter(self.id); r.counts = dict(self.counts)
        for k, v in other.counts.items(): r.counts[k] = max(r.counts.get(k, 0), v)
        return r

class ORSet:
    def __init__(self): self.elements = {}  # value -> set of unique tags
    def add(self, e):
        tag = uuid.uuid4().hex[:8]
        self.elements.setdefault(e, set()).add(tag)
    def remove(self, e): self.elements.pop(e, None)
    def lookup(self, e): return e in self.elements and len(self.elements[e]) > 0
    def merge(self, other):
        r = ORSet()
        all_keys = set(self.elements) | set(other.elements)
        for k in all_keys:
            tags = self.elements.get(k, set()) | other.elements.get(k, set())
            if tags: r.elements[k] = tags
        return r
    def values(self): return set(self.elements.keys())

def main():
    if len(sys.argv) < 2: print("Usage: crdt_set.py <demo|test>"); return
    if sys.argv[1] == "test":
        # GSet
        a, b = GSet(), GSet(); a.add(1); a.add(2); b.add(2); b.add(3)
        c = a.merge(b); assert c.elements == {1, 2, 3}
        # GCounter
        c1, c2 = GCounter("A"), GCounter("B")
        c1.increment(3); c2.increment(5)
        merged = c1.merge(c2); assert merged.value() == 8
        c1.increment(2); merged2 = c1.merge(c2); assert merged2.value() == 10
        # ORSet
        s1, s2 = ORSet(), ORSet(); s1.add("x"); s2.add("y")
        m = s1.merge(s2); assert m.lookup("x") and m.lookup("y")
        s1.remove("x"); m2 = s1.merge(s2); assert not m2.lookup("x")
        print("All tests passed!")
    else:
        g1, g2 = GCounter("node1"), GCounter("node2")
        g1.increment(5); g2.increment(3)
        print(f"Counter: {g1.merge(g2).value()}")

if __name__ == "__main__": main()
