import sys, os, time
from statistics import mean
from random import randint
import numpy as np
from numpy.core.fromnumeric import take

NB_RUNS = 10
PERIOD = 2
PERIOD_AUGMENTATION = 2
ADDITIONAL_PENALITY = 1

# variable globale qui peut servir à stocker des informations d'un appel à l'autre si besoin
global_state = {"call":-1, "cut":0, "possible_vals": [-1,1,-1], "sigma": [], "partial_best":[], "PERIOD":PERIOD, "PERIOD_AUGMENTATION":PERIOD_AUGMENTATION} 



def format_me(val, ring_size):
    if val < 0:
        return int(ring_size+val) 
    return int(val)

def online_partial_utils(ring_size, alpha, sigma, current_cut):
    freq = [0]*ring_size
    for msg in sigma:
        freq[msg] += 1
    costs = np.array(freq)
    costs = costs + np.concatenate((costs[ring_size//2:], costs[:ring_size//2]))

    nb_neighbors = 1
    rounds = len(global_state["sigma"])/(ring_size*PERIOD)
    # if rounds > 30:
    #     nb_neighbors = 2



    for i, c in enumerate(costs):
        index = i % (ring_size//2)
        if current_cut < index:
            if min(index-current_cut, current_cut+(ring_size//2)-index) <= nb_neighbors:
                costs[i] += 2*alpha*min(index-current_cut, current_cut+(ring_size//2)-index)*ADDITIONAL_PENALITY
            else :
                costs[i] +=  alpha*ring_size*len(global_state["sigma"])*ring_size*10000 #infinity
        if current_cut > index:
            if min(current_cut-index, index+(ring_size//2)-current_cut) <= nb_neighbors:
                costs[i] += 2*alpha*min(current_cut-index, index+(ring_size//2)-current_cut)*ADDITIONAL_PENALITY
            else :
                costs[i] +=  alpha*ring_size*len(global_state["sigma"])*ring_size*10000 #infinity

    # print(costs)
    return np.argmin(costs)

def online_partial(global_state, ring_size, alpha, current_cut=0, n_cuts = 5, take_only=-1):
    if take_only <0:
        sigma = global_state["sigma"]
    else:
        sigma = global_state["sigma"][-take_only:]
    sigma_len = len(sigma)
    sigma_cuts = []
    for c in range(n_cuts):
        sigma_cuts.append(sigma[sigma_len*c//n_cuts:sigma_len*(c+1)//n_cuts])
    cuts = []
    best_cut = current_cut
    for cut in sigma_cuts:
        best_cut= online_partial_utils(ring_size, alpha, cut, best_cut)
        cuts.append(best_cut)
    
    global_state["partial_cuts"] = n_cuts
    global_state["partial_best"] = cuts
    return global_state


def build_frec(sigma, ring_size):
    frec = [0]*ring_size
    for msg in sigma:
        frec[msg] += 1
    return frec
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

    # initialiser la variable globale lors du premier appel
    global_state["call"] += 1
    if first_call:
        global_state["call"] = 0
        global_state["sigma"] = []
        # index = randint(0, 2)
        # # global_state["cut"] = global_state["possible_vals"][index]
        global_state["cut"] = format_me(255, ring_size)
        # global_state["frec"] = [0]*ring_size
        global_state["period"] = ring_size*randint(30,90)//10
        global_state["period_coef"] = randint(1,3)
        global_state["algo"] = randint(0,4)
        global_state["limite"] = randint(77,83)

    global_state["sigma"].append(new_msg)

    if global_state["algo"] < 1:
        period = global_state["period"]
        period_coef = global_state["period_coef"]
        if (global_state["call"]) % (period) == 50:
            frec = build_frec(global_state["sigma"][-period//period_coef:], ring_size)
            costs = np.array(frec)

            costs = costs + np.concatenate((costs[ring_size//2:], costs[:ring_size//2]))

            #go left
            if costs[format_me(current_cut-1, ring_size)] + 2*alpha < costs[format_me(current_cut, ring_size)]:
                if randint(0,100)>global_state["limite"]:
                    global_state["cut"] = format_me(current_cut-1, ring_size)
            # #go far left
            # if costs[format_me(current_cut-2, ring_size)] + ADDITIONAL_PENALITY*2*2*alpha < costs[format_me(current_cut, ring_size)]:
            #     if randint(0,100)>980:
            #         global_state["cut"] = format_me(current_cut-2, ring_size)
            #go right
            if costs[format_me(current_cut+1, ring_size)] + 2*alpha < costs[format_me(current_cut, ring_size)]:
                if randint(0,100)>global_state["limite"]:
                    global_state["cut"] = format_me(current_cut+1, ring_size)
            # #go far right
            # if costs[format_me(current_cut+2, ring_size)] + ADDITIONAL_PENALITY*2*2*alpha < costs[format_me(current_cut, ring_size)]:
            #     if randint(0,100)>980:
            #         global_state["cut"] = format_me(current_cut+2, ring_size)
        
    else :
        if (global_state["call"]+1) % (ring_size*global_state["PERIOD"]) == 0:
            global_state["PERIOD"] *= global_state["PERIOD_AUGMENTATION"]
            global_state = online_partial(global_state, ring_size, alpha, current_cut=current_cut, n_cuts=1, take_only=-1)
            global_state["cut"] = global_state["partial_best"][-1]
        
    return format_me(global_state["cut"], ring_size) # la coupe/2-clusters courante est conservée, ceci n'est pas une solution optimale






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
        nb_runs = NB_RUNS
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
        global_state["call"] = 0 #Added
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

