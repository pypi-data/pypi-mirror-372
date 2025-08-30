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

class AnimationChannel(KeyframeSequence):
    '''A channel maps property\'s component field to a set of keyframe sequences'''
    
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
    def add(self, time : float, value : float) -> None:
        '''Create a new key frame with specified value
        
        :param time: Time position(measured in seconds)
        :param value: The value at this time position'''
        raise NotImplementedError()
    
    @overload
    def add(self, time : float, value : float, interpolation : aspose.threed.animation.Interpolation) -> None:
        '''Create a new key frame with specified value
        
        :param time: Time position(measured in seconds)
        :param value: The value at this time position
        :param interpolation: The interpolation type of this key frame'''
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
    
    def reset(self) -> None:
        '''Removes all key frames and reset the post/pre behaviors.'''
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
    def bind_point(self) -> aspose.threed.animation.BindPoint:
        '''Gets the property bind point which owns this curve'''
        raise NotImplementedError()
    
    @property
    def key_frames(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.KeyFrame]]:
        '''Gets the key frames of this curve.'''
        raise NotImplementedError()
    
    @property
    def post_behavior(self) -> aspose.threed.animation.Extrapolation:
        '''Gets the post behavior indicates what the sampled value should be after the last key frame.'''
        raise NotImplementedError()
    
    @property
    def pre_behavior(self) -> aspose.threed.animation.Extrapolation:
        '''Gets the pre behavior indicates what the sampled value should be before the first key.'''
        raise NotImplementedError()
    
    @property
    def component_type(self) -> System.Type:
        '''Gets the component field\'s type'''
        raise NotImplementedError()
    
    @property
    def default_value(self) -> Any:
        '''Gets the Default value of the channel.
        If a channel has no keyframe sequences connected, the default value will be used during the animation evaluation.
        A real scenario: Animation only animates a node\'s x coordinate, the y and z are not changed,
        then the default value will be used during full translation evaluation.'''
        raise NotImplementedError()
    
    @default_value.setter
    def default_value(self, value : Any) -> None:
        '''Sets the Default value of the channel.
        If a channel has no keyframe sequences connected, the default value will be used during the animation evaluation.
        A real scenario: Animation only animates a node\'s x coordinate, the y and z are not changed,
        then the default value will be used during full translation evaluation.'''
        raise NotImplementedError()
    
    @property
    def keyframe_sequence(self) -> aspose.threed.animation.KeyframeSequence:
        '''Gets associated keyframe sequence inside this channel'''
        raise NotImplementedError()
    
    @keyframe_sequence.setter
    def keyframe_sequence(self, value : aspose.threed.animation.KeyframeSequence) -> None:
        '''Gets associated keyframe sequence inside this channel'''
        raise NotImplementedError()
    

class AnimationClip(aspose.threed.SceneObject):
    '''The Animation clip is a collection of animations.
    The scene can have one or more animation clips.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.AnimationClip` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.AnimationClip` class.
        
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
    
    def create_animation_node(self, node_name : str) -> aspose.threed.animation.AnimationNode:
        '''A shorthand function to create and register the animation node on current clip.
        
        :param node_name: New animation node\'s name
        :returns: A new instance of :py:class:`aspose.threed.animation.AnimationNode` with given name.'''
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
    def animations(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.AnimationNode]]:
        '''Gets the animations contained inside the clip.'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Gets the description of this animation clip'''
        raise NotImplementedError()
    
    @description.setter
    def description(self, value : str) -> None:
        '''Sets the description of this animation clip'''
        raise NotImplementedError()
    
    @property
    def start(self) -> float:
        '''Gets the time in seconds of the beginning of the clip.'''
        raise NotImplementedError()
    
    @start.setter
    def start(self, value : float) -> None:
        '''Sets the time in seconds of the beginning of the clip.'''
        raise NotImplementedError()
    
    @property
    def stop(self) -> float:
        '''Gets the time in seconds of the end of the clip.'''
        raise NotImplementedError()
    
    @stop.setter
    def stop(self, value : float) -> None:
        '''Sets the time in seconds of the end of the clip.'''
        raise NotImplementedError()
    

class AnimationNode(aspose.threed.A3DObject):
    '''Aspose.3D\'s supports animation hierarchy, each animation can be composed by several animations and animation\'s key-frame definition.
    
    :py:class:`aspose.threed.animation.AnimationNode` defines the transformation of a property value over time, for example, animation node can be used to control a node\'s transformation or other :py:class:`aspose.threed.A3DObject` object\'s numerical properties.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.AnimationNode` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.AnimationNode` class.'''
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
    def get_keyframe_sequence(self, target : aspose.threed.A3DObject, prop_name : str, channel_name : str, create : bool) -> aspose.threed.animation.KeyframeSequence:
        '''Gets the keyframe sequence on given property and channel.
        
        :param target: On which instance to create the keyframe sequence.
        :param prop_name: The property\'s name.
        :param channel_name: The channel name.
        :param create: If set to ``true`` create the animation sequence if it\'s not existing.
        :returns: The keyframe sequence.'''
        raise NotImplementedError()
    
    @overload
    def get_keyframe_sequence(self, target : aspose.threed.A3DObject, prop_name : str, create : bool) -> aspose.threed.animation.KeyframeSequence:
        '''Gets the keyframe sequence on given property.
        
        :param target: On which instance to create the keyframe sequence.
        :param prop_name: The property\'s name.
        :param create: If set to ``true``, create the sequence if it\'s not existing.
        :returns: The keyframe sequence.'''
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
    
    def find_bind_point(self, target : aspose.threed.A3DObject, name : str) -> aspose.threed.animation.BindPoint:
        '''Finds the bind point by target and name.
        
        :param target: Bind point\'s target to find.
        :param name: Bind point\'s name to find.
        :returns: The bind point.'''
        raise NotImplementedError()
    
    def get_bind_point(self, target : aspose.threed.A3DObject, prop_name : str, create : bool) -> aspose.threed.animation.BindPoint:
        '''Gets the animation bind point on given property.
        
        :param target: On which object to create the bind point.
        :param prop_name: The property\'s name.
        :param create: If set to ``true`` create the bind point if it\'s not existing.
        :returns: The bind point.'''
        raise NotImplementedError()
    
    def create_bind_point(self, obj : aspose.threed.A3DObject, prop_name : str) -> aspose.threed.animation.BindPoint:
        '''Creates a BindPoint based on the property data type.
        
        :param obj: Object.
        :param prop_name: Property name.
        :returns: The bind point instance or null if the property is not defined.'''
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
    def bind_points(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.BindPoint]]:
        '''Gets the current property bind points'''
        raise NotImplementedError()
    
    @property
    def sub_animations(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.AnimationNode]]:
        '''Gets the sub-animation nodes under current animations'''
        raise NotImplementedError()
    

class BindPoint(aspose.threed.A3DObject):
    '''A :py:class:`aspose.threed.animation.BindPoint` is usually created on an object\'s property, some property types contains multiple component fields(like a Vector3 field),
    :py:class:`aspose.threed.animation.BindPoint` will generate channel for each component field and connects the field to one or more keyframe sequence instance(s) through the channels.'''
    
    def __init__(self, scene : aspose.threed.Scene, prop : aspose.threed.Property) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.BindPoint` class.
        
        :param scene: The scene that contains the animation.
        :param prop: Property.'''
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
    def add_channel(self, name : str, value : Any) -> bool:
        '''Adds the specified channel property.
        
        :param name: Name.
        :param value: Value.
        :returns: true, if channel was added, false otherwise.'''
        raise NotImplementedError()
    
    @overload
    def add_channel(self, name : str, type : System.Type, value : Any) -> bool:
        '''Adds the specified channel property.
        
        :param name: Name.
        :param type: Type.
        :param value: Value.
        :returns: true, if channel was added, false otherwise.'''
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
    
    def get_keyframe_sequence(self, channel_name : str) -> aspose.threed.animation.KeyframeSequence:
        '''Gets the first keyframe sequence in specified channel
        
        :param channel_name: The channel name to find
        :returns: First keyframe sequence with the channel name'''
        raise NotImplementedError()
    
    def create_keyframe_sequence(self, name : str) -> aspose.threed.animation.KeyframeSequence:
        '''Creates a new curve and connects it to the first channel of the curve mapping
        
        :param name: The new sequence\'s name.
        :returns: The keyframe sequence.'''
        raise NotImplementedError()
    
    def bind_keyframe_sequence(self, channel_name : str, sequence : aspose.threed.animation.KeyframeSequence) -> None:
        '''Bind the keyframe sequence to specified channel
        
        :param channel_name: Which channel the keyframe sequence will be bound to
        :param sequence: The keyframe sequence to bind'''
        raise NotImplementedError()
    
    def get_channel(self, channel_name : str) -> aspose.threed.animation.AnimationChannel:
        '''Gets channel by given name
        
        :param channel_name: The channel name to find
        :returns: Channel with the name'''
        raise NotImplementedError()
    
    def reset_channels(self) -> None:
        '''Empties the property channels of this animation curve mapping.'''
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
    def property(self) -> aspose.threed.Property:
        '''Gets the property associated with the CurveMapping'''
        raise NotImplementedError()
    
    @property
    def channels_count(self) -> int:
        '''Gets the total number of property channels defined in this animation curve mapping.'''
        raise NotImplementedError()
    

class Extrapolation:
    '''Extrapolation defines how to do when sampled value is out of the range which defined by the first and last key-frames.'''
    
    @property
    def type(self) -> aspose.threed.animation.ExtrapolationType:
        '''Gets and sets the sampling pattern of extrapolation'''
        raise NotImplementedError()
    
    @type.setter
    def type(self, value : aspose.threed.animation.ExtrapolationType) -> None:
        '''Gets and sets the sampling pattern of extrapolation'''
        raise NotImplementedError()
    
    @property
    def repeat_count(self) -> int:
        '''Gets and sets the repeat times of the extrapolation pattern.'''
        raise NotImplementedError()
    
    @repeat_count.setter
    def repeat_count(self, value : int) -> None:
        '''Gets and sets the repeat times of the extrapolation pattern.'''
        raise NotImplementedError()
    

class KeyFrame:
    '''A key frame is mainly defined by a time and a value, for some interpolation types, tangent/tension/bias/continuity is also used by calculating the final sampled value.
    Sampled values in a non-key-frame time position is interpolated by key-frames between the previous and next key-frames
    Value before/after the first/last key-frame are calculated by the :py:class:`aspose.threed.animation.Extrapolation` class.'''
    
    def __init__(self, curve : aspose.threed.animation.KeyframeSequence, time : float) -> None:
        '''Create a new key frame on specified curve
        
        :param curve: The curve that the key frame will be created on
        :param time: The time position of the key frame'''
        raise NotImplementedError()
    
    @property
    def time(self) -> float:
        '''Gets the time position of list.data[index] key frame, measured in seconds.'''
        raise NotImplementedError()
    
    @time.setter
    def time(self, value : float) -> None:
        '''Sets the time position of list.data[index] key frame, measured in seconds.'''
        raise NotImplementedError()
    
    @property
    def value(self) -> float:
        '''Gets the key-frame\'s value.'''
        raise NotImplementedError()
    
    @value.setter
    def value(self, value : float) -> None:
        '''Sets the key-frame\'s value.'''
        raise NotImplementedError()
    
    @property
    def interpolation(self) -> aspose.threed.animation.Interpolation:
        '''Gets the key\'s interpolation type, list.data[index] defines the algorithm how the sampled value is calculated.'''
        raise NotImplementedError()
    
    @interpolation.setter
    def interpolation(self, value : aspose.threed.animation.Interpolation) -> None:
        '''Sets the key\'s interpolation type, list.data[index] defines the algorithm how the sampled value is calculated.'''
        raise NotImplementedError()
    
    @property
    def tangent_weight_mode(self) -> aspose.threed.animation.WeightedMode:
        '''Gets the key\'s tangent weight mode.
        The out tangent or the next in tangent can be customized by select correct :py:class:`aspose.threed.animation.WeightedMode`'''
        raise NotImplementedError()
    
    @tangent_weight_mode.setter
    def tangent_weight_mode(self, value : aspose.threed.animation.WeightedMode) -> None:
        '''Sets the key\'s tangent weight mode.
        The out tangent or the next in tangent can be customized by select correct :py:class:`aspose.threed.animation.WeightedMode`'''
        raise NotImplementedError()
    
    @property
    def step_mode(self) -> aspose.threed.animation.StepMode:
        '''Gets the key\'s step mode.
        If the interpolation type is :py:attr:`aspose.threed.animation.Interpolation.CONSTANT`, list.data[index] decides which key-frame\'s value will be used during interpolation.
        A :py:attr:`aspose.threed.animation.StepMode.PREVIOUS_VALUE` means the left key-frame\'s value will be used
        A :py:attr:`aspose.threed.animation.StepMode.NEXT_VALUE` means the next right key-frame\'s value will be used'''
        raise NotImplementedError()
    
    @step_mode.setter
    def step_mode(self, value : aspose.threed.animation.StepMode) -> None:
        '''Sets the key\'s step mode.
        If the interpolation type is :py:attr:`aspose.threed.animation.Interpolation.CONSTANT`, list.data[index] decides which key-frame\'s value will be used during interpolation.
        A :py:attr:`aspose.threed.animation.StepMode.PREVIOUS_VALUE` means the left key-frame\'s value will be used
        A :py:attr:`aspose.threed.animation.StepMode.NEXT_VALUE` means the next right key-frame\'s value will be used'''
        raise NotImplementedError()
    
    @property
    def next_in_tangent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the next in(left) tangent on this key frame.'''
        raise NotImplementedError()
    
    @next_in_tangent.setter
    def next_in_tangent(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the next in(left) tangent on this key frame.'''
        raise NotImplementedError()
    
    @property
    def out_tangent(self) -> aspose.threed.utilities.Vector2:
        '''Gets the out(right) tangent on this key frame.'''
        raise NotImplementedError()
    
    @out_tangent.setter
    def out_tangent(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the out(right) tangent on this key frame.'''
        raise NotImplementedError()
    
    @property
    def out_weight(self) -> float:
        '''Gets the out(right) weight on this key frame.'''
        raise NotImplementedError()
    
    @out_weight.setter
    def out_weight(self, value : float) -> None:
        '''Sets the out(right) weight on this key frame.'''
        raise NotImplementedError()
    
    @property
    def next_in_weight(self) -> float:
        '''Gets the next in(left) weight on this key frame.'''
        raise NotImplementedError()
    
    @next_in_weight.setter
    def next_in_weight(self, value : float) -> None:
        '''Sets the next in(left) weight on this key frame.'''
        raise NotImplementedError()
    
    @property
    def tension(self) -> float:
        '''Gets tension used in TCB spline'''
        raise NotImplementedError()
    
    @tension.setter
    def tension(self, value : float) -> None:
        '''Sets tension used in TCB spline'''
        raise NotImplementedError()
    
    @property
    def continuity(self) -> float:
        '''Gets the continuity used in TCB spline'''
        raise NotImplementedError()
    
    @continuity.setter
    def continuity(self, value : float) -> None:
        '''Sets the continuity used in TCB spline'''
        raise NotImplementedError()
    
    @property
    def bias(self) -> float:
        '''Gets the bias used in TCB spline'''
        raise NotImplementedError()
    
    @bias.setter
    def bias(self, value : float) -> None:
        '''Sets the bias used in TCB spline'''
        raise NotImplementedError()
    
    @property
    def independent_tangent(self) -> bool:
        '''Gets the out and next in tangents are independent.'''
        raise NotImplementedError()
    
    @independent_tangent.setter
    def independent_tangent(self, value : bool) -> None:
        '''Sets the out and next in tangents are independent.'''
        raise NotImplementedError()
    
    @property
    def flat(self) -> bool:
        '''Get or set if the key frame is flat.
        Key frame should be flat if next or previous key frame has the same value.
        Flat key frame has flat tangents and fixed interpolation.'''
        raise NotImplementedError()
    
    @flat.setter
    def flat(self, value : bool) -> None:
        '''Get or set if the key frame is flat.
        Key frame should be flat if next or previous key frame has the same value.
        Flat key frame has flat tangents and fixed interpolation.'''
        raise NotImplementedError()
    
    @property
    def time_independent_tangent(self) -> bool:
        '''Gets the tangent is time-independent'''
        raise NotImplementedError()
    
    @time_independent_tangent.setter
    def time_independent_tangent(self, value : bool) -> None:
        '''Sets the tangent is time-independent'''
        raise NotImplementedError()
    

class KeyframeSequence(aspose.threed.A3DObject):
    '''The sequence of key-frames, it describes the transformation of a sampled value over time.'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.KeyframeSequence` class.
        
        :param name: Name'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`aspose.threed.animation.KeyframeSequence` class.'''
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
    def add(self, time : float, value : float) -> None:
        '''Create a new key frame with specified value
        
        :param time: Time position(measured in seconds)
        :param value: The value at this time position'''
        raise NotImplementedError()
    
    @overload
    def add(self, time : float, value : float, interpolation : aspose.threed.animation.Interpolation) -> None:
        '''Create a new key frame with specified value
        
        :param time: Time position(measured in seconds)
        :param value: The value at this time position
        :param interpolation: The interpolation type of this key frame'''
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
    
    def reset(self) -> None:
        '''Removes all key frames and reset the post/pre behaviors.'''
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
    def bind_point(self) -> aspose.threed.animation.BindPoint:
        '''Gets the property bind point which owns this curve'''
        raise NotImplementedError()
    
    @property
    def key_frames(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Animation.KeyFrame]]:
        '''Gets the key frames of this curve.'''
        raise NotImplementedError()
    
    @property
    def post_behavior(self) -> aspose.threed.animation.Extrapolation:
        '''Gets the post behavior indicates what the sampled value should be after the last key frame.'''
        raise NotImplementedError()
    
    @property
    def pre_behavior(self) -> aspose.threed.animation.Extrapolation:
        '''Gets the pre behavior indicates what the sampled value should be before the first key.'''
        raise NotImplementedError()
    

class ExtrapolationType:
    '''Extrapolation type.'''
    
    CONSTANT : ExtrapolationType
    '''Value will keep the same value of the last value'''
    GRADIENT : ExtrapolationType
    '''Value will keep the same slope by time'''
    CYCLE : ExtrapolationType
    '''The repetition.'''
    CYCLE_RELATIVE : ExtrapolationType
    '''Repeat the previous pattern based on the last value'''
    OSCILLATE : ExtrapolationType
    '''The mirror repetition.'''

class Interpolation:
    '''The key frame\'s interpolation type.'''
    
    CONSTANT : Interpolation
    '''The value will remains constant to the value of the first point until the next segment.'''
    LINEAR : Interpolation
    '''Linear interpolation is a straight line between two points.'''
    BEZIER : Interpolation
    '''A bezier or Hermite spline.'''
    B_SPLINE : Interpolation
    '''Basis splines are defined by a series of control points, for which the curve is guaranteed only to go through the first and the last point.'''
    CARDINAL_SPLINE : Interpolation
    '''A cardinal spline is a cubic Hermite spline whose tangents are defined by the endpoints and a tension parameter.'''
    TCB_SPLINE : Interpolation
    '''Also called Kochanek-Bartels spline, the behavior of tangent is defined by tension/bias/continuity'''

class StepMode:
    '''Interpolation step mode.'''
    
    PREVIOUS_VALUE : StepMode
    '''Curve value of a segment always uses the value from previous key frame'''
    NEXT_VALUE : StepMode
    '''Curve value of a segment always uses the value from the next key frame'''

class WeightedMode:
    '''Weighted mode.'''
    
    NONE : WeightedMode
    '''Both out and next in weights are not used.
    When calculation needs tangent information, default value(0.3333) will be used.'''
    OUT_WEIGHT : WeightedMode
    '''Out(right) tangent is weighted.'''
    NEXT_IN_WEIGHT : WeightedMode
    '''Next in(left) tangent is weighted.'''
    BOTH : WeightedMode
    '''Both out and next in tangents are weighted.'''

