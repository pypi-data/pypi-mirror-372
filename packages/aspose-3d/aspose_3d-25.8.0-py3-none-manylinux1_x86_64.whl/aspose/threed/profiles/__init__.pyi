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

class ArbitraryProfile(Profile):
    '''This class allows you to construct a 2D profile directly from arbitrary curve.'''
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.ArbitraryProfile`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, curve : aspose.threed.entities.Curve) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.ArbitraryProfile` with an initial curve.
        
        :param curve: Initial curve of the profile'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
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
    
    @property
    def curve(self) -> aspose.threed.entities.Curve:
        '''The Curve used to construct the profile'''
        raise NotImplementedError()
    
    @curve.setter
    def curve(self, value : aspose.threed.entities.Curve) -> None:
        '''The Curve used to construct the profile'''
        raise NotImplementedError()
    
    @property
    def holes(self) -> System.Collections.Generic.List`1[[Aspose.ThreeD.Entities.Curve]]:
        '''Holes of the profile, also represented as curve'''
        raise NotImplementedError()
    

class CShape(ParameterizedProfile):
    '''IFC compatible C-shape profile that defined by parameters.
    The center position of the profile is in the center of the bounding box.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.CShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def depth(self) -> float:
        '''Gets the depth of the profile.'''
        raise NotImplementedError()
    
    @depth.setter
    def depth(self, value : float) -> None:
        '''Sets the depth of the profile.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of the profile.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of the profile.'''
        raise NotImplementedError()
    
    @property
    def girth(self) -> float:
        '''Gets the length of girth.'''
        raise NotImplementedError()
    
    @girth.setter
    def girth(self, value : float) -> None:
        '''Sets the length of girth.'''
        raise NotImplementedError()
    
    @property
    def wall_thickness(self) -> float:
        '''Gets the thickness of the wall.'''
        raise NotImplementedError()
    
    @wall_thickness.setter
    def wall_thickness(self, value : float) -> None:
        '''Sets the thickness of the wall.'''
        raise NotImplementedError()
    
    @property
    def internal_fillet_radius(self) -> float:
        '''Gets the internal fillet radius.'''
        raise NotImplementedError()
    
    @internal_fillet_radius.setter
    def internal_fillet_radius(self, value : float) -> None:
        '''Sets the internal fillet radius.'''
        raise NotImplementedError()
    

class CenterLineProfile(Profile):
    '''IFC compatible center line profile'''
    
    def __init__(self, curve : aspose.threed.entities.Curve, thickness : float) -> None:
        '''Constructs a new :py:class:`aspose.threed.profiles.CenterLineProfile` with specified curve as center line.
        
        :param curve: Center line curve
        :param thickness: Thickness applied along the center line'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
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
    
    @property
    def thickness(self) -> float:
        '''Thickness applied along the center line'''
        raise NotImplementedError()
    
    @thickness.setter
    def thickness(self, value : float) -> None:
        '''Thickness applied along the center line'''
        raise NotImplementedError()
    
    @property
    def curve(self) -> aspose.threed.entities.Curve:
        '''The center line curve of the profile'''
        raise NotImplementedError()
    
    @curve.setter
    def curve(self, value : aspose.threed.entities.Curve) -> None:
        '''The center line curve of the profile'''
        raise NotImplementedError()
    

class CircleShape(ParameterizedProfile):
    '''IFC compatible circle profile, which can be used to construct a mesh through :py:class:`aspose.threed.entities.LinearExtrusion`'''
    
    @overload
    def __init__(self) -> None:
        '''Construct a :py:class:`aspose.threed.profiles.CircleShape` profile with default radius(5).'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, radius : float) -> None:
        '''Construct a :py:class:`aspose.threed.profiles.CircleShape` profile with specified radius.
        
        :param radius: Radius of the circle'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def radius(self) -> float:
        '''Gets the radius of the circle.'''
        raise NotImplementedError()
    
    @radius.setter
    def radius(self, value : float) -> None:
        '''Sets the radius of the circle.'''
        raise NotImplementedError()
    

class EllipseShape(ParameterizedProfile):
    '''IFC compatible ellipse shape that defined by parameters.
    The center position of the profile is in the center of the bounding box.'''
    
    def __init__(self) -> None:
        '''Initialize an SceneObject.'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def semi_axis1(self) -> float:
        '''Gets the first radius of the ellipse that measured in the direction of x axis.'''
        raise NotImplementedError()
    
    @semi_axis1.setter
    def semi_axis1(self, value : float) -> None:
        '''Sets the first radius of the ellipse that measured in the direction of x axis.'''
        raise NotImplementedError()
    
    @property
    def semi_axis2(self) -> float:
        '''Gets the second radius of the ellipse that measured in the direction of y axis.'''
        raise NotImplementedError()
    
    @semi_axis2.setter
    def semi_axis2(self, value : float) -> None:
        '''Sets the second radius of the ellipse that measured in the direction of y axis.'''
        raise NotImplementedError()
    

class FontFile(aspose.threed.A3DObject):
    '''Font file contains definitions for glyphs, this is used to create text profile.'''
    
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
    
    @staticmethod
    def from_file(file_name : str) -> aspose.threed.profiles.FontFile:
        '''Load FontFile from file name
        
        :param file_name: Path to the font file
        :returns: FontFile instance'''
        raise NotImplementedError()
    
    @staticmethod
    def parse(bytes : List[int]) -> aspose.threed.profiles.FontFile:
        '''Parse FontFile from bytes
        
        :param bytes: OTF font file raw content
        :returns: FontFile instance'''
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
    

class HShape(ParameterizedProfile):
    '''The :py:class:`aspose.threed.profiles.HShape` provides the defining parameters of an \'H\' or \'I\' shape.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.HShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def overall_depth(self) -> float:
        '''Gets the extent of the depth.'''
        raise NotImplementedError()
    
    @overall_depth.setter
    def overall_depth(self, value : float) -> None:
        '''Sets the extent of the depth.'''
        raise NotImplementedError()
    
    @property
    def bottom_flange_width(self) -> float:
        '''Gets the extent of the width.'''
        raise NotImplementedError()
    
    @bottom_flange_width.setter
    def bottom_flange_width(self, value : float) -> None:
        '''Sets the extent of the width.'''
        raise NotImplementedError()
    
    @property
    def top_flange_width(self) -> float:
        '''Gets the width of the top flange.'''
        raise NotImplementedError()
    
    @top_flange_width.setter
    def top_flange_width(self, value : float) -> None:
        '''Sets the width of the top flange.'''
        raise NotImplementedError()
    
    @property
    def top_flange_thickness(self) -> float:
        '''Gets the thickness of the top flange.'''
        raise NotImplementedError()
    
    @top_flange_thickness.setter
    def top_flange_thickness(self, value : float) -> None:
        '''Sets the thickness of the top flange.'''
        raise NotImplementedError()
    
    @property
    def top_flange_edge_radius(self) -> float:
        '''Gets the radius of the lower edges of the top flange.'''
        raise NotImplementedError()
    
    @top_flange_edge_radius.setter
    def top_flange_edge_radius(self, value : float) -> None:
        '''Sets the radius of the lower edges of the top flange.'''
        raise NotImplementedError()
    
    @property
    def top_flange_fillet_radius(self) -> float:
        '''Gets the radius of fillet between the web and the top flange.'''
        raise NotImplementedError()
    
    @top_flange_fillet_radius.setter
    def top_flange_fillet_radius(self, value : float) -> None:
        '''Sets the radius of fillet between the web and the top flange.'''
        raise NotImplementedError()
    
    @property
    def bottom_flange_thickness(self) -> float:
        '''Gets the flange thickness of H-shape.'''
        raise NotImplementedError()
    
    @bottom_flange_thickness.setter
    def bottom_flange_thickness(self, value : float) -> None:
        '''Sets the flange thickness of H-shape.'''
        raise NotImplementedError()
    
    @property
    def web_thickness(self) -> float:
        '''Gets the thickness of the web of the H-shape.'''
        raise NotImplementedError()
    
    @web_thickness.setter
    def web_thickness(self, value : float) -> None:
        '''Sets the thickness of the web of the H-shape.'''
        raise NotImplementedError()
    
    @property
    def bottom_flange_fillet_radius(self) -> float:
        '''Gets the radius of fillet between the web and the bottom flange.'''
        raise NotImplementedError()
    
    @bottom_flange_fillet_radius.setter
    def bottom_flange_fillet_radius(self, value : float) -> None:
        '''Sets the radius of fillet between the web and the bottom flange.'''
        raise NotImplementedError()
    
    @property
    def bottom_flange_edge_radius(self) -> float:
        '''Gets the radius of the upper edges of the bottom flange.'''
        raise NotImplementedError()
    
    @bottom_flange_edge_radius.setter
    def bottom_flange_edge_radius(self, value : float) -> None:
        '''Sets the radius of the upper edges of the bottom flange.'''
        raise NotImplementedError()
    

class HollowCircleShape(CircleShape):
    '''IFC compatible hollow circle profile.'''
    
    def __init__(self) -> None:
        '''Construct a :py:class:`aspose.threed.profiles.CircleShape` profile with default radius(5).'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def radius(self) -> float:
        '''Gets the radius of the circle.'''
        raise NotImplementedError()
    
    @radius.setter
    def radius(self, value : float) -> None:
        '''Sets the radius of the circle.'''
        raise NotImplementedError()
    
    @property
    def wall_thickness(self) -> float:
        '''Gets the difference between the outer and inner radius.'''
        raise NotImplementedError()
    
    @wall_thickness.setter
    def wall_thickness(self, value : float) -> None:
        '''Sets the difference between the outer and inner radius.'''
        raise NotImplementedError()
    

class HollowRectangleShape(RectangleShape):
    '''IFC compatible hollow rectangular shape with both inner/outer rounding corners.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.RectangleShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def rounding_radius(self) -> float:
        '''Gets the radius of the circular arcs of all four corners, measured in degrees.
        Default value is 0.0'''
        raise NotImplementedError()
    
    @rounding_radius.setter
    def rounding_radius(self, value : float) -> None:
        '''Sets the radius of the circular arcs of all four corners, measured in degrees.
        Default value is 0.0'''
        raise NotImplementedError()
    
    @property
    def x_dim(self) -> float:
        '''Gets the extent of the rectangle in the direction of x-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @x_dim.setter
    def x_dim(self, value : float) -> None:
        '''Sets the extent of the rectangle in the direction of x-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @property
    def y_dim(self) -> float:
        '''Gets the extent of the rectangle in the direction of y-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @y_dim.setter
    def y_dim(self, value : float) -> None:
        '''Sets the extent of the rectangle in the direction of y-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @property
    def wall_thickness(self) -> float:
        '''The thickness between the boundary of the rectangle and the inner hole'''
        raise NotImplementedError()
    
    @wall_thickness.setter
    def wall_thickness(self, value : float) -> None:
        '''The thickness between the boundary of the rectangle and the inner hole'''
        raise NotImplementedError()
    
    @property
    def inner_fillet_radius(self) -> float:
        '''The inner fillet radius of the inner rectangle.'''
        raise NotImplementedError()
    
    @inner_fillet_radius.setter
    def inner_fillet_radius(self, value : float) -> None:
        '''The inner fillet radius of the inner rectangle.'''
        raise NotImplementedError()
    

class LShape(ParameterizedProfile):
    '''IFC compatible L-shape profile that defined by parameters.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.LShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def depth(self) -> float:
        '''Gets the depth of the profile.'''
        raise NotImplementedError()
    
    @depth.setter
    def depth(self, value : float) -> None:
        '''Sets the depth of the profile.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of the profile.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of the profile.'''
        raise NotImplementedError()
    
    @property
    def thickness(self) -> float:
        '''Gets the thickness of the constant wall.'''
        raise NotImplementedError()
    
    @thickness.setter
    def thickness(self, value : float) -> None:
        '''Sets the thickness of the constant wall.'''
        raise NotImplementedError()
    
    @property
    def fillet_radius(self) -> float:
        '''Gets the radius of the fillet.'''
        raise NotImplementedError()
    
    @fillet_radius.setter
    def fillet_radius(self, value : float) -> None:
        '''Sets the radius of the fillet.'''
        raise NotImplementedError()
    
    @property
    def edge_radius(self) -> float:
        '''Gets the radius of the edge.'''
        raise NotImplementedError()
    
    @edge_radius.setter
    def edge_radius(self, value : float) -> None:
        '''Sets the radius of the edge.'''
        raise NotImplementedError()
    

class MirroredProfile(Profile):
    '''IFC compatible mirror profile.
    This profile defines a new profile by mirroring the base profile about the y axis.'''
    
    def __init__(self, base_profile : aspose.threed.profiles.Profile) -> None:
        '''Construct a new :py:class:`aspose.threed.profiles.MirroredProfile` from an existing profile.
        
        :param base_profile: The base profile to be mirrored.'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
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
    
    @property
    def base_profile(self) -> aspose.threed.profiles.Profile:
        '''The base profile to be mirrored.'''
        raise NotImplementedError()
    

class ParameterizedProfile(Profile):
    '''The base class of all parameterized profiles.'''
    
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
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.
        
        :returns: The extent of the profile'''
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
    

class Profile(aspose.threed.Entity):
    '''2D Profile in xy plane'''
    
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
        '''Gets the key of the entity renderer registered in the renderer'''
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
    

class RectangleShape(ParameterizedProfile):
    '''IFC compatible rectangular shape with rounding corners.'''
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.RectangleShape`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, xdim : float, ydim : float) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.RectangleShape` with specified dimension on x and y axis.'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def rounding_radius(self) -> float:
        '''Gets the radius of the circular arcs of all four corners, measured in degrees.
        Default value is 0.0'''
        raise NotImplementedError()
    
    @rounding_radius.setter
    def rounding_radius(self, value : float) -> None:
        '''Sets the radius of the circular arcs of all four corners, measured in degrees.
        Default value is 0.0'''
        raise NotImplementedError()
    
    @property
    def x_dim(self) -> float:
        '''Gets the extent of the rectangle in the direction of x-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @x_dim.setter
    def x_dim(self, value : float) -> None:
        '''Sets the extent of the rectangle in the direction of x-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @property
    def y_dim(self) -> float:
        '''Gets the extent of the rectangle in the direction of y-axis
        Default value is 2.0'''
        raise NotImplementedError()
    
    @y_dim.setter
    def y_dim(self, value : float) -> None:
        '''Sets the extent of the rectangle in the direction of y-axis
        Default value is 2.0'''
        raise NotImplementedError()
    

class TShape(ParameterizedProfile):
    '''IFC compatible T-shape defined by parameters.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.TShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def depth(self) -> float:
        '''Gets the length of the web.'''
        raise NotImplementedError()
    
    @depth.setter
    def depth(self, value : float) -> None:
        '''Sets the length of the web.'''
        raise NotImplementedError()
    
    @property
    def flange_width(self) -> float:
        '''Gets the length of the flange.'''
        raise NotImplementedError()
    
    @flange_width.setter
    def flange_width(self, value : float) -> None:
        '''Sets the length of the flange.'''
        raise NotImplementedError()
    
    @property
    def web_thickness(self) -> float:
        '''Gets the wall thickness of web.'''
        raise NotImplementedError()
    
    @web_thickness.setter
    def web_thickness(self, value : float) -> None:
        '''Sets the wall thickness of web.'''
        raise NotImplementedError()
    
    @property
    def flange_thickness(self) -> float:
        '''Gets the wall thickness of flange.'''
        raise NotImplementedError()
    
    @flange_thickness.setter
    def flange_thickness(self, value : float) -> None:
        '''Sets the wall thickness of flange.'''
        raise NotImplementedError()
    
    @property
    def fillet_radius(self) -> float:
        '''Gets the radius of fillet between web and flange.'''
        raise NotImplementedError()
    
    @fillet_radius.setter
    def fillet_radius(self, value : float) -> None:
        '''Sets the radius of fillet between web and flange.'''
        raise NotImplementedError()
    
    @property
    def flange_edge_radius(self) -> float:
        '''Gets the radius of the flange edge.'''
        raise NotImplementedError()
    
    @flange_edge_radius.setter
    def flange_edge_radius(self, value : float) -> None:
        '''Sets the radius of the flange edge.'''
        raise NotImplementedError()
    
    @property
    def web_edge_radius(self) -> float:
        '''Gets the radius of web edge.'''
        raise NotImplementedError()
    
    @web_edge_radius.setter
    def web_edge_radius(self, value : float) -> None:
        '''Sets the radius of web edge.'''
        raise NotImplementedError()
    

class Text(Profile):
    '''Text profile, this profile describes contours using font and text.'''
    
    def __init__(self) -> None:
        '''Initialize an SceneObject.'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
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
    
    @property
    def content(self) -> str:
        '''Content of the text'''
        raise NotImplementedError()
    
    @content.setter
    def content(self, value : str) -> None:
        '''Content of the text'''
        raise NotImplementedError()
    
    @property
    def font(self) -> aspose.threed.profiles.FontFile:
        '''The font of the text.'''
        raise NotImplementedError()
    
    @font.setter
    def font(self, value : aspose.threed.profiles.FontFile) -> None:
        '''The font of the text.'''
        raise NotImplementedError()
    
    @property
    def font_size(self) -> float:
        '''Font size scale.'''
        raise NotImplementedError()
    
    @font_size.setter
    def font_size(self, value : float) -> None:
        '''Font size scale.'''
        raise NotImplementedError()
    

class TrapeziumShape(ParameterizedProfile):
    '''IFC compatible Trapezium shape defined by parameters.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.TrapeziumShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def bottom_x_dim(self) -> float:
        '''Gets the extent of the bottom line measured along the x-axis.'''
        raise NotImplementedError()
    
    @bottom_x_dim.setter
    def bottom_x_dim(self, value : float) -> None:
        '''Sets the extent of the bottom line measured along the x-axis.'''
        raise NotImplementedError()
    
    @property
    def top_x_dim(self) -> float:
        '''Gets the extent of the top line measured along the x-axis.'''
        raise NotImplementedError()
    
    @top_x_dim.setter
    def top_x_dim(self, value : float) -> None:
        '''Sets the extent of the top line measured along the x-axis.'''
        raise NotImplementedError()
    
    @property
    def y_dim(self) -> float:
        '''Gets the distance between the top and bottom lines measured along the y-axis.'''
        raise NotImplementedError()
    
    @y_dim.setter
    def y_dim(self, value : float) -> None:
        '''Sets the distance between the top and bottom lines measured along the y-axis.'''
        raise NotImplementedError()
    
    @property
    def top_x_offset(self) -> float:
        '''Gets the offset from the beginning of the top line to the bottom line.'''
        raise NotImplementedError()
    
    @top_x_offset.setter
    def top_x_offset(self, value : float) -> None:
        '''Sets the offset from the beginning of the top line to the bottom line.'''
        raise NotImplementedError()
    

class UShape(ParameterizedProfile):
    '''IFC compatible U-shape defined by parameters.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.UShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def depth(self) -> float:
        '''Gets the length of web.'''
        raise NotImplementedError()
    
    @depth.setter
    def depth(self, value : float) -> None:
        '''Sets the length of web.'''
        raise NotImplementedError()
    
    @property
    def flange_width(self) -> float:
        '''Gets the length of flange.'''
        raise NotImplementedError()
    
    @flange_width.setter
    def flange_width(self, value : float) -> None:
        '''Sets the length of flange.'''
        raise NotImplementedError()
    
    @property
    def web_thickness(self) -> float:
        '''Gets the thickness of web.'''
        raise NotImplementedError()
    
    @web_thickness.setter
    def web_thickness(self, value : float) -> None:
        '''Sets the thickness of web.'''
        raise NotImplementedError()
    
    @property
    def flange_thickness(self) -> float:
        '''Gets the thickness of flange.'''
        raise NotImplementedError()
    
    @flange_thickness.setter
    def flange_thickness(self, value : float) -> None:
        '''Sets the thickness of flange.'''
        raise NotImplementedError()
    
    @property
    def fillet_radius(self) -> float:
        '''Gets the radius of fillet between flange and web.'''
        raise NotImplementedError()
    
    @fillet_radius.setter
    def fillet_radius(self, value : float) -> None:
        '''Sets the radius of fillet between flange and web.'''
        raise NotImplementedError()
    
    @property
    def edge_radius(self) -> float:
        '''Gets the radius of edge in flange\'s edge.'''
        raise NotImplementedError()
    
    @edge_radius.setter
    def edge_radius(self, value : float) -> None:
        '''Sets the radius of edge in flange\'s edge.'''
        raise NotImplementedError()
    

class ZShape(ParameterizedProfile):
    '''IFC compatible Z-shape profile defined by parameters.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.profiles.ZShape`'''
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
    
    def get_bounding_box(self) -> aspose.threed.utilities.BoundingBox:
        '''Gets the bounding box of current entity in its object space coordinate system.
        
        :returns: the bounding box of current entity in its object space coordinate system.'''
        raise NotImplementedError()
    
    def get_entity_renderer_key(self) -> aspose.threed.render.EntityRendererKey:
        '''Gets the key of the entity renderer registered in the renderer'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the extent in x and y dimension.'''
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
    
    @property
    def depth(self) -> float:
        '''Gets the length of web.'''
        raise NotImplementedError()
    
    @depth.setter
    def depth(self, value : float) -> None:
        '''Sets the length of web.'''
        raise NotImplementedError()
    
    @property
    def flange_width(self) -> float:
        '''Gets the length of flange.'''
        raise NotImplementedError()
    
    @flange_width.setter
    def flange_width(self, value : float) -> None:
        '''Sets the length of flange.'''
        raise NotImplementedError()
    
    @property
    def web_thickness(self) -> float:
        '''Gets the thickness of wall.'''
        raise NotImplementedError()
    
    @web_thickness.setter
    def web_thickness(self, value : float) -> None:
        '''Sets the thickness of wall.'''
        raise NotImplementedError()
    
    @property
    def flange_thickness(self) -> float:
        '''Gets the thickness of flange.'''
        raise NotImplementedError()
    
    @flange_thickness.setter
    def flange_thickness(self, value : float) -> None:
        '''Sets the thickness of flange.'''
        raise NotImplementedError()
    
    @property
    def fillet_radius(self) -> float:
        '''Gets the radius of fillet between flange and web.'''
        raise NotImplementedError()
    
    @fillet_radius.setter
    def fillet_radius(self, value : float) -> None:
        '''Sets the radius of fillet between flange and web.'''
        raise NotImplementedError()
    
    @property
    def edge_radius(self) -> float:
        '''Gets the radius of flange edge.'''
        raise NotImplementedError()
    
    @edge_radius.setter
    def edge_radius(self, value : float) -> None:
        '''Sets the radius of flange edge.'''
        raise NotImplementedError()
    

