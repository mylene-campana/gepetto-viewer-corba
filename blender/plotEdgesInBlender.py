import bpy
#from parser import parsePointVector # does NOT want to recognize the function -_-

def parsePointVector (filename, nbPointsPerEdge):
	lineNB = 0
	cList = []
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
				cList.append(points)
	return cList

def main ():
	w = 1 # weight
	#numPointsPerEdge = 4 # test
	numPointsPerEdge = 70 # real
	#filepath = '/local/mcampana/devel/hpp/src/gepetto-viewer-corba/blender/' # test
	filepath = '/local/mcampana/devel/hpp/src/animals_description/script/' # real
	#filename = filepath + 'edges_envir3d_easy.txt'
	filename = filepath + 'edges.txt'
	cList = parsePointVector (filename, numPointsPerEdge)
	numEdges = len(cList)
	# Get material
	if bpy.data.materials.get("edge") is not None:
		mat = bpy.data.materials["edge"]
	else:
		# create material
		mat = bpy.data.materials.new(name="edge")

	
	curvedatas = []
	objectdatas = []
	polylines = []
	for i in range(numEdges):
		curvedatas.append (bpy.data.curves.new(name='Curve', type='CURVE'))
		curvedatas [i].dimensions = '3D'
		curvedatas [i].extrude = 0.001 # otherwise, curve not rendered
		curvedatas [i].bevel_depth = 0.001
		
		objectdatas.append (bpy.data.objects.new('edge'+str(i), curvedatas [i]))
		objectdatas [i].location = (0,0,0) # object origin
		objectdatas [i].data.materials.append (mat) # object material
		bpy.context.scene.objects.link(objectdatas [i])
		
		polylines.append (curvedatas [i].splines.new('POLY'))
		polylines [i].points.add(numPointsPerEdge-1)
		edge = cList [i]
		for j in range(numPointsPerEdge):
			polylines[i].points[j].co = (edge [j][0], edge [j][1], edge [j][2], w)


main  ()
