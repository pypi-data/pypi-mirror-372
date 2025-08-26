from main import *
from compat import *
import logging

logger = logging.getLogger(__name__)
@property
def app(self):
	"""
	Returns application object.
	---------------------------
	:param 
	---------------------------
	:returns : Application
	"""
	try:
		self.pypcad=win32com.client.Dispatch("PCAD_AC_X.AcadApplication")
		self.pypcad.Visible=True 
	except:
		PyPCAD.__init__(self)
	return self.pypcad
		

@property
def doc(self):
	""" 
    Returns Active Document of current application.
	-----------------------------------------------
	:param 
	-----------------------------------------------
	:returns : Document
    """
	return self.app.ActiveDocument

def iter_layouts(self, activeDoc=None, skip_modelspace=True):
    """
    Iterate layouts from ActiveDocument
    activeDoc: If doc is not specified (default), :attr:ActiveDocument will be used to iterate layouts from.
    skip_modelspace: In cases of True, :class:ModelSpace should not be included.
	--------------------------------------------------------------------------------------------------------
	:param activeDoc: Document object
    :param skip_modelspace: true or false
	--------------------------------------------------------------------------------------------------------
	:returns : Layouts
    """
    if activeDoc is None:
        activeDoc = self.doc
    for layout in sorted(activeDoc.Layouts, key=lambda x: x.TabOrder):
        if skip_modelspace and not layout.TabOrder:
            continue
        yield layout

def iter_objects(self, obj_or_list=None, block=None, limit=None, dont_cast=False):
    """
    Iterate objects from `block`
    obj_or_list: Have an object type name include a part of it, or list of it.
    block: Application block, if no input is given default - :class:`ActiveDocument.ActiveLayout.Block` is taken
    limit: max number of objects to return, default infinite is taken.
    dont_cast: Iteration may be accelerated by avoiding retrieval of the best interface for the object. Casting of returned objects is the caller's responsibility.
	-------------------------------------------------------------------------------------------------------------------------------------------------------------------
	:param obj_or_list: object or list
    :param block: Application block
    :param limit: int
    :param dont_cast: true or false
	-------------------------------------------------------------------------------------------------------------------------------------------------------------------
	:returns : Block
    """
    if block is None:
        block = self.doc.ActiveLayout.Block
    obj_names = obj_or_list
    if obj_names:
        if isinstance(obj_names, basestring):
            obj_names = [obj_names]
        obj_names = [n.lower() for n in obj_names]

    count = block.Count
    for i in range(count):
        item = block.Item(i)
        if limit and i >= limit:
            return
        if obj_names:
            obj_name = item.ObjectName.lower()
            if not any(possible_name in obj_name for possible_name in obj_names):
                continue
        yield item

def iter_objects_fast(self, obj_or_list=None, container=None, limit=None):
    """
    Shortcut for iter_objects with param dont_cast=True`
    Shouldn't be used in normal situations.
	----------------------------------------------------
	:param obj_or_list: object or list
    :param container: objects container
    :param limit: int
	----------------------------------------------------
	:returns : Block
    """
    return self.iter_objects(obj_or_list, container, limit, dont_cast=True)

def find_one(self, obj_or_list, container=None, predicate=None):
    """
    Returns first occurance of object which match `predicate`
    obj_name_or_list: Have an object type name include a part of it, or list of it.
    container: like in :meth:`iter_objects`
    predicate: Returning True or False upon accepting an object as an argument in callable.
	---------------------------------------------------------------------------------------
	:param obj_or_list: object or list
    :param container: objects container
    :param predicate: true or false
	---------------------------------------------------------------------------------------
	:returns : object
    """
    if predicate is None:
        predicate = bool
    for obj in self.iter_objects(obj_or_list, container):
        if predicate(obj):
            return obj
    return None

def get_selection(self, text="Select objects"):
    """ 
    Asks to select objects by user
    text: text prompt for selection of objects.
	-------------------------------------------
	:param text: string
	-------------------------------------------
	:returns : SelectionSet
    """
    PyPCAD.prompt(self,text)
    try:
        self.doc.SelectionSets.Item("SelectionSet1").Delete()
    except Exception:
        logger.debug('failed Deletion')

    selectionset = self.doc.SelectionSets.Add('SelectionSet1')
    selectionset.SelectOnScreen()
    return selectionset

#: Same as doc
PyPCAD.ActiveDocument = doc

#: Same as app
PyPCAD.Application = app
PyPCAD.app=app
ACAD=PyPCAD
PyPCAD.doc=doc
PyPCAD.model=PyPCAD.Space
PyPCAD.iter_objects=iter_objects
PyPCAD.iter_layouts=iter_layouts
PyPCAD.iter_objects_fast=iter_objects_fast
PyPCAD.find_one=find_one
PyPCAD.get_selection=get_selection
