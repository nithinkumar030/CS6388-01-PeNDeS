"""
This is where the implementation of the plugin code goes.
The PeNDeSClassifierSim-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('PeNDeSClassifierSim')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)




class PeNDeSClassifierSim(PluginBase):

    

    def main(self):
        core = self.core
        root_node = self.root_node
        active_node = self.active_node
        META = self.META
        #logger = self.logger

        name = core.get_attribute(active_node, 'name')

        #logger.info('ActiveNode at "{0}" has name {1}'.format(core.get_path(active_node), name))

        core.set_attribute(active_node, 'name', 'newName')

        commit_info = self.util.save(root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        #logger.info('committed :{0}'.format(commit_info))


        places = []
        transitions = []
        P2Ts = []
        T2Ps = []
        placePathVsName = {}

        nodes = core.load_sub_tree(active_node)
        for node in nodes:
            if core.is_type_of(node, META['Place']):
                #logger.info('[{0}] place has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                #places.append({"name":core.get_attribute(node, 'name')})

                placeName = core.get_attribute(node, 'name')
                
                if(placeName != 'Place'):
                    placePathVsName[core.get_path(node)] =  placeName
                    places.append(node)
                    logger.info('[{0}] place has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                
        
       
            if core.is_type_of(node, META['Transition']):
              
                #logger.info('[{0}] transition has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                #transition.append({"name":core.get_attribute(node, 'name')})

                transitionName = core.get_attribute(node, 'name')

                if(transitionName != 'Transition'):
                    transitions.append(node)
                    logger.info('[{0}] transition has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                
            
            if core.is_type_of(node, META['P2T']):
              
                #logger.info('[{0}] T2P has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                #P2T.append({"name":core.get_attribute(node, 'name')})
                P2TName = core.get_attribute(node, 'name')
                if(P2TName != 'P2T'):
                    P2Ts.append(node)
                    logger.info('[{0}] P2T has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                
            
            
            if core.is_type_of(node, META['T2P']):
              
                #logger.info('[{0}] T2P has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                #T2P.append({"name":core.get_attribute(node, 'name')})
                T2PName = core.get_attribute(node, 'name')
                if(T2PName != 'T2P'):
                    T2Ps.append(node)
                    logger.info('[{0}] T2P has name: {1}'.format(core.get_path(node),core.get_attribute(node, 'name')))
                
        
    
        #check for Free choice petriNet

        NotFreeChoicePN = False

        if (len(places) == 0):
            NotFreeChoicePN = True

        if (len(transitions) == 0):
            NotFreeChoicePN = True

        
        for place in places:
            countOutgoingArcFromPlace=0
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            countOutgoingArcFromPlace = countOutgoingArcFromPlace +1


              
            if(countOutgoingArcFromPlace > 1):
                NotFreeChoicePN = True
                break
                
        
        if  NotFreeChoicePN == True:
            #logger.debug('Not a free choice petri Net!')
            self.send_notification('Not a free choice petri Net!')
        else:
            #logger.debug('Free choice petri Net!')
            self.send_notification('Free choice petri Net!')
      
        

        # check for state machine

        notSM = False

        if (len(transitions) == 0):
            notSM = True

        for transition in transitions:
            countIncomingArctoTransition=0
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(P2T,pointer)

                        transitionPath = core.get_path(transition)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1

                        logger.info('Incoming arc to transition :dstpath {0} transitionPath {1}'.format(dstpath, transitionPath))

                        if dstpath == transitionPath:
                            countIncomingArctoTransition = countIncomingArctoTransition +1

            if(countIncomingArctoTransition != 1):
                notSM = True
                break


            countOutgoingArcFromTransition=0
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(T2P,pointer)

                        transitionPath = core.get_path(transition)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        logger.info('Outgoing arc from transition :srcpath {0} transitionPath {1}'.format(dstpath, transitionPath))

                        if srcpath == transitionPath:
                            countOutgoingArcFromTransition = countOutgoingArcFromTransition + 1

            if(countOutgoingArcFromTransition != 1):
                notSM = True
                break
        
        if  notSM == True:
            #logger.debug('Not a free choice petri Net!')
            self.send_notification('Not StateMachine!')
        else:
            #logger.debug('Free choice petri Net!')
            self.send_notification('StateMachine!')



        # check for Marked graph

        notMG = False

        if (len(places) == 0):
            notMG = True

        for place in places:
            countIncomingArctoPlaces=0
            for T2P in T2Ps:
                
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(T2P,pointer)

                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        logger.info('incoming arc to place :dstpath {0} placePath {1}'.format(dstpath, placePath))
                        if dstpath == placePath:
                            countIncomingArctoPlaces = countIncomingArctoPlaces +1

            if(countIncomingArctoPlaces != 1):
                notMG = True
                break


            countOutgoingArcFromPlace=0
                   
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)

                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1

                        logger.info('outgoing arc from place :srcpath {0} placePath {1}'.format(srcpath, placePath))
                        if srcpath == placePath:
                            countOutgoingArcFromPlace = countOutgoingArcFromPlace + 1

            if(countOutgoingArcFromPlace != 1):
                notMG = True
                break


            
        
        if  notMG == True:
            #logger.debug('Not a free choice petri Net!')
            self.send_notification('Not Marked Graph!')
        else:
            #logger.debug('Free choice petri Net!')
            self.send_notification('Marked Graph!')

        

    


        #find place s which has only 1 outgoing arc
        #find place o  which has only 1 incoming arc
        # then traverse from s to o using Breadth first search (BFS) to find a path between s and o


        S = True
        source = []

        #if (len(places) == 0):
        #    NotS = True

        #if (len(transitions) == 0):
        #    NotS = True

        countS =0


        for place in places:
            countOutgoingArcFromPlace=0
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            countOutgoingArcFromPlace = countOutgoingArcFromPlace +1


            countIncomingArcToPlace=0
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        srcpath=core.get_pointer_path(T2P,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            countIncomingArcToPlace = countIncomingArcToPlace +1


            if (countIncomingArcToPlace == 0) and  (countOutgoingArcFromPlace == 1):
                countS = countS +1
                source.append(place)


        if(countS ==1):
            S=True
        else:
            source.clear()

 


        O = False
        sink =[]
        countO = 0

        for place in places:

            countIncomingArcToPlace=0
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        srcpath=core.get_pointer_path(T2P,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            countIncomingArcToPlace = countIncomingArcToPlace +1

            countOutgoingArcFromPlace=0
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            countOutgoingArcFromPlace = countOutgoingArcFromPlace +1

            if (countIncomingArcToPlace == 1) and  (countOutgoingArcFromPlace == 0):
                countO = countO +1
                sink.append(place)

        if(countO == 1 ):
            O=True
        else:
            sink.clear()    
              
                
        
        if  (S == True) and (O == True):
            #logger.debug('Not a free choice petri Net!')
            self.send_notification('Workflow Net')
        else:
            #logger.debug('Free choice petri Net!')
            self.send_notification('Not Workflow Net!')
            source.clear()
            sink.clear()



        


        ################ build the place adjacent list ######################

        O = False
        countO = 0
        placeAdjList = {}
        P2TGetDstFromSrc= {}
        P2TgetTransitionFromDst = {}
        transitionList = []


        for place in places:
            
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                srcpath=''
                dstpath=''
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)
            
                       
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(P2T,pointer)


                    if(dstpath != ""):
                        P2TGetDstFromSrc[srcpath] = dstpath
                        
                        srcpath=""
                        dstpath=""


        for transition in transitions:
            
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(P2T,pointer)

                        transitionPath = core.get_path(transition)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1

                        logger.info('Incoming arc to transition :dstpath {0} transitionPath {1}'.format(dstpath, transitionPath))

                        if dstpath == transitionPath:
                            P2TgetTransitionFromDst[dstpath] = transition

                    


        
        for place in places:
            
            countOutgoingArcFromPlace=0
            for P2T in P2Ts:
                pointers = core.get_pointer_names(P2T)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(P2T,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == placePath:
                            #countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                            if srcpath in P2TGetDstFromSrc.keys():
                                dstpath = P2TGetDstFromSrc[srcpath]
                                #get the Transition from the
                                transition = P2TgetTransitionFromDst[dstpath] 
                                transitionList.append(transition)
                                placeAdjList[placePath] = transitionList







        ################# Build the transition adjacent list ########################### 
        
        transitionAdjList = {}
        T2PGetDstFromSrc= {}
        T2PgetPlaceFromDst = {}
        placeList = []


        for transition in transitions:
            
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                srcpath=''
                dstpath=''
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(T2P,pointer)
            
                       
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(T2P,pointer)


                    if(dstpath != ""):
                        T2PGetDstFromSrc[srcpath] = dstpath
                        
                        srcpath=""
                        dstpath=""


        for place in places:
            
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'dst':
                        dstpath=core.get_pointer_path(T2P,pointer)

                        placePath = core.get_path(place)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1

                        logger.info('Incoming arc to transition :dstpath {0} transitionPath {1}'.format(dstpath, transitionPath))

                        if dstpath == placePath:
                            T2PgetPlaceFromDst[dstpath] = place

                    


        
        for transition in transitions:
            
            for T2P in T2Ps:
                pointers = core.get_pointer_names(T2P)
                for pointer in pointers:
          
                    if pointer == 'src':
                        srcpath=core.get_pointer_path(T2P,pointer)
            
                        #srcPlaceName = placePathVsName[srcpath]
            
                        #placeName = core.get_attribute(place, 'name')
                        transitionPath = core.get_path(transition)
            
                        #if placeN == srcPlaceName:
                        #    countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                        if srcpath == transitionPath:
                            #countOutgoingArcFromPlace = countOutgoingArcFromPlace +1
                            if srcpath in T2PGetDstFromSrc.keys():
                                dstpath = T2PGetDstFromSrc[srcpath]
                                #get the Transition from the
                                place = T2PgetPlaceFromDst[dstpath] 
                                placeList.append(place)
                                transitionAdjList[transitionPath] = placeList


        ########## do a Breadth first search from S to O   to check path from S to O #########

        # source node and sink node
        #source
        #sink 
        discoveredPlaceQ = []
        discoveredTransitionQ = []
        for src in source:
            discoveredPlaceQ.append(src)
    
        for place in discoveredPlaceQ:
            #discoveredPlaceQ.remove(place)
            if(place == sink[0]):
                 self.send_notification('Workflow Net .. path between S and O')
                 return

            placePath = core.get_path(place)
            if  placePath in placeAdjList.keys():
                transitionList = placeAdjList[placePath]
                for transition in transitionList:
                
                    discoveredTransitionQ.append(transition)

                for transition in discoveredTransitionQ:
                    #discoveredTransitionQ.remove(transition)
                    transitionPath = core.get_path(transition)
                    if transitionPath in transitionAdjList.keys():
                        placeList = transitionAdjList[transitionPath]
                        for place1 in placeList:
                            discoveredPlaceQ.append(place1)




                    



      
        
        

