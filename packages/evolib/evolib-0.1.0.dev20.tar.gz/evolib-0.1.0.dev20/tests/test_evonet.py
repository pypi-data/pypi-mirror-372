import numpy as np
from evonet.core import Nnet
from evonet.enums import NeuronRole


def test_forward_pass_simple() -> None:
    net = Nnet()
    net.add_layer()  # Input
    net.add_layer()  # Hidden
    net.add_layer()  # Output

    net.add_neuron(layer_idx=0, role=NeuronRole.INPUT,
                   activation="linear", connect_layer=False)
    net.add_neuron(layer_idx=0, role=NeuronRole.INPUT,
                   activation="linear", connect_layer=False)
    net.add_neuron(layer_idx=1, role=NeuronRole.HIDDEN,
                   activation="tanh", connect_layer=False)
    net.add_neuron(layer_idx=1, role=NeuronRole.HIDDEN,
                   activation="tanh", connect_layer=False)
    net.add_neuron(layer_idx=1, role=NeuronRole.HIDDEN,
                   activation="tanh", connect_layer=False)
    net.add_neuron(layer_idx=2, role=NeuronRole.OUTPUT,
                   activation="linear", connect_layer=False)

    # fully connect manually
    for src in net.layers[0].neurons:
        for dst in net.layers[1].neurons:
            net.add_connection(src, dst, weight=1.0)
    for src in net.layers[1].neurons:
        for dst in net.layers[2].neurons:
            net.add_connection(src, dst, weight=1.0)

    result = net.calc([0.5, -0.5])
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], float)


def test_weight_vector_manipulation() -> None:
    net = Nnet()
    net.add_layer(3)
    net.add_neuron(layer_idx=0, role=NeuronRole.INPUT,
                   activation="linear", connect_layer=False)
    net.add_neuron(layer_idx=1, role=NeuronRole.HIDDEN,
                   activation="linear", connect_layer=False)
    net.add_neuron(layer_idx=2, role=NeuronRole.OUTPUT,
                   activation="linear", connect_layer=False)

    net.add_connection(net.layers[0].neurons[0], net.layers[1].neurons[0], weight=1.0)
    net.add_connection(net.layers[1].neurons[0], net.layers[2].neurons[0], weight=2.0)

    result = net.calc([1.0])
    expected = (1.0 * 1.0) * 2.0  # no bias
    assert abs(result[0] - expected) < 1e-6

    # mutate weights manually
    conn = net.get_all_connections()[0]
    conn.weight = -1.0
    result = net.calc([1.0])
    assert result[0] < 0

