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

class LambertMaterial(Material):
    '''Material for lambert shading model'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.LambertMaterial` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.LambertMaterial` class.
        
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()

    @property
    def emissive_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the emissive color'''
        raise NotImplementedError()
    
    @emissive_color.setter
    def emissive_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the emissive color'''
        raise NotImplementedError()
    
    @property
    def ambient_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the ambient color'''
        raise NotImplementedError()
    
    @ambient_color.setter
    def ambient_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the ambient color'''
        raise NotImplementedError()
    
    @property
    def diffuse_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the diffuse color'''
        raise NotImplementedError()
    
    @diffuse_color.setter
    def diffuse_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the diffuse color'''
        raise NotImplementedError()
    
    @property
    def transparent_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the transparent color.'''
        raise NotImplementedError()
    
    @transparent_color.setter
    def transparent_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the transparent color.'''
        raise NotImplementedError()
    
    @property
    def transparency(self) -> float:
        '''Gets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    

class Material(aspose.threed.A3DObject):
    '''Material defines the parameters necessary for visual appearance of geometry.
    Aspose.3D provides shading model for :py:class:`aspose.threed.shading.LambertMaterial`, :py:class:`aspose.threed.shading.PhongMaterial` and :py:class:`aspose.threed.shading.ShaderMaterial`'''
    
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()


class PbrMaterial(Material):
    '''Material for physically based rendering based on albedo color/metallic/roughness'''
    
    @overload
    def __init__(self) -> None:
        '''Construct a default PBR material instance'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, albedo : aspose.threed.utilities.Vector3) -> None:
        '''Construct a default PBR material with specified albedo color value.
        
        :param albedo: The default albedo color value'''
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
        raise NotImplementedError()
    
    @staticmethod
    def from_material(material : aspose.threed.shading.Material) -> aspose.threed.shading.PbrMaterial:
        '''Allow convert other material to PbrMaterial'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()

    @property
    def transparency(self) -> float:
        '''Gets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @property
    def normal_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture of normal mapping'''
        raise NotImplementedError()
    
    @normal_texture.setter
    def normal_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture of normal mapping'''
        raise NotImplementedError()
    
    @property
    def specular_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for specular color'''
        raise NotImplementedError()
    
    @specular_texture.setter
    def specular_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for specular color'''
        raise NotImplementedError()
    
    @property
    def albedo_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for albedo'''
        raise NotImplementedError()
    
    @albedo_texture.setter
    def albedo_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for albedo'''
        raise NotImplementedError()
    
    @property
    def albedo(self) -> aspose.threed.utilities.Vector3:
        '''Gets the base color of the material'''
        raise NotImplementedError()
    
    @albedo.setter
    def albedo(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the base color of the material'''
        raise NotImplementedError()
    
    @property
    def occlusion_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for ambient occlusion'''
        raise NotImplementedError()
    
    @occlusion_texture.setter
    def occlusion_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for ambient occlusion'''
        raise NotImplementedError()
    
    @property
    def occlusion_factor(self) -> float:
        '''Gets the factor of ambient occlusion'''
        raise NotImplementedError()
    
    @occlusion_factor.setter
    def occlusion_factor(self, value : float) -> None:
        '''Sets the factor of ambient occlusion'''
        raise NotImplementedError()
    
    @property
    def metallic_factor(self) -> float:
        '''Gets the metalness of the material, value of 1 means the material is a metal and value of 0 means the material is a dielectric.'''
        raise NotImplementedError()
    
    @metallic_factor.setter
    def metallic_factor(self, value : float) -> None:
        '''Sets the metalness of the material, value of 1 means the material is a metal and value of 0 means the material is a dielectric.'''
        raise NotImplementedError()
    
    @property
    def roughness_factor(self) -> float:
        '''Gets the roughness of the material, value of 1 means the material is completely rough and value of 0 means the material is completely smooth'''
        raise NotImplementedError()
    
    @roughness_factor.setter
    def roughness_factor(self, value : float) -> None:
        '''Sets the roughness of the material, value of 1 means the material is completely rough and value of 0 means the material is completely smooth'''
        raise NotImplementedError()
    
    @property
    def metallic_roughness(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for metallic(in R channel) and roughness(in G channel)'''
        raise NotImplementedError()
    
    @metallic_roughness.setter
    def metallic_roughness(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for metallic(in R channel) and roughness(in G channel)'''
        raise NotImplementedError()
    
    @property
    def emissive_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for emissive'''
        raise NotImplementedError()
    
    @emissive_texture.setter
    def emissive_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for emissive'''
        raise NotImplementedError()
    
    @property
    def emissive_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the emissive color'''
        raise NotImplementedError()
    
    @emissive_color.setter
    def emissive_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the emissive color'''
        raise NotImplementedError()
    

class PbrSpecularMaterial(Material):
    '''Material for physically based rendering based on diffuse color/specular/glossiness'''
    
    def __init__(self) -> None:
        '''Constructor of the :py:class:`aspose.threed.shading.PbrSpecularMaterial`'''
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()

    @property
    def transparency(self) -> float:
        '''Gets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @property
    def normal_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture of normal mapping'''
        raise NotImplementedError()
    
    @normal_texture.setter
    def normal_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture of normal mapping'''
        raise NotImplementedError()
    
    @property
    def specular_glossiness_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for specular color, channel RGB stores the specular color and channel A stores the glossiness.'''
        raise NotImplementedError()
    
    @specular_glossiness_texture.setter
    def specular_glossiness_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for specular color, channel RGB stores the specular color and channel A stores the glossiness.'''
        raise NotImplementedError()
    
    @property
    def glossiness_factor(self) -> float:
        '''Gets the glossiness(smoothness) of the material, 1 means perfectly smooth and 0 means perfectly rough, default value is 1, range is [0, 1]'''
        raise NotImplementedError()
    
    @glossiness_factor.setter
    def glossiness_factor(self, value : float) -> None:
        '''Sets the glossiness(smoothness) of the material, 1 means perfectly smooth and 0 means perfectly rough, default value is 1, range is [0, 1]'''
        raise NotImplementedError()
    
    @property
    def specular(self) -> aspose.threed.utilities.Vector3:
        '''Gets the specular color of the material, default value is (1, 1, 1).'''
        raise NotImplementedError()
    
    @specular.setter
    def specular(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the specular color of the material, default value is (1, 1, 1).'''
        raise NotImplementedError()
    
    @property
    def diffuse_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for diffuse'''
        raise NotImplementedError()
    
    @diffuse_texture.setter
    def diffuse_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for diffuse'''
        raise NotImplementedError()
    
    @property
    def diffuse(self) -> aspose.threed.utilities.Vector3:
        '''Gets the diffuse color of the material, default value is (1, 1, 1)'''
        raise NotImplementedError()
    
    @diffuse.setter
    def diffuse(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the diffuse color of the material, default value is (1, 1, 1)'''
        raise NotImplementedError()
    
    @property
    def emissive_texture(self) -> aspose.threed.shading.TextureBase:
        '''Gets the texture for emissive'''
        raise NotImplementedError()
    
    @emissive_texture.setter
    def emissive_texture(self, value : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture for emissive'''
        raise NotImplementedError()
    
    @property
    def emissive_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the emissive color, default value is (0, 0, 0)'''
        raise NotImplementedError()
    
    @emissive_color.setter
    def emissive_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the emissive color, default value is (0, 0, 0)'''
        raise NotImplementedError()
    
    @property
    def MAP_SPECULAR_GLOSSINESS(self) -> str:
        '''The texture map for specular glossiness'''
        raise NotImplementedError()


class PhongMaterial(LambertMaterial):
    '''Material for blinn-phong shading model.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.PhongMaterial` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.PhongMaterial` class.
        
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()

    @property
    def emissive_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the emissive color'''
        raise NotImplementedError()
    
    @emissive_color.setter
    def emissive_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the emissive color'''
        raise NotImplementedError()
    
    @property
    def ambient_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the ambient color'''
        raise NotImplementedError()
    
    @ambient_color.setter
    def ambient_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the ambient color'''
        raise NotImplementedError()
    
    @property
    def diffuse_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the diffuse color'''
        raise NotImplementedError()
    
    @diffuse_color.setter
    def diffuse_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the diffuse color'''
        raise NotImplementedError()
    
    @property
    def transparent_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the transparent color.'''
        raise NotImplementedError()
    
    @transparent_color.setter
    def transparent_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the transparent color.'''
        raise NotImplementedError()
    
    @property
    def transparency(self) -> float:
        '''Gets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency factor.
        The factor should be ranged between 0(0%, fully opaque) and 1(100%, fully transparent)
        Any invalid factor value will be clamped.'''
        raise NotImplementedError()
    
    @property
    def specular_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the specular color.'''
        raise NotImplementedError()
    
    @specular_color.setter
    def specular_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the specular color.'''
        raise NotImplementedError()
    
    @property
    def specular_factor(self) -> float:
        '''Gets the specular factor.
        The formula of specular:
        SpecularColor * SpecularFactor * (N dot H) ^ Shininess'''
        raise NotImplementedError()
    
    @specular_factor.setter
    def specular_factor(self, value : float) -> None:
        '''Sets the specular factor.
        The formula of specular:
        SpecularColor * SpecularFactor * (N dot H) ^ Shininess'''
        raise NotImplementedError()
    
    @property
    def shininess(self) -> float:
        '''Gets the shininess, this controls the specular highlight\'s size.
        The formula of specular:
        SpecularColor * SpecularFactor * (N dot H) ^ Shininess'''
        raise NotImplementedError()
    
    @shininess.setter
    def shininess(self, value : float) -> None:
        '''Sets the shininess, this controls the specular highlight\'s size.
        The formula of specular:
        SpecularColor * SpecularFactor * (N dot H) ^ Shininess'''
        raise NotImplementedError()
    
    @property
    def reflection_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the reflection color.'''
        raise NotImplementedError()
    
    @reflection_color.setter
    def reflection_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the reflection color.'''
        raise NotImplementedError()
    
    @property
    def reflection_factor(self) -> float:
        '''Gets the attenuation of the reflection color.'''
        raise NotImplementedError()
    
    @reflection_factor.setter
    def reflection_factor(self, value : float) -> None:
        '''Sets the attenuation of the reflection color.'''
        raise NotImplementedError()
    

class ShaderMaterial(Material):
    '''A shader material allows to describe the material by external rendering engine or shader language.
    :py:class:`aspose.threed.shading.ShaderMaterial` uses :py:class:`aspose.threed.shading.ShaderTechnique` to describe the concrete rendering details,
    and the most suitable one will be used according to the final rendering platform.
    For example, your :py:class:`aspose.threed.shading.ShaderMaterial` instance can have two technique, one is defined by HLSL, and another is defined by GLSL
    Under non-window platform the GLSL should be used instead of HLSL'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.ShaderMaterial` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.ShaderMaterial` class.
        
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
    
    def get_texture(self, slot_name : str) -> aspose.threed.shading.TextureBase:
        '''Gets the texture from the specified slot, it can be material\'s property name or shader\'s parameter name
        
        :param slot_name: Slot name.
        :returns: The texture.'''
        raise NotImplementedError()
    
    def set_texture(self, slot_name : str, texture : aspose.threed.shading.TextureBase) -> None:
        '''Sets the texture to specified slot
        
        :param slot_name: Slot name.
        :param texture: Texture.'''
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
    def MAP_SPECULAR(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a specular texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_DIFFUSE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a diffuse texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_EMISSIVE(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a emissive texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_AMBIENT(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a ambient texture mapping.'''
        raise NotImplementedError()

    @property
    def MAP_NORMAL(self) -> str:
        '''Used in :py:func:`aspose.threed.shading.Material.set_texture` to assign a normal texture mapping.'''
        raise NotImplementedError()

    @property
    def techniques(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Shading.ShaderTechnique]]:
        '''Gets all available techniques defined in this material.'''
        raise NotImplementedError()
    

class ShaderTechnique:
    '''A shader technique represents a concrete rendering implementation.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.ShaderTechnique` class.'''
        raise NotImplementedError()
    
    def add_binding(self, property : str, shader_parameter : str) -> None:
        '''Binds the dynamic property to shader parameter
        
        :param property: The name of the dynamic property.
        :param shader_parameter: The name of the shader parameter.'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Gets the description of this technique'''
        raise NotImplementedError()
    
    @description.setter
    def description(self, value : str) -> None:
        '''Sets the description of this technique'''
        raise NotImplementedError()
    
    @property
    def shader_language(self) -> str:
        '''Gets the shader language used by this technique.'''
        raise NotImplementedError()
    
    @shader_language.setter
    def shader_language(self, value : str) -> None:
        '''Sets the shader language used by this technique.'''
        raise NotImplementedError()
    
    @property
    def shader_version(self) -> str:
        '''Gets the shader version used by this technique.'''
        raise NotImplementedError()
    
    @shader_version.setter
    def shader_version(self, value : str) -> None:
        '''Sets the shader version used by this technique.'''
        raise NotImplementedError()
    
    @property
    def shader_file(self) -> str:
        '''Gets the file name of the external shader file.'''
        raise NotImplementedError()
    
    @shader_file.setter
    def shader_file(self, value : str) -> None:
        '''Sets the file name of the external shader file.'''
        raise NotImplementedError()
    
    @property
    def shader_content(self) -> List[int]:
        '''Gets the content of a embedded shader script.
        It could be HLSL/GLSL shader source file.'''
        raise NotImplementedError()
    
    @shader_content.setter
    def shader_content(self, value : List[int]) -> None:
        '''Sets the content of a embedded shader script.
        It could be HLSL/GLSL shader source file.'''
        raise NotImplementedError()
    
    @property
    def shader_entry(self) -> str:
        '''Gets the entry point of the shader, some shader like HLSL can have customized shader entries.'''
        raise NotImplementedError()
    
    @shader_entry.setter
    def shader_entry(self, value : str) -> None:
        '''Sets the entry point of the shader, some shader like HLSL can have customized shader entries.'''
        raise NotImplementedError()
    
    @property
    def render_api(self) -> str:
        '''Gets the rendering API used by this technique'''
        raise NotImplementedError()
    
    @render_api.setter
    def render_api(self, value : str) -> None:
        '''Sets the rendering API used by this technique'''
        raise NotImplementedError()
    
    @property
    def render_api_version(self) -> str:
        '''Gets the version of the rendering API.'''
        raise NotImplementedError()
    
    @render_api_version.setter
    def render_api_version(self, value : str) -> None:
        '''Sets the version of the rendering API.'''
        raise NotImplementedError()
    

class Texture(TextureBase):
    '''This class defines the texture from an external file.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.Texture` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.Texture` class.
        
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
    
    def set_translation(self, u : float, v : float) -> None:
        '''Sets the UV translation.
        
        :param u: U.
        :param v: V.'''
        raise NotImplementedError()
    
    def set_scale(self, u : float, v : float) -> None:
        '''Sets the UV scale.
        
        :param u: U.
        :param v: V.'''
        raise NotImplementedError()
    
    def set_rotation(self, u : float, v : float) -> None:
        '''Sets the UV rotation.
        
        :param u: U.
        :param v: V.'''
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
    def alpha(self) -> float:
        '''Gets the default alpha value of the texture
        This is valid when the :py:attr:`aspose.threed.shading.TextureBase.alpha_source` is :py:attr:`aspose.threed.shading.AlphaSource.PIXEL_ALPHA`
        Default value is 1.0, valid value range is between 0 and 1'''
        raise NotImplementedError()
    
    @alpha.setter
    def alpha(self, value : float) -> None:
        '''Sets the default alpha value of the texture
        This is valid when the :py:attr:`aspose.threed.shading.TextureBase.alpha_source` is :py:attr:`aspose.threed.shading.AlphaSource.PIXEL_ALPHA`
        Default value is 1.0, valid value range is between 0 and 1'''
        raise NotImplementedError()
    
    @property
    def alpha_source(self) -> aspose.threed.shading.AlphaSource:
        '''Gets whether the texture defines the alpha channel.
        Default value is :py:attr:`aspose.threed.shading.AlphaSource.NONE`'''
        raise NotImplementedError()
    
    @alpha_source.setter
    def alpha_source(self, value : aspose.threed.shading.AlphaSource) -> None:
        '''Sets whether the texture defines the alpha channel.
        Default value is :py:attr:`aspose.threed.shading.AlphaSource.NONE`'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_u(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in U.'''
        raise NotImplementedError()
    
    @wrap_mode_u.setter
    def wrap_mode_u(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in U.'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_v(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in V.'''
        raise NotImplementedError()
    
    @wrap_mode_v.setter
    def wrap_mode_v(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in V.'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_w(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in W.'''
        raise NotImplementedError()
    
    @wrap_mode_w.setter
    def wrap_mode_w(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in W.'''
        raise NotImplementedError()
    
    @property
    def min_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for minification.'''
        raise NotImplementedError()
    
    @min_filter.setter
    def min_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for minification.'''
        raise NotImplementedError()
    
    @property
    def mag_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for magnification.'''
        raise NotImplementedError()
    
    @mag_filter.setter
    def mag_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for magnification.'''
        raise NotImplementedError()
    
    @property
    def mip_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for mip-level sampling.'''
        raise NotImplementedError()
    
    @mip_filter.setter
    def mip_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for mip-level sampling.'''
        raise NotImplementedError()
    
    @property
    def uv_rotation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation of the texture'''
        raise NotImplementedError()
    
    @uv_rotation.setter
    def uv_rotation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the rotation of the texture'''
        raise NotImplementedError()
    
    @property
    def uv_scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the UV scale.'''
        raise NotImplementedError()
    
    @uv_scale.setter
    def uv_scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the UV scale.'''
        raise NotImplementedError()
    
    @property
    def uv_translation(self) -> aspose.threed.utilities.Vector2:
        '''Gets the UV translation.'''
        raise NotImplementedError()
    
    @uv_translation.setter
    def uv_translation(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the UV translation.'''
        raise NotImplementedError()
    
    @property
    def enable_mip_map(self) -> bool:
        '''Gets if the mipmap is enabled for this texture'''
        raise NotImplementedError()
    
    @enable_mip_map.setter
    def enable_mip_map(self, value : bool) -> None:
        '''Sets if the mipmap is enabled for this texture'''
        raise NotImplementedError()
    
    @property
    def content(self) -> List[int]:
        '''Gets the binary content of the texture.
        The embedded texture content is optional, user should load texture from external file if this is missing.'''
        raise NotImplementedError()
    
    @content.setter
    def content(self, value : List[int]) -> None:
        '''Sets the binary content of the texture.
        The embedded texture content is optional, user should load texture from external file if this is missing.'''
        raise NotImplementedError()
    
    @property
    def file_name(self) -> str:
        '''Gets the associated texture file.'''
        raise NotImplementedError()
    
    @file_name.setter
    def file_name(self, value : str) -> None:
        '''Sets the associated texture file.'''
        raise NotImplementedError()
    

class TextureBase(aspose.threed.A3DObject):
    '''Base class for all concrete textures.
    Texture defines the look and feel of a geometry surface.'''
    
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.shading.TextureBase` class.
        
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
    
    def set_translation(self, u : float, v : float) -> None:
        '''Sets the UV translation.
        
        :param u: U.
        :param v: V.'''
        raise NotImplementedError()
    
    def set_scale(self, u : float, v : float) -> None:
        '''Sets the UV scale.
        
        :param u: U.
        :param v: V.'''
        raise NotImplementedError()
    
    def set_rotation(self, u : float, v : float) -> None:
        '''Sets the UV rotation.
        
        :param u: U.
        :param v: V.'''
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
    def alpha(self) -> float:
        '''Gets the default alpha value of the texture
        This is valid when the :py:attr:`aspose.threed.shading.TextureBase.alpha_source` is :py:attr:`aspose.threed.shading.AlphaSource.PIXEL_ALPHA`
        Default value is 1.0, valid value range is between 0 and 1'''
        raise NotImplementedError()
    
    @alpha.setter
    def alpha(self, value : float) -> None:
        '''Sets the default alpha value of the texture
        This is valid when the :py:attr:`aspose.threed.shading.TextureBase.alpha_source` is :py:attr:`aspose.threed.shading.AlphaSource.PIXEL_ALPHA`
        Default value is 1.0, valid value range is between 0 and 1'''
        raise NotImplementedError()
    
    @property
    def alpha_source(self) -> aspose.threed.shading.AlphaSource:
        '''Gets whether the texture defines the alpha channel.
        Default value is :py:attr:`aspose.threed.shading.AlphaSource.NONE`'''
        raise NotImplementedError()
    
    @alpha_source.setter
    def alpha_source(self, value : aspose.threed.shading.AlphaSource) -> None:
        '''Sets whether the texture defines the alpha channel.
        Default value is :py:attr:`aspose.threed.shading.AlphaSource.NONE`'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_u(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in U.'''
        raise NotImplementedError()
    
    @wrap_mode_u.setter
    def wrap_mode_u(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in U.'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_v(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in V.'''
        raise NotImplementedError()
    
    @wrap_mode_v.setter
    def wrap_mode_v(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in V.'''
        raise NotImplementedError()
    
    @property
    def wrap_mode_w(self) -> aspose.threed.shading.WrapMode:
        '''Gets the texture wrap modes in W.'''
        raise NotImplementedError()
    
    @wrap_mode_w.setter
    def wrap_mode_w(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the texture wrap modes in W.'''
        raise NotImplementedError()
    
    @property
    def min_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for minification.'''
        raise NotImplementedError()
    
    @min_filter.setter
    def min_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for minification.'''
        raise NotImplementedError()
    
    @property
    def mag_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for magnification.'''
        raise NotImplementedError()
    
    @mag_filter.setter
    def mag_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for magnification.'''
        raise NotImplementedError()
    
    @property
    def mip_filter(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter for mip-level sampling.'''
        raise NotImplementedError()
    
    @mip_filter.setter
    def mip_filter(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter for mip-level sampling.'''
        raise NotImplementedError()
    
    @property
    def uv_rotation(self) -> aspose.threed.utilities.Vector3:
        '''Gets the rotation of the texture'''
        raise NotImplementedError()
    
    @uv_rotation.setter
    def uv_rotation(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the rotation of the texture'''
        raise NotImplementedError()
    
    @property
    def uv_scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the UV scale.'''
        raise NotImplementedError()
    
    @uv_scale.setter
    def uv_scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the UV scale.'''
        raise NotImplementedError()
    
    @property
    def uv_translation(self) -> aspose.threed.utilities.Vector2:
        '''Gets the UV translation.'''
        raise NotImplementedError()
    
    @uv_translation.setter
    def uv_translation(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the UV translation.'''
        raise NotImplementedError()
    

class TextureSlot:
    '''Texture slot in :py:class:`aspose.threed.shading.Material`, can be enumerated through material instance.'''
    
    @property
    def slot_name(self) -> str:
        '''The slot name that indicates where this texture will be bounded to.'''
        raise NotImplementedError()
    
    @property
    def texture(self) -> aspose.threed.shading.TextureBase:
        '''The texture that will be bounded to the material.'''
        raise NotImplementedError()
    

class AlphaSource:
    '''Defines whether the texture contains the alpha channel.'''
    
    NONE : AlphaSource
    '''No alpha is defined in the texture'''
    PIXEL_ALPHA : AlphaSource
    '''The alpha is defined by pixel\'s alpha channel'''
    FIXED_VALUE : AlphaSource
    '''The Alpha is a fixed value which is defined by :py:attr:`aspose.threed.shading.TextureBase.alpha`'''

class TextureFilter:
    '''Filter options during texture sampling.'''
    
    NONE : TextureFilter
    '''No minification, this is only used by minification filter.'''
    POINT : TextureFilter
    '''Use point sampling'''
    LINEAR : TextureFilter
    '''Use linear interpolation for sampling'''
    ANISOTROPIC : TextureFilter
    '''Use anisotropic interpolation for sampling, this is only used by minification filter.'''

class WrapMode:
    '''Texture\'s wrap mode.'''
    
    WRAP : WrapMode
    '''Tiles the texture on the model\'s surface, creating a repeating pattern.'''
    CLAMP : WrapMode
    '''Clamps the texture to the last pixel at the border.'''
    MIRROR : WrapMode
    '''The texture will be repeated, but it will be mirrored when the integer part of the coordinate is odd.'''
    MIRROR_ONCE : WrapMode
    '''The texture will be mirrored once, and then clamps to the maximum value.'''
    BORDER : WrapMode
    '''The coordinates that outside of the range [0.0, 1.0] are set to a specified border color.'''

