from pandas.util.testing import assert_frame_equal

from causalinfo.variables import (Variable, make_variables, UniformDist,
                                  expand_variables, JointDistByState) 
from causalinfo.network import Equation, CausalNetwork
from causalinfo.measure import Measure
from causalinfo import mappings


def signal_complex():
    c1, c2, s1, s2, s3, s4, a1 = make_variables('c1 c2 s1 s2 s3 s4 a1', 2)
    in_dist = UniformDist(c1, c2)

    eq1 = Equation('SAME', [c1], [s1], mappings.f_same)
    eq2 = Equation('SAMEB', [c2], [s2, s3], mappings.f_branch_same)
    eq3 = Equation('AND', [s1, s2], [s4], mappings.f_and)
    eq4 = Equation('OR', [s3, s4], [a1], mappings.f_or)
    net = CausalNetwork([eq1, eq2, eq3, eq4])
    m = Measure(net)
    print m.causal_flow(s3, a1, c1, in_dist)
    print m.causal_flow(s4, a1, c1, in_dist)


def testing():
    w, x, y, z = make_variables("W X Y Z", 2)

    wdist = UniformDist(w)

    # Ay & Polani, Example 3
    eq1 = Equation('BR', [w], [x, y], mappings.f_branch_same)
    eq2 = Equation('XOR', [x, y], [z], mappings.f_xor)
    network = CausalNetwork([eq1, eq2])
    m = Measure(network)
    print m.causal_flow(x, y, w, wdist)
    print m.causal_flow(w, z, y, wdist)

    # Ay & Polani, Example 5.1
    def f_copy_first(i1, i2, o1):
        o1[i1] = 1.0

    eq2 = Equation('COPYX', [x, y], [z], f_copy_first)
    network = CausalNetwork([eq1, eq2])
    m = Measure(network)
    # print network.generate_joint().mutual_info(x, z, y)
    print m.causal_flow(x, z, y, wdist)

    # Ay & Polani, Example 5.2
    def f_random_sometimes(i1, i2, o1):
        if i1 != i2:
            o1[:] = .5
        else:
            mappings.f_xor(i1, i2, o1)

    eq2 = Equation('RAND', [x, y], [z], f_random_sometimes)
    network = CausalNetwork([eq1, eq2])
    m = Measure(network)
    # print network.generate_joint().mutual_info(x, z, y)
    print m.causal_flow(x, z, y, root_dist=wdist)

def test_signal():
    print 'signaling'
    c, s, a = make_variables('C S A', 2)
    eq1 = Equation('Send', [c], [s], mappings.f_same)
    eq2 = Equation('Recv', [s], [a], mappings.f_same)
    network = CausalNetwork([eq1, eq2])
    root_dist = JointDist({c: [.7, .3]})
    m = Measure(network, root_dist)
    print m.mutual_info(s, a)
    print m.causal_flow(s, a)
    print m.average_sad(s, a)
    

def test_half_signal():

    def merge(i1, i2, o1):
        if i2:
            o1[i1] = 1.0
        else:
            o1[0] = 1.0

    print 'signaling 2'
    c1, c2, s1, s2, s3, a = make_variables('C1 C2 S1 S2 S3 A', 2)
    eq1 = Equation('Send1', [c1], [s1], mappings.f_same)
    eq2 = Equation('Send2', [c2], [s2], mappings.f_same)
    eq3 = Equation('Rec1', [s1, s2], [a], merge)
    network = CausalNetwork([eq1, eq2, eq3])
    root_dist = UniformDist(c1, c2)
    root_dist = JointDist({c1: [.5, .5], c2: [0, 1]})
    print root_dist.probabilities
    m = Measure(network)
    print m.causal_flow2(s1, a, root_dist)
    # print m.causal_flow2(s2, a, root_dist)
    #
def test_signal3():

    def merge(i1, i2, o1):
        if i2:
            # Perfect spec
            o1[i1] = 1.0
        else:
            o1[i1/2] = 1.0

    print 'signaling 2'
    c1, s1, s3, a = make_variables('C1 S1 S3 A', 4)
    c2, s2 = make_variables('C2 S2', 2)
    eq1 = Equation('Send1', [c1], [s1], mappings.f_same)
    eq2 = Equation('Send2', [c2], [s2], mappings.f_same)
    eq3 = Equation('Rec1', [s1, s2], [a], merge)
    network = CausalNetwork([eq1, eq2, eq3])
    root_dist = JointDist({c1: [.25] * 4, c2: [.2, .8]})
    m = Measure(network)
    # print m.causal_flow2(s1, a, root_dist)
    # print m.causal_flow2(s2, a, root_dist)
    print m.causal_flow(s1, a, s2, root_dist)
    print m.average_sad(s1, a, root_dist)

    print m.causal_flow(s2, a, s1, root_dist)
    print m.average_sad(s2, a, root_dist)

def test_signal4():

    def merge1(i1, i2, o1):
        if i2:
            # Perfect spec
            o1[i1] = 1.0
        else:
            o1[i1/2] = 1.0

    def merge2(i1, i2, o1):
        if i1:
            # Perfect spec
            o1[i2] = 1.0
        else:
            # Swap them
            if i2 == 0:
                o1[1] = 1.0
            elif i2 == 1:
                o1[0] = 1.0
            else:
                o1[i2] = 1.0

    print 'signaling 4'
    c1, s1, s3, a = make_variables('C1 S1 S3 A', 4)
    c2, s2, c3, s4 = make_variables('C2 S2 C3 S4', 2)
    eq1 = Equation('Send1', [c1], [s1], mappings.f_same)
    eq2 = Equation('Send2', [c2], [s2], mappings.f_same)
    eq3 = Equation('Rec1', [s2, s1], [s4], merge1)
    eq4 = Equation('Rec2', [c3], [s3], mappings.f_same)
    eq5 = Equation('Rec3', [s3, s4], [a], merge2)
    network = CausalNetwork([eq1, eq2, eq3, eq4, eq5])
    root_dist = JointDist({c1: [.25] * 4, c2: [.2, .8], c3: [.5, .5]})
    # for ass, p in root_dist.iter_assignments():
    #     print ass, p
    m = Measure(network, root_dist)
    # print m.causal_flow2(s1, a, root_dist)
    # print m.causal_flow2(s2, a, root_dist)
    print m.causal_flow(s1, a, [s2, s3])
    print m.average_sad(s1, a)
    print m.causal_flow(s3, a, [s1, s2])
    print m.average_sad(s3, a)

    # print m.causal_flow(s2, a, s1, root_dist)
    # print m.average_sad(s2, a, root_dist)

    # print 'observe signal s1'
    # j_observe_tree = network.generate_tree(root_dist)
    # j_observe = TreeDistribution(j_observe_tree)
    # print j_observe.joint(s1).probabilities
    # print j_observe.joint(c1, c2, a).probabilities

def test_diamond():
    def merge(i1, i2, o1):
        if i2:
            # Perfect spec
            o1[i1] = 1.0
        else:
            o1[i1/2] = 1.0

    c, s1, s2, s3, s4, a = make_variables('C S1 S2 S3 S4 A', 2)
    eq1 = Equation('Send', [c], [s1, s2], mappings.f_branch_same)
    eq2 = Equation('Relay1', [s1], [s3], mappings.f_same)
    eq3 = Equation('Relay2', [s2], [s4], mappings.f_same)
    eq4 = Equation('XOR', [s3, s4], [a], mappings.f_xor)
    n = CausalNetwork([eq1, eq2, eq3, eq4])
    root_dist = JointDist({c: [.5, .5]})
    m = Measure(n, root_dist)
    print m.mutual_info(s3, a)
    print m.causal_flow(s3, a, s4)
    print m.average_sad(s3, a)
