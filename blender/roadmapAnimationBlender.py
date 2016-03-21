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


#skpiList: avoid modifying animation on edges which are related to solution path
def setObjectNotInListVisibility (bpy, namePrefix, firstIndex, lastIndex, skipList, visibleFrame, hideFrame):
	for i in range(firstIndex,lastIndex+1):
		if (not (i in skpiList)):
			print ("set visibility on" + namePrefix + str(i))
			objectName_i = namePrefix+str(i)
			setVisibilities (bpy, objectName_i, visibleFrame, hideFrame)

def setObjectInListVisibility (bpy, namePrefix, firstIndex, lastIndex, theList, visibleFrame, hideFrame):
	for i in range(firstIndex,lastIndex+1):
		if (i in theList):
			print ("set visibility on" + namePrefix + str(i))
			objectName_i = namePrefix+str(i)
			setVisibilities (bpy, objectName_i, visibleFrame, hideFrame)

def main ():
	visibleFrame = 0
	hideFrame = 248
	
	edgeNamePrefix = 'edge'
	edgeSkipList = [1083, 1085, 34, 816, 36, 74, 1058, 1059, 50, 288, 289]
	setObjectNotInListVisibility (bpy, edgeNamePrefix, 0, 1086, edgeSkipList, visibleFrame, hideFrame) # RM
	setObjectInListVisibility (bpy, edgeNamePrefix, 0, 1086, edgeSkipList, 120, 0) # PATH
	
	coneNamePrefix = 'Cone_'
	coneSkipList = [91, 337, 293, 92, 73, 108, 331, 100, 44, 179]
	setObjectNotInListVisibility (bpy, coneNamePrefix, 0, 338, coneSkipList, visibleFrame, hideFrame) # RM
	setObjectInListVisibility (bpy, coneNamePrefix, 0, 338, coneSkipList, 120, 0) # PATH
	

main  ()
