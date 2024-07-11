import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm
from collections import Counter
from functools import partial
'''
ANIMATION CLEAN-UP TOOL
Description: Add this code to your toolbar for easy animation baking and pre-export prep. 
This code will import your references, clean up your rig's namespace, bake your animation, and delete your controllers.
Date: 10/22/2022
Author: Miranda Koulogeorge & Jennifer Menndez
'''



def Warning():
    response = pm.confirmDialog( title='Warning', message='This process will import your referance and delete your rig without saving your file. Do you wish to continue?', button=['Yes', 'Cancel'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel' )           
    if response == "Yes":
        print("Yes")
    if response == "Cancel":
        pm.error("Operation Canceled by User.")

def doIt():
    ''' 
    Find all namespaces in scene and remove them.
    Except for default namespaces
    '''
    # Get a list of namespaces in the scene
    # recursive Flag seraches also children
    # internal Flag excludes default namespaces of Maya
    namespaces = []
    for ns in pm.listNamespaces(root=None, recursive =True, internal =False):
        namespaces.append(ns)
        print ('Namespace ' + ns + ' added to list.')

    # Reverse Iterate through the contents of the list to remove the deepest layers first
    for ns in reversed(namespaces):
        currentSpace = ns
        cmds.namespace(removeNamespace = ns, mergeNamespaceWithRoot = True)
        print (currentSpace + ' has been merged with Root!')

    # Empty the List
    namespaces[:] = [] 

def importRef(*args):    
    all_ref_paths = cmds.file(q=True, reference=True) or []  # Get a list of all top-level references in the scene
    for ref_path in all_ref_paths:
        if cmds.referenceQuery(ref_path, isLoaded=True):  # Only import it if it's loaded, otherwise it would throw an error.                      
            cmds.file(ref_path, importReference=True)  # Import the reference.
            new_ref_paths = cmds.file(q=True, reference=True)  # If the reference had any nested references they will now become top-level references, so recollect them.
            if new_ref_paths:
                for new_ref_path in new_ref_paths:
                    if new_ref_path not in all_ref_paths:  # Only add on ones that we don't already have.
                        all_ref_paths.append(new_ref_path)
    	

def bakeKeys(*args):
    rootJnt=[]
    tStart = cmds.playbackOptions(q=True, min=True)
    tEnd = cmds.playbackOptions(q=True, max=True)
    print ("tStart-->" , tStart )
    print ("tEnd-->" , tEnd)
    #------------------------
              
    meshSel=cmds.ls(dag=True,type='mesh')  #selecats all potetial meshes on the scene
    print ("meshSel-->", meshSel)  
         
    for m in meshSel:
        #for X in skinList[0]:
        print ("skinList[0] for X", m)
        names ='findRelatedSkinCluster("' + m + '")'    
        skinCls=mm.eval(names) #looking for the skinClurster out of the list of potential meshes
        print ("skinCls---->", skinCls)
    
        if skinCls == '':
                print("-----> no actual skin on " + m + "!") 
        else:
    
           
            jnts = cmds.skinCluster(m, ibp=False, inf = True, q = True) ## get the bnd jnts data from the skincluster mesh NOTE(since joint data are taken by a skin joints will be not be in roder)
            print ("jnts---->", jnts)
      
            parentList = cmds.listRelatives(jnts, c=True, f=True) #<-----List all joint with all full paths and  children data. making the ROOT joint first in line, then SPLITS it and take the first one [0] single out the first joint of the hierchy   ##<-----------Most maya.cmds function return strings or list of strings.
                    
                                    
                             ### MAKING SURE IF THE ROOT JOINT IS ON THE parentList LIST ####
            if parentList == None:
                print ("*****All Parent flag route****")
                parentList = cmds.listRelatives(jnts, ap=1, f=True)[0].split('|') if jnts else [] #<-----List all joint with all full paths and  children data. making the ROOT joint first in line, then SPLITS it and take the first one [0] single out the first joint of the hierchy                                                                                         ##<-----------Most maya.cmds function return strings or list of strings.
            
            else:
                print ("*****Children flag route*****")
                parentList = cmds.listRelatives(jnts, c=1, f=True)[0].split('|') if jnts else []
            print ("parentList", parentList)

            for jnt in parentList:   
                if jnt and cmds.nodeType(jnt) == 'joint':
    
                    rootJnt.append(jnt)
    print  ("rootJnt" , rootJnt[0])                
     ######******* making saure if key frames text field has numbers      
    cmds.bakeResults(rootJnt[0] , simulation= True,  t=(tStart,tEnd), hierarchy='below', sampleBy=1, oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False ,minimizeRotation=True, controlPoints=False, shape=True)
    
    ##*********delete all cons of the jnty hi and release the BND jnt grp free******
    cmds.delete(cmds.ls(rootJnt[0],dag=1,ap=1,type='constraint'))
    cmds.select(cmds.ls(rootJnt[0],dag=1,ap=1,type='transform'))
    cmds.select(cmds.ls(rootJnt[0],dag=1,ap=1,type='joint'),d=1)
    cmds.delete()

def deleteRig(*args):
	 # tells maya to detect all transform nodes in the scene file
    transforms =  cmds.ls(type='transform')
    deleteList = []

    #ask if there is any empty groups on from the list
    for tran in transforms:
        if cmds.nodeType(tran) == 'transform':
            children = cmds.listRelatives(tran, c=True)
            if children == None:
                print ('%s, has no childred' %(tran))
                deleteList.append(tran)
    #cmds.select(deleteList)

    # ask maya to detects the second parent source where the empty goups are coming from 
    topParent=cmds.listRelatives(deleteList, ad=1,ap=1,f=1)[0].split('|')
    cmds.select( topParent[2])
    cmds.delete()

# Export the file with the saved data

def cleaner(*args):
    Warning()
    print ("cleaning animation time!!")
    importRef()
    doIt() # del namesspce 
    bakeKeys()
    deleteRig()
    print("Animation has been exported")

cleaner()