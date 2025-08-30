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

class Bone(aspose.threed.A3DObject):
    '''A bone defines the subset of the geometry\'s control point, and defined blend weight for each control point.
    The :py:class:`aspose.threed.deformers.Bone` object cannot be used directly, a :py:class:`aspose.threed.deformers.SkinDeformer` instance is used to deform the geometry, and :py:class:`aspose.threed.deformers.SkinDeformer` comes with a set of bones, each bone linked to a node.
    NOTE: A control point of a geometry can be bounded to more than one Bones.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.Bone` class.
        
        :param name: Name.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.Bone` class.'''
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
    
    def get_weight(self, index : int) -> float:
        '''Gets the weight for control point specified by index
        
        :param index: Control point\'s index
        :returns: the weight at specified index, or 0 if the index is invalid'''
        raise NotImplementedError()
    
    def set_weight(self, index : int, weight : float) -> None:
        '''Sets the weight for control point specified by index
        
        :param index: Control point\'s index
        :param weight: New weight'''
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
    def link_mode(self) -> aspose.threed.deformers.BoneLinkMode:
        '''A bone\'s link mode refers to the way in which a bone is connected or linked to its parent bone within a hierarchical structure.'''
        raise NotImplementedError()
    
    @link_mode.setter
    def link_mode(self, value : aspose.threed.deformers.BoneLinkMode) -> None:
        '''A bone\'s link mode refers to the way in which a bone is connected or linked to its parent bone within a hierarchical structure.'''
        raise NotImplementedError()
    
    @property
    def weight_count(self) -> int:
        '''Gets the count of weight, this is automatically extended by :py:func:`aspose.threed.deformers.Bone.set_weight`'''
        raise NotImplementedError()
    
    @property
    def transform(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the transform matrix of the node containing the bone.'''
        raise NotImplementedError()
    
    @transform.setter
    def transform(self, value : aspose.threed.utilities.Matrix4) -> None:
        '''Sets the transform matrix of the node containing the bone.'''
        raise NotImplementedError()
    
    @property
    def bone_transform(self) -> aspose.threed.utilities.Matrix4:
        '''Gets the transform matrix of the bone.'''
        raise NotImplementedError()
    
    @bone_transform.setter
    def bone_transform(self, value : aspose.threed.utilities.Matrix4) -> None:
        '''Sets the transform matrix of the bone.'''
        raise NotImplementedError()
    
    @property
    def node(self) -> aspose.threed.Node:
        '''Gets the node. The bone node is the bone which skin attached to, the :py:class:`aspose.threed.deformers.SkinDeformer` will use bone node to influence the displacement of the control points.
        Bone node usually has a :py:class:`aspose.threed.entities.Skeleton` attached, but it\'s not required.
        Attached :py:class:`aspose.threed.entities.Skeleton` is usually used by DCC software to show skeleton to user.'''
        raise NotImplementedError()
    
    @node.setter
    def node(self, value : aspose.threed.Node) -> None:
        '''Sets the node. The bone node is the bone which skin attached to, the :py:class:`aspose.threed.deformers.SkinDeformer` will use bone node to influence the displacement of the control points.
        Bone node usually has a :py:class:`aspose.threed.entities.Skeleton` attached, but it\'s not required.
        Attached :py:class:`aspose.threed.entities.Skeleton` is usually used by DCC software to show skeleton to user.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> float:
        raise NotImplementedError()
    
    def __setitem__(self, key : int, value : float):
        raise NotImplementedError()
    

class Deformer(aspose.threed.A3DObject):
    '''Base class for :py:class:`aspose.threed.deformers.SkinDeformer` and :py:class:`aspose.threed.deformers.MorphTargetDeformer`'''
    
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
    def owner(self) -> aspose.threed.entities.Geometry:
        '''Gets the geometry which owns this deformer'''
        raise NotImplementedError()
    

class MorphTargetChannel(aspose.threed.A3DObject):
    '''A MorphTargetChannel is used by :py:class:`aspose.threed.deformers.MorphTargetDeformer` to organize the target geometries.
    Some file formats like FBX support multiple channels in parallel.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.MorphTargetChannel` class.
        
        :param name: Name.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.MorphTargetChannel` class.'''
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
    
    def get_weight(self, target : aspose.threed.entities.Shape) -> float:
        '''Gets the weight for the specified target, if the target is not belongs to this channel, default value 0 is returned.'''
        raise NotImplementedError()
    
    def set_weight(self, target : aspose.threed.entities.Shape, weight : float) -> None:
        '''Sets the weight for the specified target, default value is 1, range should between 0~1'''
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
    def weights(self) -> System.Collections.Generic.IList`1[[System.Double]]:
        '''Gets the full weight values of target geometries.'''
        raise NotImplementedError()
    
    @property
    def channel_weight(self) -> float:
        '''Gets the deformer weight of this channel.
        The weight is between 0.0 and 1.0'''
        raise NotImplementedError()
    
    @channel_weight.setter
    def channel_weight(self, value : float) -> None:
        '''Sets the deformer weight of this channel.
        The weight is between 0.0 and 1.0'''
        raise NotImplementedError()
    
    @property
    def targets(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Entities.Shape]]:
        '''Gets all targets associated with the channel.'''
        raise NotImplementedError()
    
    @property
    def DEFAULT_WEIGHT(self) -> float:
        '''Default weight for morph target.'''
        raise NotImplementedError()


class MorphTargetDeformer(Deformer):
    '''MorphTargetDeformer provides per-vertex animation.
    MorphTargetDeformer organize all targets via :py:class:`aspose.threed.deformers.MorphTargetChannel`, each channel can organize multiple targets.
    A common use of morph target deformer is to apply facial expression to a character.
    More details can be found at https://en.wikipedia.org/wiki/Morph_target_animation'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.MorphTargetDeformer` class.
        
        :param name: Name.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.MorphTargetDeformer` class.'''
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
    def owner(self) -> aspose.threed.entities.Geometry:
        '''Gets the geometry which owns this deformer'''
        raise NotImplementedError()
    
    @property
    def channels(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Deformers.MorphTargetChannel]]:
        '''Gets all channels contained in this deformer'''
        raise NotImplementedError()
    

class SkinDeformer(Deformer):
    '''A skin deformer contains multiple bones to work, each bone blends a part of the geometry by control point\'s weights.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.SkinDeformer` class.
        
        :param name: Name.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.deformers.SkinDeformer` class.'''
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
    def owner(self) -> aspose.threed.entities.Geometry:
        '''Gets the geometry which owns this deformer'''
        raise NotImplementedError()
    
    @property
    def bones(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Deformers.Bone]]:
        '''Gets all bones that the skin deformer contains'''
        raise NotImplementedError()
    

class BoneLinkMode:
    '''A bone\'s link mode refers to the way in which a bone is connected or linked to its parent bone within a hierarchical structure.'''
    
    NORMALIZE : BoneLinkMode
    '''In this mode, the transformations of child bones are normalized concerning their parent bone\'s transformations.'''
    ADDITIVE : BoneLinkMode
    '''Additive mode calculates the transformations of child bones by adding their own local transformations to those of their parent bones.'''
    TOTAL_ONE : BoneLinkMode
    '''Total One ensures that combined transformations of the parent and child bones result in a combined transformation that scales to an overall length of one unit.'''

