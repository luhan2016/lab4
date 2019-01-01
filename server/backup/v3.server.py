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
    FinalResult = []

    # ------------------------------------------------------------------------------------------------------
    # BOARD FUNCTIONS
    # ------------------------------------------------------------------------------------------------------
    def add_new_element_to_store(vesselID, vote_value):
        print "in add_new_element_to_store"
        global board
        success = False
        try:
            board[vesselID] = vote_value
            print "node_id {} vote is{} ".format(node_id, board)
            success = True
        except Exception as e:
            print e
        return success

    def add_new_vectore(vesselID, vote_result_dict):
        print "in add_new_element_to_store"
        global vector
        success = False
        try:
            vector[vesselID] = vote_result_dict
            print "nfdfdfdfode_id {} vote is{} ".format(node_id, vote_result_dict)
            success = True
        except Exception as e:
            print e
        return success

    # ------------------------------------------------------------------------------------------------------
    # DISTRIBUTED COMMUNICATIONS FUNCTIONS
    # ------------------------------------------------------------------------------------------------------
    def contact_vessel(vessel_ip, path, payload=None, req='POST'):
        # Try to contact another server (vessel) through a POST or GET, once
        print "in contract verssel"
        success = False
        try:
            if 'POST' in req:
                print "post {}, {},payload is {}".format(vessel_ip, path,payload)
                res = requests.post('http://{}{}'.format(vessel_ip, path), data=payload)
            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(vessel_ip, path))
            else:
                print 'Non implemented feature!'
            # result is in res.text or res.json()
            if res.status_code == 200:
                success = True
        except Exception as e:
            print e
        return success


    def propagate_to_vessels(path, payload = None, req = 'POST'):
        global vessel_list, node_id
        print "in propagate_to_vessels"
        for vessel_id, vessel_ip in vessel_list.items():
            print "vessel_id is ",vessel_id
            if int(vessel_id) != node_id: # don't propagate to yourself
                success = contact_vessel(vessel_ip, path, payload, req)
                if not success:
                    print "Could not contact vessel {}".format(vessel_id)


    def propagate_byzantine_vote_to_vessels(byzantine_vote):
        print "\npropagate_byzantine_vote_to_vessels\n"
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                payload = byzantine_vote.pop()
                print 'payload is: ',payload
                t = Thread(target=contact_vessel, args = (vessel_ip,'/propagate/{}'.format(node_id),payload)) 
                t.daemon = True
                t.start()


    def propagate_byzantine_vectors_to_vessels(byzantine_vectors):
        print "\npropagate_byzantine_vectors_to_vessels\n"
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            temp_dict = {}
            if int(vessel_id) != node_id: # don't propagate to yourself
                temp = byzantine_vectors.pop()
                tem = temp.pop()
                if tem == 'True':
                    for i in range(0, no_total):
                        result_vector_dict[i] = 'Attack'
                else:
                    for i in range(0, no_total):
                        result_vector_dict[i] = 'Retreat'
                t = Thread(target=contact_vessel, args = (vessel_ip,'/propagateVector/{}'.format(node_id),result_vector_dict)) 
                t.daemon = True
                t.start()




    # ------------------------------------------------------------------------------------------------------
    # ROUTES
    # ------------------------------------------------------------------------------------------------------
    # a single example (index) should be done for get, and one for post
    # ------------------------------------------------------------------------------------------------------
    @app.route('/')
    def index():
        return template('server/index.tpl', board_title='Vessel {}'.format(node_id), vote_dict = sorted(board.iteritems()),f_result = final_result,\
                                            members_name_string='lhan@student.chalmers.se;shahn@student.chalmers.se')


    @app.get('/vote/result')
    def vote_result():
        global final_result,FinalResult,no_total,no_loyal
        count_attack = 0
        count_retreat = 0
        if len(FinalResult) == no_loyal:
            for i in range(0,no_total):
                if FinalResult.pop == 'Attack':
                    count_attack = count_attack + 1:
                elif FinalResult.pop() == 'Retreat':
                    count_retreat = count_retreat + 1
        if count_retreat > count_attack:
            final_result = 'Retreat'
        elif count_attack > count_retreat:
            final_result = 'Attack'
        elif count_retreat == count_attack and count_attack != 0:
            final_result = "Unknown"
        return template('server/boardcontents_template.tpl',board_title ='Vessel {}'.format(node_id), f_result= final_result,\
                                                                     vote_dict =sorted(board.iteritems()))

    @app.post('/vote/attack')
    def vote_attack():
        print "attack"
        add_new_element_to_store(node_id,"Attack")
        t = Thread(target=propagate_to_vessels, args = ('/propagate/{}'.format(node_id),'Attack')) 
        t.daemon = True
        t.start()


    @app.post('/vote/retreat')
    def vote_retreat():
        print "retreat"
        add_new_element_to_store(node_id, "Retreat")
        t = Thread(target=propagate_to_vessels, args = ('/propagate/{}'.format(node_id),'Retreat')) 
        t.daemon = True
        t.start()


    @app.post('/propagate/<precede_id:int>')
    def propagation_received_vote(precede_id):
        global no_total
        try:
            body = request.body.read()
            add_new_element_to_store(precede_id, body)
            if len(board) == no_total:
                print "receive all votes, vote is: ", board
                t = Thread(target=propagate_to_vessels, args = ('/propagateVector/{}'.format(node_id),board)) 
                t.daemon = True
                t.start()
            return True
        except Exception as e:
            print e
        return False


    @app.post('/vote/byzantine')
    def vote_byzantine():
        global no_loyal,no_total, node_id
        add_new_element_to_store(node_id, "Byzantine")

        byzantine_vote = compute_byzantine_vote_round1(no_loyal,no_total,True)
        byzantine_vectors = compute_byzantine_vote_round2(no_loyal,no_total,True)

        print "byzantine_vote is :", result_vote
        print "byzantine_vectors is :", result_vectors

        t1 = Thread(target=propagate_byzantine_vote_to_vessels, args = (byzantine_vote))
        t1.daemon = True
        t1.start()

        t2 = Thread(target=propagate_byzantine_vectors_to_vessels, args = (byzantine_vectors))
        t2.daemon = True
        t2.start()


    @app.post('/propagateVector/<precede_id:int>')
    def propagation_received_vector(precede_id):
        global no_total,vector
        try:
            body = request.body.read()
            print "hiiiiii, body is: ",body
            add_new_vectore(precede_id, body)
            if len(vector) == no_total:
                vessel_vote_result()
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
        print "compute_byzantine_vote_round1"
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
        print "compute_byzantine_vote_round2"
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
        global vessel_list, node_id, app, vote_dict,no_total,no_loyal, final_result, board, vector,FinalResult
        no_loyal = 3
        port = 80
        final_result = ''
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