import unittest

import sure

from compiler import ast, smartdict


class TestSmartdict(unittest.TestCase):

    def test_smartdict(self):
        sd = smartdict.Smartdict()
        t = ast.User("foo")
        t.lineno, t.lexpos = 1, 1
        sd[t] = "foo"
        sd[t].should.be.equal("foo")

        tt = ast.User("foo")
        tt.lineno, tt.lexpos = 0, 0
        ttt = sd.getKey(tt)
        ttt.lineno.should.be.equal(1)
        ttt.lexpos.should.be.equal(1)

        del sd[t]
        sd.get(t).should.be(None)
        sd.getKey(t).should.be(None)
