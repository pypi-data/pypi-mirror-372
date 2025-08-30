
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

class A3DObject(INamedObject):
    '''The base class of all Aspose.ThreeD objects, all sub classes will support dynamic properties.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.A3DObject` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.A3DObject` class with no name.'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    

class AssetInfo(A3DObject):
    '''Information of asset.
    Asset information can be attached to a :py:class:`aspose.threed.Scene`.
    Child :py:class:`aspose.threed.Scene` can have its own :py:class:`aspose.threed.AssetInfo` to override parent\'s definition.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.AssetInfo` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.AssetInfo` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def creation_time(self) -> System.Nullable`1[[System.DateTime]]:
        '''Gets or Sets the creation time of this asset'''
        raise NotImplementedError()
    
    @creation_time.setter
    def creation_time(self, value : System.Nullable`1[[System.DateTime]]) -> None:
        '''Gets or Sets the creation time of this asset'''
        raise NotImplementedError()
    
    @property
    def modification_time(self) -> System.Nullable`1[[System.DateTime]]:
        '''Gets or Sets the modification time of this asset'''
        raise NotImplementedError()
    
    @modification_time.setter
    def modification_time(self, value : System.Nullable`1[[System.DateTime]]) -> None:
        '''Gets or Sets the modification time of this asset'''
        raise NotImplementedError()
    
    @property
    def ambient(self) -> System.Nullable`1[[Aspose.ThreeD.Utilities.Vector4]]:
        '''Gets or Sets the default ambient color of this asset'''
        raise NotImplementedError()
    
    @ambient.setter
    def ambient(self, value : System.Nullable`1[[Aspose.ThreeD.Utilities.Vector4]]) -> None:
        '''Gets or Sets the default ambient color of this asset'''
        raise NotImplementedError()
    
    @property
    def url(self) -> str:
        '''Gets or Sets the URL of this asset.'''
        raise NotImplementedError()
    
    @url.setter
    def url(self, value : str) -> None:
        '''Gets or Sets the URL of this asset.'''
        raise NotImplementedError()
    
    @property
    def application_vendor(self) -> str:
        '''Gets the application vendor\'s name'''
        raise NotImplementedError()
    
    @application_vendor.setter
    def application_vendor(self, value : str) -> None:
        '''Sets the application vendor\'s name'''
        raise NotImplementedError()
    
    @property
    def copyright(self) -> str:
        '''Gets the document\'s copyright'''
        raise NotImplementedError()
    
    @copyright.setter
    def copyright(self, value : str) -> None:
        '''Sets the document\'s copyright'''
        raise NotImplementedError()
    
    @property
    def application_name(self) -> str:
        '''Gets the application that created this asset'''
        raise NotImplementedError()
    
    @application_name.setter
    def application_name(self, value : str) -> None:
        '''Sets the application that created this asset'''
        raise NotImplementedError()
    
    @property
    def application_version(self) -> str:
        '''Gets the version of the application that created this asset.'''
        raise NotImplementedError()
    
    @application_version.setter
    def application_version(self, value : str) -> None:
        '''Sets the version of the application that created this asset.'''
        raise NotImplementedError()
    
    @property
    def title(self) -> str:
        '''Gets the title of this asset'''
        raise NotImplementedError()
    
    @title.setter
    def title(self, value : str) -> None:
        '''Sets the title of this asset'''
        raise NotImplementedError()
    
    @property
    def subject(self) -> str:
        '''Gets the subject of this asset'''
        raise NotImplementedError()
    
    @subject.setter
    def subject(self, value : str) -> None:
        '''Sets the subject of this asset'''
        raise NotImplementedError()
    
    @property
    def author(self) -> str:
        '''Gets the author of this asset'''
        raise NotImplementedError()
    
    @author.setter
    def author(self, value : str) -> None:
        '''Sets the author of this asset'''
        raise NotImplementedError()
    
    @property
    def keywords(self) -> str:
        '''Gets the keywords of this asset'''
        raise NotImplementedError()
    
    @keywords.setter
    def keywords(self, value : str) -> None:
        '''Sets the keywords of this asset'''
        raise NotImplementedError()
    
    @property
    def revision(self) -> str:
        '''Gets the revision number of this asset, usually used in version control system.'''
        raise NotImplementedError()
    
    @revision.setter
    def revision(self, value : str) -> None:
        '''Sets the revision number of this asset, usually used in version control system.'''
        raise NotImplementedError()
    
    @property
    def comment(self) -> str:
        '''Gets the comment of this asset.'''
        raise NotImplementedError()
    
    @comment.setter
    def comment(self, value : str) -> None:
        '''Sets the comment of this asset.'''
        raise NotImplementedError()
    
    @property
    def unit_name(self) -> str:
        '''Gets the unit of length used in this asset.
        e.g. cm/m/km/inch/feet'''
        raise NotImplementedError()
    
    @unit_name.setter
    def unit_name(self, value : str) -> None:
        '''Sets the unit of length used in this asset.
        e.g. cm/m/km/inch/feet'''
        raise NotImplementedError()
    
    @property
    def unit_scale_factor(self) -> float:
        '''Gets the scale factor to real-world meter.'''
        raise NotImplementedError()
    
    @unit_scale_factor.setter
    def unit_scale_factor(self, value : float) -> None:
        '''Sets the scale factor to real-world meter.'''
        raise NotImplementedError()
    
    @property
    def coordinate_system(self) -> System.Nullable`1[[Aspose.ThreeD.CoordinateSystem]]:
        '''Gets the coordinate system used in this asset.'''
        raise NotImplementedError()
    
    @coordinate_system.setter
    def coordinate_system(self, value : System.Nullable`1[[Aspose.ThreeD.CoordinateSystem]]) -> None:
        '''Sets the coordinate system used in this asset.'''
        raise NotImplementedError()
    
    @property
    def up_vector(self) -> System.Nullable`1[[Aspose.ThreeD.Axis]]:
        '''Gets the up-vector used in this asset.'''
        raise NotImplementedError()
    
    @up_vector.setter
    def up_vector(self, value : System.Nullable`1[[Aspose.ThreeD.Axis]]) -> None:
        '''Sets the up-vector used in this asset.'''
        raise NotImplementedError()
    
    @property
    def front_vector(self) -> System.Nullable`1[[Aspose.ThreeD.Axis]]:
        '''Gets the front-vector used in this asset.'''
        raise NotImplementedError()
    
    @front_vector.setter
    def front_vector(self, value : System.Nullable`1[[Aspose.ThreeD.Axis]]) -> None:
        '''Sets the front-vector used in this asset.'''
        raise NotImplementedError()
    
    @property
    def axis_system(self) -> aspose.threed.AxisSystem:
        '''Gets the coordinate system/up vector/front vector of the asset info.'''
        raise NotImplementedError()
    
    @axis_system.setter
    def axis_system(self, value : aspose.threed.AxisSystem) -> None:
        '''Sets the coordinate system/up vector/front vector of the asset info.'''
        raise NotImplementedError()
    

class AxisSystem:
    '''Axis system is an combination of coordinate system, up vector and front vector.'''
    
    @overload
    def __init__(self, coordinate_system : aspose.threed.CoordinateSystem, up : aspose.threed.Axis, front : aspose.threed.Axis) -> None:
        '''Constructs a new axis system
        
        :param coordinate_system: The coordinate system used in this axis system
        :param up: The up vector of the axis system
        :param front: The front vector of the axis system'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, coordinate_system : aspose.threed.CoordinateSystem, up : aspose.threed.Axis) -> None:
        '''Constructs a new axis system
        
        :param coordinate_system: The coordinate system used in this axis system
        :param up: The up vector of the axis system'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, up : aspose.threed.Axis, front : System.Nullable`1[[Aspose.ThreeD.Axis]]) -> None:
        raise NotImplementedError()
    
    @overload
    def __init__(self, coordinate_system : System.Nullable`1[[Aspose.ThreeD.CoordinateSystem]], up : System.Nullable`1[[Aspose.ThreeD.Axis]], front : System.Nullable`1[[Aspose.ThreeD.Axis]]) -> None:
        raise NotImplementedError()
    
    def transform_to(self, target_system : aspose.threed.AxisSystem) -> aspose.threed.utilities.Matrix4:
        '''Create a matrix used to convert from current axis system to target axis system.
        
        :param target_system: Target axis system
        :returns: A new transformation matrix to do the axis conversion'''
        raise NotImplementedError()
    
    @staticmethod
    def from_asset_info(asset_info : aspose.threed.AssetInfo) -> aspose.threed.AxisSystem:
        '''Create :py:class:`aspose.threed.AxisSystem` from :py:class:`aspose.threed.AssetInfo`
        
        :param asset_info: From which asset info to read coordinate system, up and front vector.
        :returns: Axis system containg coordinate system, up, front from given asset info'''
        raise NotImplementedError()
    
    @property
    def coordinate_system(self) -> aspose.threed.CoordinateSystem:
        '''Gets the coordinate system of this axis system.'''
        raise NotImplementedError()
    
    @property
    def up(self) -> aspose.threed.Axis:
        '''Gets the up vector of this axis system.'''
        raise NotImplementedError()
    
    @property
    def front(self) -> aspose.threed.Axis:
        '''Gets the front vector of this axis system'''
        raise NotImplementedError()
    

class BonePose:
    '''The :py:class:`aspose.threed.BonePose` contains the transformation matrix for a bone node'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def node(self) -> aspose.threed.Node:
        '''Gets the scene node, points to a skinned skeleton node'''
        raise NotImplementedError()
    
    @node.setter
    def node(self, value : aspose.threed.Node) -> None:
        '''Sets the scene node, points to a skinned skeleton node'''
        raise NotImplementedError()
    
    @property
    def matrix(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the transform matrix of the node in current pose.'''
        raise NotImplementedError()
    
    @matrix.setter
    def matrix(self, value : aspose.threed.utilities.Matrix4) -> None:
        '''Sets the transform matrix of the node in current pose.'''
        raise NotImplementedError()
    
    @property
    def is_local(self) -> bool:
        '''Gets if the matrix is defined in local coordinate.'''
        raise NotImplementedError()
    
    @is_local.setter
    def is_local(self, value : bool) -> None:
        '''Sets if the matrix is defined in local coordinate.'''
        raise NotImplementedError()
    

class CustomObject(A3DObject):
    '''Meta data or custom objects used in 3D files are managed by this class.
    All custom properties are saved as dynamic properties.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.CustomObject` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.CustomObject` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    

class Entity(SceneObject):
    '''The base class of all entities.
    Entity represents a concrete object that attached under a node like :py:class:`aspose.threed.entities.Light`/:py:class:`aspose.threed.entities.Geometry`.'''
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer
        
        :returns: the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def scene(self) -> aspose.threed.Scene:
        '''Gets the scene that this object belongs to'''
        raise NotImplementedError()
    
    @property
    def parent_nodes(self) -> System.Collections.Generic.List`1[[Aspose.ThreeD.Node]]:
        '''Gets all parent nodes, an entity can be attached to multiple parent nodes for geometry instancing'''
        raise NotImplementedError()
    
    @property
    def excluded(self) -> bool:
        '''Gets whether to exclude this entity during exporting.'''
        raise NotImplementedError()
    
    @excluded.setter
    def excluded(self, value : bool) -> None:
        '''Sets whether to exclude this entity during exporting.'''
        raise NotImplementedError()
    
    @property
    def parent_node(self) -> aspose.threed.Node:
        '''Gets the first parent node, if set the first parent node, this entity will be detached from other parent nodes.'''
        raise NotImplementedError()
    
    @parent_node.setter
    def parent_node(self, value : aspose.threed.Node) -> None:
        '''Sets the first parent node, if set the first parent node, this entity will be detached from other parent nodes.'''
        raise NotImplementedError()
    

class ExportException:
    '''Exceptions when Aspose.3D failed to export the scene to file'''
    
    def __init__(self, msg : str) -> None:
        '''Initializes a new instance
        
        :param msg: Error message'''
        raise NotImplementedError()
    

class FileFormat:
    '''File format definition'''
    
    @overload
    @staticmethod
    def detect(stream : io._IOBase, file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from data stream, file name is optional for guessing types that has no magic header.
        
        :param stream: Stream containing data to detect
        :param file_name: Original file name of the data, used as hint.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def detect(file_name : str) -> aspose.threed.FileFormat:
        '''Detect the file format from file name, file must be readable so Aspose.3D can detect the file format through file header.
        
        :param file_name: Path to the file to detect file format.
        :returns: The :py:class:`aspose.threed.FileFormat` instance of the detected type or null if failed.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_format_by_extension(extension_name : str) -> aspose.threed.FileFormat:
        '''Gets the preferred file format from the file extension name
        The extension name should starts with a dot(\'.\').
        
        :param extension_name: The extension name started with \'.\' to query.
        :returns: Instance of :py:class:`aspose.threed.FileFormat`, otherwise null returned.'''
        raise NotImplementedError()
    
    def create_load_options(self) -> aspose.threed.formats.LoadOptions:
        '''Create a default load options for this file format
        
        :returns: A default load option for current format'''
        raise NotImplementedError()
    
    def create_save_options(self) -> aspose.threed.formats.SaveOptions:
        '''Create a default save options for this file format
        
        :returns: A default save option for current format'''
        raise NotImplementedError()
    
    @property
    def formats(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.FileFormat]]:
        '''Access to all supported formats'''
        raise NotImplementedError()

    @property
    def version(self) -> System.Version:
        '''Gets file format version'''
        raise NotImplementedError()
    
    @property
    def can_export(self) -> bool:
        '''Gets whether Aspose.3D supports export scene to current file format.'''
        raise NotImplementedError()
    
    @property
    def can_import(self) -> bool:
        '''Gets whether Aspose.3D supports import scene from current file format.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the extension name of this type.'''
        raise NotImplementedError()
    
    @property
    def extensions(self) -> List[str]:
        '''Gets the extension names of this type.'''
        raise NotImplementedError()
    
    @property
    def content_type(self) -> aspose.threed.FileContentType:
        '''Gets file format content type'''
        raise NotImplementedError()
    
    @property
    def file_format_type(self) -> aspose.threed.FileFormatType:
        '''Gets file format type'''
        raise NotImplementedError()
    
    @property
    def FBX6100ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX6100_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 6.1.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7200_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.2.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7300_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.3.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7400_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.4.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7500_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.5.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7600_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.6.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700ASCII(self) -> aspose.threed.FileFormat:
        '''ASCII FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def FBX7700_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary FBX file format, with 7.7.0 version'''
        raise NotImplementedError()

    @property
    def MAYA_ASCII(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in ASCII format'''
        raise NotImplementedError()

    @property
    def MAYA_BINARY(self) -> aspose.threed.FileFormat:
        '''Autodesk Maya in Binary format'''
        raise NotImplementedError()

    @property
    def STL_BINARY(self) -> aspose.threed.FileFormat:
        '''Binary STL file format'''
        raise NotImplementedError()

    @property
    def STLASCII(self) -> aspose.threed.FileFormat:
        '''ASCII STL file format'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormat:
        '''Wavefront\'s Obj file format'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormat:
        '''3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormat:
        '''Collada file format'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormat:
        '''Universal3D file format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def GLTF2(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def GLTF_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF in Binary format'''
        raise NotImplementedError()

    @property
    def GLTF2_BINARY(self) -> aspose.threed.FileFormat:
        '''Khronos Group\'s glTF version 2.0'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.formats.PdfFormat:
        '''Adobe\'s Portable Document Format'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormat:
        '''Blender\'s 3D file format'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormat:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.formats.PlyFormat:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X_BINARY(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def X_TEXT(self) -> aspose.threed.FileFormat:
        '''DirectX X File in binary format'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.formats.DracoFormat:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.formats.Microsoft3MFFormat:
        '''Microsoft 3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM_TEXT(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in text format'''
        raise NotImplementedError()

    @property
    def RVM_BINARY(self) -> aspose.threed.formats.RvmFormat:
        '''AVEVA Plant Design Management System Model in binary format'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormat:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormat:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT8(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 8'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT9(self) -> aspose.threed.FileFormat:
        '''Siemens JT File Version 9'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormat:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormat:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormat:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormat:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormat:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def USDA(self) -> aspose.threed.FileFormat:
        '''Universal Scene Description in ASCII format.'''
        raise NotImplementedError()

    @property
    def USDZ(self) -> aspose.threed.FileFormat:
        '''Compressed Universal Scene Description'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormat:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in ASCII mode'''
        raise NotImplementedError()

    @property
    def PCD_BINARY(self) -> aspose.threed.FileFormat:
        '''PCL Point Cloud Data file in Binary mode'''
        raise NotImplementedError()


class FileFormatType:
    '''File format type'''
    
    @property
    def extension(self) -> str:
        '''The extension name of this file format, started with .'''
        raise NotImplementedError()
    
    @property
    def MAYA(self) -> aspose.threed.FileFormatType:
        '''Autodesk Maya format type'''
        raise NotImplementedError()

    @property
    def BLENDER(self) -> aspose.threed.FileFormatType:
        '''Blender format type'''
        raise NotImplementedError()

    @property
    def FBX(self) -> aspose.threed.FileFormatType:
        '''FBX file format type'''
        raise NotImplementedError()

    @property
    def STL(self) -> aspose.threed.FileFormatType:
        '''STL file format type'''
        raise NotImplementedError()

    @property
    def WAVEFRONT_OBJ(self) -> aspose.threed.FileFormatType:
        '''Wavefront OBJ format type'''
        raise NotImplementedError()

    @property
    def DISCREET_3DS(self) -> aspose.threed.FileFormatType:
        '''Discreet 3D Studio\'s file format'''
        raise NotImplementedError()

    @property
    def COLLADA(self) -> aspose.threed.FileFormatType:
        '''Khronos Group\'s Collada file format.'''
        raise NotImplementedError()

    @property
    def UNIVERSAL_3D(self) -> aspose.threed.FileFormatType:
        '''Universal 3D file format type'''
        raise NotImplementedError()

    @property
    def PDF(self) -> aspose.threed.FileFormatType:
        '''Portable Document Format'''
        raise NotImplementedError()

    @property
    def GLTF(self) -> aspose.threed.FileFormatType:
        '''Khronos Group\'s glTF'''
        raise NotImplementedError()

    @property
    def DXF(self) -> aspose.threed.FileFormatType:
        '''AutoCAD DXF'''
        raise NotImplementedError()

    @property
    def PLY(self) -> aspose.threed.FileFormatType:
        '''Polygon File Format or Stanford Triangle Format'''
        raise NotImplementedError()

    @property
    def X(self) -> aspose.threed.FileFormatType:
        '''DirectX\'s X File'''
        raise NotImplementedError()

    @property
    def DRACO(self) -> aspose.threed.FileFormatType:
        '''Google Draco Mesh'''
        raise NotImplementedError()

    @property
    def MICROSOFT_3MF(self) -> aspose.threed.FileFormatType:
        '''3D Manufacturing Format'''
        raise NotImplementedError()

    @property
    def RVM(self) -> aspose.threed.FileFormatType:
        '''AVEVA Plant Design Management System Model.'''
        raise NotImplementedError()

    @property
    def ASE(self) -> aspose.threed.FileFormatType:
        '''3D Studio Max\'s ASCII Scene Exporter format.'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> aspose.threed.FileFormatType:
        '''Zip archive that contains other 3d file format.'''
        raise NotImplementedError()

    @property
    def USD(self) -> aspose.threed.FileFormatType:
        '''Universal Scene Description'''
        raise NotImplementedError()

    @property
    def PCD(self) -> aspose.threed.FileFormatType:
        '''Point Cloud Data used by Point Cloud Library'''
        raise NotImplementedError()

    @property
    def XYZ(self) -> aspose.threed.FileFormatType:
        '''Xyz point cloud file'''
        raise NotImplementedError()

    @property
    def IFC(self) -> aspose.threed.FileFormatType:
        '''ISO 16739-1 Industry Foundation Classes data model.'''
        raise NotImplementedError()

    @property
    def SIEMENS_JT(self) -> aspose.threed.FileFormatType:
        '''Siemens PLM Software NX\'s JT File'''
        raise NotImplementedError()

    @property
    def AMF(self) -> aspose.threed.FileFormatType:
        '''Additive manufacturing file format'''
        raise NotImplementedError()

    @property
    def VRML(self) -> aspose.threed.FileFormatType:
        '''The Virtual Reality Modeling Language'''
        raise NotImplementedError()

    @property
    def HTML5(self) -> aspose.threed.FileFormatType:
        '''HTML5 File'''
        raise NotImplementedError()

    @property
    def ASPOSE_3D_WEB(self) -> aspose.threed.FileFormatType:
        '''Aspose.3D Web format.'''
        raise NotImplementedError()


class GlobalTransform:
    '''Global transform is similar to :py:class:`aspose.threed.Transform` but it\'s immutable while it represents the final evaluated transformation.
    Right-hand coordinate system is used while evaluating global transform'''
    
    @property
    def translation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the translation'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> aspose.threed.utilities.Vector3:
        '''Gets the scale'''
        raise NotImplementedError()
    
    @property
    def euler_angles(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation represented in Euler angles, measured in degree'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> aspose.threed.utilities.Quaternion:
        '''Gets the rotation represented in quaternion.'''
        raise NotImplementedError()
    
    @property
    def transform_matrix(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the transform matrix.'''
        raise NotImplementedError()
    

class Group(A3DObject):
    '''A :py:class:`aspose.threed.Group` represents the logical relationships of :py:class:`aspose.threed.Node`.'''
    
    def __init__(self, name : str) -> None:
        '''Construct a new instance of :py:class:`aspose.threed.Group`
        
        :param name: Group\'s name'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.threed.Group:
        '''Parent group of current group'''
        raise NotImplementedError()
    
    @property
    def groups(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Group]]:
        '''Sub-groups'''
        raise NotImplementedError()
    
    @property
    def nodes(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Node]]:
        '''The nodes in this group'''
        raise NotImplementedError()
    

class INamedObject:
    '''Object that has a name'''
    
    @property
    def name(self) -> str:
        '''Gets the name of the object'''
        raise NotImplementedError()
    

class ImageRenderOptions(A3DObject):
    '''Options for :py:func:`aspose.threed.Scene.render` and  :py:func:`aspose.threed.Scene.render`'''
    
    def __init__(self) -> None:
        '''Initialize an instance of :py:class:`aspose.threed.ImageRenderOptions`'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.threed.utilities.Vector3:
        '''The background color of the render result.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''The background color of the render result.'''
        raise NotImplementedError()
    
    @property
    def asset_directories(self) -> System.Collections.Generic.List`1[[System.String]]:
        '''Directories that stored external assets(like textures)'''
        raise NotImplementedError()
    
    @asset_directories.setter
    def asset_directories(self, value : System.Collections.Generic.List`1[[System.String]]) -> None:
        '''Directories that stored external assets(like textures)'''
        raise NotImplementedError()
    
    @property
    def enable_shadows(self) -> bool:
        '''Gets whether to render shadows.'''
        raise NotImplementedError()
    
    @enable_shadows.setter
    def enable_shadows(self, value : bool) -> None:
        '''Sets whether to render shadows.'''
        raise NotImplementedError()
    

class ImportException:
    '''Exception when Aspose.3D failed to open the specified source'''
    
    def __init__(self, msg : str) -> None:
        '''Initializes a new instance
        
        :param msg: Error message'''
        raise NotImplementedError()
    

class License:
    '''Provides methods to license the component.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of this class.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, license_name : str) -> None:
        '''Licenses the component.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, stream : io._IOBase) -> None:
        '''Licenses the component.
        
        :param stream: A stream that contains the license.'''
        raise NotImplementedError()
    

class Metered:
    '''Provides methods to set metered key.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of this class.'''
        raise NotImplementedError()
    
    def set_metered_key(self, public_key : str, private_key : str) -> None:
        '''Sets metered public and private key.
        If you purchase metered license, when start application, this API should be called, normally, this is enough. However, if always fail to upload consumption data and exceed 24 hours, the license will be set to evaluation status, to avoid such case, you should regularly check the license status, if it is evaluation status, call this API again.
        
        :param public_key: public key
        :param private_key: private key'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_quantity() -> System.Decimal:
        '''Gets consumption file size
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_credit() -> System.Decimal:
        '''Gets consumption credit
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    

class Node(SceneObject):
    '''Represents an element in the scene graph.
    A scene graph is a tree of Node objects. The tree management services are self contained in this class.
    Note the Aspose.3D SDK does not test the validity of the constructed scene graph. It is the responsibility of the caller to make sure that it does not generate cyclic graphs in a node hierarchy.
    Besides the tree management, this class defines all the properties required to describe the position of the object in the scene. This information include the basic Translation, Rotation and Scaling properties and the more advanced options for pivots, limits, and IK joints attributes such the stiffness and dampening.
    When it is first created, the Node object is "empty" (i.e: it is an object without any graphical representation that only contains the position information). In this state, it can be used to represent parents in the node tree structure but not much more. The normal use of this type of objects is to add them an entity that will specialize the node (see the "Entity").
    The entity is an object in itself and is connected to the the Node. This also means that the same entity can be shared among multiple nodes. Camera, Light, Mesh, etc... are all entities and they all derived from the base class Entity.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Node` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str, entity : aspose.threed.Entity) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Node` class.
        
        :param name: Name.
        :param entity: Default entity.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Node` class.
        
        :param name: Name.'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def create_child_node(self) -> aspose.threed.Node:
        '''Creates a child node
        
        :returns: The new child node.'''
        raise NotImplementedError()
    
    @overload
    def create_child_node(self, node_name : str) -> aspose.threed.Node:
        '''Create a new child node with given node name
        
        :param node_name: The new child node\'s name
        :returns: The new child node.'''
        raise NotImplementedError()
    
    @overload
    def create_child_node(self, entity : aspose.threed.Entity) -> aspose.threed.Node:
        '''Create a new child node with given entity attached
        
        :param entity: Default entity attached to the node
        :returns: The new child node.'''
        raise NotImplementedError()
    
    @overload
    def create_child_node(self, node_name : str, entity : aspose.threed.Entity) -> aspose.threed.Node:
        '''Create a new child node with given node name
        
        :param node_name: The new child node\'s name
        :param entity: Default entity attached to the node
        :returns: The new child node.'''
        raise NotImplementedError()
    
    @overload
    def create_child_node(self, node_name : str, entity : aspose.threed.Entity, material : aspose.threed.shading.Material) -> aspose.threed.Node:
        '''Create a new child node with given node name, and attach specified entity and a material
        
        :param node_name: The new child node\'s name
        :param entity: Default entity attached to the node
        :param material: The material attached to the node
        :returns: The new child node.'''
        raise NotImplementedError()
    
    @overload
    def get_child(self, index : int) -> aspose.threed.Node:
        '''Gets the child node at specified index.
        
        :param index: Index.
        :returns: The child.'''
        raise NotImplementedError()
    
    @overload
    def get_child(self, node_name : str) -> aspose.threed.Node:
        '''Gets the child node with the specified name
        
        :param node_name: The child name to find.
        :returns: The child.'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    def merge(self, node : aspose.threed.Node) -> None:
        '''Detach everything under the node and attach them to current node.'''
        raise NotImplementedError()
    
    def evaluate_global_transform(self, with_geometric_transform : bool) -> aspose.threed.utilities.Matrix4:
        '''Evaluate the global transform, include the geometric transform or not.
        
        :param with_geometric_transform: Whether the geometric transform is needed.
        :returns: The global transform matrix.'''
        raise NotImplementedError()
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Calculate the bounding box of the node
        
        :returns: The bounding box of current node'''
        raise NotImplementedError()
    
    def add_entity(self, entity : aspose.threed.Entity) -> None:
        '''Add an entity to the node.
        
        :param entity: The entity to be attached to the node'''
        raise NotImplementedError()
    
    def add_child_node(self, node : aspose.threed.Node) -> None:
        '''Add a child node to this node
        
        :param node: The child node to be attached'''
        raise NotImplementedError()
    
    def select_single_object(self, path : str) -> Any:
        '''Select single object under current node using XPath-like query syntax.
        
        :param path: The XPath-like query
        :returns: Object located by the XPath-like query.'''
        raise NotImplementedError()
    
    def select_objects(self, path : str) -> System.Collections.Generic.List`1[[System.Object]]:
        '''Select multiple objects under current node using XPath-like query syntax.
        
        :param path: The XPath-like query
        :returns: Multiple object matches the XPath-like query.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def scene(self) -> aspose.threed.Scene:
        '''Gets the scene that this object belongs to'''
        raise NotImplementedError()
    
    @property
    def asset_info(self) -> aspose.threed.AssetInfo:
        '''Per-node asset info'''
        raise NotImplementedError()
    
    @asset_info.setter
    def asset_info(self, value : aspose.threed.AssetInfo) -> None:
        '''Per-node asset info'''
        raise NotImplementedError()
    
    @property
    def visible(self) -> bool:
        '''Gets to show the node'''
        raise NotImplementedError()
    
    @visible.setter
    def visible(self, value : bool) -> None:
        '''Sets to show the node'''
        raise NotImplementedError()
    
    @property
    def child_nodes(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Node]]:
        '''Gets the children nodes.'''
        raise NotImplementedError()
    
    @property
    def entity(self) -> aspose.threed.Entity:
        '''Gets the first entity attached to this node, if sets, will clear other entities.'''
        raise NotImplementedError()
    
    @entity.setter
    def entity(self, value : aspose.threed.Entity) -> None:
        '''Sets the first entity attached to this node, if sets, will clear other entities.'''
        raise NotImplementedError()
    
    @property
    def excluded(self) -> bool:
        '''Gets whether to exclude this node and all child nodes/entities during exporting.'''
        raise NotImplementedError()
    
    @excluded.setter
    def excluded(self, value : bool) -> None:
        '''Sets whether to exclude this node and all child nodes/entities during exporting.'''
        raise NotImplementedError()
    
    @property
    def entities(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Entity]]:
        '''Gets all node entities.'''
        raise NotImplementedError()
    
    @property
    def meta_datas(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.CustomObject]]:
        '''Gets the meta data defined in this node.'''
        raise NotImplementedError()
    
    @property
    def materials(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Shading.Material]]:
        '''Gets the materials associated with this node.'''
        raise NotImplementedError()
    
    @property
    def material(self) -> aspose.threed.shading.Material:
        '''Gets the first material associated with this node, if sets, will clear other materials'''
        raise NotImplementedError()
    
    @material.setter
    def material(self, value : aspose.threed.shading.Material) -> None:
        '''Sets the first material associated with this node, if sets, will clear other materials'''
        raise NotImplementedError()
    
    @property
    def parent_node(self) -> aspose.threed.Node:
        '''Gets the parent node.'''
        raise NotImplementedError()
    
    @parent_node.setter
    def parent_node(self, value : aspose.threed.Node) -> None:
        '''Sets the parent node.'''
        raise NotImplementedError()
    
    @property
    def transform(self) -> aspose.threed.Transform:
        '''Gets the local transform.'''
        raise NotImplementedError()
    
    @property
    def global_transform(self) -> aspose.threed.GlobalTransform:
        '''Gets the global transform.'''
        raise NotImplementedError()
    

class Pose(A3DObject):
    '''The pose is used to store transformation matrix when the geometry is skinned.
    The pose is a set of :py:class:`aspose.threed.BonePose`, each :py:class:`aspose.threed.BonePose` saves the concrete transformation information of the bone node.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Pose` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Pose` class.'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def add_bone_pose(self, node : aspose.threed.Node, matrix : aspose.threed.utilities.Matrix4, local_matrix : bool) -> None:
        '''Saves pose transformation matrix for the given bone node.
        
        :param node: Bone Node.
        :param matrix: Transformation matrix.
        :param local_matrix: If set to ``true`` means to use local matrix otherwise means global matrix.'''
        raise NotImplementedError()
    
    @overload
    def add_bone_pose(self, node : aspose.threed.Node, matrix : aspose.threed.utilities.Matrix4) -> None:
        '''Saves pose transformation matrix for the given bone node.
        Global transformation matrix is implied.
        
        :param node: Bone Node.
        :param matrix: Transformation matrix.'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def pose_type(self) -> aspose.threed.PoseType:
        '''Gets the type of the pose.'''
        raise NotImplementedError()
    
    @pose_type.setter
    def pose_type(self, value : aspose.threed.PoseType) -> None:
        '''Sets the type of the pose.'''
        raise NotImplementedError()
    
    @property
    def bone_poses(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.BonePose]]:
        '''Gets all :py:class:`aspose.threed.BonePose`.'''
        raise NotImplementedError()
    

class Property:
    '''Class to hold user-defined properties.'''
    
    def get_extra(self, name : str) -> Any:
        '''Gets extra data of the property associated by name.
        
        :param name: The name of the property\'s extra data
        :returns: The extra data associated by name'''
        raise NotImplementedError()
    
    def set_extra(self, name : str, value : Any) -> None:
        '''Sets extra data of the property associated by name.
        
        :param name: The name of the property\'s extra data
        :param value: The value of the property\'s extra data'''
        raise NotImplementedError()
    
    def get_bind_point(self, anim : aspose.threed.animation.AnimationNode, create : bool) -> aspose.threed.animation.BindPoint:
        '''Gets the property bind point on specified animation instance.
        
        :param anim: On which animation to create the bind point.
        :param create: Create the property bind point if it\'s not found.
        :returns: The property bind point on specified animation instance'''
        raise NotImplementedError()
    
    def get_keyframe_sequence(self, anim : aspose.threed.animation.AnimationNode, create : bool) -> aspose.threed.animation.KeyframeSequence:
        '''Gets the keyframe sequence on specified animation instance.
        
        :param anim: On which animation to create the keyframe sequence.
        :param create: Create the keyframe sequence if it\'s not found.
        :returns: The keyframe sequence on specified animation instance'''
        raise NotImplementedError()
    
    @property
    def value(self) -> Any:
        '''Gets the value.'''
        raise NotImplementedError()
    
    @value.setter
    def value(self, value : Any) -> None:
        '''Sets the value.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of the property'''
        raise NotImplementedError()
    
    @property
    def value_type(self) -> System.Type:
        '''Gets the type of the property value.'''
        raise NotImplementedError()
    

class PropertyCollection:
    '''The collection of properties'''
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def find_property(self, property : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    def get(self, property : str) -> Any:
        '''Gets the value of the property by property name.
        
        :param property: The name of the property
        :returns: The property\'s value'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the count of declared properties.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.threed.Property:
        raise NotImplementedError()
    

class Scene(SceneObject):
    '''A scene is a top-level object that contains the nodes, geometries, materials, textures, animation, poses, sub-scenes and etc.
    Scene can have sub-scenes, acts as multiple-document support in files like collada/blender/fbx
    Node hierarchy can be accessed through :py:attr:`aspose.threed.Scene.root_node`:py:attr:`aspose.threed.Scene.library` is used to keep a reference of unattached objects during serialization(like meta data or custom objects) so it can be used as a library.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Scene` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, entity : aspose.threed.Entity) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Scene` class with an entity attached to a new node.
        
        :param entity: The initial entity that attached to the scene'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, parent_scene : aspose.threed.Scene, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.Scene` class as a sub-scene.
        
        :param parent_scene: The parent scene.
        :param name: Scene\'s name.'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def open(self, stream : io._IOBase) -> None:
        '''Opens the scene from given stream
        
        :param stream: Input stream, user is responsible for closing the stream.'''
        raise NotImplementedError()
    
    @overload
    def open(self, file_name : str, options : aspose.threed.formats.LoadOptions) -> None:
        '''Opens the scene from given path using specified file format.
        
        :param file_name: File name.
        :param options: More detailed configuration to open the stream.'''
        raise NotImplementedError()
    
    @overload
    def open(self, file_name : str) -> None:
        '''Opens the scene from given path
        
        :param file_name: File name.'''
        raise NotImplementedError()
    
    @overload
    def save(self, stream : io._IOBase, format : aspose.threed.FileFormat) -> None:
        '''Saves the scene to stream using specified file format.
        
        :param stream: Input stream, user is responsible for closing the stream.
        :param format: Format.'''
        raise NotImplementedError()
    
    @overload
    def save(self, stream : io._IOBase, options : aspose.threed.formats.SaveOptions) -> None:
        '''Saves the scene to stream using specified file format.
        
        :param stream: Input stream, user is responsible for closing the stream.
        :param options: More detailed configuration to save the stream.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str) -> None:
        '''Saves the scene to specified path using specified file format.
        
        :param file_name: File name.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str, format : aspose.threed.FileFormat) -> None:
        '''Saves the scene to specified path using specified file format.
        
        :param file_name: File name.
        :param format: Format.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str, options : aspose.threed.formats.SaveOptions) -> None:
        '''Saves the scene to specified path using specified file format.
        
        :param file_name: File name.
        :param options: More detailed configuration to save the stream.'''
        raise NotImplementedError()
    
    @overload
    def render(self, camera : aspose.threed.entities.Camera, file_name : str) -> None:
        '''Render the scene into external file from given camera\'s perspective.
        The default output size is 1024x768 and output format is png
        
        :param camera: From which camera\'s perspective to render the scene
        :param file_name: The file name of output file'''
        raise NotImplementedError()
    
    @overload
    def render(self, camera : aspose.threed.entities.Camera, file_name : str, size : aspose.threed.utilities.Vector2, format : str) -> None:
        '''Render the scene into external file from given camera\'s perspective.
        
        :param camera: From which camera\'s perspective to render the scene
        :param file_name: The file name of output file
        :param size: The size of final rendered image
        :param format: The image format of the output file'''
        raise NotImplementedError()
    
    @overload
    def render(self, camera : aspose.threed.entities.Camera, file_name : str, size : aspose.threed.utilities.Vector2, format : str, options : aspose.threed.ImageRenderOptions) -> None:
        '''Render the scene into external file from given camera\'s perspective.
        
        :param camera: From which camera\'s perspective to render the scene
        :param file_name: The file name of output file
        :param size: The size of final rendered image
        :param format: The image format of the output file
        :param options: The option to customize some internal settings.'''
        raise NotImplementedError()
    
    @overload
    def render(self, camera : aspose.threed.entities.Camera, bitmap : aspose.threed.render.TextureData) -> None:
        '''Render the scene into bitmap from given camera\'s perspective.
        
        :param camera: From which camera\'s perspective to render the scene
        :param bitmap: Target of the rendered result'''
        raise NotImplementedError()
    
    @overload
    def render(self, camera : aspose.threed.entities.Camera, bitmap : aspose.threed.render.TextureData, options : aspose.threed.ImageRenderOptions) -> None:
        '''Render the scene into bitmap from given camera\'s perspective.
        
        :param camera: From which camera\'s perspective to render the scene
        :param bitmap: Target of the rendered result
        :param options: The option to customize some internal settings.'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    def get_animation_clip(self, name : str) -> aspose.threed.animation.AnimationClip:
        '''Gets a named :py:class:`aspose.threed.animation.AnimationClip`
        
        :param name: The :py:class:`aspose.threed.animation.AnimationClip`\'s name to look up
        :returns: Returned AnimationClip'''
        raise NotImplementedError()
    
    def clear(self) -> None:
        '''Clears the scene content and restores the default settings.'''
        raise NotImplementedError()
    
    def create_animation_clip(self, name : str) -> aspose.threed.animation.AnimationClip:
        '''A shorthand function to create and register the :py:class:`aspose.threed.animation.AnimationClip`
        The first :py:class:`aspose.threed.animation.AnimationClip` will be assigned to the :py:attr:`aspose.threed.Scene.current_animation_clip`
        
        :param name: Animation clip\'s name
        :returns: A new animation clip instance with given name'''
        raise NotImplementedError()
    
    @staticmethod
    def from_file(file_name : str) -> aspose.threed.Scene:
        '''Opens the scene from given path
        
        :param file_name: File name.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def scene(self) -> aspose.threed.Scene:
        '''Gets the scene that this object belongs to'''
        raise NotImplementedError()
    
    @property
    def sub_scenes(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Scene]]:
        '''Gets all sub-scenes'''
        raise NotImplementedError()
    
    @property
    def library(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.A3DObject]]:
        '''Objects that not directly used in scene hierarchy can be defined in Library.
        This is useful when you\'re using sub-scenes and put reusable components under sub-scenes.'''
        raise NotImplementedError()
    
    @property
    def animation_clips(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.AnimationClip]]:
        '''Gets all :py:class:`aspose.threed.animation.AnimationClip` defined in the scene.'''
        raise NotImplementedError()
    
    @property
    def current_animation_clip(self) -> aspose.threed.animation.AnimationClip:
        '''Gets the active :py:class:`aspose.threed.animation.AnimationClip`'''
        raise NotImplementedError()
    
    @current_animation_clip.setter
    def current_animation_clip(self, value : aspose.threed.animation.AnimationClip) -> None:
        '''Sets the active :py:class:`aspose.threed.animation.AnimationClip`'''
        raise NotImplementedError()
    
    @property
    def asset_info(self) -> aspose.threed.AssetInfo:
        '''Gets the top-level asset information'''
        raise NotImplementedError()
    
    @asset_info.setter
    def asset_info(self, value : aspose.threed.AssetInfo) -> None:
        '''Sets the top-level asset information'''
        raise NotImplementedError()
    
    @property
    def poses(self) -> System.Collections.Generic.ICollection`1[[Aspose.ThreeD.Pose]]:
        '''Gets all :py:class:`aspose.threed.Pose` used in this scene.'''
        raise NotImplementedError()
    
    @property
    def root_node(self) -> aspose.threed.Node:
        '''Gets the root node of the scene.'''
        raise NotImplementedError()
    
    @property
    def VERSION(self) -> str:
        '''Gets the current release version'''
        raise NotImplementedError()


class SceneObject(A3DObject):
    '''The root class of objects that will be stored inside a scene.'''
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def scene(self) -> aspose.threed.Scene:
        '''Gets the scene that this object belongs to'''
        raise NotImplementedError()
    

class Transform(A3DObject):
    '''A transform contains information that allow access to object\'s translate/scale/rotation or transform matrix at minimum cost
    This is used by local transform.'''
    
    @overload
    def remove_property(self, property : aspose.threed.Property) -> bool:
        '''Removes a dynamic property.
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    @overload
    def remove_property(self, property : str) -> bool:
        '''Remove the specified property identified by name
        
        :param property: Which property to remove
        :returns: true if the property is successfully removed'''
        raise NotImplementedError()
    
    def get_property(self, property : str) -> Any:
        '''Get the value of specified property
        
        :param property: Property name
        :returns: The value of the found property'''
        raise NotImplementedError()
    
    def set_property(self, property : str, value : Any) -> None:
        '''Sets the value of specified property
        
        :param property: Property name
        :param value: The value of the property'''
        raise NotImplementedError()
    
    def find_property(self, property_name : str) -> aspose.threed.Property:
        '''Finds the property.
        It can be a dynamic property (Created by CreateDynamicProperty/SetProperty)
        or native property(Identified by its name)
        
        :param property_name: Property name.
        :returns: The property.'''
        raise NotImplementedError()
    
    def set_geometric_translation(self, x : float, y : float, z : float) -> aspose.threed.Transform:
        '''Sets the geometric translation.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    def set_geometric_scaling(self, sx : float, sy : float, sz : float) -> aspose.threed.Transform:
        '''Sets the geometric scaling.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    def set_geometric_rotation(self, rx : float, ry : float, rz : float) -> aspose.threed.Transform:
        '''Sets the geometric Euler rotation(measured in degree).
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    def set_translation(self, tx : float, ty : float, tz : float) -> aspose.threed.Transform:
        '''Sets the translation of current transform.'''
        raise NotImplementedError()
    
    def set_scale(self, sx : float, sy : float, sz : float) -> aspose.threed.Transform:
        '''Sets the scale of current transform.'''
        raise NotImplementedError()
    
    def set_euler_angles(self, rx : float, ry : float, rz : float) -> aspose.threed.Transform:
        '''Sets the Euler angles in degrees of current transform.'''
        raise NotImplementedError()
    
    def set_rotation(self, rw : float, rx : float, ry : float, rz : float) -> aspose.threed.Transform:
        '''Sets the rotation(as quaternion components) of current transform.'''
        raise NotImplementedError()
    
    def set_pre_rotation(self, rx : float, ry : float, rz : float) -> aspose.threed.Transform:
        '''Sets the pre-rotation represented in degree'''
        raise NotImplementedError()
    
    def set_post_rotation(self, rx : float, ry : float, rz : float) -> aspose.threed.Transform:
        '''Sets the post-rotation represented in degree'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def properties(self) -> aspose.threed.PropertyCollection:
        '''Gets the collection of all properties.'''
        raise NotImplementedError()
    
    @property
    def geometric_translation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the geometric translation.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @geometric_translation.setter
    def geometric_translation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the geometric translation.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @property
    def geometric_scaling(self) -> aspose.threed.utilities.Vector3:
        '''Gets the geometric scaling.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @geometric_scaling.setter
    def geometric_scaling(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the geometric scaling.
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @property
    def geometric_rotation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the geometric Euler rotation(measured in degree).
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @geometric_rotation.setter
    def geometric_rotation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the geometric Euler rotation(measured in degree).
        Geometric transformation only affects the entities attached and leave the child nodes unaffected.
        It will be merged as local transformation when you export the geometric transformation to file types that does not support it.'''
        raise NotImplementedError()
    
    @property
    def translation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the translation'''
        raise NotImplementedError()
    
    @translation.setter
    def translation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the translation'''
        raise NotImplementedError()
    
    @property
    def scaling(self) -> aspose.threed.utilities.Vector3:
        '''Gets the scaling'''
        raise NotImplementedError()
    
    @scaling.setter
    def scaling(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the scaling'''
        raise NotImplementedError()
    
    @property
    def scaling_offset(self) -> aspose.threed.utilities.Vector3:
        '''Gets the scaling offset'''
        raise NotImplementedError()
    
    @scaling_offset.setter
    def scaling_offset(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the scaling offset'''
        raise NotImplementedError()
    
    @property
    def scaling_pivot(self) -> aspose.threed.utilities.Vector3:
        '''Gets the scaling pivot'''
        raise NotImplementedError()
    
    @scaling_pivot.setter
    def scaling_pivot(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the scaling pivot'''
        raise NotImplementedError()
    
    @property
    def pre_rotation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the pre-rotation represented in degree'''
        raise NotImplementedError()
    
    @pre_rotation.setter
    def pre_rotation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the pre-rotation represented in degree'''
        raise NotImplementedError()
    
    @property
    def rotation_offset(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation offset'''
        raise NotImplementedError()
    
    @rotation_offset.setter
    def rotation_offset(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the rotation offset'''
        raise NotImplementedError()
    
    @property
    def rotation_pivot(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation pivot'''
        raise NotImplementedError()
    
    @rotation_pivot.setter
    def rotation_pivot(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the rotation pivot'''
        raise NotImplementedError()
    
    @property
    def post_rotation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the post-rotation represented in degree'''
        raise NotImplementedError()
    
    @post_rotation.setter
    def post_rotation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the post-rotation represented in degree'''
        raise NotImplementedError()
    
    @property
    def euler_angles(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation represented in Euler angles, measured in degree'''
        raise NotImplementedError()
    
    @euler_angles.setter
    def euler_angles(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the rotation represented in Euler angles, measured in degree'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> aspose.threed.utilities.Quaternion:
        '''Gets the rotation represented in quaternion.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : aspose.threed.utilities.Quaternion) -> None:
        '''Sets the rotation represented in quaternion.'''
        raise NotImplementedError()
    
    @property
    def transform_matrix(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the transform matrix.'''
        raise NotImplementedError()
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.threed.utilities.Matrix4) -> None:
        '''Sets the transform matrix.'''
        raise NotImplementedError()
    

class TrialException:
    '''This is raised in Scene.Open/Scene.Save when no licenses are applied.
    You can turn off this exception by setting SuppressTrialException to true.'''
    
    @overload
    def __init__(self, msg : str) -> None:
        '''Constructor of :py:class:`aspose.threed.TrialException`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.TrialException`'''
        raise NotImplementedError()
    
    @staticmethod
    def set_suppress_trial_exception(value: bool) -> None:
        '''Sets this to true to suppress trial exception for unlicensed usage, but the restrictions will not be lifted.
        In order to lift the restrictions, please use a proper license.
        And sets this to true also means you\'re aware of the unlicensed restrictions.'''
    @property
    def suppress_trial_exception(self) -> bool:
        '''Sets this to true to suppress trial exception for unlicensed usage, but the restrictions will not be lifted.
        In order to lift the restrictions, please use a proper license.
        And sets this to true also means you\'re aware of the unlicensed restrictions.'''
        raise NotImplementedError()


class Axis:
    '''The coordinate axis.'''
    
    X_AXIS : Axis
    '''The +X axis.'''
    Y_AXIS : Axis
    '''The +Y axis.'''
    Z_AXIS : Axis
    '''The +Z axis.'''
    NEGATIVE_X_AXIS : Axis
    '''The -X axis.'''
    NEGATIVE_Y_AXIS : Axis
    '''The -Y axis.'''
    NEGATIVE_Z_AXIS : Axis
    '''The -Z axis.'''

class CoordinateSystem:
    '''The left handed or right handed coordinate system.'''
    
    RIGHT_HANDED : CoordinateSystem
    '''The right handed.'''
    LEFT_HANDED : CoordinateSystem
    '''The left handed.'''

class FileContentType:
    '''File content type'''
    
    BINARY : FileContentType
    '''Binary format type, such as binary FBX, binary STL'''
    ASCII : FileContentType
    '''ASCII format type, such as ASCII FBX, ASCII STL'''

class PoseType:
    '''Pose type.'''
    
    BIND_POSE : PoseType
    '''The bind pose.'''
    SNAPSHOT : PoseType
    '''The rest pose, means it\'s a snapshot of the bind pose.'''

class PropertyFlags:
    '''Property\'s flags'''
    
    NONE : PropertyFlags
    '''The property has no flags'''
    NOT_SERIALIZABLE : PropertyFlags
    '''This property is not serializable'''
    USER_DEFINED : PropertyFlags
    '''This is a user defined property'''
    ANIMATABLE : PropertyFlags
    '''The property is animatable'''
    ANIMATED : PropertyFlags
    '''The property is animated'''
    HIDDEN : PropertyFlags
    '''The property is marked as hidden.'''

