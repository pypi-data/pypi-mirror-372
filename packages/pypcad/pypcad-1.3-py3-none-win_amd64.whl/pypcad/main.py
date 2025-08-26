import time
import pythoncom
import win32com.client
import math

#----------------------------------------
def variants(object):
    """
    Converts object in python into required variant.
    ------------------------------------------------
    :param object: Any
    ------------------------------------------------
    :returns : variant
	"""
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, (object))

def Apoint(x,y,z=0):
	"""
	Converts x,y,z into required float array as the arguments of coordinates of a point.
	------------------------------------------------------------------------------------
	:param x: int or float
	:param y: int or float
	:param z: int or float
	------------------------------------------------------------------------------------
	:returns : variant array of coordinates of a point
	"""
	return win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,(x,y,z))  # | means the type combination

def aDouble(*argv):
    """
	Converts *argv into required float variant.
	-------------------------------------------
	:param *argv: tuple
	-------------------------------------------
	:returns : float variant
	"""
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (argv))
#----------------------------------------

def ArrayTransform(x):
	"""
 	Converts x into required float variant.
	-----------------------------------------------------------------------
	:param x: any kind of array in python,such as ((1,2,3),(1,2,3),(1,2,3))
	-----------------------------------------------------------------------
	:returns : float variant
	"""
	return win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,x) 

def VtVertex(*args):
	"""
	Converts *args into the required float variant.
 	--------------------------------------------------------
	:param *args: 2D coordinates of a serial points in tuple
	--------------------------------------------------------
	:returns : float variant
 
	"""
	return win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,args)

def VtObject(*obj):
	"""
	Converts *obj in python into required object array.
 	---------------------------------------------------
	:param *obj: tuple
	---------------------------------------------------
	:returns : object variant
	"""
	return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, obj)

def VtFloat(list):
    """
    Converts list in python into required float.
    --------------------------------------------
	:param list: list
	--------------------------------------------
	:returns : float variant
    """
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list)

def VtInt(list):
    """
    Converts list in python into required int.
    ------------------------------------------
    :param list: list
	------------------------------------------
	:returns : int variant
    """
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, list)

def VtVariant(list):
    """
    Converts list in python into required variant.
    ----------------------------------------------
    :param list: list
	----------------------------------------------
	:returns : variant
    """
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list)

def AngleDtoR(degree):
	"""
	Convert degree to radian.
 	---------------------------
    :param degree: int or float
	---------------------------
	:returns : int or float
	"""
	radian=degree*math.pi/180
	return radian

def AngleRtoD(radian):
	"""
	Convert radian to degree.
 	---------------------------
    :param degree: int or float
	---------------------------
	:returns : int or float
	"""
	degree=180*radian/math.pi 
	return degree

def FilterType(ftype):
	"""
	Converts ftype to filter type value refer to DXF reference to learn about DXF group code.
	-----------------------------------------------------------------------------------------
 	:param ftype: DXF group code
	-----------------------------------------------------------------------------------------
	:returns : variant
	"""
	return win32com.client.VARIANT(pythoncom.VT_I2|pythoncom.VT_ARRAY,ftype)

def FilterData(fdata):
	"""
	Converts fdata to filter data value refer to DXF reference to learn about DXF group code.
	-----------------------------------------------------------------------------------------
 	:param ftype: DXF group code
	-----------------------------------------------------------------------------------------
	:returns : variant
	"""
	return win32com.client.VARIANT(pythoncom.VT_VARIANT|pythoncom.VT_ARRAY,fdata)

class PycomError(Exception):
	"""
	To raise exception.
	------------------------------------
	:param Exception: Exception to raise
	------------------------------------
	:returns : Exception
	"""
	def __init__(self,info):
		print(info)
  
class PyPCAD():
	"""
	To creates application object.
	------------------------------
	:param 
	------------------------------
	:returns : Application
	"""
	def __init__(self):
		try:
			self.pypcad=win32com.client.Dispatch("PCAD_AC_X.AcadApplication")
			time.sleep(5)
			self.pypcad.Visible=True 
		except Exception as e:
			raise PycomError(f"Failed to initialize PCAD_AC_X.AcadApplication: {e}")
		
	
	"""
	Application
	"""
	@property 
	def Space(self):
		"""
		Automatically deciding the active layout is ModelSpace or PaperSpace.
		---------------------------------------------------------------------
		:param 
		---------------------------------------------------------------------
		:returns : ModelSpace or PaperSpace
		"""
		if self.pypcad.ActiveDocument.ActiveLayout.ModelType:
			return self.pypcad.ActiveDocument.ModelSpace
		else:
			return self.pypcad.ActiveDocument.PaperSpace

	@property
	def IsEarlyBind(self):
		if 'activeDoc' in str(type(self.pypcad)):
			return True
		else:
			return False

	def TurnOnEarlyBind(self):
		import os,sys
		makepyPath=r'Lib\site-packages\win32com\client\makepy.py'
		ExePath=os.path.split(sys.executable)[0]
		MakePyPath=os.path.join(ExePath,makepyPath)
		os.execl(sys.executable,'python',MakePyPath)
  
	@property
	def AppPath(self):
		"""
		Returns PyPCAD Application path.
		--------------------------------
		:param
		--------------------------------
		:returns : String
		"""
		return self.pypcad.Path

	def SendCommand(self,command):
		"""
		Sends a command string from script
		for example, to draw a circle whose center is 0,0,0, and radius is 100
		>>>pypcad.SendCommand('circle 0,0,0 100 ') 
		#Please notice that there is a blank following 100, meaning the end of input.
		-----------------------------------------------------------------------------
		:param command: String
		-----------------------------------------------------------------------------
		:returns : 
  		"""
		self.pypcad.ActiveDocument.SendCommand(command)
	
	"""
	Registered Applications
	"""
	@property 
	def RApps(self):
		"""
		Returns registered applications collections.
		--------------------------------------------
		:param
		--------------------------------------------
		:returns : RegisteredApplications
		"""
		return self.pypcad.ActiveDocument.RegisteredApplications
	
	@property 
	def RAppNames(self):
		"""
		Returns registerd application names list.
		-----------------------------------------
		:param
		-----------------------------------------
		:returns : list of strings
		"""
		names=[]
		for item in range(self.rApps.Count):
			names.append(self.rApps.Item(item).Name)
		return names

	def SetXData(self,entity,xdataPairs):
		"""
		Sets XData for entity
		>>>circle=pypcad.AddCircle(Apoint(0,0),20)
		>>>pypcad.SetXdata(circle,[(1001,'test'),(1000,'this is an example')]).
		----------------------------------------------------------------------------
		:param entity: entity
		:param xdataPairs: list containing tuple which represent xdataType and xdata
		----------------------------------------------------------------------------
		:returns : 
		"""
		xdataType=[]
		xdataValue=[]
		for i,j in xdataPairs:
			xdataType.append(i)
			xdataValue.append(j)
		entity.SetXData(FilterType(xdataType),FilterData(xdataValue))
		
	"""
	Layouts
	"""
	@property 
	def LayoutNames(self):
		"""
		Gets Layouts name.
		------------------
		:param 
		------------------
		:returns : Layouts
		"""
		layoutnames={}
		for i in range(self.pypcad.ActiveDocument.Layouts.Count):
			layoutnames[self.pypcad.ActiveDocument.Layouts.Item(i).Name]=i
		return layoutnames

	def EnterLayout(self,name_or_index):
		"""
		Enters layout, so the active layout may become model,or one paperspace
		For example:
		>>>pypcad.EnterLayout('model') #Enter the modelSpace
		>>>pypcad.EnterLayout('onePaperSpace') #Enter the paperSpace named onePaperSpace
		>>>pypcad.EnterLayout('notExist') # Will raise an error
		>>>pypcad.EnterLayout(0) # Enter the modelSpace.
		--------------------------------------------------------------------------------
		:param name_or_index: string or int
		--------------------------------------------------------------------------------
		:returns : 
		"""
		if isinstance(name_or_index,int):
			self.pypcad.ActiveDocument.ActiveLayout=self.pypcad.ActiveDocument.Layouts.Item(name_or_index)
		if isinstance(name_or_index,str):
			if name_or_index in ['Model','模型']:
				self.pypcad.ActiveDocument.ActiveSpace=win32com.client.constants.acModelSpace
				return None 
			index=self.LayoutNames.get(name_or_index,-1)
			self.pypcad.ActiveDocument.ActiveLayout=self.pypcad.ActiveDocument.Layouts.Item(index)
			return None 

	"""
	System variable
	"""
	def SetVariable(self,name,value):
		"""
		Sets system variable.
		---------------------
		:param name: string
		:param value: object
		---------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.SetVariable(name,value)
  
	def GetVariable(self,name):
		"""
		Gets system variable.
		---------------------
		:param name: string
		---------------------
		:returns : dynamic
		"""
		return self.pypcad.ActiveDocument.GetVariable(name)

	"""
	File processing
	"""

	def OpenFile(self,path):
		"""
		Opens a dwg file in the path.
		-----------------------------
		:param path: string
		-----------------------------
		:returns : Document
		"""
		self.pypcad.Documents.Open(path)
  
	def CreateNewFile(self):
		"""
		Creates a new dwg file,by default name.
		---------------------------------------
		:param 
		---------------------------------------
		:returns : Document
		"""
		self.pypcad.Documents.Add()
  
	def SaveFile(self):
		"""
		Saves file.
		-----------
		:param 
		-----------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Save()
  
	def SaveAsFile(self,path):
		"""
		Saves as file.
		-------------------
		:param path: String
		-------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.SaveAs(path)
  
	def Close(self):
		"""
		Close current file.
		-------------------
		:param 
		-------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Close()
	
	def PurgeAll(self):
		"""
		Removes unused named references such as unused blocks or layers from the document.
		This method is the equivalent of entering purge at the Command prompt, selecting the 
		All option, and then choosing Yes to the "Purge Everything?" prompt.
		------------------------------------------------------------------------------------
		:param 
		------------------------------------------------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.PurgeAll()

	def Regen(self,enum):
		"""
		Regenerates the entire drawing and recomputes the screen coordinates and view resolution for all objects.
		---------------------------------------------------------------------------------------------------------
		:param enum: 0:Regenerates only the active viewport
					 1:Regenerates all viewports on the document
		---------------------------------------------------------------------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Regen(enum)

	@property
	def OpenedFilenames(self):
		"""
		Returns opened file names.
		--------------------------
		:param 
		--------------------------
		:returns : list
		"""
		names=[]
		for i in range(self.OpenedFilenumbers):
			names.append(self.pypcad.Documents.Item(i).Name)
		return names

	@property
	def OpenedFilenumbers(self):
		"""
		Returns opened files count.
		---------------------------
		:param 
		---------------------------
		:returns : int
		"""
		return self.pypcad.Documents.Count

	def GetOpenedFile(self,file):
		"""
		Returns already opened file whose index is index or name is name as the Current file.
		-------------------------------------------------------------------------------------
		:param file: int or string
		-------------------------------------------------------------------------------------
		:returns : Document
		"""
		if isinstance(file,str):
			index = self.OpenedFilenames.index(file)
		elif isinstance(file,int):
			index=file
		else:
			raise PycomError('Type of file in GetOpenedFile is wrong ')
		return self.pypcad.Documents.Item(index)

	def ActivateFile(self,file):
		"""
		Activates already opened file whose index is index or name is name as the Current file.
		---------------------------------------------------------------------------------------
		:param file: int or string
		---------------------------------------------------------------------------------------
		:returns : 
		"""
		if isinstance(file,str):
			index = self.OpenedFilenames.index(file)
		elif isinstance(file,int):
			index=file
		else:
			raise PycomError('Type of file in ActivateFile() is wrong')
		self.pypcad.Documents.Item(index).Activate()

	def DeepClone(self,objects,Owner=None,IDPairs=win32com.client.VARIANT(pythoncom.VT_VARIANT, ())):
		"""
		Deep clone objects from current file to specified file's ModelSpace
		For example:
		>>>from pycomcad import *
		>>>pypcad=PyPCAD()
		>>>te1=pypcad.AddCircle(Apoint(0,0,0),200)
		>>>te2=pypcad.AddCircle(Apoint(100,100,0),200)
		>>>pypcad.CreateNewFile()
		>>>pypcad.ActivateFile(0)
		>>>result=pypcad.DeepClone((te1,),1) 
		# Deep Clone one object,notice the naunce between (te1,)and (te1),the latter one is int
		>>>result[0][0].Move(Apoint(0,0,0),Apoint(100,100,0))
		>>>pypcad.CurrentFilename
		>>>slt=pypcad.GetSelectionSets('slt1')
		>>>slt.SelectOnScreen()
		>>>result1=pypcad.DeepClone(slt,'Drawing2.dwg').
		---------------------------------------------------------------------------------------
		:param objects: SelectionSet(selection sets) or tuple of entity object
		:param Owner: string or index of file
		:param IDPairs: variant.Default value has been set
		---------------------------------------------------------------------------------------
		:returns : tuple of deep cloned object
		"""
		if isinstance(objects,tuple):
			if not objects:
				raise PycomError('Objects in DeepClone() is empty tuple ')
			else:
				obj=VtObject(*objects)
		elif 'IpypcadSelectionSet' in str(type(objects)):
			if objects.Count==0:
				raise PycomError('SelectionSets in DeepClone() is empty')
			else:
				obj=[]
				for i in range(objects.Count):
					obj.append(objects.Item(i))
				obj=VtObject(*obj)
		else:
			raise PycomError('Type of objects in DeepClone() is wrong')
		if not Owner:
			return self.pypcad.ActiveDocument.CopyObjects(obj)
		else:
			try:
				newOwnerDoc=self.GetOpenedFile(Owner)   
				if newOwnerDoc.ActiveLayout.ModelType:  # make deepclone method can be applied to paperspace or modelspace automatically
					newOwner=newOwnerDoc.ModelSpace
				else:
					newOwner=newOwnerDoc.PaperSpace
			except:
				raise PycomError('File %s is not opened'% Owner)
			return self.pypcad.ActiveDocument.CopyObjects(obj,newOwner,IDPairs)

	@property
	def CurrentFilename(self):
		"""
		Returns the name of current file name.
		--------------------------------------
		:param 
		--------------------------------------
		:returns : String
		"""
		return self.pypcad.ActiveDocument.Name

	@property
	def FilePath(self):
		"""
		Returns current file path.
		--------------------------
		:param 
		--------------------------
		:returns : String
		"""
		return self.pypcad.ActiveDocument.Path

	@property
	def IsSaved(self):
		"""
		Specifies if the document has any unsaved changes.
		--------------------------------------------------
		:param 
		--------------------------------------------------
		:returns : True or False
		"""
		return self.pypcad.ActiveDocument.Saved

	"""
	Zoom
	"""

	def ZoomExtents(self):
		"""
		Zooms to extents of entities.
		-----------------------------
		:param 
		-----------------------------
		:returns : 
		"""
		self.pypcad.ZoomExtents()
	def ZoomAll(self):
		"""
		Zooms all entities.
		-------------------
		:param 
		-------------------
		:returns : 
		"""
		self.pypcad.ZoomAll()

	"""
	precise-drawing setting
	"""

	def GridOn(self,boolean):
		"""
		Sets grid value.
		-----------------------------
		:param boolean: True or False
		-----------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.ActiveViewport.GridOn=boolean
		self.pypcad.ActiveDocument.ActiveViewport=self.pypcad.ActiveDocument.ActiveViewport
  
	def SnapOn(self,boolean):
		"""
		Sets snap value.
		-----------------------------
		:param boolean: True or False
		-----------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.ActiveViewport.SnapOn=boolean
		self.pypcad.ActiveDocument.ActiveViewport=self.pypcad.ActiveDocument.ActiveViewport

	"""
	CAD entity Object drawing
	"""

	def AddPoint(self,apoint):
		"""
		Adds point in ActiveSpace.
		--------------------------
		:param apoint: APoint
		--------------------------
		:returns : Point
		"""
		point=self.Space.AddPoint(apoint)
		return point 

	def AddLine(self,startPoint,endPoint):
		"""
		Adds Line in ActiveSpace.
		-------------------------
		:param startPoint: APoint
		:param endPoint: APoint
		-------------------------
		:returns : Line
		"""
		line=self.Space.AddLine(startPoint,endPoint)
		return line 

	def AddLwpline(self,*vertexCoord):
		"""
		Adds lightweight polyline in ActiveSpace, this method is recommended to draw line.
		----------------------------------------------------------------------------------
		:param *vertexCoord: tuple of vertices
		----------------------------------------------------------------------------------
		:returns : LWPolyline
		"""
		lwpline=self.Space.AddLightWeightPolyline(VtVertex(*vertexCoord))
		return lwpline

	def AddCircle(self,centerPnt,radius):
		"""
		Adds circle in ActiveSpace.
		---------------------------
		:param centerPnt: APoint
		:param radius: int or float
		---------------------------
		:returns : Line
		"""
		circle=self.Space.AddCircle(centerPnt,radius)
		return circle

	def AddArc(self,centerPnt,radius,startAngle,endAngle):
		"""
		Adds arc in ActiveSpace.
		-------------------------------
		:param centerPnt: APoint
		:param radius: int or float
		:param startAngle: int or float
		:param endAngle: int or float
		-------------------------------
		:returns : Arc
		"""
		arc=self.Space.AddArc(centerPnt,radius,AngleDtoR(startAngle),AngleDtoR(endAngle))
		return arc 
	
	def AddTable(self,InsertionPoint,NumRows,NumColumns,RowHeight,ColWidth):
		"""
		Adds table in ActiveSpace.
		-------------------------------
		:param InsertionPoint: Apoint
		:param NumRows: int
		:param NumColumns: int
		:param RowHeight : int or float
		:param ColWidth : int or float
		-------------------------------
		:returns : Table
		"""
		return self.Space.AddTable(InsertionPoint,NumRows,NumColumns,RowHeight,ColWidth)

	def AddSpline(self,*fitPoints,startTan=None,endTan=None):
		"""
		Adds Spline in ActiveSpace.
		---------------------------
		:param fitPoints: tuple
		:param startTan: APoint
		:param endTan: APoint
		---------------------------
		:returns : Spline
		"""
		spline=self.Space.addSpline(VtVertex(*fitPoints),startTan,endTan)
		return spline

	def AddEllipse(self,centerPnt,majorAxis,radiusRatio):
		"""
		Adds Ellipse in ActiveSpace.
		---------------------------------
		:param centerPnt: APoint
		:param majorAxis: APoint
		:param radiusRatio: int or float
		---------------------------------
		:returns : Ellipse
		"""
		ellipse=self.Space.addEllipse(centerPnt,majorAxis,radiusRatio)
		return ellipse

	def AddHatch(self,patternType,patterName,associative,outLoopTuple,innerLoopTuple=None):
		"""
		Adds Hatch in ActiveSpace.
		The note of arguments can be seen as below:
		(1)patternType is the built-in integer constants which can be got by win32com.client.constants.X,here x can be 
		acHatchPatternTypeDefined(it means that using standard application's pattern drawing file to hatch, and the integer is 1),
		acHatchPatternTypeUserDefined(it means that using the current linetype to hatch,and the integer is 0),
		acHatchPatternTypeCustomDefined(it means that using user-defined drawing file to hatch,and the integer is 2)
		(2)patterName is a string specifying the hatch pattern name, such as "SOLID","ANSI31"
		(3)associative is boolean. If it is True, when the border is modified, the hatch pattern will adjust automatically 
		to keep in the modified border.
		(4)outLoop is a sequence of object,such as line,circle,etc. For example, outLoopTuple=(circle1,),or outLoopTuple=(line1,line2,
		line3).
		(5)innerLoop is the same with outLoop

		------------------------------------------------------------------------------------------------------------------------------
		:param patternType: int
		:param patterName: string
		:param associative: True or False
		:param outLoopTuple: tuple
		:param innerLoopTuple: tuple
		------------------------------------------------------------------------------------------------------------------------------
		:returns : Hatch
		"""
		hatch=self.Space.AddHatch(patternType,patterName,associative)
		out=VtObject(*outLoopTuple)
		hatch.AppendOuterLoop(out)
		if innerLoopTuple:
			inn=VtObject(*innerLoopTuple)
			hatch.AppendInnerLoop(inn)
		hatch.Evaluate()
		return hatch
	
	def AddSolid(self,pnt1,pnt2,pnt3,pnt4):
		"""
		Adds 2D Solid Polygon in ActiveSpace.
		-------------------------------------
		:param pnt1: APoint
		:param pnt2: APoint
		:param pnt3: APoint
		:param pnt4: APoint
		-------------------------------------
		:returns : Solid
		"""
		return self.Space.AddSolid(pnt1,pnt2,pnt3,pnt4)

	def AboutEntityObject(self):

		"""
		<This method is created only for the noting purpose>
		About editting PyPCAD entity object:Users shall consult the reference document for exact supported property in terms of every kind of cad 
		entity.Some commen property and method has been summed up as below:
			(1)Commen Property:
				(a)object.color=X
				X:built-in contant, such as win32com.client.constants.acRed.Here,color is lowercase.
				(b)object.Layer=X
				X:string, the name of the layer
				(c)object.Linetype=X
				X:string,the name of the loaded linetype
				(d)object.LinetypeScale=X
				X:float,the linetype scale
				(e)object.Visible=X
				X:boolean,Determining whether the object is visible or invisible
				(f)object.EntityType
				read-only,returns an integer.
				(g)object.EntytyName
				read-only,returns a string
				(h)object.Handle
				read-only,returns a string
				(i)object.ObjectID
				read-only,returns a long integer
				(j)object.Lineweight=X
				X:built-in constants,(For example, win32com.client.constants.acLnWt030(0.3mm),acLnWt120 is
				1.2mm, and the scope of lineweight is 0~2.11mm),or acByLayer(the same with the layer
				where it lies),acByBlock,acBylwDefault.

			(2)Commen Method:
				(a)Copy
				RetVal=object.Copy
				RetVal: New created object
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.

				(b)Offset
				RetVal=object.Offset(Distance)
				RetVal:New created object tuple
				Distance:Double,positive or negative
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.

				(c)Mirror
				RetVal=object.Mirror(point1,point2)
				RetVal:mirror object
				point1,point2:end of mirror axis, Apoint type.
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.

				(d)ArrayPolar
				RetVal=object.ArrayPolar(NumberOfObject,AngleToFill,CenterPoint)
				RetVal:New created object tuple
				NumberOfObject:integer,the number of array object(including object itself)
				AngleToFill:Double,rad angle, positive->anticlockwise,negative->clockwise
				CenterPoint:Double,Apoint type. The center of the array.
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.

				(e)ArrayRectangular
				RetVal=object.ArrayRectangular(NumberOfRows,NumberOfColumns,NumberOfLevels,
				DistBetweenRows,DistBetweenColumns,DistBetweenLevels)
				RetVal:new created object tuple
				NumberOfRows,NumberOfColumns,NumberOfLevels:integer,the number of row,column,level,
				if it is the plain array that is performed, NumberOfLevels=1
				DistBetweenRows,DistBetweenColumns,DistBetweenLevels:Double,the distance between rows,
				columns,levels respectively.When NumberOfLevels=1,DistBetweenLevels is valid but still
				need to be passed
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.

				(f)Move
				object.Move(point1,point2)
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.
				point1,point2:Double,Apoint type. The moving vector shall be determined by the
				two points and point1 is the start point, point2 is the end point.

				(g)Rotate
				object.Rotate(BasePoint,RotationAngle)
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.
				BasePoint:Double,Apoint type.The rotation basepoint.
				RotationAngle:Double,rad angle.

				(h)ScaleEntity
				object.ScaleEntity(BasePoint,ScaleFactor)
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.
				BasePoint:Double,Apoint type.The scale basepoint.
				ScaleFactor:Double,Apoint type.

				(i)Erase
				object.Erase()
				object:Choosed set
				Delete all entity in the choosen scope

				(J)Delete
				object.Delete()
				object:specified entity, as for set object,such as modelSpace set and layerSet , this
				method is valid.

				(k)Update
				object.Update()
				update object after some kind of the objects' editing.

				(L)color
				object.color
				Here attention please, it is color,Not Color.(lowercase)

				(M)TransformBy
				object.TransformBy(transformationMatrix)
				object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.
				transformationMatrix:4*4 Double array, need to be passed to ArrayTransform() method to be the required type 


			(3)Refer to Object

				(a)HandleToObject
				RetVal=object.HandleToObject(Handle)
				Retval:the entity object corresponding to Handle
				object:Document object
				Handle: the handle of entity object

				(b)ObjectIdToObject
				RetVal=object.ObjectIdToObject(ID)
				RetVal:the entity object corresponding to ID
				object:Document object
				ID: the identifier of object 
		"""
		pass

	"""
	Refer and select entity
	"""

	def Handle2Object(self,handle):
		"""
		Returns the object of specified handle.
		---------------------------------------
		:param handle: string
		---------------------------------------
		:returns : object of specified handle
		"""
		return self.pypcad.ActiveDocument.HandleToObject(handle)
	

	def GetEntityByItem(self,i):
		"""
		Returns the Entity on specified index.
		--------------------------------------
		:param i: int
		--------------------------------------
		:returns : Entity
		"""
		return self.Space.Item(i)

	def GetSelectionSets(self,setname):
		"""
		Adds selection set to selectionsets
		There are 2 steps to select entity object:
		(1) create selection set 
		(2)Add entity into set
		Also note that: one set once has been created,
		it can never be created again, unless it is
		deleted.
		This method provides the first step.
		For example:
		>>>ft=[0, -4, 40, 8]  # define filter type
		>>>fd=['Circle', '>=', 5, '0'] #define filter data
		>>>ft=VtInt(ft) # data type Convertion
		>>>fd=VtVariant(fd) #data type Convertion
		>>>slt=pypcad.GetSelectionSets('slt') # Create selectionset object
		>>>slt.SelectOnScreen(ft,fd) # select on screen
		>>>slt.Erase() # Erase selected entity
		>>>slt.Delete() # Delete selectionsets object
		Using select method:
		>>>slt=pypcad.GetSelectionSets('slt1')
		>>>slt.Select(Mode=win32com.client.constants.acSelectionSetAll,FilterType=ft,FilterData=fd) # Attention about the keyword arguments
		(3) Using SelectByPolygon method to automatically select entity
		>>>pnt=pypcad.GetPoint()
		>>>pnt1=pypcad.GetPoint()
		>>>pnt2=pypcad.GetPoint()
		>>>pnt3=pypcad.GetPoint()  # select 4 points
		>>>c=list(pnt)+list(pnt1)+list(pnt2)+list(pnt3)
		>>>slt=pypcad.GetSelectionSets('test2')
		>>>slt.SelectByPolygon(Mode=win32com.client.constants.acSelectionSetWindowPolygon,PointsList=VtVertex(*c)).
		----------------------------------------------------------------------------------------------------------------------------------
		:param setname:string
		----------------------------------------------------------------------------------------------------------------------------------
		:returns : Selectionset
		"""
		return self.pypcad.ActiveDocument.SelectionSets.Add(setname)

	"""
	There are 5 methods to add entity into selection set:

	(1)object.AddItems(Items)
	object:selection set
	Items:Variant tuple. For example, Items=VtObject((c1,c2)),where c1,c2 
	is the object being ready to join in selection set

	(2)object.Select(Mode[,Point1][,Point2][,FilterType][,FilterData])
	object:selection set
	Mode=win32com.client.constants.X
	X is as below:
	acSelectionSetWindow,acSelectionSetPrevious,acSelectionSetLast,
	acSelectionSetAll
	Point1,Point2: 2 diagonal points defining a window
	FilterType,FilterData: DXF group code; filter type. 

	(3)object.SelectAtPoint(Point[,FilterType][,FilterData])
	object:selection set
	Point:Given point

	(4)object.SelectByPolygon(Mode,PointsLists[,FilterType][,FilterData])
	object:selection set
	Mode=win32com.client.constants.X
	X is as below:
	acSelectionSetFence,acSelectionSetWindowPolygon,acSelectionSetCrossingPolygon
	PointsLists:a serial points(3D) defining polygon
	FilterType,FilterData: DXF group code; filter type.

	(5)object.SelectOnScreen(filterType,filterData)
	object:selection set
	FilterType,FilterData: DXF group code; filter type.
	"""

	"""
	Filter Mechanism:
	DXF                  filter type
	0              entity ,such as Line,Circle,Ac,etc.
	2              name of object (string)
	5              entity handle
	8              layer
	60             visible of entity
	62             color integer,0->BYBLOCK,256->BYLAYER,negative->closed layer
	67             ignored or 0->ModelSpace,1->PaperSpace

	DXF shall be passed into FilterType() in the form of tuple to be the required type,
	while filter type shall be passed into FilterData() in the form of tuple to be the 
	required type.
	"""


	"""
	Deletion of selection set:
	(1)Clear:clear the selection set, the selection set still exists and the member entities still
	exist but they no longer belong to this selection set.

	(2)RemoveItems:the removed member entities still exist, but they no longer belong to this selection
	set.

	(3)Erase:delete all the member entities and the selection set itsel still exists.

	(4)Delete:delete the selection set itself, but the member entities still exist.

	"""

	"""
	Layer
	"""
	def CreateLayer(self,layername):
		"""
		Creates new layer.
		------------------------
		:param layername: string
		------------------------
		:returns : Layer
		"""
		return self.pypcad.ActiveDocument.Layers.Add(layername)


	def ActivateLayer(self,layer):
		"""
		Activates layer.
		---------------------------
		:param layer: int or string
		---------------------------
		:returns : Layer
		"""
		self.pypcad.ActiveDocument.ActiveLayer=self.GetLayer(layer)

	@property
	def LayerNumbers(self):
		"""
		Returns the number of layers in the active document.
		----------------------------------------------------
		:param 
		----------------------------------------------------
		:returns : int
		"""
		return self.pypcad.ActiveDocument.Layers.Count

	@property
	def LayerNames(self):
		"""
		Returns a list containing all layer names.
		-----------------------------------------
		:param 
		-----------------------------------------
		:returns : list
		"""
		a=[]
		for i in range(self.LayerNumbers):
			a.append(self.pypcad.ActiveDocument.Layers.Item(i).Name)
		return a

	def GetLayer(self,layer):
		"""
		Gets an indexed layer.
		---------------------------
		:param layer: int or string
		---------------------------
		:returns : Layer
		"""
		if isinstance(layer,str):
			index=self.LayerNames.index(layer)
		elif isinstance(layer,int):
			index=layer
		else:
			raise PycomError('Type of layer in GetLayer() is wrong')
		return self.pypcad.ActiveDocument.Layers.Item(index)

	@property 
	def Layers(self):
		"""
		Returns layer set object.
		---------------------------
		:param 
		---------------------------
		:returns : Layers
		"""
		return self.pypcad.ActiveDocument.Layers

	@property
	def ActiveLayer(self):
		"""
		Returns ActiveLayer object.
		---------------------------
		:param 
		---------------------------
		:returns : Layer
		"""
		return self.pypcad.ActiveDocument.ActiveLayer
	"""
	The state change and deletion of layer:
	(1)Obj.LayerOn=True/False
	Obj:Layer object
	closed or not,if it is  closed, new entity object can be created on layer,while it cannot be seen.
	(2)Obj.Freeze=True/False
	Obj:Layer object
	if freezed,the layer can neighter be shown or created entities on it.
	(3)Obj.Lock=True/False
	Obj:Layer object
	The entity on a locked layer can be shown, if the locked layer is activated, new entity can be 
	created there, but the entities cannot be edited or deleted.
	(4)Obj.Delete
	Obj:Layer object
	Delete any layer, except for cunnrent layer and 0 layer(default layer).

	The property of layer:
	(1)Obj.color=X
	X:built-in contant, such as win32com.client.constants.acRed
	(2)Obj.Linetype=X
	X:string, the name of loaded linetype
	(3)Obj.Name
	"""
	"""
	Linetype
	"""
	def LoadLinetype(self,typename,filename='pypcad.lin'):
		"""
		Loads linetype in ActiveDocument.
		typename:string, the name of type needed to be load.such as 'dashed','center'
		filename:string, the name of the file the linetype is in.'pypcad.lin','pypcadiso.lin'
		---------------------------
		:param typename: string
		:param filename: string
		---------------------------
		:returns :
		"""
		self.pypcad.ActiveDocument.Linetypes.Load(typename,filename)

	def ActivateLinetype(self,typename):
		"""
		Activate linetype in ActiveDocument.
		typename:string, the name of type needed to be load.such as 'dashed','center'
		---------------------------
		:param typename: string
		---------------------------
		:returns : LineType
		"""
		try:
			self.pypcad.ActiveDocument.ActivateLinetype=self.pypcad.ActiveDocument.Linetypes.Item(typename)
		except:
			print('The typename has not been loaded')

	def ShowLineweight(self,TrueorFalse):
		"""
		Sets whether the lineweight be shown or not.
		--------------------------------------------
		:param TrueorFalse: True or False
		--------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Preferences.LineWeightDisplay=TrueorFalse
  
	@property
	def Linetypes(self):
		"""
		Returns linetype set.
		----------------------
		:param 
		----------------------
		:returns : LineTypes
		"""
		return self.pypcad.ActiveDocument.Linetypes 
		
	

	"""
	Block
	There are 3 steps as for the creation and reference about Block.
	(1)create a block, see  the following method CreateBlcok
	(2)The created blcok adds enity;
	Obj.AddX
	X can be entity object,text object,etc.
	(3)insert block, see the fowllowing method InsertBlcok

	Block Explode
	Obj.Explode()
	Obj:Reference Block object
	This method returns a tuple containing the exploded object

	Block attribute object
	Retval=blockObj.AddAttribute(height,mode,prompt,insertPoint,tag,value)
	blockObj:Block reference object
	Retval:Attribute object
	height:Double float, the height of text
	Mode:built-in constants,win32com.client.constants.X,and X is as the following
		acAttributeModeInvisible:the attribute value is invisible
		acAttributeModeConstant:constant attribute, cannot be editted
		acAttributeModeVerify:when inserting block, prompt users to ensure the attribute value
		acAttributeModePreset:when inserting block, use default attribute value, cannot be editted
		These constants can be used as a combination
	
	GetAttribute method
		To access an attribute reference of an inserted block, use the GetAttributes method. 
		This method returns an array of all attribute references attached to the inserted block. 
	Retval=obj.GetAttributes()
	obj:Block reference object
	Retval:Block attribute object tuple
	Retval's 2 main property:(1)TagString(2)TextString
	Note:since Retval is a tuple, we may use len() method to get the number of the member in it
	"""

	def CreateBlock(self,insertPnt,blockName):
		"""
		Creates Block.
		------------------------
		:param insertPnt: APoint
		:param blockName: string
		------------------------
		:returns : Block
		"""
		return self.pypcad.ActiveDocument.Blocks.Add(insertPnt,blockName)

	def InsertBlock(self,insertPnt,blockName,Xscale=1,Yscale=1,Zscale=1,Rotation=0):
		"""
		Adds Block to ActiveSpace.
		--------------------------
		:param insertPnt: APoint
		:param blockName: string
		--------------------------
		:returns : BlockReference
		"""
		return self.Space.InsertBlock(insertPnt,blockName,Xscale,Yscale,Zscale,Rotation)

	"""
	User-defined coordinate system
	Normally, users perform drawing work in WCS(world coordinate system).However,in some case, it is easy
	to draw in UCS(user coordinate system). In UCS, it's necessary to use coordinate transform, and the steps
	are as follow:
	(1)Create entity in WCS directly
	(2)Create UCS and get transform matrix of UCS by method GetUCSMatrix (here, also need array type conversion
	 by ArrayTransform method)
	(3)Transform the entity created in WCS to UCS through method TransformBy
	Also attention that after the transform perform , it's better to set the previous coordinate system.

	TransMatrix=ucsObj.GetUCSMatrix()
	TransMatrix:4*4 Double array, need to be passed to ArrayTransform() method to be the required type 
	ucsObj:UCS object

	TransformBy
	object.TransformBy(transformationMatrix)
	object:Drawing entity,such as Arc,Line,LightweithPolyline,Spline,etc.
	transformationMatrix:4*4 Double array, need to be passed to ArrayTransform() method to be the required type 
	"""
	def CreateUCS(self,origin,xAxisPnt,yAxisPnt,csName):
		"""
		Creats UCS to ActiveSpace.
		origin:Apoint type,origin point of the new CS
		xAxisPnt:Apoint type,one point directing the positive direction of x axis of the new CS
		yAxisPnt:Apoint type,one point directing the positive direction of y axis of the new CS
		csName:string,the name of the new CS

		---------------------------------------------------------------------------------------
		:param origin: APoint
		:param xAxisPnt: APoint
		:param yAxisPnt: APoint
		:param csName: string
		---------------------------------------------------------------------------------------
		:returns : UCS
		"""
		return self.pypcad.ActiveDocument.UserCoordinateSystems.Add(origin,xAxisPnt,yAxisPnt,csName)

	def ActivateUCS(self,ucsObj):
		"""
		Activates UCS object.
		---------------------
		:param ucsObj: UCS
		---------------------
		:returns : UCS
		"""
		self.pypcad.ActiveDocument.ActiveUCS=ucsObj

	def GetCurrentUCS(self):
		"""
		Gets current UCS object.
		------------------------
		:param 
		------------------------
		:returns : UCS
		"""
		if self.pypcad.ActiveDocument.GetVariable('ucsname')=='':
			origin=self.pypcad.ActiveDocument.GetVariable('ucsorg')
			origin=ArrayTransform(origin)
			xAxisPnt=self.pypcad.ActiveDocument.Utility.TranslateCoordinates(ArrayTransform(self.pypcad.ActiveDocument.GetVariable('ucsxdir')),
				win32com.client.constants.acUCS,win32com.client.constants.acWorld,0)
			xAxisPnt=ArrayTransform(xAxisPnt)
			yAxisPnt=self.pypcad.ActiveDocument.Utility.TranslateCoordinates(ArrayTransform(self.pypcad.ActiveDocument.GetVariable('ucsydir')),
				win32com.client.constants.acUCS,win32com.client.constants.acWorld,0)
			yAxisPnt=ArrayTransform(yAxisPnt)
			currCS=self.pypcad.ActiveDocument.UserCoordinateSystems.Add(origin,xAxisPnt,yAxisPnt,'currentUCS')
		else:
			currCS=self.pypcad.ActiveDocument.ActiveUCS
		return currCS

	def ShowUCSIcon(self,booleanOfUCSIcon,booleanOfUCSatOrigin):
		"""
		Shows UCS Icon.
		booleanOfUCSIcon:boolean,Specifies if the UCS icon is on
		booleanOfUCSatOrigin:boolean,Specifies if the UCS icon is displayed at the origin
		---------------------------------------------------------------------------------
		:param booleanOfUCSIcon: True or False
		:param booleanOfUCSatOrigin: True or False
		---------------------------------------------------------------------------------
		:returns :
		"""
		self.pypcad.ActiveDocument.ActiveViewport.UCSIconOn=booleanOfUCSIcon
		self.pypcad.ActiveDocument.ActiveViewport.UCSIconAtOrigin=booleanOfUCSatOrigin


	"""
	Text

	Text Style Object
		(1)SetFont method
		object.SetFont(TypeFace,Bold,Italic,CharSet,PitchandFamily)
		Function->Set the font for created text style object
		object:text style object
		TypeFace:string, font name, such as "宋体"
		Bold:boolean,if True, bold, if False, normal
		Italic:boolean, if True, italic,if False,normal
		CharSet: long integer, defining font character set, the constants's meaning is as below
			Constant 			Meaning
			0					ANSI character set
			1 					Default character set
			2 					Symbol set
			128 				Japanese character set
			255					OEM character set 
		PitchandFamily: consists of 2 part:(a)Pitch,defining character's pitch(b)Family,defining character'stroke
			Pitch:
				Constant 					Meanning
				0 							Default value
				1 							Fixed value
				2 							variable value
			Family:
				Conatant 					Meanning
				0 							No consideration of stroke form
				16							Variable stroke width,with serif
				32 							Variable stroke width,without serif
				48 							Fixed stroke width,with or without serif
				64 							Grass writting
				80 							Old English stroke
		(2) FontFile property
		obj.fontFile=path
		obj:textstyle object
		set the given textstyle's font file by the path of character file,
		for example, path=self.pypcad.Path+r'\tssdeng.shx'

		(3)BigFontFile property
		obj.BigFontFile=path
		obj:textstyle object
		This property is similar to the FontFile property, except that it is used to specify 
		an Asian-language Big Font file. The only valid file type is SHX

	"""

	def CreateTextStyle(self,textStyleName):
		"""
		Creates text style.
		-----------------------------
		:param textStyleName: string
		-----------------------------
		:returns : TextStyle
		"""
		return self.pypcad.ActiveDocument.TextStyles.Add(textStyleName)

	def ActivateTextStyle(self,textStyleObj):
		"""
		Activates the created textstyle object.
		---------------------------------------
		:param textStyleObj: textStyle object
		---------------------------------------
		:returns : TextStyle
		"""
		self.pypcad.ActiveDocument.ActiveTextStyle=textStyleObj

	def GetActiveFontInfo(self):
		"""
		Returns a tuple (typeFace,Bold,Italic,charSet,PitchandFamily) of the active textstyle object.
		---------------------------------------------------------------------------------------------
		:param 
		---------------------------------------------------------------------------------------------
		:returns : tuple
		"""
		return self.pypcad.ActiveDocument.ActiveTextStyle.GetFont()

	def SetActiveFontFile(self,path):
		"""
		Sets the active textstyle's font file by the path of character file,
		for example, path=self.pypcad.Path+r'\tssdeng.shx'.
		--------------------------------------------------------------------
		:param path: string
		--------------------------------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.ActiveTextStyle.fontFile=path 
  
	def SetActiveBigFontFile(self,path):
		"""
		Sets the active Asian-language Big Font file by the path of character file,
		This property is similar to the FontFile property, except that it is used to specify 
		an Asian-language Big Font file. The only valid file type is SHX.
		------------------------------------------------------------------------------------
		:param path: string
		------------------------------------------------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.ActiveTextStyle.BigFontFile=path

	"""
	Single Text

	Formatted text
		(1)Alignment
			object.Alignment=win32com.client.constants.X
			[object.TextAlignmentPoint=pnt1]
			[object.InsertionPoint=pnt2]
			object:single text object
			X:acAlignmentLeft 
			acAlignmentCenter 
			acAlignmentRight 
			acAlignmentAligned 
			acAlignmentMiddle 
			acAlignmentFit 
			acAlignmentTopLeft 
			acAlignmentTopCenter 
			acAlignmentTopRight 
			acAlignmentMiddleLeft 
			acAlignmentMiddleCenter 
			acAlignmentMiddleRight 
			acAlignmentBottomLeft 
			acAlignmentBottomCenter 
			acAlignmentBottomRight
		Note that:Alignment property has to be set before TextAlignmentPoint or InsertionPoint property be set!
		Text aligned to acAlignmentLeft uses the InsertionPoint property to position the text. Text aligned to 
		acAlignmentAligned or acAlignmentFit uses both the InsertionPoint and TextAlignmentPoint properties to
		position the text. Text aligned to any other position uses the TextAlignmentPoint property to position the text.

		(2)InsertionPoint
			object.InsertionPoint=pnt
			pnt:Apoint type
		Note:This property is read-only except for text whose Alignment property is set to acAlignmentLeft, 
		acAlignmentAligned, or acAlignmentFit. To position text whose justification is other than left, aligned,
		or fit, use the TextAlignmentPoint property.

		(3)ObliqueAngle
			object.ObliqueAngle=rad
			rad:Double,rad angle
			The angle in radians within the range of -85 to +85 degrees. A positive angle denotes a lean to the right; 
			a negative value will have 2*PI added to it to Convert it to its positive equivalent. 

		(4)Rotation
			object.Rotation=rad
			rad:Double,The rotation angle in radians. 

		(5)TextAlignmentPoint
		objcet.TextAlignmentPoint=pnt
		pnt:Apoint type
		Specifies the alignment point for text and attributes;Note that:Alignment property has to be set before 
		TextAlignmentPoint or InsertionPoint property be set!Text aligned to acAlignmentLeft uses the InsertionPoint 
		property to position the text.

		(6)TextGenerationFlag
		object.TextGenerationFlat=win32com.client.constants.x
		X:acTextFlagBackward,acTextFlagUpsideDown
		Specifies the attribute text generation flag,To specify both flags, add them together,
		that is acTextFlagBackward+acTextFlagUpsideDown

		(7)TextString
		object.TextString
		This method returns the text string of single text object

		(8)commen editing method:
		ArrayPolar,ArrayRectangular,Copy,Delete,Mirror,Move,Rotate.
	"""
	def AddText(self,textString,insertPnt,height):
		"""
		Adds single text in ActiveSpace.
		textString:string,the inserted single text
		insertPnt:Apoint type,insert point
		height:the text height
		-------------------------------------------
		:param textString: string
		:param insertPnt: Apoint
		:param height: int or float
		-------------------------------------------
		:returns : Text
		"""
		return self.Space.AddText(textString,insertPnt,height)
	"""
	MutiText
	"""
	def AddMText(self,textString,insertPnt,width):
		"""
		Creates an MText entity in a rectangle defined by the insertion point and width of the bounding box.
		----------------------------------------------------------------------------------------------------
		:param textString: string
		:param insertPnt: Apoint
		:param width: int or float
		----------------------------------------------------------------------------------------------------
		:returns : MText
		"""
		return self.Space.AddMText(insertPnt,width,textString)

	"""
	Dimension and Tolerance

	Common property of dim object
		(1)obj.DecimalSeparator=X
		X:string,such as '.',can be any string.

		(2)obj.ArrowheadSize=X
		X:Double,The size of the arrowhead must be specified as a positive real >= 0.0,The initial value for this property is 0.1800.

		(3)obj.DimensionLineColor=X
		X:Use a color index number from 0 to 256, or bilt-in constants

		(4)obj.DimLineInside=X
		X:Boolean, default is False. Specifies the display of dimension lines inside the extension lines . Dimension line is the line below
		the dimenion text and extension lines are a pair of lines pointing to the limit point of a dimension.

		(5)obj.Fit=win32com.client.constants.X
		Specifies the placement of text and arrowheads inside or outside extension lines, based on the available space between the extension lines
		X:acTextAndArrows,acArrowsOnly,acTextOnly,acBestFit

		(6)obj.Measurement
		Read-only,returns the actural dimension value.

		(7)obj.TextColor
		the text color

		(8)obj.TextHeight
		the text height

		(9)obj.TextOverride=X
		X:string. ''represents the actural measurement.'<>'represents the actural measurment value,such as '<>mm'

		(10)obj.Arrowhead1Type=win32com.client.constants.X
		obj.Arrowhead2Type=win32com.client.constants.X
		X:
			acArrowDefault,acArrowDot,acArrowDotSmall,acArrowDotBlank,acArrowOpen,acArrowOblique,acArrowArchTick,etc.

		(11)obj.TextPosition=X
		X:Apoint type. the position of text.

		(12)obj.TextPrefix=X
		X:string

		(13)obj.TextSuffix=X
		X:string
		(14)obj.UnitsFormat=win32com.client.constants.X
		Specifies the unit format for all dimensions except angular
		X:
			acDimLScientific,acDimLDecimal,acDimLEngineering,acDimLArchitectural,acDimLFractional
		The initial value for this property is acDimLDecimal.If this property is set to acDimLDecimal, 
		the format specified by the DecimalSeparator and PrimaryUnitsPrecision properties will be used to format the decimal value

		(15)obj.PrimaryUnitsPrecision=win32com.client.constants.X
		Specifies the number of decimal places displayed for the primary units of a dimension or tolerance
		X:
			acDimPrecisionZero: 0
			acDimPrecisionOne: 0.0
			acDimPrecisionTwo: 0.00
			acDimPrecisionThree: 0.000
			acDimPrecisionFour: 0.0000 
			acDimPrecisionFive: 0.00000
			acDimPrecisionSix: 0.000000
			acDimPrecisionSeven: 0.0000000
			acDimPrecisionEight: 0.00000000 

		(16)obj.VerticalTextPosition=win32com.client.constants.X
		X:
			acAbove,acOutside,acVertCentered,acJI

		(17)obj.TextOutsideAlign=X
		obj:
		X:Boolean,Specifies the position of dimension text outside the extension lines for all dimension types except ordinate
		True: Align the text horizontally
		False: Align the text with the dimension line

		(18)obj.CenterType=win32com.client.constants.X
		Specifies the type of center mark for radial and diameter dimensions
		obj: DimDiametric, DimRadial, DimRadialLarge 
			X:
			acCenterMark 
			acCenterLine 
			acCenterNone
		Note:The center mark is visible only if you place the dimension line outside the circle or arc.

		(19) obj.CenterMarkSize=X
		Specifies the size of the center mark for radial and diameter dimensions.
		X:Double,A positive real number specifying the size of the center mark or lines
		Note:The initial value for this property is 0.0900. This property is not available if the CenterType property is set to acCenterNone.

		(20)obj.ForceLineInside=X
		Specifies whether a dimension line is drawn between the extension lines even when the text is placed outside the extension lines
		X:Boolean
		True: Draw dimension lines between the measured points when arrowheads are placed outside the measured points. 
		False: Do not draw dimension lines between the measured points when arrowheads are placed outside the measured points

		(21)obj.StyleName=X
		X:string
		Specifies the name of the style used with the object

	"""
	def AddDimAligned(self,extPnt1,extPnt2,textPosition):
		"""
		Creates an aligned dimension object
		extPnt1:Apoint type,the 3D WCS coordinates specifying the first endpoint of the extension line
		extPnt2:Apoint type,the 3D WCS coordinates specifying the second endpoint of the extension line
		textPosition:Apoint type,the 3D WCS coordinates specifying the text position
		----------------------------------------------------------------------------------------------------
		:param extPnt1: Apoint
		:param extPnt2: Apoint
		:param textPosition: Apoint
		----------------------------------------------------------------------------------------------------
		:returns : DimAligned
		"""
		return self.Space.AddDimAligned(extPnt1,extPnt2,textPosition)

	def AddDimRotated(self,xlPnt1,xlPnt2,dimLineLocation,rotAngle):
		"""
		Creates a rotated linear dimension
		xlPnt1:Apoint type,the 3D WCS coordinates specifying the first endpoint of the extension line
		xlPnt2:Apoint type,the 3D WCS coordinates specifying the first endpoint of the extension line
		rotAngle:Double,The angle, in radians, of rotation displaying the linear dimension
		---------------------------------------------------------------------------------------------
		:param xlPnt1: Apoint
		:param xlPnt2: Apoint
		:param dimLineLocation: Apoint
		:param rotAngle: int or float
		---------------------------------------------------------------------------------------------
		:returns : DimRotated
		"""
		return self.Space.AddDimRotated(xlPnt1,xlPnt2,dimLineLocation,rotAngle)

	def AddDimRadial(self,center,chordPnt,leaderLength):
		"""
		Creates a radial dimension for the selected object at the given location
		center:Apoint type
		chordPnt:Apoint type,The 3D WCS coordinates specifying the point on the circle or arc to attach the leader line
		leaderLength:double,The positive value representing the length from the ChordPoint to the annotation text
		---------------------------------------------------------------------------------------------
		:param center: Apoint
		:param chordPnt: Apoint
		:param leaderLength: int or float
		---------------------------------------------------------------------------------------------
		:returns : DimRadial
		"""
		return self.Space.AddDimRadial(center,chordPnt,leaderLength)

	def AddDimDiametric(self,chordPnt,farChordPnt,leaderLength):
		"""
		Creates a diametric dimension for a circle or arc given the two points on the diameter and the length of the leader line
		chordPnt:Apoint type,The 3D WCS coordinates specifying the first diameter point on the circle or arc
		farChordPnt:Apoint type,The 3D WCS coordinates specifying the second diameter point on the circle or arc
		leaderLength:The positive value representing the length from the ChordPoint to the annotation text or dogleg, when it is 0,
		using obj.Fit=win32com.client.constants.acTextAndArrows can make the arrow and text inside the circle or dogleg
		---------------------------------------------------------------------------------------------------------------------------
		:param chordPnt: Apoint
		:param farChordPnt: Apoint
		:param leaderLength: int or float
		--------------------------------------------------------------------------------------------------------------------------
		:returns : DimDiametric
		"""
		return self.Space.AddDimDiametric(chordPnt,farChordPnt,leaderLength)

	def AddDimAngular(self,vertex,firstPnt,secondPnt,textPnt):
		"""
		Creates an angular dimension for an arc, two lines, or a circle
		vertex,Apoint type,The 3D WCS coordinates specifying the center of the circle or arc, or the common vertex between the two dimensioned lines
		firstPnt,Apoint type,The 3D WCS coordinates specifying the point through which the first extension line passes
		secondPnt,Apoint type,The 3D WCS coordinates specifying the point through which the second extension line passes
		textPnt,Apoint type,The 3D WCS coordinates specifying the point at which the dimension text is to be displayed
		--------------------------------------------------------------------------------------------------------------------------------------------
		:param vertex: Apoint
		:param firstPnt: Apoint
		:param secondPnt: Apoint
		:param textPnt: Apoint
		--------------------------------------------------------------------------------------------------------------------------------------------
		:returns : DimAngular
		"""
		return self.Space.AddDimAngular(vertex,firstPnt,secondPnt,textPnt)

	def AddDimOrdinate(self,definitionPnt,leaderPnt,axis):
		"""
		Creates an ordinate dimension given the definition point and the leader endpoint
		definitionPnt,Apoint type,The 3D WCS coordinates specifying the point to be dimensioned
		leaderPnt,Apoint type,The 3D WCS coordinates specifying the endpoint of the leader. This will be the location at which the dimension text is displayed
		axis,Boolean,True: Creates an ordinate dimension displaying the X axis value;False: Creates an ordinate dimension displaying the Y axis value
		------------------------------------------------------------------------------------------------------------------------------------------------------
		:param definitionPnt: Apoint
		:param leaderPnt: Apoint
		:param axis: true or false
		------------------------------------------------------------------------------------------------------------------------------------------------------
		:returns : DimOrdinate
  		"""
		return self.Space.AddDimOrdinate(definitionPnt,leaderPnt,axis)

	def AddLeader(self,*pntArray,annotation=None,type=None):
		"""
		Creates a leader line based on the provided coordinates or adds a new leader cluster to the MLeader object
		pntArray,The array of 3D WCS coordinates,such as (1,2,3,4,5,6), specifying the leader. You must provide at least two points to define the leader. The third point is optional
		annotation,BlockReference,MText,Tolerance type.The object that should be attached to the leader. The value can also be NULL to not attach an 
		Type:built-in contants, win32com.client.constants.X,X is as the following:
		acLineNoArrow 
		acLineWithArrow 
		acSplineNoArrow 
		acSplineWithArrow
		>>>ann=pypcad.AddMText('demo',Apoint(30,30,0),2)
		>>>import win32com.client
		>>>pypcad.AddLeader(0,0,0,30,30,0,annotation=a,type=win32com.client.constants.acLineWithArrow)
		----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		:param *pntArray: tuple
		:param annotation: Entity object
		:param type: LeaderType object
		----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		:returns : Leader
		"""
		return self.Space.AddLeader(VtVertex(*pntArray),annotation,type)

	"""
	Dimension style object

	(1)obj.CopyFrom(X)
	X:self.DimStyle0, self.ActiveDimStyle,and other dimension style object

	"""
	def CreateDimStyle(self,name):
		"""
		creat a new dimension style named name.
		name:string
		Once created, Using the created dimstyle object's CopyFrom() method to get an existed dimstyle's
		attributes.DimStyle0 is prefered to be copied from,when a new dim factor is needed, just reset corresponding system variable.For example:
		>>>pypcad=PyPCAD()
		>>>testDim=pypcad.CreateDimStyle('test')
		>>>pypcad.SetSystemVariable('dimlfac',100)
		>>>testDim.CopyFrom(pypcad.DimStyle0)
		------------------------------------------------------------------------------------------------------------------------------------------
		:param name: string
		------------------------------------------------------------------------------------------------------------------------------------------
		:returns : DimStyle
		"""
		return self.pypcad.ActiveDocument.DimStyles.Add(name)

	@property
	def DimStyleNumbers(self):
		"""
		Returns the total number of defined dim style.
		----------------------------------------------
		:param 
		----------------------------------------------
		:returns : int
		"""
		return self.DimStyles.Count

	@property
	def DimStyleNames(self):
		"""
		Returns list,all names of defined dim style.
		--------------------------------------------
		:param 
		--------------------------------------------
		:returns : list
		"""
		dimnames=[]
		for i in range(self.DimStyleNumbers):
			dimnames.append(self.DimStyles.Item(i).Name)
		return dimnames

	@property 
	def DimStyle0(self):
		"""
		Returns created dimension style object whose index is 0 in modelspace.
		----------------------------------------------------------------------
		:param 
		----------------------------------------------------------------------
		:returns : DimStyle
		"""
		return self.Space(0)

	@property 
	def DimStyles(self):
		"""
		Returns dimstyles object.
		-------------------------
		:param 
		-------------------------
		:returns : DimStyles
		"""
		return self.pypcad.ActiveDocument.DimStyles

	@property 
	def ActiveDimStyle(self):
		"""
		Returns a dim style set by system variable.
		-------------------------------------------
		:param 
		-------------------------------------------
		:returns : DimStyle
		"""
		return self.pypcad.ActiveDocument.ActiveDimStyle

	def GetDimStyle(self,dimname):
		"""
		Returns specified dim style object.
		-----------------------------------
		:param dimname:int or string
		-----------------------------------
		:returns : DimStyle
		"""
		if isinstance(dimname,str):
			index=self.DimStyleNames.index(dimname)
		elif isinstance(dimname,int):
			index=dimname
		else:
			raise PycomError('dimname in GetDimStyle is wrong')
		return self.DimStyles.Item(index)

	def ActivateDimStyle(self,dimname):
		"""
		Activates DimStyle dimname.
		----------------------------
		:param dimname:int or string
		----------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.ActiveDimStyle=self.GetDimStyle(dimname)
  
	"""
	Utility object method
	"""
	def GetString(self,hasSpaces,Prompt=''):
		"""
		Gets string
		hasSpaces:
			0:input string shall not has empty char('') meaning input has been done;
			1:input string can have empty char(''), and the 'Entery' keystroke means the input process has been done.
		Prompt:
			string,default to None
		-------------------------------------------------------------------------------------------------------------
		:param hasSpaces: int
		:param Prompt: string
		-------------------------------------------------------------------------------------------------------------
		:returns : string
		"""
		return self.pypcad.ActiveDocument.Utility.GetString(hasSpaces,Prompt)

	def AngleFromXAxis(self,pnt1,pnt2):
		"""
		Gets the angle of a line from the X axis.
		-----------------------------------------
		:param pnt1: APoint
		:param pnt2: APoint
		-----------------------------------------
		:returns : double
  
		"""
		return self.pypcad.ActiveDocument.Utility.AngleFromXAxis(pnt1,pnt2)

	def GetAngle(self,basePnt=Apoint(0,0,0),prompt=''):
		"""
		Gets the angle specified.
		-------------------------
		:param basePnt: APoint
		:param prompt: string
		-------------------------
		:returns : double
		"""
		return self.pypcad.ActiveDocument.Utility.GetAngle(Point=basePnt,Prompt=prompt)

	def GetPoint(self,Point=None,Prompt=''):
		"""
		Gets the selected point.
		------------------------
		:param Point: APoint
		:param prompt: string
		------------------------
		:returns : dynamic
		"""
		if Point:
			return self.pypcad.ActiveDocument.Utility.GetPoint(Point=Point,Prompt=Prompt)
		else:
			return self.pypcad.ActiveDocument.Utility.GetPoint(Prompt=Prompt)

	def GetDistance(self,pnt='',prompt=''):
		"""
		Gets the point selected in PyPCAD.
		----------------------------------
		:param pnt: APoint
		:param prompt: string
		----------------------------------
		:returns : double
		"""
		if not pnt:
			return self.pypcad.ActiveDocument.Utility.GetDistance(ArrayTransform(self.GetPoint()),prompt)
		else:
			return self.pypcad.ActiveDocument.Utility.GetDistance(pnt,prompt)

	def InitializeUserInput(self,bits,keywords):
		"""
		Before using GetKeyword method,this method has to be used to limit the user-input forms , and this method
		can also used with GetAngle,GetCorner,GetDistance,GetInteger,GetOrientation,GetPoint,GetReal, and cannot be
		used with GetString.Unless it is set again,or it will control the type of input forever.
		bits:integer
			1: Disallows NULL input. This prevents the user from responding to the request by entering only [Return] or a space. 
			2: Disallows input of zero (0). This prevents the user from responding to the request by entering 0. 
			4: Disallows negative values. This prevents the user from responding to the request by entering a negative value. 
			8: Does not check drawing limits, even if the LIMCHECK system variable is on. This enables the user to enter a point outside the current drawing limits. This condition applies to the next user-input function even if the PyPCAD LIMCHECK system variable is currently set. 
			16: Not currently used. 
			32: Uses dashed lines when drawing rubber-band lines or boxes. This causes the rubber-band line or box that PyPCAD displays to be dashed instead of solid, for those methods that let the user specify a point by selecting a location on the graphics screen. (Some display drivers use a distinctive color instead of dashed lines.) If the PyPCAD POPUPS system variable is 0, PyPCAD ignores this bit. 
			64: Ignores Z coordinate of 3D points (GetDistance method only). This option ignores the Z coordinate of 3D points returned by the GetDistance method, so an application can ensure this function returns a 2D distance. 
			128: Allows arbitrary input—whatever the user types. 
		keywords:strings,such as 'width length height'
		---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		:param bits: int
		:param keywords: string
		---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Utility.InitializeUserInput(bits,keywords)
  
	def GetKeyword(self,prompt=''):
		"""
		Before using GetKeyword method,this method has to be used to limit the user-input forms
		Gets a keyword string from the user
		---------------------------------------------------------------------------------------
		:param prompt: string
		---------------------------------------------------------------------------------------
		:returns : string
		"""
		return self.pypcad.ActiveDocument.Utility.GetKeyword(prompt)

	def GetEntity(self):
		"""
		Return a tuple containing the picked object and the coordinate of picked point.
		-------------------------------------------------------------------------------
		:param 
		-------------------------------------------------------------------------------
		:returns : tuple
		"""
		return self.pypcad.ActiveDocument.Utility.GetEntity()

	def GetReal(self,prompt=''):
		"""
		Gets a real (double) value from the user.
		-----------------------------------------
		:param prompt: string
		-----------------------------------------
		:returns : double
		"""
		return self.pypcad.ActiveDocument.Utility.GetReal(prompt)

	def GetInteger(self,prompt=''):
		"""
		Gets an integer value from the user.
		-----------------------------------------
		:param prompt: string
		-----------------------------------------
		:returns : int
		"""
		return self.pypcad.ActiveDocument.Utility.GetInteger(prompt)
	
	def prompt(self,message):
		"""
		Displays a prompt on the command line.
		-----------------------------------------
		:param message: string
		-----------------------------------------
		:returns : 
		"""
		self.pypcad.ActiveDocument.Utility.Prompt(message)
	
	"""
	Preferences object
	There are 9 sub-objects of preferences:
		(1) Display--->pypcad.Preferences.Display
		(2)Drafting--->pypcad.Preferences.Drafting
		(3)Files--->pypcad.Preferences.Files
		(4)OpenSave--->pypcad.Preferences.OpenSave
		(5)Output--->pypcad.Preferences.Output
		(6)Profiles--->pypcad.Preferences.Profiles
		(7)Selection--->pypcad.Preferences.Selection
		(8)System--->pypcad.Preferences.System
		(9)User--->pypcad.Preferences.User

	"""
	@property
	def Preferences(self):
		"""
		Returns preferences object
		-----------------------------------------
		:param 
		-----------------------------------------
		:returns : Preferences
		"""
		return self.pypcad.Preferences


if __name__=='__main__':
	table={'dimclrd':62,'dimdlI':0,'dimclre':62,
	   'dimexe':2,'dimexo':3,
	   'dimfxlon':1,
	   'dimfxl':3,'dimblk1':'_archtick',
	   'dimldrblk':'_dot',
	   'dimcen':2.5,'dimclrt':62,'dimtxt':3,'dimtix':1,
	   'dimdsep':'.','dimlfac':50}
	
	acad=PyPCAD()
	pypcad=PyPCAD()
	p1=Apoint(0,0,0)
	p2 = Apoint(100,0,0)
	p3 = Apoint(100,100,0)
	p4 = Apoint(0,100,0)
	l1=pypcad.AddLine(p1,p2)
	l2=pypcad.AddLine(p2,p3)
	l3=pypcad.AddLine(p3,p4)
	l4=pypcad.AddLine(p4,p1)
	pypcad.ZoomExtents()
	