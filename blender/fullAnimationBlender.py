import bpy
from math import *
import yaml
"""
Contains all Blender actions to:
  - import initial and final cones, (and create associated spheres ?)
  - import roadmap and path cones-edges,
  - set their materials and visibilities along the animation,
  - import the robot and its path.
User has to fill the parameters (names of files mostly), for now files will have to be in the 
same directory where the script is.
"""

""" Update:
Not supported by Blender Python, or not convenient:
 - Texts (start, goal, roadmap...)
 - Camera poses
"""

def parseEdgeVector (filename, nbPointsPerEdge):
	lineNB = 0
	listOfEdges = []
	with open (filename) as f:
		lines=f.readlines()
		for line in lines:
			points = []
			lineNB = lineNB + 1
			if line [0] == 'e': # edge beginning
				for i in range(0, nbPointsPerEdge): # parse each point of the edge
					actualLine = lines[lineNB + i]
					st = actualLine.strip ('\n').split (',') # remove end character and separate
					point = list(map (float, st)) # map not subscriptable in Python 3
					points.append (point [0:3])
				listOfEdges.append(points)
	return listOfEdges

def parsePathPoints (filename):
	pathPoints = []
	with open (filename) as f:
		for line in f.readlines():
			st = line.strip ('\n').split (',')
			point = list(map (float, st))
			pathPoints.append (point [0:3])
	return pathPoints

def parseEdgeNodeIndexes (filename, lineNB):
	# lineNB = 0 for edge indexes, 1 for node indexes
	indexes = []
	with open (filename) as f:
		lines = f.readlines()
		line = lines [lineNB]
		st = line.strip ('\n').split (',')
		indexes = list(map (float, st))
	return indexes

def curveToMesh (selected_object):
	#http://gappyfacets.com/2016/03/03/blender-python-snippet-duplicate-object-curves-data-visualization/
	# Select and active only the curve per loop.
	bpy.ops.object.select_all(action='DESELECT')
	selected_object.select = True
	bpy.context.scene.objects.active = selected_object
	# Convert curve into mesh.
	bpy.ops.object.convert(target='MESH', keep_original=False)
	bpy.ops.object.select_all(action='DESELECT')

def plotEdges (listOfEdges, edgeNamePrefix, numPointsPerEdge, mat):
	w = 1 # weight for point plot
	curvedatas = []; objectdatas = []; polylines = []
	numEdges = len(listOfEdges)
	for i in range(numEdges):
		curvedatas.append (bpy.data.curves.new(name='Curve', type='CURVE'))
		curvedatas [i].dimensions = '3D'
		objectdatas.append (bpy.data.objects.new(edgeNamePrefix+str(i), curvedatas [i]))
		objectdatas [i].location = (0,0,0)
		objectdatas [i].data.materials.append (mat)
		bpy.context.scene.objects.link(objectdatas [i])
		polylines.append (curvedatas [i].splines.new('POLY'))
		polylines [i].points.add(numPointsPerEdge-1)
		edge = listOfEdges [i]
		for j in range(numPointsPerEdge):
			polylines[i].points[j].co = (edge [j][0], edge [j][1], edge [j][2], w)
		curveToMesh(objectdatas [i])

def plotPath (pathPoints, pathName, matPath):
	w = 1 # weight for point plot
	curvedatas = []; objectdatas = []; polylines = []
	curvedata =  bpy.data.curves.new(name='Curve', type='CURVE')
	curvedata.dimensions = '3D'
	#curvedata.extrude = 0.001; curvedata.bevel_depth = 0.001
	objectdata = bpy.data.objects.new(pathName, curvedata)
	objectdata.location = (0,0,0)
	objectdata.data.materials.append (matPath)
	bpy.context.scene.objects.link(objectdata)
	polyline = curvedata.splines.new('POLY')
	polyline.points.add(len(pathPoints)-1)
	for i in range(len(pathPoints)):
		polyline.points[i].co = (pathPoints [i][0], pathPoints [i][1], pathPoints [i][2], w)
	curveToMesh(objectdata)

def plotGlobalFrameLine (frameName, location, locOffset, mat):
	w = 1 # weight for point plot
	curvedatas = []; objectdatas = []; polylines = []
	curvedata =  bpy.data.curves.new(name='Curve', type='CURVE')
	curvedata.dimensions = '3D'
	objectdata = bpy.data.objects.new(frameName, curvedata)
	objectdata.location = location
	objectdata.data.materials.append (mat)
	bpy.context.scene.objects.link(objectdata)
	polyline = curvedata.splines.new('POLY')
	polyline.points.add(2)
	#polyline.points[0].co = (location[0], location[1], location[2], w)
	polyline.points[0].co = (locOffset[0], locOffset[1], locOffset[2], w)
	curveToMesh(objectdata)

def plotGlobalFrame (frameName, location):
	locOffsetVal = 0.4
	matExFrame = getOrCreateMaterial ("exFrame", 'WIRE', [1,0,0], 1, True, False, False)
	matEyFrame = getOrCreateMaterial ("eyFrame", 'WIRE', [0,1,0], 1, True, False, False)
	matEzFrame = getOrCreateMaterial ("ezFrame", 'WIRE', [0,0,1], 1, True, False, False)
	plotGlobalFrameLine (frameName+'_ex', location, [locOffsetVal,0,0], matExFrame)
	plotGlobalFrameLine (frameName+'_ey', location, [0,locOffsetVal,0], matEyFrame)
	plotGlobalFrameLine (frameName+'_ez', location, [0,0,locOffsetVal], matEzFrame)

def getOrCreateMaterial (materialName, matType, RGBcolor, alphaTransp, shadeless, traceable, receiveShadows):
	if bpy.data.materials.get(materialName) is not None:
		mat = bpy.data.materials[materialName]
	else:
		mat = bpy.data.materials.new(name=materialName)
	# Set properties
	if (alphaTransp == 1):
		mat.use_transparency = False
	else:
		mat.use_transparency = True
		mat.alpha = alphaTransp
	mat.type = matType # 'SURFACE' or 'WIRE'
	mat.diffuse_color[0:3] = RGBcolor # [0.5,0.5,0.5] or [0,0,1]
	mat.use_shadeless = shadeless # True or False
	mat.use_raytrace = traceable # True or False
	mat.use_shadows = receiveShadows # True or False
	return mat

def tagObjects (bpy):
  taggedObjects = list ()
  for obj in bpy.data.objects:
    taggedObjects.append (obj.name)
  return taggedObjects

def getNonTaggedObjects (taggedObjects):
  return [obj for obj in bpy.data.objects if obj.name not in taggedObjects]

def setParent (children, parent):
  for child in children:
    child.parent = parent

def importDaeRobot (daeFileName, robotName, material): # from jmirabel@laas.fr
	taggedObjects = tagObjects(bpy)
	bpy.ops.wm.collada_import (filepath=daeFileName)
	imported_objects = getNonTaggedObjects (taggedObjects)
	#print(imported_objects)
	bpy.ops.object.empty_add ()
	currentObj = bpy.context.object
	setParent (imported_objects, currentObj)
	currentObj.name = robotName
	currentObj.location = [0.0, 0.0, 0.0]
	currentObj.rotation_euler = [0.0, 0.0, 0.0]
	bpy.data.objects["Sphere"].data.materials [0] = material # "Sphere" hardcoded

def importDaeObjects (daeFileName, objNamePrefix, material):
	taggedObjects = tagObjects(bpy)
	bpy.ops.wm.collada_import (filepath=daeFileName)
	imported_objects = getNonTaggedObjects (taggedObjects)
	#print(imported_objects)
	for impObj in imported_objects:
		if (impObj.name[0:4] == objNamePrefix):
			impObj.data.materials [0] = material

def createSphereMesh (sphereName, spherePose, sphereMat, numSegments, numRings, sphereSize):
	bpy.ops.mesh.primitive_uv_sphere_add(location=spherePose, segments=numSegments, ring_count=numRings, size = sphereSize)
	bpy.context.object.name = sphereName
	bpy.context.object.data.materials.append(sphereMat)

def loadmotion (filename, startFrame): # from stonneau@laas.fr
	with open (filename) as file:
		data = yaml.load (file)
		for frameId in range (len(data.keys())):
			frameKey = "frame_" + str (frameId)
			objPositions = data[frameKey]
			for objName, pos in objPositions.items ():
				currentObj = bpy.context.scene.objects.get(objName)
				if currentObj:
					currentObj.rotation_mode = 'QUATERNION'
					posF = [float(x) for x in pos]
					currentObj.location = posF[0:3]
					currentObj.rotation_quaternion = posF[3:7]
					currentObj.keyframe_insert (data_path="location", frame=frameId+startFrame)
					currentObj.keyframe_insert (data_path="rotation_quaternion", frame=frameId+startFrame)
				else:
					#print("Unknown object " + objName)
					frameKey
	return len(data.keys())+startFrame

def setVisibility (objectName, frame, state):
	if (bpy.data.objects.find(objectName) != -1):
		bpy.context.scene.objects.active = bpy.data.objects[objectName] # set active object
		bpy.context.scene.frame_set(frame)
		bpy.context.active_object.hide = state
		bpy.context.active_object.hide_render = state
		bpy.context.active_object.keyframe_insert(data_path="hide", index=-1, frame=frame)
		bpy.context.active_object.keyframe_insert(data_path="hide_render", index=-1, frame=frame)
	else:
		print ("Object not found: " + objectName)

def setObjectNotInListVisibility (namePrefix, numberOfObjects, skipList, frame, state):
	for i in range(0, numberOfObjects):
		if (not (i in skipList)):
			#print ("set visibility on " + namePrefix + str(i))
			objectName_i = namePrefix+str(i)
			setVisibility (objectName_i, frame, state)

def setObjectInListVisibility (namePrefix, numberOfObjects, theList, frame, state):
	for i in range(0, numberOfObjects):
		if (i in theList):
			#print ("set visibility on " + namePrefix + str(i))
			objectName_i = namePrefix+str(i)
			setVisibility (objectName_i, frame, state)

def setObjectPose (objectName, pose, poseFrame):
	if (bpy.data.objects.find(objectName) != -1):
		bpy.context.scene.objects.active = bpy.data.objects[objectName] # set active object
		bpy.context.scene.frame_set(poseFrame)
		bpy.context.active_object.location = pose[0:3]
		bpy.context.active_object.rotation_euler = [x*pi/180.0 for x in pose[3:6]]
		#print ("pose: " + str(pose))
		bpy.context.active_object.keyframe_insert(data_path="location", index=-1, frame=poseFrame)
		bpy.context.active_object.keyframe_insert(data_path="rotation_euler", index=-1, frame=poseFrame)
	else:
		print ("Object not found: " + objectName)

#---------------------------------------------------------------------------#

def main ():
	# Parameters that do not change from one problem to another
	daeRobotFilePath = '/local/mcampana/devel/hpp/src/animals_description/meshes/'
	daeRobotFileName = daeRobotFilePath + 'sphere_1.dae'
	daeFilePath = '/local/mcampana/devel/hpp/videos/'
	daeRMConeFileName = daeFilePath + 'cones_RM.dae'
	daeStartConeFileName = daeFilePath + 'cone_start.dae'
	daeGoalConeFileName = daeFilePath + 'cone_goal.dae'
	daePathConeFileName = daeFilePath + 'cones_path.dae'
	yamlFileName = daeFilePath + 'frames.yaml'
	scriptFilePath = '/local/mcampana/devel/hpp/src/animals_description/script/'
	edgeRMFilename = scriptFilePath + 'edges.txt'
	pathFileName = scriptFilePath + 'path.txt'
	indexesFileName = scriptFilePath + 'indexes.txt'
	edgeNamePrefix = 'edge'; coneNamePrefix = 'Cone_'; coneWpNamePrefix = 'Cone_WP_'; pathName = 'path'
	robotName = 'robot/base_link'; startSphereName = 'startSphere'; goalSphereName = 'goalSphere'
	numPointsPerEdge = 70
	initFrame = 0
	
	# Parameters that CAN change from one problem to another
	""" envir3d_hard_IROS
	pathVisibFrame = 120; rmDisappearFrame = 248; beginMotionFrame = 252
	numberOfEdges = 1086; numberOfCones = 337 # should not be needed
	edgeSkipList = [1083, 1085, 34, 816, 36, 74, 1058, 1059, 50, 288, 289]
	coneSkipList = [91, 337, 293, 92, 73, 108, 331, 100, 44, 179]
	cameraInitPose = [7.33,8.92,6.86,56.4,-2.16,162.9]
	cameraFollowPose = [-2.80,0.782,0.683,82.7,0,254]
	"""
	pathVisibFrame = 120; rmDisappearFrame = 260; beginMotionFrame = 270
	numberOfCones = 21
	edgeSkipList = parseEdgeNodeIndexes (indexesFileName, 0)
	coneSkipList = parseEdgeNodeIndexes (indexesFileName, 1)
	#print ("edgeSkipList= " + str(parseEdgeNodeIndexes (indexesFileName, 0)))
	#print ("coneSkipList= " + str(parseEdgeNodeIndexes (indexesFileName, 1)))
	cameraInitPose = [7.33,8.92,6.86,56.4,-2.16,162.9]
	cameraFollowPose = [-2.80,0.782,0.683,82.7,0,254]

	# Materials
	matSphereRobot = getOrCreateMaterial ("sphereRobot", 'SURFACE', [0.8,0,0.03], 1, False, False, False)
	matSphereSG = getOrCreateMaterial ("sphereSG", 'SURFACE', [0,0.3,0], 1, False, False, False)
	matConeSG = getOrCreateMaterial ("coneSG", 'SURFACE', [0,0.3,0], 0.4, True, False, False)
	matEdgeRM = getOrCreateMaterial ("edgeRM", 'WIRE', [0.5,0.5,0.5], 1, True, False, False)
	matConeRM = getOrCreateMaterial ("coneRM", 'SURFACE', [0.5,0.5,0.5], 0.4, True, False, False)
	matPath = getOrCreateMaterial ("path", 'WIRE', [0,0,1], 1, True, False, False)
	matConePath = getOrCreateMaterial ("cone_path", 'SURFACE', [0,0,1], 0.4, True, False, False)
	matText = getOrCreateMaterial ("text", 'SURFACE', [0,0,0], 1, True, False, False)
	matTextPath = getOrCreateMaterial ("path_text", 'SURFACE', [0,0,0.4], 1, True, False, False)
	
	# Set World
	world = bpy.data.worlds["World"]
	world.horizon_color[0:3] = [0.3,0.3,0.4] # I find it a lil'bit dark...
	
	# Import meshes
	importDaeRobot (daeRobotFileName, robotName, matSphereRobot)
	importDaeObjects (daeStartConeFileName, 'Cone', matConeSG)
	importDaeObjects ( daeGoalConeFileName, 'Cone', matConeSG)
	importDaeObjects (daePathConeFileName, 'Cone', matConePath)
	importDaeObjects (daeRMConeFileName, 'Cone', matConeRM)

	# Plot edges
	listOfEdges = parseEdgeVector (edgeRMFilename, numPointsPerEdge)
	numberOfEdges = len(listOfEdges);
	print ("Number of edges: " + str(numberOfEdges))
	plotEdges (listOfEdges, edgeNamePrefix, numPointsPerEdge, matEdgeRM)
	
	# Import solution path
	pathPoints = parsePathPoints (pathFileName)
	plotPath ( pathPoints, pathName, matPath)
	startPos = pathPoints [0]
	goalPos = pathPoints [len(pathPoints)-1]
	createSphereMesh (startSphereName, startPos, matSphereSG, 24, 12, 0.02)
	createSphereMesh (goalSphereName, goalPos, matSphereSG, 24, 12, 0.02)
	
	# Import motion
	endMotionFrame = loadmotion (yamlFileName, beginMotionFrame)
	bpy.data.scenes["Scene"].frame_end = endMotionFrame + 50
	
	# Visibilities
	# Roadmap
	setObjectNotInListVisibility ( edgeNamePrefix, numberOfEdges, [], initFrame, False)
	setObjectNotInListVisibility (edgeNamePrefix, numberOfEdges, edgeSkipList, rmDisappearFrame,True)
	setObjectNotInListVisibility (coneNamePrefix, numberOfCones, [], initFrame, False)
	setObjectNotInListVisibility (coneNamePrefix, numberOfCones, coneSkipList, rmDisappearFrame, True)
	setObjectInListVisibility ( edgeNamePrefix, numberOfEdges, edgeSkipList, pathVisibFrame, True)
	setObjectInListVisibility (coneNamePrefix, numberOfCones, coneSkipList, pathVisibFrame, True)
	setVisibility ('Cone', initFrame, False) # 'cause first RM cone name is not following the prefix
	setVisibility ('Cone', rmDisappearFrame, True)
	# Path
	setObjectNotInListVisibility (coneWpNamePrefix, numberOfCones, [], initFrame, True)
	setObjectNotInListVisibility (coneWpNamePrefix, numberOfCones, [], pathVisibFrame, False)
	setVisibility ('Cone_WP', initFrame, True) # 'cause first WP cone name is not following the prefix
	setVisibility ('Cone_WP', pathVisibFrame, False)
	setVisibility (pathName, initFrame, True)
	setVisibility (pathName, pathVisibFrame, False)
	
	# Set some camera poses
	cameraObj = bpy.data.objects["Camera"]
	#bpy.ops.object.select_camera(); bpy.ops.object.constraint_add(type='COPY_LOCATION') # not necessary
	cameraObj.constraints.new(type='COPY_LOCATION')
	cameraConstrLocRobot = cameraObj.constraints["Copy Location"]
	cameraConstrLocRobot.target = bpy.data.objects[robotName]
	cameraConstrLocRobot.use_offset = True
	setObjectPose ("Camera", cameraInitPose, initFrame)
	setObjectPose ("Camera", cameraFollowPose, beginMotionFrame-10)
	print ("edgeSkipList test= " + str(parseEdgeNodeIndexes (indexesFileName, 0)))
	print ("coneSkipList test= " + str(parseEdgeNodeIndexes (indexesFileName, 1)))
	
	plotGlobalFrame ('GlobalFrame', [0,0,3])

main  ()

