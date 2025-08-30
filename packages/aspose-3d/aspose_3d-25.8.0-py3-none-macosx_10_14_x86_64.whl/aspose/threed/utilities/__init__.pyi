from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import aspose.threed
import aspose.threed.animation
import aspose.threed.deformers
import aspose.threed.entities
import aspose.threed.formats
import aspose.threed.formats.gltf
import aspose.threed.profiles
import aspose.threed.render
import aspose.threed.shading
import aspose.threed.utilities

class BoundingBox:
    '''The axis-aligned bounding box'''
    
    @overload
    def __init__(self, minimum : aspose.threed.utilities.Vector3, maximum : aspose.threed.utilities.Vector3) -> None:
        '''Initialize a finite bounding box with given minimum and maximum corner
        
        :param minimum: The minimum corner
        :param maximum: The maximum corner'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, min_x : float, min_y : float, min_z : float, max_x : float, max_y : float, max_z : float) -> None:
        '''Initialize a finite bounding box with given minimum and maximum corner
        
        :param min_x: The minimum corner\'s X
        :param min_y: The minimum corner\'s Y
        :param min_z: The minimum corner\'s Z
        :param max_x: The maximum corner\'s X
        :param max_y: The maximum corner\'s Y
        :param max_z: The maximum corner\'s Z'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def merge(self, pt : aspose.threed.utilities.Vector4) -> None:
        '''Merge current bounding box with given point
        
        :param pt: The point to be merged into the bounding box'''
        raise NotImplementedError()
    
    @overload
    def merge(self, pt : aspose.threed.utilities.Vector3) -> None:
        '''Merge current bounding box with given point
        
        :param pt: The point to be merged into the bounding box'''
        raise NotImplementedError()
    
    @overload
    def merge(self, x : float, y : float, z : float) -> None:
        '''Merge current bounding box with given point
        
        :param x: The point to be merged into the bounding box
        :param y: The point to be merged into the bounding box
        :param z: The point to be merged into the bounding box'''
        raise NotImplementedError()
    
    @overload
    def merge(self, bb : aspose.threed.utilities.BoundingBox) -> None:
        '''Merges the new box into the current bounding box.
        
        :param bb: The bounding box to merge'''
        raise NotImplementedError()
    
    @overload
    def contains(self, p : aspose.threed.utilities.Vector3) -> bool:
        '''Check if the point p is inside the bounding box
        
        :param p: The point to test
        :returns: True if the point is inside the bounding box'''
        raise NotImplementedError()
    
    @overload
    def contains(self, bbox : aspose.threed.utilities.BoundingBox) -> bool:
        '''The bounding box to check if it\'s inside current bounding box.'''
        raise NotImplementedError()
    
    def scale(self) -> float:
        '''Calculates the absolute largest coordinate value of any contained point.
        
        :returns: the calculated absolute largest coordinate value of any contained point.'''
        raise NotImplementedError()
    
    @staticmethod
    def from_geometry(geometry : aspose.threed.entities.Geometry) -> aspose.threed.utilities.BoundingBox:
        '''Construct a bounding box from given geometry
        
        :param geometry: The geometry to calculate bounding box
        :returns: The bounding box of given geometry'''
        raise NotImplementedError()
    
    def overlaps_with(self, box : aspose.threed.utilities.BoundingBox) -> bool:
        '''Check if current bounding box overlaps with specified bounding box.
        
        :param box: The other bounding box to test
        :returns: True if the current bounding box overlaps with the given one.'''
        raise NotImplementedError()
    
    @property
    def null(self) -> aspose.threed.utilities.BoundingBox:
        '''The null bounding box'''
        raise NotImplementedError()

    @property
    def infinite(self) -> aspose.threed.utilities.BoundingBox:
        '''The infinite bounding box'''
        raise NotImplementedError()

    @property
    def extent(self) -> aspose.threed.utilities.BoundingBoxExtent:
        '''Gets the extent of the bounding box.'''
        raise NotImplementedError()
    
    @property
    def minimum(self) -> aspose.threed.utilities.Vector3:
        '''The minimum corner of the bounding box'''
        raise NotImplementedError()
    
    @property
    def maximum(self) -> aspose.threed.utilities.Vector3:
        '''The maximum corner of the bounding box'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.threed.utilities.Vector3:
        '''The size of the bounding box'''
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.threed.utilities.Vector3:
        '''The center of the bounding box.'''
        raise NotImplementedError()
    

class BoundingBox2D:
    '''The axis-aligned bounding box for :py:class:`aspose.threed.utilities.Vector2`'''
    
    @overload
    def __init__(self, minimum : aspose.threed.utilities.Vector2, maximum : aspose.threed.utilities.Vector2) -> None:
        '''Initialize a finite bounding box with given minimum and maximum corner
        
        :param minimum: The minimum corner
        :param maximum: The maximum corner'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def merge(self, pt : aspose.threed.utilities.Vector2) -> None:
        '''Merges the new box into the current bounding box.
        
        :param pt: The point to merge'''
        raise NotImplementedError()
    
    @overload
    def merge(self, bb : aspose.threed.utilities.BoundingBox2D) -> None:
        '''Merges the new box into the current bounding box.
        
        :param bb: The bounding box to merge'''
        raise NotImplementedError()
    
    @property
    def extent(self) -> aspose.threed.utilities.BoundingBoxExtent:
        '''Gets the extent of the bounding box.'''
        raise NotImplementedError()
    
    @property
    def minimum(self) -> aspose.threed.utilities.Vector2:
        '''The minimum corner of the bounding box'''
        raise NotImplementedError()
    
    @property
    def maximum(self) -> aspose.threed.utilities.Vector2:
        '''The maximum corner of the bounding box'''
        raise NotImplementedError()
    
    @property
    def NULL(self) -> aspose.threed.utilities.BoundingBox2D:
        '''The null bounding box'''
        raise NotImplementedError()

    @property
    def INFINITE(self) -> aspose.threed.utilities.BoundingBox2D:
        '''The infinite bounding box'''
        raise NotImplementedError()


class FMatrix4:
    '''Matrix 4x4 with all component in float type'''
    
    @overload
    def __init__(self, m00 : float, m01 : float, m02 : float, m03 : float, m10 : float, m11 : float, m12 : float, m13 : float, m20 : float, m21 : float, m22 : float, m23 : float, m30 : float, m31 : float, m32 : float, m33 : float) -> None:
        '''Initialize the instance of :py:class:`aspose.threed.utilities.FMatrix4`
        
        :param m00: The m[0, 0]
        :param m01: The m[0, 1]
        :param m02: The m[0, 2]
        :param m03: The m[0, 3]
        :param m10: The m[1, 0]
        :param m11: The m[1, 1]
        :param m12: The m[1, 2]
        :param m13: The m[1, 3]
        :param m20: The m[2, 0]
        :param m21: The m[2, 1]
        :param m22: The m[2, 2]
        :param m23: The m[2, 3]
        :param m30: The m[3, 0]
        :param m31: The m[3, 1]
        :param m32: The m[3, 2]
        :param m33: The m[3, 3]'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, mat : aspose.threed.utilities.Matrix4) -> None:
        '''Initialize the instance of :py:class:`aspose.threed.utilities.FMatrix4` from a :py:class:`aspose.threed.utilities.Matrix4` instance.
        
        :param mat: The :py:class:`aspose.threed.utilities.Matrix4` instance.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, r0 : aspose.threed.utilities.FVector4, r1 : aspose.threed.utilities.FVector4, r2 : aspose.threed.utilities.FVector4, r3 : aspose.threed.utilities.FVector4) -> None:
        '''Constructs matrix from 4 rows.
        
        :param r0: R0.
        :param r1: R1.
        :param r2: R2.
        :param r3: R3.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def concatenate(self, m2 : aspose.threed.utilities.FMatrix4) -> aspose.threed.utilities.FMatrix4:
        '''Concatenates the two matrices
        
        :param m2: M2.
        :returns: New matrix4'''
        raise NotImplementedError()
    
    @overload
    def concatenate(self, m2 : aspose.threed.utilities.Matrix4) -> aspose.threed.utilities.FMatrix4:
        '''Concatenates the two matrices
        
        :param m2: M2.
        :returns: New matrix4'''
        raise NotImplementedError()
    
    def transpose(self) -> aspose.threed.utilities.FMatrix4:
        '''Transposes this instance.
        
        :returns: The transposed matrix.'''
        raise NotImplementedError()
    
    def inverse(self) -> aspose.threed.utilities.FMatrix4:
        '''Calculate the inverse matrix of current instance.
        
        :returns: Inverse matrix4'''
        raise NotImplementedError()
    
    @property
    def identity(self) -> aspose.threed.utilities.FMatrix4:
        '''The identity matrix'''
        raise NotImplementedError()

    @property
    def m00(self) -> float:
        '''The m00.'''
        raise NotImplementedError()
    
    @m00.setter
    def m00(self, value : float) -> None:
        '''The m00.'''
        raise NotImplementedError()
    
    @property
    def m01(self) -> float:
        '''The m01.'''
        raise NotImplementedError()
    
    @m01.setter
    def m01(self, value : float) -> None:
        '''The m01.'''
        raise NotImplementedError()
    
    @property
    def m02(self) -> float:
        '''The m02.'''
        raise NotImplementedError()
    
    @m02.setter
    def m02(self, value : float) -> None:
        '''The m02.'''
        raise NotImplementedError()
    
    @property
    def m03(self) -> float:
        '''The m03.'''
        raise NotImplementedError()
    
    @m03.setter
    def m03(self, value : float) -> None:
        '''The m03.'''
        raise NotImplementedError()
    
    @property
    def m10(self) -> float:
        '''The m10.'''
        raise NotImplementedError()
    
    @m10.setter
    def m10(self, value : float) -> None:
        '''The m10.'''
        raise NotImplementedError()
    
    @property
    def m11(self) -> float:
        '''The m11.'''
        raise NotImplementedError()
    
    @m11.setter
    def m11(self, value : float) -> None:
        '''The m11.'''
        raise NotImplementedError()
    
    @property
    def m12(self) -> float:
        '''The m12.'''
        raise NotImplementedError()
    
    @m12.setter
    def m12(self, value : float) -> None:
        '''The m12.'''
        raise NotImplementedError()
    
    @property
    def m13(self) -> float:
        '''The m13.'''
        raise NotImplementedError()
    
    @m13.setter
    def m13(self, value : float) -> None:
        '''The m13.'''
        raise NotImplementedError()
    
    @property
    def m20(self) -> float:
        '''The m20.'''
        raise NotImplementedError()
    
    @m20.setter
    def m20(self, value : float) -> None:
        '''The m20.'''
        raise NotImplementedError()
    
    @property
    def m21(self) -> float:
        '''The m21.'''
        raise NotImplementedError()
    
    @m21.setter
    def m21(self, value : float) -> None:
        '''The m21.'''
        raise NotImplementedError()
    
    @property
    def m22(self) -> float:
        '''The m22.'''
        raise NotImplementedError()
    
    @m22.setter
    def m22(self, value : float) -> None:
        '''The m22.'''
        raise NotImplementedError()
    
    @property
    def m23(self) -> float:
        '''The m23.'''
        raise NotImplementedError()
    
    @m23.setter
    def m23(self, value : float) -> None:
        '''The m23.'''
        raise NotImplementedError()
    
    @property
    def m30(self) -> float:
        '''The m30.'''
        raise NotImplementedError()
    
    @m30.setter
    def m30(self, value : float) -> None:
        '''The m30.'''
        raise NotImplementedError()
    
    @property
    def m31(self) -> float:
        '''The m31.'''
        raise NotImplementedError()
    
    @m31.setter
    def m31(self, value : float) -> None:
        '''The m31.'''
        raise NotImplementedError()
    
    @property
    def m32(self) -> float:
        '''The m32.'''
        raise NotImplementedError()
    
    @m32.setter
    def m32(self, value : float) -> None:
        '''The m32.'''
        raise NotImplementedError()
    
    @property
    def m33(self) -> float:
        '''The m33.'''
        raise NotImplementedError()
    
    @m33.setter
    def m33(self, value : float) -> None:
        '''The m33.'''
        raise NotImplementedError()
    

class FVector2:
    '''A float vector with two components.'''
    
    @overload
    def __init__(self, x : float, y : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector2`.
        
        :param x: X component of the vector
        :param y: Y component of the vector'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector2) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector2`.
        
        :param vec: Vector2 in double type'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def equals(self, rhs : aspose.threed.utilities.FVector2) -> bool:
        '''Check if two vectors are equal
        
        :returns: True if all components are equal.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    

class FVector3:
    '''A float vector with three components.'''
    
    @overload
    def __init__(self, x : float, y : float, z : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector3`.
        
        :param x: X component of the vector
        :param y: Y component of the vector
        :param z: Z component of the vector'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector3) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector3`.
        
        :param vec: Vector3 in double type'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector4) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.
        
        :param vec: Vector4 in double type'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def normalize(self) -> aspose.threed.utilities.FVector3:
        '''Normalizes this instance.
        
        :returns: Normalized vector.'''
        raise NotImplementedError()
    
    def cross(self, rhs : aspose.threed.utilities.FVector3) -> aspose.threed.utilities.FVector3:
        '''Cross product of two vectors
        
        :param rhs: Right hand side value.
        :returns: Cross product of two :py:class:`aspose.threed.utilities.FVector3`s.'''
        raise NotImplementedError()
    
    @property
    def zero(self) -> aspose.threed.utilities.FVector3:
        '''The Zero vector.'''
        raise NotImplementedError()

    @property
    def one(self) -> aspose.threed.utilities.FVector3:
        '''The unit scale vector with all components are all 1'''
        raise NotImplementedError()

    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    
    @property
    def z(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    

class FVector4:
    '''A float vector with four components.'''
    
    @overload
    def __init__(self, x : float, y : float, z : float, w : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.
        
        :param x: X component
        :param y: Y component
        :param z: Z component
        :param w: W component'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, x : float, y : float, z : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.
        
        :param x: X component
        :param y: Y component
        :param z: Z component'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector4) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector3) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector3, w : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.FVector4`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    
    @property
    def z(self) -> float:
        '''The z component.'''
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : float) -> None:
        '''The z component.'''
        raise NotImplementedError()
    
    @property
    def w(self) -> float:
        '''The w component.'''
        raise NotImplementedError()
    
    @w.setter
    def w(self, value : float) -> None:
        '''The w component.'''
        raise NotImplementedError()
    

class FileSystem:
    '''File system encapsulation.
    Aspose.3D will use this to read/write dependencies.'''
    
    @overload
    @staticmethod
    def create_zip_file_system(stream : io._IOBase, base_dir : str) -> aspose.threed.utilities.FileSystem:
        '''Create a file system to provide to the read-only access to speicified zip file or zip stream.
        File system will be disposed after the open/save operation.
        
        :param stream: The stream to access the zip file
        :param base_dir: The base directory inside the zip file.
        :returns: A zip file system'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create_zip_file_system(file_name : str) -> aspose.threed.utilities.FileSystem:
        '''File system to provide to the read-only access to speicified zip file or zip stream.
        File system will be disposed after the open/save operation.
        
        :param file_name: File name to the zip file.
        :returns: A zip file system'''
        raise NotImplementedError()
    
    def read_file(self, file_name : str, options : aspose.threed.formats.IOConfig) -> io._IOBase:
        '''Create a stream for reading dependencies.
        
        :param file_name: File\'s name to open for reading
        :param options: Save or load options
        :returns: Stream for reading the file.'''
        raise NotImplementedError()
    
    def write_file(self, file_name : str, options : aspose.threed.formats.IOConfig) -> io._IOBase:
        '''Create a stream for writing dependencies.
        
        :param file_name: The file\'s name to open for writing
        :param options: Save or load options
        :returns: Stream for writing the file'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local_file_system(directory : str) -> aspose.threed.utilities.FileSystem:
        '''Initialize a new :py:class:`aspose.threed.utilities.FileSystem` that only access local directory.
        All file read/write on this FileSystem instance will be mapped to specified directory.
        
        :param directory: The directory in your physical file system as the virtual root directory.
        :returns: A new instance of file system to provide local file access'''
        raise NotImplementedError()
    
    @staticmethod
    def create_dummy_file_system() -> aspose.threed.utilities.FileSystem:
        '''Create a dummy file system, read/write operations are dummy operations.
        
        :returns: A dummy file system'''
        raise NotImplementedError()
    

class IOExtension:
    '''Utilities to write matrix/vector to binary writer'''
    

class MathUtils:
    '''A set of useful mathematical utilities.'''
    
    @overload
    @staticmethod
    def to_degree(radian : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Vector3:
        '''Convert a :py:class:`aspose.threed.utilities.Vector3` from radian to degree.
        
        :param radian: The radian value.
        :returns: The degree value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_degree(radian : float) -> float:
        '''Convert a number from radian to degree
        
        :param radian: The radian value.
        :returns: The degree value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_degree(radian : float) -> float:
        '''Convert a number from radian to degree
        
        :param radian: The radian value.
        :returns: The degree value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_degree(x : float, y : float, z : float) -> aspose.threed.utilities.Vector3:
        '''Convert a number from radian to degree
        
        :param x: The x component in radian value.
        :param y: The y component in radian value.
        :param z: The z component in radian value.
        :returns: The degree value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_radian(degree : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Vector3:
        '''Convert a :py:class:`aspose.threed.utilities.Vector3` from degree to radian
        
        :param degree: The degree value.
        :returns: The radian value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_radian(degree : float) -> float:
        '''Convert a number from degree to radian
        
        :param degree: The degree value.
        :returns: The radian value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_radian(degree : float) -> float:
        '''Convert a number from degree to radian
        
        :param degree: The degree value.
        :returns: The radian value.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def to_radian(x : float, y : float, z : float) -> aspose.threed.utilities.Vector3:
        '''Convert a vector from degree to radian
        
        :param x: The x component in degree value.
        :param y: The y component in degree value.
        :param z: The z component in degree value.
        :returns: The radian value.'''
        raise NotImplementedError()
    
    @staticmethod
    def calc_normal(points : List[aspose.threed.utilities.Vector3]) -> aspose.threed.utilities.Vector3:
        raise NotImplementedError()
    
    @staticmethod
    def find_intersection(p0 : aspose.threed.utilities.Vector2, d0 : aspose.threed.utilities.Vector2, p1 : aspose.threed.utilities.Vector2, d1 : aspose.threed.utilities.Vector2, results : List[aspose.threed.utilities.Vector2]) -> int:
        raise NotImplementedError()
    
    @staticmethod
    def point_inside_triangle(p : aspose.threed.utilities.Vector2, p0 : aspose.threed.utilities.Vector2, p1 : aspose.threed.utilities.Vector2, p2 : aspose.threed.utilities.Vector2) -> bool:
        '''Check if point p is inside triangle (p0, p1, p2)'''
        raise NotImplementedError()
    
    @staticmethod
    def ray_intersect(origin : aspose.threed.utilities.Vector2, dir : aspose.threed.utilities.Vector2, a : aspose.threed.utilities.Vector2, b : aspose.threed.utilities.Vector2) -> System.Nullable`1[[Aspose.ThreeD.Utilities.Vector2]]:
        '''Check if ray (origin, dir) intersects with line segment(start, end)'''
        raise NotImplementedError()
    
    @staticmethod
    def clamp(val : float, min : float, max : float) -> float:
        '''Clamp value to range [min, max]
        
        :param val: Value to clamp.
        :param min: Minimum value.
        :param max: Maximum value.
        :returns: The value between [min, max]'''
        raise NotImplementedError()
    

class Matrix4:
    '''4x4 matrix implementation.'''
    
    @overload
    def __init__(self, r0 : aspose.threed.utilities.Vector4, r1 : aspose.threed.utilities.Vector4, r2 : aspose.threed.utilities.Vector4, r3 : aspose.threed.utilities.Vector4) -> None:
        '''Constructs matrix from 4 rows.
        
        :param r0: R0.
        :param r1: R1.
        :param r2: R2.
        :param r3: R3.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, m00 : float, m01 : float, m02 : float, m03 : float, m10 : float, m11 : float, m12 : float, m13 : float, m20 : float, m21 : float, m22 : float, m23 : float, m30 : float, m31 : float, m32 : float, m33 : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Matrix4` struct.
        
        :param m00: M00.
        :param m01: M01.
        :param m02: M02.
        :param m03: M03.
        :param m10: M10.
        :param m11: M11.
        :param m12: M12.
        :param m13: M13.
        :param m20: M20.
        :param m21: M21.
        :param m22: M22.
        :param m23: M23.
        :param m30: M30.
        :param m31: M31.
        :param m32: M32.
        :param m33: M33.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, m : aspose.threed.utilities.FMatrix4) -> None:
        '''Construct :py:class:`aspose.threed.utilities.Matrix4` from an :py:class:`aspose.threed.utilities.FMatrix4` instance'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, m : List[float]) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Matrix4` struct.
        
        :param m: M.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def translate(t : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Matrix4:
        '''Creates a matrix that translates along the x-axis, the y-axis and the z-axis
        
        :param t: Translate offset'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def translate(tx : float, ty : float, tz : float) -> aspose.threed.utilities.Matrix4:
        '''Creates a matrix that translates along the x-axis, the y-axis and the z-axis
        
        :param tx: X-coordinate offset
        :param ty: Y-coordinate offset
        :param tz: Z-coordinate offset'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def scale(s : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Matrix4:
        '''Creates a matrix that scales along the x-axis, the y-axis and the z-axis.
        
        :param s: Scaling factories applies to the x-axis, the y-axis and the z-axis'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def scale(s : float) -> aspose.threed.utilities.Matrix4:
        '''Creates a matrix that scales along the x-axis, the y-axis and the z-axis.
        
        :param s: Scaling factories applies to all axex'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def scale(sx : float, sy : float, sz : float) -> aspose.threed.utilities.Matrix4:
        '''Creates a matrix that scales along the x-axis, the y-axis and the z-axis.
        
        :param sx: Scaling factories applies to the x-axis
        :param sy: Scaling factories applies to the y-axis
        :param sz: Scaling factories applies to the z-axis'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def rotate_from_euler(eul : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Matrix4:
        '''Create a rotation matrix from Euler angle
        
        :param eul: Rotation in radian'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def rotate_from_euler(rx : float, ry : float, rz : float) -> aspose.threed.utilities.Matrix4:
        '''Create a rotation matrix from Euler angle
        
        :param rx: Rotation in x axis in radian
        :param ry: Rotation in y axis in radian
        :param rz: Rotation in z axis in radian'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def rotate(angle : float, axis : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Matrix4:
        '''Create a rotation matrix by rotation angle and axis
        
        :param angle: Rotate angle in radian
        :param axis: Rotation axis'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def rotate(q : aspose.threed.utilities.Quaternion) -> aspose.threed.utilities.Matrix4:
        '''Create a rotation matrix from a quaternion
        
        :param q: Rotation quaternion'''
        raise NotImplementedError()
    
    def concatenate(self, m2 : aspose.threed.utilities.Matrix4) -> aspose.threed.utilities.Matrix4:
        '''Concatenates the two matrices
        
        :param m2: M2.
        :returns: New matrix4'''
        raise NotImplementedError()
    
    def transpose(self) -> aspose.threed.utilities.Matrix4:
        '''Transposes this instance.
        
        :returns: The transposed matrix.'''
        raise NotImplementedError()
    
    def normalize(self) -> aspose.threed.utilities.Matrix4:
        '''Normalizes this instance.
        
        :returns: Normalize matrix4'''
        raise NotImplementedError()
    
    def inverse(self) -> aspose.threed.utilities.Matrix4:
        '''Inverses this instance.
        
        :returns: Inverse matrix4'''
        raise NotImplementedError()
    
    def set_trs(self, translation : aspose.threed.utilities.Vector3, rotation : aspose.threed.utilities.Vector3, scale : aspose.threed.utilities.Vector3) -> None:
        '''Initializes the matrix with translation/rotation/scale
        
        :param translation: Translation.
        :param rotation: Euler angles for rotation, fields are in degree.
        :param scale: Scale.'''
        raise NotImplementedError()
    
    def to_array(self) -> List[float]:
        '''Converts matrix to array.
        
        :returns: The array.'''
        raise NotImplementedError()
    
    def decompose(self, translation : List[aspose.threed.utilities.Vector3], scaling : List[aspose.threed.utilities.Vector3], rotation : List[aspose.threed.utilities.Quaternion]) -> bool:
        raise NotImplementedError()
    
    @property
    def identity(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the identity matrix.'''
        raise NotImplementedError()

    @property
    def determinant(self) -> float:
        '''Gets the determinant of the matrix.'''
        raise NotImplementedError()
    
    @property
    def m00(self) -> float:
        '''The m00.'''
        raise NotImplementedError()
    
    @m00.setter
    def m00(self, value : float) -> None:
        '''The m00.'''
        raise NotImplementedError()
    
    @property
    def m01(self) -> float:
        '''The m01.'''
        raise NotImplementedError()
    
    @m01.setter
    def m01(self, value : float) -> None:
        '''The m01.'''
        raise NotImplementedError()
    
    @property
    def m02(self) -> float:
        '''The m02.'''
        raise NotImplementedError()
    
    @m02.setter
    def m02(self, value : float) -> None:
        '''The m02.'''
        raise NotImplementedError()
    
    @property
    def m03(self) -> float:
        '''The m03.'''
        raise NotImplementedError()
    
    @m03.setter
    def m03(self, value : float) -> None:
        '''The m03.'''
        raise NotImplementedError()
    
    @property
    def m10(self) -> float:
        '''The m10.'''
        raise NotImplementedError()
    
    @m10.setter
    def m10(self, value : float) -> None:
        '''The m10.'''
        raise NotImplementedError()
    
    @property
    def m11(self) -> float:
        '''The m11.'''
        raise NotImplementedError()
    
    @m11.setter
    def m11(self, value : float) -> None:
        '''The m11.'''
        raise NotImplementedError()
    
    @property
    def m12(self) -> float:
        '''The m12.'''
        raise NotImplementedError()
    
    @m12.setter
    def m12(self, value : float) -> None:
        '''The m12.'''
        raise NotImplementedError()
    
    @property
    def m13(self) -> float:
        '''The m13.'''
        raise NotImplementedError()
    
    @m13.setter
    def m13(self, value : float) -> None:
        '''The m13.'''
        raise NotImplementedError()
    
    @property
    def m20(self) -> float:
        '''The m20.'''
        raise NotImplementedError()
    
    @m20.setter
    def m20(self, value : float) -> None:
        '''The m20.'''
        raise NotImplementedError()
    
    @property
    def m21(self) -> float:
        '''The m21.'''
        raise NotImplementedError()
    
    @m21.setter
    def m21(self, value : float) -> None:
        '''The m21.'''
        raise NotImplementedError()
    
    @property
    def m22(self) -> float:
        '''The m22.'''
        raise NotImplementedError()
    
    @m22.setter
    def m22(self, value : float) -> None:
        '''The m22.'''
        raise NotImplementedError()
    
    @property
    def m23(self) -> float:
        '''The m23.'''
        raise NotImplementedError()
    
    @m23.setter
    def m23(self, value : float) -> None:
        '''The m23.'''
        raise NotImplementedError()
    
    @property
    def m30(self) -> float:
        '''The m30.'''
        raise NotImplementedError()
    
    @m30.setter
    def m30(self, value : float) -> None:
        '''The m30.'''
        raise NotImplementedError()
    
    @property
    def m31(self) -> float:
        '''The m31.'''
        raise NotImplementedError()
    
    @m31.setter
    def m31(self, value : float) -> None:
        '''The m31.'''
        raise NotImplementedError()
    
    @property
    def m32(self) -> float:
        '''The m32.'''
        raise NotImplementedError()
    
    @m32.setter
    def m32(self, value : float) -> None:
        '''The m32.'''
        raise NotImplementedError()
    
    @property
    def m33(self) -> float:
        '''The m33.'''
        raise NotImplementedError()
    
    @m33.setter
    def m33(self, value : float) -> None:
        '''The m33.'''
        raise NotImplementedError()
    

class ParseException:
    '''Exception when Aspose.3D failed to parse the input.'''
    
    def __init__(self, msg : str) -> None:
        '''Constructor of :py:class:`aspose.threed.utilities.ParseException`'''
        raise NotImplementedError()
    

class Quaternion:
    '''Quaternion is usually used to perform rotation in computer graphics.'''
    
    @overload
    def __init__(self, w : float, x : float, y : float, z : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Quaternion` class.
        
        :param w: w component of the quaternion
        :param x: x component of the quaternion
        :param y: y component of the quaternion
        :param z: z component of the quaternion'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_euler_angle(pitch : float, yaw : float, roll : float) -> aspose.threed.utilities.Quaternion:
        '''Creates quaternion from given Euler angle
        
        :param pitch: Pitch in radian
        :param yaw: Yaw in radian
        :param roll: Roll in radian
        :returns: Created quaternion'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_euler_angle(euler_angle : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Quaternion:
        '''Creates quaternion from given Euler angle
        
        :param euler_angle: Euler angle in radian
        :returns: Created quaternion'''
        raise NotImplementedError()
    
    @overload
    def to_matrix(self) -> aspose.threed.utilities.Matrix4:
        '''Convert the rotation presented by quaternion to transform matrix.
        
        :returns: The matrix representation of current quaternion.'''
        raise NotImplementedError()
    
    @overload
    def to_matrix(self, translation : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Matrix4:
        '''Convert the rotation presented by quaternion to transform matrix.
        
        :param translation: The translation part of the matrix.
        :returns: The matrix representation of current quaternion.'''
        raise NotImplementedError()
    
    def conjugate(self) -> aspose.threed.utilities.Quaternion:
        '''Returns a conjugate quaternion of current quaternion
        
        :returns: The conjugate quaternion.'''
        raise NotImplementedError()
    
    def inverse(self) -> aspose.threed.utilities.Quaternion:
        '''Returns a inverse quaternion of current quaternion
        
        :returns: Inverse quaternion.'''
        raise NotImplementedError()
    
    def dot(self, q : aspose.threed.utilities.Quaternion) -> float:
        '''Dots product
        
        :param q: The quaternion
        :returns: Dot value'''
        raise NotImplementedError()
    
    def euler_angles(self) -> aspose.threed.utilities.Vector3:
        '''Converts quaternion to rotation represented by Euler angles
        All components are in radian
        
        :returns: Result vector'''
        raise NotImplementedError()
    
    def normalize(self) -> aspose.threed.utilities.Quaternion:
        '''Normalize the quaternion
        
        :returns: Normalized quaternion.'''
        raise NotImplementedError()
    
    def to_angle_axis(self, angle : List[float], axis : List[aspose.threed.utilities.Vector3]) -> None:
        raise NotImplementedError()
    
    def concat(self, rhs : aspose.threed.utilities.Quaternion) -> aspose.threed.utilities.Quaternion:
        '''Concatenate two quaternions'''
        raise NotImplementedError()
    
    @staticmethod
    def from_angle_axis(a : float, axis : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Quaternion:
        '''Creates a quaternion around given axis and rotate in clockwise
        
        :param a: Clockwise rotation in radian
        :param axis: Axis
        :returns: Created quaternion'''
        raise NotImplementedError()
    
    @staticmethod
    def from_rotation(orig : aspose.threed.utilities.Vector3, dest : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Quaternion:
        '''Creates a quaternion that rotate from original to destination direction
        
        :param orig: Original direction
        :param dest: Destination direction
        :returns: Created quaternion'''
        raise NotImplementedError()
    
    @staticmethod
    def interpolate(t : float, from_address : aspose.threed.utilities.Quaternion, to : aspose.threed.utilities.Quaternion) -> aspose.threed.utilities.Quaternion:
        '''Populates this quaternion with the interpolated value between the given quaternion arguments for a t between from and to.
        
        :param t: The coefficient to interpolate.
        :param from_address: Source quaternion.
        :param to: Target quaternion.
        :returns: The interpolated quaternion.'''
        raise NotImplementedError()
    
    @staticmethod
    def slerp(t : float, v1 : aspose.threed.utilities.Quaternion, v2 : aspose.threed.utilities.Quaternion) -> aspose.threed.utilities.Quaternion:
        '''Perform spherical linear interpolation between two values
        
        :param t: t is between 0 to 1
        :param v1: First value
        :param v2: Second value'''
        raise NotImplementedError()
    
    @property
    def length(self) -> float:
        '''Gets the length of the quaternion'''
        raise NotImplementedError()
    
    @property
    def IDENTITY(self) -> aspose.threed.utilities.Quaternion:
        '''The Identity quaternion.'''
        raise NotImplementedError()

    @property
    def w(self) -> float:
        '''The w component.'''
        raise NotImplementedError()
    
    @w.setter
    def w(self, value : float) -> None:
        '''The w component.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    
    @property
    def z(self) -> float:
        '''The z component.'''
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : float) -> None:
        '''The z component.'''
        raise NotImplementedError()
    

class Rect:
    '''A class to represent the rectangle'''
    
    @overload
    def __init__(self, x : int, y : int, width : int, height : int) -> None:
        '''Constructor of class :py:class:`aspose.threed.utilities.Rect`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def contains(self, x : int, y : int) -> bool:
        '''Return true if the given point is inside the rectangle.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of the size'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Sets the width of the size'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of the size'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Sets the height of the size'''
        raise NotImplementedError()
    
    @property
    def x(self) -> int:
        '''Gets the x of the size'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : int) -> None:
        '''Sets the x of the size'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''Gets the y of the size'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : int) -> None:
        '''Sets the y of the size'''
        raise NotImplementedError()
    
    @property
    def left(self) -> int:
        '''Gets the left of the rectangle'''
        raise NotImplementedError()
    
    @property
    def right(self) -> int:
        '''Gets the right of the rectangle'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''Gets the top of the rectangle'''
        raise NotImplementedError()
    
    @property
    def bottom(self) -> int:
        '''Gets the bottom of the rectangle'''
        raise NotImplementedError()
    

class RelativeRectangle:
    '''Relative rectangle
    The formula between relative component to absolute value is:
    Scale * (Reference Width) + offset
    So if we want it to represent an absolute value, leave all scale fields zero, and use offset fields instead.'''
    
    @overload
    def __init__(self, left : int, top : int, width : int, height : int) -> None:
        '''Construct a :py:class:`aspose.threed.utilities.RelativeRectangle`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def to_absolute(self, left : int, top : int, width : int, height : int) -> aspose.threed.utilities.Rect:
        '''Convert the relative rectangle to absolute rectangle
        
        :param left: Left of the rectangle
        :param top: Top of the rectangle
        :param width: Width of the rectangle
        :param height: Height of the rectangle'''
        raise NotImplementedError()
    
    @staticmethod
    def from_scale(scale_x : float, scale_y : float, scale_width : float, scale_height : float) -> aspose.threed.utilities.RelativeRectangle:
        '''Construct a :py:class:`aspose.threed.utilities.RelativeRectangle` with all offset fields zero and scale fields from given parameters.'''
        raise NotImplementedError()
    
    @property
    def scale_x(self) -> float:
        '''Relative coordinate X'''
        raise NotImplementedError()
    
    @scale_x.setter
    def scale_x(self, value : float) -> None:
        '''Relative coordinate X'''
        raise NotImplementedError()
    
    @property
    def scale_y(self) -> float:
        '''Relative coordinate Y'''
        raise NotImplementedError()
    
    @scale_y.setter
    def scale_y(self, value : float) -> None:
        '''Relative coordinate Y'''
        raise NotImplementedError()
    
    @property
    def scale_width(self) -> float:
        '''Relative width'''
        raise NotImplementedError()
    
    @scale_width.setter
    def scale_width(self, value : float) -> None:
        '''Relative width'''
        raise NotImplementedError()
    
    @property
    def scale_height(self) -> float:
        '''Relative height'''
        raise NotImplementedError()
    
    @scale_height.setter
    def scale_height(self, value : float) -> None:
        '''Relative height'''
        raise NotImplementedError()
    
    @property
    def offset_x(self) -> int:
        '''Gets the offset for coordinate X'''
        raise NotImplementedError()
    
    @offset_x.setter
    def offset_x(self, value : int) -> None:
        '''Sets the offset for coordinate X'''
        raise NotImplementedError()
    
    @property
    def offset_y(self) -> int:
        '''Gets the offset for coordinate Y'''
        raise NotImplementedError()
    
    @offset_y.setter
    def offset_y(self, value : int) -> None:
        '''Sets the offset for coordinate Y'''
        raise NotImplementedError()
    
    @property
    def offset_width(self) -> int:
        '''Gets the offset for width'''
        raise NotImplementedError()
    
    @offset_width.setter
    def offset_width(self, value : int) -> None:
        '''Sets the offset for width'''
        raise NotImplementedError()
    
    @property
    def offset_height(self) -> int:
        '''Gets the offset for height'''
        raise NotImplementedError()
    
    @offset_height.setter
    def offset_height(self, value : int) -> None:
        '''Sets the offset for height'''
        raise NotImplementedError()
    

class SemanticAttribute:
    '''Allow user to use their own structure for static declaration of :py:class:`aspose.threed.utilities.VertexDeclaration`'''
    
    @overload
    def __init__(self, semantic : aspose.threed.utilities.VertexFieldSemantic) -> None:
        '''Initialize a :py:class:`aspose.threed.utilities.SemanticAttribute`
        
        :param semantic: The semantic of the struct\'s field.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, semantic : aspose.threed.utilities.VertexFieldSemantic, alias : str) -> None:
        '''Initialize a :py:class:`aspose.threed.utilities.SemanticAttribute`
        
        :param semantic: The semantic of the struct\'s field.
        :param alias: Alias of the field.'''
        raise NotImplementedError()
    
    @property
    def semantic(self) -> aspose.threed.utilities.VertexFieldSemantic:
        '''Semantic of the vertex field'''
        raise NotImplementedError()
    
    @property
    def alias(self) -> str:
        '''Alias of the vertex field'''
        raise NotImplementedError()
    

class TransformBuilder:
    '''The :py:class:`aspose.threed.utilities.TransformBuilder` is used to build transform matrix by a chain of transformations.'''
    
    @overload
    def __init__(self, initial : aspose.threed.utilities.Matrix4, order : aspose.threed.utilities.ComposeOrder) -> None:
        '''Construct a :py:class:`aspose.threed.utilities.TransformBuilder` with initial transform matrix and specified compose order'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, order : aspose.threed.utilities.ComposeOrder) -> None:
        '''Construct a :py:class:`aspose.threed.utilities.TransformBuilder` with initial identity transform matrix and specified compose order'''
        raise NotImplementedError()
    
    @overload
    def scale(self, s : float) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a scaling transform matrix with a component scaled by s'''
        raise NotImplementedError()
    
    @overload
    def scale(self, x : float, y : float, z : float) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a scaling transform matrix'''
        raise NotImplementedError()
    
    @overload
    def scale(self, s : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a scale transform'''
        raise NotImplementedError()
    
    @overload
    def rotate_degree(self, angle : float, axis : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation transform in degree
        
        :param angle: The angle to rotate in degree
        :param axis: The axis to rotate'''
        raise NotImplementedError()
    
    @overload
    def rotate_degree(self, rot : aspose.threed.utilities.Vector3, order : aspose.threed.utilities.RotationOrder) -> None:
        '''Append rotation with specified order
        
        :param rot: Rotation in degrees'''
        raise NotImplementedError()
    
    @overload
    def rotate_radian(self, angle : float, axis : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation transform in radian
        
        :param angle: The angle to rotate in radian
        :param axis: The axis to rotate'''
        raise NotImplementedError()
    
    @overload
    def rotate_radian(self, rot : aspose.threed.utilities.Vector3, order : aspose.threed.utilities.RotationOrder) -> None:
        '''Append rotation with specified order
        
        :param rot: Rotation in radian'''
        raise NotImplementedError()
    
    @overload
    def rotate_euler_radian(self, x : float, y : float, z : float) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation by Euler angles in radian'''
        raise NotImplementedError()
    
    @overload
    def rotate_euler_radian(self, r : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation by Euler angles in radian'''
        raise NotImplementedError()
    
    @overload
    def translate(self, tx : float, ty : float, tz : float) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a translation transform'''
        raise NotImplementedError()
    
    @overload
    def translate(self, v : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a translation transform'''
        raise NotImplementedError()
    
    def compose(self, m : aspose.threed.utilities.Matrix4) -> None:
        '''Append or prepend the argument to internal matrix.'''
        raise NotImplementedError()
    
    def append(self, m : aspose.threed.utilities.Matrix4) -> aspose.threed.utilities.TransformBuilder:
        '''Append the new transform matrix to the transform chain.'''
        raise NotImplementedError()
    
    def prepend(self, m : aspose.threed.utilities.Matrix4) -> aspose.threed.utilities.TransformBuilder:
        '''Prepend the new transform matrix to the transform chain.'''
        raise NotImplementedError()
    
    def rearrange(self, new_x : aspose.threed.Axis, new_y : aspose.threed.Axis, new_z : aspose.threed.Axis) -> aspose.threed.utilities.TransformBuilder:
        '''Rearrange the layout of the axis.
        
        :param new_x: The new x component source
        :param new_y: The new y component source
        :param new_z: The new z component source'''
        raise NotImplementedError()
    
    def rotate(self, q : aspose.threed.utilities.Quaternion) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation by a quaternion'''
        raise NotImplementedError()
    
    def rotate_euler_degree(self, deg_x : float, deg_y : float, deg_z : float) -> aspose.threed.utilities.TransformBuilder:
        '''Chain a rotation by Euler angles in degree'''
        raise NotImplementedError()
    
    def reset(self) -> None:
        '''Reset the transform to identity matrix'''
        raise NotImplementedError()
    
    @property
    def matrix(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the current matrix value'''
        raise NotImplementedError()
    
    @matrix.setter
    def matrix(self, value : aspose.threed.utilities.Matrix4) -> None:
        '''Sets the current matrix value'''
        raise NotImplementedError()
    
    @property
    def compose_order(self) -> aspose.threed.utilities.ComposeOrder:
        '''Gets the chain compose order.'''
        raise NotImplementedError()
    
    @compose_order.setter
    def compose_order(self, value : aspose.threed.utilities.ComposeOrder) -> None:
        '''Sets the chain compose order.'''
        raise NotImplementedError()
    

class Vector2:
    '''A vector with two components.'''
    
    @overload
    def __init__(self, s : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector2` struct.
        
        :param s: S.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, s : aspose.threed.utilities.Vector3) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector2` struct.
        
        :param s: S.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.FVector2) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector2` struct.
        
        :param vec: Vector in float.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, x : float, y : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector2` struct.
        
        :param x: The x coordinate.
        :param y: The y coordinate.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def dot(self, rhs : aspose.threed.utilities.Vector2) -> float:
        '''Gets the dot product of two vectors
        
        :param rhs: Right hand side value.
        :returns: The dot product of the two vectors.'''
        raise NotImplementedError()
    
    def equals(self, rhs : aspose.threed.utilities.Vector2) -> bool:
        '''Check if two vector2 equals
        
        :param rhs: The right hand side value.
        :returns: True if all components are identically equal.'''
        raise NotImplementedError()
    
    def cross(self, v : aspose.threed.utilities.Vector2) -> float:
        '''Cross product of two vectors'''
        raise NotImplementedError()
    
    def normalize(self) -> aspose.threed.utilities.Vector2:
        '''Normalizes this instance.
        
        :returns: Normalized vector.'''
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.threed.utilities.Vector2) -> int:
        '''Compare current vector to another instance.'''
        raise NotImplementedError()
    
    @property
    def u(self) -> float:
        '''Gets the U component if the :py:class:`aspose.threed.utilities.Vector2` is used as a mapping coordinate.
        It\'s an alias of x component.'''
        raise NotImplementedError()
    
    @u.setter
    def u(self, value : float) -> None:
        '''Sets the U component if the :py:class:`aspose.threed.utilities.Vector2` is used as a mapping coordinate.
        It\'s an alias of x component.'''
        raise NotImplementedError()
    
    @property
    def v(self) -> float:
        '''Gets the V component if the :py:class:`aspose.threed.utilities.Vector2` is used as a mapping coordinate.
        It\'s an alias of y component.'''
        raise NotImplementedError()
    
    @v.setter
    def v(self, value : float) -> None:
        '''Sets the V component if the :py:class:`aspose.threed.utilities.Vector2` is used as a mapping coordinate.
        It\'s an alias of y component.'''
        raise NotImplementedError()
    
    @property
    def length(self) -> float:
        '''Gets the length.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    

class Vector3:
    '''A vector with three components.'''
    
    @overload
    def __init__(self, x : float, y : float, z : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector3` struct.
        
        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.FVector3) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector3` struct.
        
        :param vec: The x coordinate.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, v : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector3` struct.
        
        :param v: V.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec4 : aspose.threed.utilities.Vector4) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector3` struct.
        
        :param vec4: Vec4.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def angle_between(self, dir : aspose.threed.utilities.Vector3, up : aspose.threed.utilities.Vector3) -> float:
        '''Calculate the inner angle between two direction
        Two direction can be non-normalized vectors
        
        :param dir: The direction vector to compare with
        :param up: The up vector of the two direction\'s shared plane
        :returns: inner angle in radian'''
        raise NotImplementedError()
    
    @overload
    def angle_between(self, dir : aspose.threed.utilities.Vector3) -> float:
        '''Calculate the inner angle between two direction
        Two direction can be non-normalized vectors
        
        :param dir: The direction vector to compare with
        :returns: inner angle in radian'''
        raise NotImplementedError()
    
    def dot(self, rhs : aspose.threed.utilities.Vector3) -> float:
        '''Gets the dot product of two vectors
        
        :param rhs: Right hand side value.
        :returns: The dot product of the two vectors.'''
        raise NotImplementedError()
    
    def normalize(self) -> aspose.threed.utilities.Vector3:
        '''Normalizes this instance.
        
        :returns: Normalized vector.'''
        raise NotImplementedError()
    
    def sin(self) -> aspose.threed.utilities.Vector3:
        '''Calculates sine on each component
        
        :returns: Calculated :py:class:`aspose.threed.utilities.Vector3`.'''
        raise NotImplementedError()
    
    def cos(self) -> aspose.threed.utilities.Vector3:
        '''Calculates cosine on each component
        
        :returns: Calculated :py:class:`aspose.threed.utilities.Vector3`.'''
        raise NotImplementedError()
    
    def cross(self, rhs : aspose.threed.utilities.Vector3) -> aspose.threed.utilities.Vector3:
        '''Cross product of two vectors
        
        :param rhs: Right hand side value.
        :returns: Cross product of two :py:class:`aspose.threed.utilities.Vector3`s.'''
        raise NotImplementedError()
    
    def set(self, new_x : float, new_y : float, new_z : float) -> None:
        '''Sets the x/y/z component in one call.
        
        :param new_x: The x component.
        :param new_y: The y component.
        :param new_z: The z component.'''
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.threed.utilities.Vector3) -> int:
        '''Compare current vector to another instance.'''
        raise NotImplementedError()
    
    @property
    def length2(self) -> float:
        '''Gets the square of the length.'''
        raise NotImplementedError()
    
    @property
    def length(self) -> float:
        '''Gets the length of this vector.'''
        raise NotImplementedError()
    
    @property
    def zero(self) -> aspose.threed.utilities.Vector3:
        '''Gets unit vector (0, 0, 0)'''
        raise NotImplementedError()

    @property
    def one(self) -> aspose.threed.utilities.Vector3:
        '''Gets unit vector (1, 1, 1)'''
        raise NotImplementedError()

    @property
    def unit_x(self) -> aspose.threed.utilities.Vector3:
        '''Gets unit vector (1, 0, 0)'''
        raise NotImplementedError()

    @property
    def unit_y(self) -> aspose.threed.utilities.Vector3:
        '''Gets unit vector (0, 1, 0)'''
        raise NotImplementedError()

    @property
    def unit_z(self) -> aspose.threed.utilities.Vector3:
        '''Gets unit vector (0, 0, 1)'''
        raise NotImplementedError()

    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    
    @property
    def z(self) -> float:
        '''The z component.'''
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : float) -> None:
        '''The z component.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> float:
        raise NotImplementedError()
    
    def __setitem__(self, key : int, value : float):
        raise NotImplementedError()
    

class Vector4:
    '''A vector with four components.'''
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector3, w : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector4` struct.
        
        :param vec: Vec.
        :param w: The width.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.Vector3) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector4` struct.
        
        :param vec: Vec.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, vec : aspose.threed.utilities.FVector4) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector4` struct.
        
        :param vec: Vec.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, x : float, y : float, z : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector4` struct.
        
        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, x : float, y : float, z : float, w : float) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.utilities.Vector4` struct.
        
        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.
        :param w: The width.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def set(self, new_x : float, new_y : float, new_z : float) -> None:
        '''Sets vector\'s xyz components at a time, w will be set to 1
        
        :param new_x: New X component.
        :param new_y: New Y component.
        :param new_z: New Z component.'''
        raise NotImplementedError()
    
    @overload
    def set(self, new_x : float, new_y : float, new_z : float, new_w : float) -> None:
        '''Sets vector\'s all components at a time
        
        :param new_x: New X component.
        :param new_y: New Y component.
        :param new_z: New Z component.
        :param new_w: New W component.'''
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.threed.utilities.Vector4) -> int:
        '''Compare current vector to another instance.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''The x component.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The x component.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The y component.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The y component.'''
        raise NotImplementedError()
    
    @property
    def z(self) -> float:
        '''The z component.'''
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : float) -> None:
        '''The z component.'''
        raise NotImplementedError()
    
    @property
    def w(self) -> float:
        '''The w component.'''
        raise NotImplementedError()
    
    @w.setter
    def w(self, value : float) -> None:
        '''The w component.'''
        raise NotImplementedError()
    

class Vertex:
    '''Vertex reference, used to access the raw vertex in :py:class:`aspose.threed.entities.TriMesh`.'''
    
    def compare_to(self, other : aspose.threed.utilities.Vertex) -> int:
        '''Compare the vertex with another vertex instance'''
        raise NotImplementedError()
    
    def read_vector4(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.Vector4:
        '''Read the vector4 field
        
        :param field: The field with a Vector4/FVector4 data type'''
        raise NotImplementedError()
    
    def read_f_vector4(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.FVector4:
        '''Read the vector4 field
        
        :param field: The field with a Vector4/FVector4 data type'''
        raise NotImplementedError()
    
    def read_vector3(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.Vector3:
        '''Read the vector3 field
        
        :param field: The field with a Vector3/FVector3 data type'''
        raise NotImplementedError()
    
    def read_f_vector3(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.FVector3:
        '''Read the vector3 field
        
        :param field: The field with a Vector3/FVector3 data type'''
        raise NotImplementedError()
    
    def read_vector2(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.Vector2:
        '''Read the vector2 field
        
        :param field: The field with a Vector2/FVector2 data type'''
        raise NotImplementedError()
    
    def read_f_vector2(self, field : aspose.threed.utilities.VertexField) -> aspose.threed.utilities.FVector2:
        '''Read the vector2 field
        
        :param field: The field with a Vector2/FVector2 data type'''
        raise NotImplementedError()
    
    def read_double(self, field : aspose.threed.utilities.VertexField) -> float:
        '''Read the double field
        
        :param field: The field with a float/double compatible data type'''
        raise NotImplementedError()
    
    def read_float(self, field : aspose.threed.utilities.VertexField) -> float:
        '''Read the float field
        
        :param field: The field with a float/double compatible data type'''
        raise NotImplementedError()
    

class VertexDeclaration:
    '''The declaration of a custom defined vertex\'s structure'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def clear(self) -> None:
        '''Clear all fields.'''
        raise NotImplementedError()
    
    def add_field(self, data_type : aspose.threed.utilities.VertexFieldDataType, semantic : aspose.threed.utilities.VertexFieldSemantic, index : int, alias : str) -> aspose.threed.utilities.VertexField:
        '''Add a new vertex field
        
        :param data_type: The data type of the vertex field
        :param semantic: How will this field used for
        :param index: The index for same field semantic, -1 for auto-generation
        :param alias: The alias name of the field'''
        raise NotImplementedError()
    
    @staticmethod
    def from_geometry(geometry : aspose.threed.entities.Geometry, use_float : bool) -> aspose.threed.utilities.VertexDeclaration:
        '''Create a :py:class:`aspose.threed.utilities.VertexDeclaration` based on a :py:class:`aspose.threed.entities.Geometry`\'s layout.
        
        :param use_float: Use float instead of double type'''
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.threed.utilities.VertexDeclaration) -> int:
        '''Compares this instance to a specified object and returns an indication of their relative values.'''
        raise NotImplementedError()
    
    @property
    def sealed(self) -> bool:
        '''A :py:class:`aspose.threed.utilities.VertexDeclaration` will be sealed when its been used by :py:class:`Aspose.ThreeD.Entities.TriMesh`1` or :py:class:`aspose.threed.entities.TriMesh`, no more modifications is allowed.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the count of all fields defined in this :py:class:`aspose.threed.utilities.VertexDeclaration`'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''The size in byte of the vertex structure.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.threed.utilities.VertexField:
        raise NotImplementedError()
    

class VertexField:
    '''Vertex\'s field memory layout description.'''
    
    def compare_to(self, other : aspose.threed.utilities.VertexField) -> int:
        '''Compares this instance to a specified object and returns an indication of their relative values.'''
        raise NotImplementedError()
    
    @property
    def data_type(self) -> aspose.threed.utilities.VertexFieldDataType:
        '''Data type of this field.'''
        raise NotImplementedError()
    
    @property
    def semantic(self) -> aspose.threed.utilities.VertexFieldSemantic:
        '''The usage semantic of this field.'''
        raise NotImplementedError()
    
    @property
    def alias(self) -> str:
        '''Alias annotated by attribute :py:class:`aspose.threed.utilities.SemanticAttribute`'''
        raise NotImplementedError()
    
    @property
    def index(self) -> int:
        '''Index of this field in the vertex\'s layout with same semantic.'''
        raise NotImplementedError()
    
    @property
    def offset(self) -> int:
        '''The offset in bytes of this field.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''The size in bytes of this field'''
        raise NotImplementedError()
    

class Watermark:
    '''Utility to encode/decode blind watermark  to/from a mesh.'''
    
    @overload
    @staticmethod
    def encode_watermark(input : aspose.threed.entities.Mesh, text : str) -> aspose.threed.entities.Mesh:
        '''Encode a text into mesh\' blind watermark.
        
        :param input: Mesh to encode a blind watermark
        :param text: Text to encode to the mesh
        :returns: A new mesh instance with blind watermark encoded'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def encode_watermark(input : aspose.threed.entities.Mesh, text : str, password : str) -> aspose.threed.entities.Mesh:
        '''Encode a text into mesh\' blind watermark.
        
        :param input: Mesh to encode a blind watermark
        :param text: Text to encode to the mesh
        :param password: Password to protect the watermark, it\'s optional
        :returns: A new mesh instance with blind watermark encoded'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def encode_watermark(input : aspose.threed.entities.Mesh, text : str, password : str, permanent : bool) -> aspose.threed.entities.Mesh:
        '''Encode a text into mesh\' blind watermark.
        
        :param input: Mesh to encode a blind watermark
        :param text: Text to encode to the mesh
        :param password: Password to protect the watermark, it\'s optional
        :param permanent: The permanent watermark will not be overwritten or removed.
        :returns: A new mesh instance with blind watermark encoded'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def decode_watermark(input : aspose.threed.entities.Mesh) -> str:
        '''Decode the watermark from a mesh
        
        :param input: The mesh to extract watermark
        :returns: Blind watermark or null if no watermark decoded.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def decode_watermark(input : aspose.threed.entities.Mesh, password : str) -> str:
        '''Decode the watermark from a mesh
        
        :param input: The mesh to extract watermark
        :param password: The password to decrypt the watermark
        :returns: Blind watermark or null if no watermark decoded.'''
        raise NotImplementedError()
    

class BoundingBoxExtent:
    '''The extent of the bounding box'''
    
    NULL : BoundingBoxExtent
    '''Null bounding box'''
    FINITE : BoundingBoxExtent
    '''Finite bounding box'''
    INFINITE : BoundingBoxExtent
    '''Infinite bounding box'''

class ComposeOrder:
    '''The order to compose transform matrix'''
    
    APPEND : ComposeOrder
    '''Append the new transform to the chain'''
    PREPEND : ComposeOrder
    '''Prepend the new transform to the chain'''

class RotationOrder:
    '''The order controls which rx ry rz are applied in the transformation matrix.'''
    
    XYZ : RotationOrder
    '''Rotate in X,Y,Z order'''
    XZY : RotationOrder
    '''Rotate in X,Z,Y order'''
    YZX : RotationOrder
    '''Rotate in Y,Z,X order'''
    YXZ : RotationOrder
    '''Rotate in Y,X,Z order'''
    ZXY : RotationOrder
    '''Rotate in Z,X,Y order'''
    ZYX : RotationOrder
    '''Rotate in Z,Y,X order'''

class VertexFieldDataType:
    '''Vertex field\'s data type'''
    
    FLOAT : VertexFieldDataType
    '''Type of :py:class:`float`'''
    F_VECTOR2 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.FVector2`'''
    F_VECTOR3 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.FVector3`'''
    F_VECTOR4 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.FVector4`'''
    DOUBLE : VertexFieldDataType
    '''Type of :py:class:`float`'''
    VECTOR2 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.Vector2`'''
    VECTOR3 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.Vector3`'''
    VECTOR4 : VertexFieldDataType
    '''Type of :py:class:`aspose.threed.utilities.Vector4`'''
    BYTE_VECTOR4 : VertexFieldDataType
    '''Type of byte[4], can be used to represent color with less memory consumption.'''
    INT8 : VertexFieldDataType
    '''Type of :py:class:`int`'''
    INT16 : VertexFieldDataType
    '''Type of :py:class:`int`'''
    INT32 : VertexFieldDataType
    '''Type of :py:class:`int`'''
    INT64 : VertexFieldDataType
    '''Type of :py:class:`int`'''

class VertexFieldSemantic:
    '''The semantic of the vertex field'''
    
    POSITION : VertexFieldSemantic
    '''Position data'''
    BINORMAL : VertexFieldSemantic
    '''Binormal vector'''
    NORMAL : VertexFieldSemantic
    '''Normal vector'''
    TANGENT : VertexFieldSemantic
    '''Tangent vector'''
    UV : VertexFieldSemantic
    '''Texture UV coordinate'''
    VERTEX_COLOR : VertexFieldSemantic
    '''Vertex color'''
    VERTEX_CREASE : VertexFieldSemantic
    '''Vertex crease'''
    EDGE_CREASE : VertexFieldSemantic
    '''Edge crease'''
    USER_DATA : VertexFieldSemantic
    '''User data, usually for application-specific purpose'''
    VISIBILITY : VertexFieldSemantic
    '''Visibility for components'''
    SPECULAR : VertexFieldSemantic
    '''Specular colors'''
    WEIGHT : VertexFieldSemantic
    '''Blend weights'''
    MORPH_POSITION : VertexFieldSemantic
    '''Position data for morph target'''
    MORPH_NORMAL : VertexFieldSemantic
    '''Normal data for morph target'''

