import bpy

def parseConeConfig (filename):
    configs = []
    with open (filename) as f:
        lines=f.readlines()
        for line in lines:
            config = []
            st = line.strip ('\n').split (',') # remove end character and separate
            config = list(map (float, st)) # map not subscriptable in Python 3
            configs.append (config)
    return configs


def main ():
    # Get material
    if bpy.data.materials.get("cones_RM") is not None:
        mat = bpy.data.materials["cones_RM"]
    else:
        # create material
        mat = bpy.data.materials.new(name="cones_RM")
    
    fileName = '/local/mcampana/devel/hpp/src/animals_description/script/nodes.txt'
    configs = parseConeConfig (fileName)
    numCones = len(configs)
    
    #coneMeshFileName = "/local/mcampana/devel/hpp/src/animals_description/meshes/cone2.dae"
    #obj = bpy.ops.wm.collada_import (coneMeshFileName) # NOT WORKING :(
    coneName = 'Cone'
    #WARN: user has to manually import the cone as 'Cone'
    coneReference = bpy.data.objects[coneName]
    #coneReference.location = (0,0,0.132)
    coneMeshReference = bpy.data.meshes[coneName]
    """
    currentObjectName = coneName+'_rm_'+'test'
    currentObject = bpy.data.objects.new (currentObjectName, coneMeshReference)
    currentObject.data = coneReference.data.copy ()
    currentObject.scale = coneReference.scale
    currentObject.location[0] = 0
    currentObject.location[1] = 0
    currentObject.location[2] = 0
    currentObject.rotation_mode = 'QUATERNION'
    currentObject.rotation_quaternion[0] = 0
    currentObject.rotation_quaternion[1] = 1
    currentObject.rotation_quaternion[2] = 0
    currentObject.rotation_quaternion[3] = 0
    currentObject.data.materials [0] = (mat)
    bpy.context.scene.objects.link(currentObject)
    """
    for i in range(numCones):
        # create copy of coneReference
        currentObjectName = coneName+'_rm_'+str(i)
        currentObject = bpy.data.objects.new (currentObjectName, coneMeshReference)
        currentObject.data = coneReference.data.copy ()
        currentObject.scale = coneReference.scale
        
        # move currentObject according to roadmap
        config_i = configs [i]
        x = config_i [0]; y = config_i [1]; z = config_i [2]
        qw = -config_i [6]; qx = config_i [3]; qy = config_i [4]; qz = -config_i [5]
        #qw = config_i [3]; qx = config_i [4]; qy = config_i [5]; qz = config_i [6]
        M31 = 2*qw*qy + 2*qx*qz; M32 = 2*qy*qz - 2*qw*qx; M33 = qw**2 - qx**2 - qy**2 + qz**2
        z_shift = -0.132 # of reference
        currentObject.location[0] = x + M31*z_shift
        currentObject.location[1] = y + M32*z_shift
        currentObject.location[2] = z + M33*z_shift
        currentObject.rotation_mode = 'QUATERNION'
        currentObject.rotation_quaternion[0] = qz
        currentObject.rotation_quaternion[1] = -qw # correct unperfect cone rotation ??
        currentObject.rotation_quaternion[2] = qx
        currentObject.rotation_quaternion[3] = qy
        currentObject.data.materials [0] = (mat)
        bpy.context.scene.objects.link(currentObject)


main ()
