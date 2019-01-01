# coding=utf-8
# ------------------------------------------------------------------------------------------------------
# TDA596 - Lab 1
# server/server.py
# Input: Node_ID total_number_of_ID
# Student: John Doe
# ------------------------------------------------------------------------------------------------------
import traceback
import sys
import time
import json
import argparse
from threading import Thread

from bottle import Bottle, run, request, template
import requests
# ------------------------------------------------------------------------------------------------------
try:
    app = Bottle()
    board = {} 
    vector = {}
    result_vector = ""
    vote_vector_result_dict = {}

    # ------------------------------------------------------------------------------------------------------
    # BOARD FUNCTIONS
    # ------------------------------------------------------------------------------------------------------
    def add_new_element_to_store(vesselID, vote_value):
        global board
        success = False
        try:
            board[vesselID] = vote_value
            success = True
        except Exception as e:
            print e
        return success

    def add_new_vector(vesselID, vote_result_dict):
        global vector
        success = False
        try:
            vector[vesselID] = vote_result_dict
            success = True
        except Exception as e:
            print e
        return success

    # ------------------------------------------------------------------------------------------------------
    # DISTRIBUTED COMMUNICATIONS FUNCTIONS
    # ------------------------------------------------------------------------------------------------------
    def contact_vessel(vessel_ip, path, payload=None, req='POST'):
        # Try to contact another server (vessel) through a POST or GET, once
        success = False
        try:
            if 'POST' in req:
                res = requests.post('http://{}{}'.format(vessel_ip, path), data=payload)
            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(vessel_ip, path))
            # result is in res.text or res.json()
            if res.status_code == 200:
                success = True
        except Exception as e:
            print e
        return success


    def propagate_to_vessels(path, payload = None, req = 'POST'):
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                contact_vessel(vessel_ip, path, payload, req)


    def propagate_byzantine_vote_to_vessels(byzantine_vote):
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                payload = byzantine_vote.pop()
                if payload == 'True':
                    payload = 'Attack'
                elif payload == "False":
                    payload = 'Retreat'
                t = Thread(target=contact_vessel, args = (vessel_ip,'/propagate/{}'.format(node_id),payload)) 
                t.daemon = True
                t.start()


    def propagate_byzantine_vectors_to_vessels(byzantine_vectors):
        global vessel_list, node_id
        byzantine_vectors_to_dict = {}
        print "byzantine_vectors is: ",byzantine_vectors
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                temp = byzantine_vectors.pop().pop()
                print temp
                if temp == 'True':
                    for i in range(0, no_total):
                        byzantine_vectors_to_dict[str(i+1)] = 'Attack'
                elif temp == 'False':
                    for i in range(0, no_total):
                        byzantine_vectors_to_dict[str(i+1)] = 'Retreat'
                t = Thread(target=contact_vessel, args = (vessel_ip,'/propagate_vector/{}'.format(node_id),byzantine_vectors_to_dict)) 
                t.daemon = True
                t.start()
                time.sleep(1)
                byzantine_vectors_to_dict = {}



    def find_result_vector():
        global vector,no_total,no_loyal,result_vector
        result_vector = []
        count_attack = []
        count_retreat = []
        for i in range(0,no_total):
            count_attack.append(0)
            count_retreat.append(0)
        for general_id,vote_results in vector.items():
            for i in range(0,no_total):
                if vote_results[str(i+1)] == "Attack":
                    count_attack[i] = count_attack[i] + 1
                elif vote_results[str(i+1)] == "Retreat":
                    count_retreat[i] = count_retreat[i] + 1
        for i in range(0,no_total):
            if count_attack[i] > count_retreat[i]:
                result_vector.append("Attack")
            elif count_attack[i] < count_retreat[i]:
                result_vector.append("Retreat")
            else:
                result_vector.append("UNKNOWN")
        print "\nresult_vectors is:",result_vector
        find_final_result(result_vector)


    def find_final_result(result_vector):
        global no_total,no_loyal,final_result
        count_attack = 0
        count_retreat = 0
        for i in range(0,no_total):
            if result_vector[i] == "Attack":
                count_attack = count_attack + 1
            elif result_vector[i] == "Retreat":
                count_retreat = count_retreat + 1
        if count_attack > count_retreat:
            final_result = "Attack"
        elif count_attack < count_retreat:
            final_result = "Retreat"
        else:
            final_result = "UNKNOWN"


    # ------------------------------------------------------------------------------------------------------
    # ROUTES
    # ------------------------------------------------------------------------------------------------------
    # a single example (index) should be done for get, and one for post
    # ------------------------------------------------------------------------------------------------------
    @app.route('/')
    def index():
        global final_result,vote_vector_result_dict,result_vector
        return template('server/index.tpl', board_title='Vessel {}'.format(node_id), vote_dict = sorted(board.iteritems()),\
                                            vote_vector_dict = sorted(vote_vector_result_dict.iteritems()), final_result_vector = result_vector, \
                                            f_result = final_result,members_name_string='lhan@student.chalmers.se;shahn@student.chalmers.se')


    @app.get('/vote/result')
    def vote_result():
        global final_result,vote_vector_result_dict,result_vector,byzantine_node,node_id
        for temp_vessel_id, temp_vector_result in vector.items():
            vote_vector_result_dict[temp_vessel_id] = sorted(temp_vector_result.iteritems())
        return template('server/boardcontents_template.tpl',board_title ='Vessel {}'.format(node_id), vote_dict = sorted(board.iteritems()),\
            vote_vector_dict = sorted(vote_vector_result_dict.iteritems()),final_result_vector = result_vector, f_result= final_result)

    @app.post('/vote/attack')
    def vote_attack():
        add_new_element_to_store(node_id,"Attack")
        t = Thread(target=propagate_to_vessels, args = ('/propagate/{}'.format(node_id),'Attack')) 
        t.daemon = True
        t.start()


    @app.post('/vote/retreat')
    def vote_retreat():
        add_new_element_to_store(node_id, "Retreat")
        t = Thread(target=propagate_to_vessels, args = ('/propagate/{}'.format(node_id),'Retreat')) 
        t.daemon = True
        t.start()


    @app.post('/propagate/<precede_id:int>')
    def propagation_received_vote(precede_id):
        global no_total,byzantine_node,node_id
        try:
            body = request.body.read()
            add_new_element_to_store(precede_id, body)
            if len(board) == no_total:
                t = Thread(target=propagate_to_vessels, args = ('/propagate_vector/{}'.format(node_id),board)) 
                t.daemon = True
                t.start()
            return True
        except Exception as e:
            print e
        return False


    @app.post('/vote/byzantine')
    def vote_byzantine():
        global no_loyal,no_total, node_id,byzantine_node
        byzantine_node = node_id
        #add_new_element_to_store(node_id, "Byzantine")

        byzantine_vote = compute_byzantine_vote_round1(no_loyal,no_total,True)
        byzantine_vectors = compute_byzantine_vote_round2(no_loyal,no_total,True)

        print "\nbyzantine_vote is :", byzantine_vote
        print "\nbyzantine_vectors is :", byzantine_vectors
        t1 = Thread(target=propagate_byzantine_vote_to_vessels(byzantine_vote))
        t1.daemon = True
        t1.start()
        t2 = Thread(target=propagate_byzantine_vectors_to_vessels(byzantine_vectors))
        t2.daemon = True
        t2.start()



    @app.post('/propagate_vector/<precede_id:int>')
    def receive_propagated_vector(precede_id):
        global no_total,vector
        try:
            received_value = request.body.read()
            temp = received_value.split("&")
            received_vector = {}
            for i in range(0,no_total):
                tem1,tem2 = temp[i].split("=")
                received_vector[tem1] = tem2
            add_new_vector(precede_id, received_vector)
            if len(vector) == no_loyal:
                find_result_vector()
            return True
        except Exception as e:
            print e
        return False



    #Simple methods that the byzantine node calls to decide what to vote.
    #Compute byzantine votes for round 1, by trying to create
    #a split decision.
    #input: 
    #   number of loyal nodes,
    #   number of total nodes,
    #   Decision on a tie: True or False 
    #output:
    #   A list with votes to send to the loyal nodes
    #   in the form [True,False,True,.....]
    def compute_byzantine_vote_round1(no_loyal,no_total,on_tie): 
        result_vote = []
        for i in range(0,no_loyal):
            if i%2==0:
                result_vote.append(str(not on_tie))
            else:
                result_vote.append(str(on_tie))
        return result_vote

    #Compute byzantine votes for round 2, trying to swing the decision
    #on different directions for different nodes.
    #input: 
    #   number of loyal nodes,
    #   number of total nodes,
    #   Decision on a tie: True or False
    #output:
    #   A list where every element is a the vector that the 
    #   byzantine node will send to every one of the loyal ones
    #   in the form [[True,...],[False,...],...]
    def compute_byzantine_vote_round2(no_loyal,no_total,on_tie):
        result_vectors=[]
        for i in range(0,no_loyal):
            if i%2==0:
                result_vectors.append([str(on_tie)]*no_total)
            else:
                result_vectors.append([str(not on_tie)]*no_total)
        return result_vectors


    # ------------------------------------------------------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------------------------------------------------------
    # Execute the code
    def main():
        global vessel_list, node_id, app, vote_dict,no_total,no_loyal, final_result, board, vector,vote_vector_result_dict,result_vector,byzantine_node
        byzantine_node = 0
        port = 80
        final_result = ""
        parser = argparse.ArgumentParser(description='Your own implementation of the distributed blackboard')
        parser.add_argument('--id', nargs='?', dest='nid', default=1, type=int, help='This server ID')
        parser.add_argument('--vessels', nargs='?', dest='nbv', default=1, type=int, help='The total number of vessels present in the system')
        args = parser.parse_args()
        node_id = args.nid
        vessel_list = dict()
        # We need to write the other vessels IP, based on the knowledge of their number
        for i in range(1, args.nbv+1):
            vessel_list[str(i)] = '10.1.0.{}'.format(str(i))
        no_total = args.nbv
        no_loyal = no_total-1
        try:
            run(app, host=vessel_list[str(node_id)], port=port)
        except Exception as e:
            print e
    # ------------------------------------------------------------------------------------------------------
    if __name__ == '__main__':
        main()
except Exception as e:
        traceback.print_exc()
        while True:
            time.sleep(60.)