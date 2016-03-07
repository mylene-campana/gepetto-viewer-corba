import bpy
# Set the objects visible at Frame 'visibleFrame' and hide them at Frame 'hideFrame'
# Principally for roadmap display purpose ...

def setVisibilities (bpy, objectName, visibleFrame, hideFrame):
	if (bpy.data.objects.find(objectName) != -1):
		bpy.context.scene.objects.active = bpy.data.objects[objectName] # set active object
		bpy.context.scene.frame_set(visibleFrame)
		#bpy.ops.anim.change_frame(frame=visibleFrame) # need an animation to be set ?
		bpy.context.active_object.hide = False
		bpy.context.active_object.hide_render = False
		bpy.context.active_object.keyframe_insert(data_path="hide", index=-1, frame=visibleFrame)
		bpy.context.active_object.keyframe_insert(data_path="hide_render", index=-1, frame=visibleFrame)
		bpy.context.active_object.hide = True
		bpy.context.active_object.hide_render = True
		bpy.context.active_object.keyframe_insert(data_path="hide", index=-1, frame=hideFrame)
		bpy.context.active_object.keyframe_insert(data_path="hide_render", index=-1, frame=hideFrame)
	else:
		print ("Object not found: " + objectName)


def main ():
	visibleFrame = 0
	hideFrame = 248
	
	## EDGES:
	# TO FILL MANUALLY: first and last indexes of edges
	i_first = 0
	i_last = 1086 # (last + 1)
	i_test = 0
	for i in range(i_first,i_last):
		# avoid modifying animation on edges related to solution path
		if (i != 1083 and i != 1085 and i != 34 and i != 816 and i != 36 and i != 74 and i != 1058 and i != 1059 and i != 50 and i != 288 and i != 289):
			print ("set visibility of edge number " + str(i))
			objectName_i = 'edge'+str(i)
		setVisibilities (bpy, objectName_i, visibleFrame, hideFrame)
	
	## NODES/CONES:
	# TO FILL MANUALLY: first and last indexes of cones
	i_first = 0
	i_last = 338 # (last + 1)
	i_test = 0
	for i in range(i_first,i_last):
		# avoid modifying animation on cones related to waypoints
		if (i != 91 and i != 337 and i != 293 and i != 92 and i != 73 and i != 108 and i != 331 and i != 100 and i != 44 and i != 179):
			print ("set visibility of cone number " + str(i))
			objectName_i = 'Cone_'+str(i)
			setVisibilities (bpy, objectName_i, visibleFrame, hideFrame)


main  ()
