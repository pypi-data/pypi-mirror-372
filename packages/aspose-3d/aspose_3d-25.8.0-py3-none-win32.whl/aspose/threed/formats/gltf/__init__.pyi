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

class StructuralMetadata:
    '''This class provides support for EXT_structural_metadata, only used in glTF.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def create_class(self, name : str) -> Aspose.ThreeD.Formats.GLTF.StructuralMetadata+ClassType:
        '''Create a meta class type
        
        :param name: The class\'s name
        :returns: Instance of the meta class'''
        raise NotImplementedError()
    
    def create_enum(self, name : str) -> Aspose.ThreeD.Formats.GLTF.StructuralMetadata+EnumType:
        '''Create an enum type
        
        :param name: The enum type\'s name
        :returns: Instance of the enum type'''
        raise NotImplementedError()
    
    def create_property_table(self, name : str, clazz : Aspose.ThreeD.Formats.GLTF.StructuralMetadata+ClassType) -> Aspose.ThreeD.Formats.GLTF.StructuralMetadata+PropertyTable:
        raise NotImplementedError()
    
    def attach(self, scene : aspose.threed.Scene) -> None:
        '''Attach current meta data to specified scene'''
        raise NotImplementedError()
    
    @staticmethod
    def from_address(scene : aspose.threed.Scene) -> aspose.threed.formats.gltf.StructuralMetadata:
        '''Get :py:class:`aspose.threed.formats.gltf.StructuralMetadata` associated with specified scene.
        
        :param scene: Which scene to look for the structural metadata
        :returns: A valid instance of :py:class:`aspose.threed.formats.gltf.StructuralMetadata` if its found in the scene, otherwise null returned'''
        raise NotImplementedError()
    
    @property
    def property_tables(self) -> System.Collections.Generic.List`1[[Aspose.ThreeD.Formats.GLTF.StructuralMetadata+PropertyTable]]:
        '''The property tables in this metadata.'''
        raise NotImplementedError()
    

