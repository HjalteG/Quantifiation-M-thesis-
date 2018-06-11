import os
import sys
from ij import IJ, ImagePlus
from ij.gui import GenericDialog
from ij.measure import ResultsTable as RT
from ij.plugin.frame import RoiManager

def getfilesDIRS():
	# Miscellaneous values
	filelist = []
	subdirectories = []
	ORGfiles = []
	SORTstring = ''
	counter = 0
	global channel1, channel2

	# Find all subdirectories and files
	for root, dirs, files in os.walk(directory, topdown=True):
		filelist.append(files)
		subdirectories.append(root)

	# Find all files with 'ORG' in file name, and pair them together according to channel input
	for folders in filelist:
		for image in folders:
			if 'ORG' in image:
				if '_'+channel1+'_' in image or '_'+channel2+'_' in image:
					if image[0:15] == SORTstring[0:15]:
						ORGfiles[counter].append(image)
						SORTstring = image
						counter = counter + 1
		
					else:						
						ORGfiles.append([])
						ORGfiles[counter].append(image)
						SORTstring = image

	# if directory is empty, ouput error
	if not ORGfiles:
		print 'Wrong directory'

	else:
		return ORGfiles, subdirectories[1:]

def getfilesNoDIRS():

	# Miscellaneous values
	filelist = []
	ORGfiles = []
	subdirectories = []
	SORTstring = ''
	counter = 0
	global channel1, channel2

	# Find all files in directory
	for root, dirs, files in os.walk(directory, topdown=True):
		filelist = files
		if len(dirs) > 0:
			sys.exit('Did you check the right box?')
			

	#Find all files with ORG in their name, and pair them together according to channel input 
	for image in filelist:
			if 'ORG' in image:
				if channel1 in image or channel2 in image:
					if image[0:15] == SORTstring[0:15]:
						ORGfiles[counter].append(image)
						SORTstring = image
						counter = counter + 1
		
					else:						
						ORGfiles.append([])
						ORGfiles[counter].append(image)
						SORTstring = image
						
						# Add given directory to list. Room for improvement
						subdirectories.append(directory)

	# if directory is empty, ouput error
	if not ORGfiles:
		print 'Wrong directory'

	else:
		return ORGfiles, subdirectories


def analyzeTUB():

	rm = RoiManager().getInstance()

	#Set imageJ preference meassurements to "area"
	IJ.run("Set Measurements...", "area display redirect=None decimal=3");

	#Variable used for iteration
	counter = 0

	#Clear previous resuslts
	IJ.run("Clear Results")

	# Make library, to be iterated through. Room for improvement
	lis_dic = [{'path':sub[i]} for i in range(len(sub))]
	if not lis_dic:
		sys.exit('Did you check the right box?')

	# Calculate area of channel #1 (Calculation requires that area is chosen as measured value)
	for i in lis_dic:
		print i
		for p in data[counter][::-1]:
			print p
			if '_'+channel1+'_' in p:
				imp1 = IJ.openImage(i['path']+'/'+p)
				IJ.setThreshold(imp1,lowth1,255)
				IJ.run(imp1,"Create Selection","")
				roi = rm.getRoi(imp1)
				#rm.runCommand(imp1, 'Add')	
				IJ.run(imp1,"Measure","")
				
			if '_'+channel2+'_' in p:
				imp2 = IJ.openImage(i['path']+'/'+p)
				IJ.setThreshold(imp2,lowth2,255)
				rm.runCommand(imp1, 'Select')	
				IJ.run(imp2, "Analyze Particles...", "size=0-4000 summarize")
				
			
		counter += 1
	#IJ.renameResults(channel1)

	# Reset counter
	counter = 0
	
	# Calculate area of channel #2
	#for i in lis_dic:
	#	for p in data[counter]:
	#		if '_'+channel2+'_' in p:
	#			imp2 = IJ.openImage(i['path']+'/'+p)
	#			IJ.setThreshold(imp2,lowth2,255)
	#			IJ.run(imp2, "Restore Selection","")
	#			IJ.run(imp2, "Analyze Particles...", "summarize");
	#	counter += 1
	#rt = RT.getResultsTable()
	#area = rt.getColumn(rt.getColumnIndex('Area'))
	#print area
	IJ.renameResults(channel2)


def analyzeDAPI():

	#Set imageJ preference meassurements to "area"
	IJ.run("Set Measurements...", "area display redirect=None decimal=3");

	#Variable used for iteration
	counter = 0

	#Clear previous resuslts
	IJ.run("Clear Results")

	# Make library, to be iterated through. Room for improvement
	lis_dic = [{'path':sub[i]} for i in range(len(sub))]
	if not lis_dic:
		sys.exit('Did you check the right box?')

	# Calculate area of channel #1 (Calculation requires that area is chosen as measured value)
	for i in lis_dic:
		for p in data[counter]:
			if '_'+channel1+'_' in p:
				imp1 = IJ.openImage(i['path']+'/'+p)
				IJ.setThreshold(imp1,lowth1,255)
				IJ.run(imp1, "Convert to Mask", "")
				IJ.run(imp1, "Watershed", "");
				IJ.run(imp1, "Analyze Particles...", "size=200-3000 pixel summarize");
				
		counter += 1
	IJ.renameResults(channel1)

	# Reset counter
	counter = 0
	
	# Calculate area of channel #2
	for i in lis_dic:
		for p in data[counter]:
			if '_'+channel2+'_' in p:
				imp2 = IJ.openImage(i['path']+'/'+p)
				IJ.setThreshold(imp2,lowth2,255)
				IJ.run(imp2,"Create Selection","")
				IJ.run(imp2,"Measure","")
		counter += 1
	IJ.renameResults(channel2)



# User input directory
directory = IJ.getDirectory("Input_directory")

# Make dialog box, with channel, threshold and "subdirectory" inputs
gd = GenericDialog("Insert values")
gd.addStringField("1. channel (DAPI/Tub)",'c1')
gd.addNumericField("1. channel lower threshold: ",0, 0)
gd.addStringField("2. channel",'c2')
gd.addNumericField("2. channel lower threshold: ",0, 0)
gd.addChoice("Quantify by:", ["Tubulin area", "DAPI #"],'')
gd.showDialog()
	
# Assign values from dialog
channel1, channel2 = gd.getNextString(), gd.getNextString()
lowth1, lowth2 = gd.getNextNumber(), gd.getNextNumber()

# Check if the chosen folder has subdirectories, or simply just a folder with pictures
for root, dirs, files in os.walk(directory, topdown=True):
	if dirs:
		data, sub = getfilesDIRS()
		break
	else:
		data, sub = getfilesNoDIRS()
		break

#If the chosen directory does not contain ORG files; outpus error
if len(data[0]) != 2:
	sys.exit("Channels should be written as ex 'c1'")

#Initialize quantification, according to previous choice
if gd.getNextChoice() == "Tubulin area":
	analyzeTUB()
else:
	analyzeDAPI()


#rt = RT.getResultsTable()
#print rt.getColumn(1)
