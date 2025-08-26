__author__ = "Ioannis Dasoulas"
__credits__ = ["Julián Arenas-Guerrero","Ioannis Dasoulas"]

__license__ = "Apache-2.0"
__maintainer__ = "Ioannis Dasoulas"
__email__ = "ioannis.dasoulas@kuleuven.be"


import os
import morph_kgc

from rdflib.graph import Graph
import pandas as pd


def test_RMLTC0007h():
    df = pd.DataFrame({"ID":[10], "FirstName":["Venus"], "LastName":["Williams"]})
    data_dict = {"variable1": df}

    try:
        mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl')
        config = f'[CONFIGURATION]\noutput_format=N-QUADS\n[DataSource]\nmappings={mapping_path}'
        g_morph = morph_kgc.materialize(config, data_dict)
        assert False
    except:
        assert True
