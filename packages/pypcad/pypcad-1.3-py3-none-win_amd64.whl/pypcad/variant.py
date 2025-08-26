from main import *
import array
import operator
import math
from compat import *

variant=win32com.client.VARIANT
class APoint(array.array):
    """ 
    3D point with basic geometric operations and support for passing as a
        parameter for ARES Automation functions

    Usage::

        >>> p1 = APoint(10, 10)
        >>> p2 = APoint(20, 20)
        >>> p1 + p2
        APoint(30.00, 30.00, 0.00)

    Also it supports iterable as parameter::

        >>> APoint([10, 20, 30])
        APoint(10.00, 20.00, 30.00)
        >>> APoint(range(3))
        APoint(0.00, 1.00, 2.00)

    Supported math operations: `+`, `-`, `*`, `/`, `+=`, `-=`, `*=`, `/=`::

        >>> p = APoint(10, 10)
        >>> p + p
        APoint(20.00, 20.00, 0.00)
        >>> p + 10
        APoint(20.00, 20.00, 10.00)
        >>> p * 2
        APoint(20.00, 20.00, 0.00)
        >>> p -= 1
        >>> p
        APoint(9.00, 9.00, -1.00)

    It can be converted to `tuple` or `list`::

        >>> tuple(APoint(1, 1, 1))
        (1.0, 1.0, 1.0)
        >>> list(APoint(1, 1, 1))
        [1.0, 1.0, 1.0]
	-----------------------------------------------------------------------
	:param 
	-----------------------------------------------------------------------
	:returns : variant

    """
    def __new__(cls, x_or_seq, y=0.0, z=0.0):
        if isinstance(x_or_seq, (array.array, list, tuple)) and len(x_or_seq) == 3:
           return win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,(x_or_seq)) 
        return win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,(x_or_seq,y,z)) 
        
    @property
    def x(self):
        """ 
        Returns x coordinate of 3D point.
        ---------------------------------
        :param 
        ---------------------------------
        :returns : int or float
        """
        return (self.value)[0]

    @x.setter
    def x(self, value):
        """ 
        Sets value of x coordinate of 3D point.
        ----------------------------------------
        :param value: int or float
        ----------------------------------------
        :returns : 
        """
        self.value= (value,(self.value)[1],(self.value)[2])

    @property
    def y(self):
        """ 
        Returns y coordinate of 3D point.
        ---------------------------------
        :param 
        ---------------------------------
        :returns : int or float
        """
        return (self.value)[1]

    @y.setter
    def y(self, value):
        """ 
        Sets value of y coordinate of 3D point.
        ----------------------------------------
        :param value: int or float
        ----------------------------------------
        :returns : 
        """
        self.value= ((self.value)[0],value,(self.value)[2])

    @property
    def z(self):
        """ 
        Returns z coordinate of 3D point.
        ---------------------------------
        :param 
        ---------------------------------
        :returns : int or float
        """
        return (self.value)[2]

    @z.setter
    def z(self, value):
        """ 
        Sets value of z coordinate of 3D point.
        ----------------------------------------
        :param value: int or float
        ----------------------------------------
        :returns : 
        """
        self.value= ((self.value)[0],(self.value)[1],value)

    def __add__(self, other):
        return self.__left_op(self, other, operator.add)
    
    def __sub__(self, other):
        return self.__left_op(self, other, operator.sub)

    def __mul__(self, other):
        return self.__left_op(self, other, operator.mul)

    if IS_PY3:
        def __truediv__(self, other):
            return self.__left_op(self, other, operator.truediv)
    else:
        def __truediv__(self, other):
            return self.__left_op(self, other, operator.div)

    def __neg__(self):
        return self.__left_op(self, -1, operator.mul)

    def __left_op(self, p1, p2, op):
        if isinstance(p2, (float, int)):
            return APoint(op(p1.x, p2), op(p1.y,p2), op(p1.z, p2))
        elif(op==operator.truediv ):
            if p2.x==0:
                return APoint(p1.x, op(p1.y,p2.y), op(p1.z, p2.z))
            elif p2.y==0:
                return APoint(op(p1.x, p2.x),p1.y, op(p1.z, p2.z))
            elif p2.z==0:
                return APoint(op(p1.x, p2.x), op(p1.y,p2.y), p1.z)
        return APoint(op(p1.x, p2.x), op(p1.y, p2.y), op(p1.z, p2.z))

    def __iop(self, p2, op):
        if isinstance(p2, (float, int)):
            self.x = op(self.x, p2)
            self.y = op(self.y, p2)
            self.z = op(self.z, p2)
        else:
            self.x= op(self.x, p2.x)
            self.y= op(self.y, p2.y)
            self.z = op(self.z, p2.z)
        return self

    def __repr__(self):
        return self.value.__str__()

    def __str__(self):
        return 'APoint(%.2f, %.2f, %.2f)' % tuple(self.value)

    def __eq__(self, other):
        if isinstance(other,(float,int)):
            return False
        return self.x==other.x and self.y==other.y and self.z==other.z
    
    variant.x=x
    variant.y=y
    variant.z=z
    variant.__add__=__add__
    variant.__left_op=__left_op
    variant.__add__=__add__
    variant.__sub__=__sub__
    variant.__mul__=__mul__
    variant.__truediv__=__truediv__
    variant.__neg__=__neg__
    variant.__iop=__iop
    variant.__repr__=__repr__
    variant.__str__=__str__
    variant.__eq__=__eq__

def distance(p1, p2):
    """ 
    Returns distance between two points p1 and p2.
    ----------------------------------------------
    :param p1: APoint
    :param p2: APoint
    ----------------------------------------
    :returns : int or float
    """
    return math.sqrt((p1.x - p2.x) ** 2 +
                     (p1.y - p2.y) ** 2 +
                     (p1.z - p2.z) ** 2)

variant.distance=distance
PyPCAD.APoint=APoint
