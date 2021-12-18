from osm2gmns.movement.connection_from_turns import *
from osm2gmns.movement.auto_connection import *




def generateMovements(net, auto_connection=True):
    processed_node_set = generateMovementsFromTurns(net)

    if auto_connection:
        guessMovements(net, processed_node_set)


    pass