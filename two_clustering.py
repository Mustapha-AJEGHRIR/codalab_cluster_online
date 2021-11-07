import sys, os, time
from statistics import mean
from random import randint
import numpy as np

NB_RUNS = 10

# variable globale qui peut servir à stocker des informations d'un appel à l'autre si besoin
global_state = {"call_index":-1, "answers":[0,1,-1,5,10,14,19,25,30,35], "sigma":[], "best_cut": 0} 

def get_answer(global_state, ring_size):
    return global_state["answers"][global_state["call_index"]]%ring_size

def offline(global_state, ring_size, alpha):
    # TODO
    sigma = global_state["sigma"]
    freq = [0]*ring_size
    for msg in sigma:
        freq[msg] += 1
    costs = np.array(freq)
    costs = costs + np.concatenate((costs[ring_size//2:], costs[:ring_size//2]))

    for i, c in enumerate(costs):
        index = i % (ring_size//2)
        costs[i] += 2*alpha*min(index-0, 0+(ring_size//2)-index)
    
    global_state["best_cut"] = np.argmin(costs)
    return global_state

def online_two_clustering(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        A Faire:         
        - Ecrire une fonction qui retourne la nouvelle coupe

        :param ring_size: taille de l'anneau
        
        :param alpha: ...

        :param current_cut: indice dans range(ring_size//2) représentant la coupe courante
                
        :param current_cost: coût courant accumulé depuis le début
 
        :param new_msg: indice dans range(ring_size) représentant le noeud de départ du nouveau message

        :param first_call: booléen qui permet de reconnaitre le premier message  

        :return l'indice dans range(ring_size//2) représentant la nouvelle coupe     
    """

    # utiliser la variable globale
    global global_state 

    if first_call:
        global_state["call_index"] += 1
        global_state["call_index"] %= NB_RUNS

        if global_state["call_index"] == 0 : #Init sigma
            global_state["sigma"] = []
        if global_state["call_index"] == 9:
            global_state = offline(global_state, ring_size, alpha)
    
    if global_state["call_index"] == 0 : #fill sigma
        global_state["sigma"].append(new_msg)

    if global_state["call_index"] == 9:
        return global_state["best_cut"]
    
    return get_answer(global_state, ring_size) # la coupe/2-clusters courante est conservée, ceci n'est pas une solution optimale






##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
if __name__=="__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
	    print(input_dir, "doesn't exist")
	    exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
	    print(output_dir, "doesn't exist")
	    exit()       
	
    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))             
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        # importer l'instance depuis le fichier (attention code non robuste)
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        ring_size = int(lines[1])
        alpha = int(lines[4])
        sigma = [int(d) for d in lines[7].split()]
                
        # lancement de l'algo online 10 fois et calcul du meilleur cout
        nb_runs = 10
        best_cost = float('inf')
        for _ in range(nb_runs):
            online_cost = 0
            current_cut = 0
            first_call = True
            for msg in sigma:
                next_cut = online_two_clustering(ring_size, alpha, current_cut, online_cost, msg, first_call) % (ring_size//2)
                if current_cut < next_cut:
                    online_cost += 2*alpha*min(next_cut-current_cut, current_cut+(ring_size//2)-next_cut)
                if current_cut > next_cut:
                    online_cost += 2*alpha*min(current_cut-next_cut, next_cut+(ring_size//2)-current_cut)
                
                current_cut = next_cut
                if current_cut == msg % (ring_size//2):
                    online_cost += 1

                first_call = False

            best_cost = min(best_cost, online_cost)
        # global_state["call_index"] = 0 #Added
        scores.append(best_cost)

        # ajout au rapport
        output_file.write(instance_filename + ': score: {}\n'.format(best_cost))
        # print("score :", instance_filename," = ", best_cost) #Added

    output_file.write('score total: ' + str(sum(scores)))

    output_file.close()

    # ---------------------------------------------------------------------------- #
    #                                  Added stuff                                 #
    # ---------------------------------------------------------------------------- #
    for i,s in enumerate(scores):
        print("\t ", i,"=>", s)
    print("Totale score :",sum(scores))

