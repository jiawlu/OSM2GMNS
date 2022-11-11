from osm2gmns.movement.exp_connection_from_turns import *
from osm2gmns.movement.exp_auto_connection import *




def generateMovements(net, auto_connection=True):
    processed_node_set = generateMovementsFromTurns(net)

    if auto_connection:
        guessMovements(net, processed_node_set)


    pass