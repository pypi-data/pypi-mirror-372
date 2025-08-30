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

class DescriptorSetUpdater:
    '''This class allows to update the :py:class:`aspose.threed.render.IDescriptorSet` in a chain operation.'''
    
    @overload
    def bind(self, buffer : aspose.threed.render.IBuffer, offset : int, size : int) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the buffer to current descriptor set
        
        :param buffer: Which buffer to bind
        :param offset: Offset of the buffer to bind
        :param size: Size of the buffer to bind
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    
    @overload
    def bind(self, buffer : aspose.threed.render.IBuffer) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the entire buffer to current descriptor
        
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    
    @overload
    def bind(self, binding : int, buffer : aspose.threed.render.IBuffer) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the buffer to current descriptor set at specified binding location.
        
        :param binding: Binding location
        :param buffer: The entire buffer to bind
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    
    @overload
    def bind(self, binding : int, buffer : aspose.threed.render.IBuffer, offset : int, size : int) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the buffer to current descriptor set at specified binding location.
        
        :param binding: Binding location
        :param buffer: The buffer to bind
        :param offset: Offset of the buffer to bind
        :param size: Size of the buffer to bind
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    
    @overload
    def bind(self, texture : aspose.threed.render.ITextureUnit) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the texture unit to current descriptor set
        
        :param texture: The texture unit to bind
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    
    @overload
    def bind(self, binding : int, texture : aspose.threed.render.ITextureUnit) -> aspose.threed.render.DescriptorSetUpdater:
        '''Bind the texture unit to current descriptor set
        
        :param binding: The binding location
        :param texture: The texture unit to bind
        :returns: Return current instance for chaining operation'''
        raise NotImplementedError()
    

class DriverException:
    '''The exception raised by internal rendering drivers.'''
    
    def __init__(self, code : int, message : str) -> None:
        '''Initialize an instance of :py:class:`aspose.threed.render.DriverException` with specified native driver error code and message.'''
        raise NotImplementedError()
    
    @property
    def error_code(self) -> int:
        '''Gets the native error code.'''
        raise NotImplementedError()
    

class EntityRenderer:
    '''Subclass this to implement rendering for different kind of entities.'''
    
    @overload
    def __init__(self, key : str, features : aspose.threed.render.EntityRendererFeatures) -> None:
        '''Constructor of :py:class:`aspose.threed.render.EntityRenderer`
        
        :param key: The key of the entity renderer
        :param features: The extra features of the entity renderer'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, key : str) -> None:
        '''Constructor of :py:class:`aspose.threed.render.EntityRenderer`
        
        :param key: The key of the entity renderer'''
        raise NotImplementedError()
    
    def initialize(self, renderer : aspose.threed.render.Renderer) -> None:
        '''Initialize the entity renderer'''
        raise NotImplementedError()
    
    def reset_scene_cache(self) -> None:
        '''The scene has changed or removed, need to dispose scene-level render resources in this'''
        raise NotImplementedError()
    
    def frame_begin(self, renderer : aspose.threed.render.Renderer, render_queue : aspose.threed.render.IRenderQueue) -> None:
        '''Begin rendering a frame
        
        :param renderer: Current renderer
        :param render_queue: Render queue'''
        raise NotImplementedError()
    
    def frame_end(self, renderer : aspose.threed.render.Renderer, render_queue : aspose.threed.render.IRenderQueue) -> None:
        '''Ends rendering a frame
        
        :param renderer: Current renderer
        :param render_queue: Render queue'''
        raise NotImplementedError()
    
    def prepare_render_queue(self, renderer : aspose.threed.render.Renderer, queue : aspose.threed.render.IRenderQueue, node : aspose.threed.Node, entity : aspose.threed.Entity) -> None:
        '''Prepare rendering commands for specified node/entity pair.
        
        :param renderer: The current renderer instance
        :param queue: The render queue used to manage render tasks
        :param node: Current node
        :param entity: The entity that need to be rendered'''
        raise NotImplementedError()
    
    def render_entity(self, renderer : aspose.threed.render.Renderer, command_list : aspose.threed.render.ICommandList, node : aspose.threed.Node, renderable_resource : Any, sub_entity : int) -> None:
        '''Each render task pushed to the :py:class:`aspose.threed.render.IRenderQueue` will have a corresponding RenderEntity call
        to perform the concrete rendering job.
        
        :param renderer: The renderer
        :param command_list: The commandList used to record the rendering commands
        :param node: The same node that passed to PrepareRenderQueue of the entity that will be rendered
        :param renderable_resource: The custom object that passed to IRenderQueue during the PrepareRenderQueue
        :param sub_entity: The index of the sub entity that passed to IRenderQueue'''
        raise NotImplementedError()
    
    def dispose(self) -> None:
        '''The entity renderer is being disposed, release shared resources.'''
        raise NotImplementedError()
    

class EntityRendererKey:
    '''The key of registered entity renderer'''
    
    def __init__(self, name : str) -> None:
        '''Constructor of :py:class:`aspose.threed.render.EntityRendererKey`'''
        raise NotImplementedError()
    

class GLSLSource(ShaderSource):
    '''The source code of shaders in GLSL'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def define_include(self, file_name : str, content : str) -> None:
        '''Define virtual file for #include in GLSL source code
        
        :param file_name: File name of the virtual file'''
        raise NotImplementedError()
    
    @property
    def compute_shader(self) -> str:
        '''Gets the source code of the compute shader.'''
        raise NotImplementedError()
    
    @compute_shader.setter
    def compute_shader(self, value : str) -> None:
        '''Sets the source code of the compute shader.'''
        raise NotImplementedError()
    
    @property
    def geometry_shader(self) -> str:
        '''Gets the source code of the geometry shader.'''
        raise NotImplementedError()
    
    @geometry_shader.setter
    def geometry_shader(self, value : str) -> None:
        '''Sets the source code of the geometry shader.'''
        raise NotImplementedError()
    
    @property
    def vertex_shader(self) -> str:
        '''Gets the source code of the vertex shader'''
        raise NotImplementedError()
    
    @vertex_shader.setter
    def vertex_shader(self, value : str) -> None:
        '''Sets the source code of the vertex shader'''
        raise NotImplementedError()
    
    @property
    def fragment_shader(self) -> str:
        '''Gets the source code of the fragment shader.'''
        raise NotImplementedError()
    
    @fragment_shader.setter
    def fragment_shader(self, value : str) -> None:
        '''Sets the source code of the fragment shader.'''
        raise NotImplementedError()
    

class IBuffer:
    '''The base interface of all managed buffers used in rendering'''
    
    def load_data(self, data : List[int]) -> None:
        '''Load the data into current buffer'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Size of this buffer in bytes'''
        raise NotImplementedError()
    

class ICommandList:
    '''Encodes a sequence of commands which will be sent to GPU to render.'''
    
    @overload
    def draw(self, start : int, count : int) -> None:
        '''Draw without index buffer'''
        raise NotImplementedError()
    
    @overload
    def draw(self) -> None:
        '''Draw without index buffer'''
        raise NotImplementedError()
    
    @overload
    def draw_index(self) -> None:
        '''Issue an indexed draw into a command list'''
        raise NotImplementedError()
    
    @overload
    def draw_index(self, start : int, count : int) -> None:
        '''Issue an indexed draw into a command list
        
        :param start: The first index to draw
        :param count: The count of indices to draw'''
        raise NotImplementedError()
    
    @overload
    def push_constants(self, stage : aspose.threed.render.ShaderStage, data : List[int]) -> None:
        '''Push the constant to the pipeline
        
        :param stage: Which shader stage will consume the constant data
        :param data: The data that will be sent to the shader'''
        raise NotImplementedError()
    
    @overload
    def push_constants(self, stage : aspose.threed.render.ShaderStage, data : List[int], size : int) -> None:
        '''Push the constant to the pipeline
        
        :param stage: Which shader stage will consume the constant data
        :param data: The data that will be sent to the shader
        :param size: Bytes to write to the pipeline'''
        raise NotImplementedError()
    
    def bind_pipeline(self, pipeline : aspose.threed.render.IPipeline) -> None:
        '''Bind the pipeline instance for rendering'''
        raise NotImplementedError()
    
    def bind_vertex_buffer(self, vertex_buffer : aspose.threed.render.IVertexBuffer) -> None:
        '''Bind the vertex buffer for rendering'''
        raise NotImplementedError()
    
    def bind_index_buffer(self, index_buffer : aspose.threed.render.IIndexBuffer) -> None:
        '''Bind the index buffer for rendering'''
        raise NotImplementedError()
    
    def bind_descriptor_set(self, descriptor_set : aspose.threed.render.IDescriptorSet) -> None:
        '''Bind the descriptor set to current pipeline'''
        raise NotImplementedError()
    

class IDescriptorSet:
    '''The descriptor sets describes different resources that can be used to bind to the render pipeline like buffers, textures'''
    
    def begin_update(self) -> aspose.threed.render.DescriptorSetUpdater:
        '''Begin to update the descriptor set'''
        raise NotImplementedError()
    

class IIndexBuffer(IBuffer):
    '''The index buffer describes the geometry used in rendering pipeline.'''
    
    @overload
    def load_data(self, mesh : aspose.threed.entities.TriMesh) -> None:
        '''Load indice data from :py:class:`aspose.threed.entities.TriMesh`'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, indices : List[int]) -> None:
        '''Load indice data'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, indices : List[int]) -> None:
        '''Load indice data'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, indices : List[int]) -> None:
        '''Load indice data'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, data : List[int]) -> None:
        '''Load the data into current buffer'''
        raise NotImplementedError()
    
    @property
    def index_data_type(self) -> aspose.threed.render.IndexDataType:
        '''Gets the data type of each element.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the number of index in this buffer.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Size of this buffer in bytes'''
        raise NotImplementedError()
    

class IPipeline:
    '''The pre-baked sequence of operations to draw in GPU side.'''
    

class IRenderQueue:
    '''Entity renderer uses this queue to manage render tasks.'''
    
    def add(self, group_id : aspose.threed.render.RenderQueueGroupId, pipeline : aspose.threed.render.IPipeline, renderable_resource : Any, sub_entity : int) -> None:
        '''Add render task to the render queue.
        
        :param group_id: Which group of the queue the render task will be in
        :param pipeline: The pipeline instance used for this render task
        :param renderable_resource: Custom object that will be sent to :py:func:`aspose.threed.render.EntityRenderer.render_entity`
        :param sub_entity: The index of sub entities, useful when the entity is consisting of more than one sub renderable components.'''
        raise NotImplementedError()
    

class IRenderTarget:
    '''The base interface of render target'''
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, background_color : aspose.threed.utilities.Vector3, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with specified background color and position/size in specified camera perspective.
        
        :param camera: The camera
        :param background_color: The background of the viewport
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with position/size in specified camera perspective.
        
        :param camera: The camera
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera) -> aspose.threed.render.Viewport:
        '''Create a viewport in specified camera perspective.
        
        :param camera: The camera'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.threed.utilities.Vector2:
        '''Gets the size of the render target.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the size of the render target.'''
        raise NotImplementedError()
    
    @property
    def viewports(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Render.Viewport]]:
        '''Gets all viewports that associated with this render target.'''
        raise NotImplementedError()
    

class IRenderTexture(IRenderTarget):
    '''The interface of render texture'''
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, background_color : aspose.threed.utilities.Vector3, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with specified background color and position/size in specified camera perspective.
        
        :param camera: The camera
        :param background_color: The background of the viewport
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with position/size in specified camera perspective.
        
        :param camera: The camera
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera) -> aspose.threed.render.Viewport:
        '''Create a viewport in specified camera perspective.
        
        :param camera: The camera'''
        raise NotImplementedError()
    
    @property
    def targets(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Render.ITextureUnit]]:
        '''Color output targets.'''
        raise NotImplementedError()
    
    @property
    def depth_texture(self) -> aspose.threed.render.ITextureUnit:
        '''Depth buffer texture'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.threed.utilities.Vector2:
        '''Gets the size of the render target.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the size of the render target.'''
        raise NotImplementedError()
    
    @property
    def viewports(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Render.Viewport]]:
        '''Gets all viewports that associated with this render target.'''
        raise NotImplementedError()
    

class IRenderWindow(IRenderTarget):
    '''IRenderWindow represents the native window created by operating system that supports rendering.'''
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, background_color : aspose.threed.utilities.Vector3, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with specified background color and position/size in specified camera perspective.
        
        :param camera: The camera
        :param background_color: The background of the viewport
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera, rect : aspose.threed.utilities.RelativeRectangle) -> aspose.threed.render.Viewport:
        '''Create a viewport with position/size in specified camera perspective.
        
        :param camera: The camera
        :param rect: Position and size of the viewport'''
        raise NotImplementedError()
    
    @overload
    def create_viewport(self, camera : aspose.threed.entities.Camera) -> aspose.threed.render.Viewport:
        '''Create a viewport in specified camera perspective.
        
        :param camera: The camera'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.threed.utilities.Vector2:
        '''Gets the size of the render target.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the size of the render target.'''
        raise NotImplementedError()
    
    @property
    def viewports(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Render.Viewport]]:
        '''Gets all viewports that associated with this render target.'''
        raise NotImplementedError()
    

class ITexture1D(ITextureUnit):
    '''1D texture'''
    
    @overload
    def save(self, path : str, format : str) -> None:
        '''Save the texture content to external file.
        
        :param path: File name to save.
        :param format: Image format'''
        raise NotImplementedError()
    
    @overload
    def save(self, bitmap : aspose.threed.render.TextureData) -> None:
        '''Save the texture content to external file.
        
        :param bitmap: Result bitmap to save.'''
        raise NotImplementedError()
    
    def load(self, bitmap : aspose.threed.render.TextureData) -> None:
        '''Load texture content from specified Bitmap'''
        raise NotImplementedError()
    
    def to_bitmap(self) -> aspose.threed.render.TextureData:
        '''Convert the texture unit to :py:class:`aspose.threed.render.TextureData` instance'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.threed.render.TextureType:
        '''Gets the type of this texture unit.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of this texture.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of this texture.'''
        raise NotImplementedError()
    
    @property
    def depth(self) -> int:
        '''Gets the height of this texture, for none-3D texture it\'s always 1.'''
        raise NotImplementedError()
    
    @property
    def u_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @u_wrap.setter
    def u_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @property
    def v_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @v_wrap.setter
    def v_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @property
    def w_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @w_wrap.setter
    def w_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @property
    def minification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for minification.'''
        raise NotImplementedError()
    
    @minification.setter
    def minification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for minification.'''
        raise NotImplementedError()
    
    @property
    def magnification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @magnification.setter
    def magnification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @property
    def mipmap(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @mipmap.setter
    def mipmap(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @property
    def scroll(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @scroll.setter
    def scroll(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scale of the UV coordinate.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scale of the UV coordinate.'''
        raise NotImplementedError()
    

class ITexture2D(ITextureUnit):
    '''2D texture'''
    
    @overload
    def save(self, path : str, format : str) -> None:
        '''Save the texture content to external file.
        
        :param path: File name to save.
        :param format: Image format'''
        raise NotImplementedError()
    
    @overload
    def save(self, bitmap : aspose.threed.render.TextureData) -> None:
        '''Save the texture content to external file.
        
        :param bitmap: Result bitmap to save.'''
        raise NotImplementedError()
    
    def load(self, bitmap : aspose.threed.render.TextureData) -> None:
        '''Load texture content from specified Bitmap'''
        raise NotImplementedError()
    
    def to_bitmap(self) -> aspose.threed.render.TextureData:
        '''Convert the texture unit to :py:class:`aspose.threed.render.TextureData` instance'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.threed.render.TextureType:
        '''Gets the type of this texture unit.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of this texture.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of this texture.'''
        raise NotImplementedError()
    
    @property
    def depth(self) -> int:
        '''Gets the height of this texture, for none-3D texture it\'s always 1.'''
        raise NotImplementedError()
    
    @property
    def u_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @u_wrap.setter
    def u_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @property
    def v_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @v_wrap.setter
    def v_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @property
    def w_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @w_wrap.setter
    def w_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @property
    def minification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for minification.'''
        raise NotImplementedError()
    
    @minification.setter
    def minification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for minification.'''
        raise NotImplementedError()
    
    @property
    def magnification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @magnification.setter
    def magnification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @property
    def mipmap(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @mipmap.setter
    def mipmap(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @property
    def scroll(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @scroll.setter
    def scroll(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scale of the UV coordinate.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scale of the UV coordinate.'''
        raise NotImplementedError()
    

class ITextureCodec:
    '''Codec for textures'''
    
    def get_decoders(self) -> List[aspose.threed.render.ITextureDecoder]:
        '''Gets supported texture decoders.
        
        :returns: An array of supported texture decoders'''
        raise NotImplementedError()
    
    def get_encoders(self) -> List[aspose.threed.render.ITextureEncoder]:
        '''Gets supported texture encoders.
        
        :returns: An array of supported texture encoders'''
        raise NotImplementedError()
    

class ITextureCubemap(ITextureUnit):
    '''Cube map texture'''
    
    def load(self, face : aspose.threed.render.CubeFace, data : aspose.threed.render.TextureData) -> None:
        '''Load the data into specified face'''
        raise NotImplementedError()
    
    def save(self, side : aspose.threed.render.CubeFace, bitmap : aspose.threed.render.TextureData) -> None:
        '''Save the specified side to memory'''
        raise NotImplementedError()
    
    def to_bitmap(self, side : aspose.threed.render.CubeFace) -> aspose.threed.render.TextureData:
        '''Convert the texture unit to :py:class:`aspose.threed.render.TextureData` instance'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.threed.render.TextureType:
        '''Gets the type of this texture unit.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of this texture.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of this texture.'''
        raise NotImplementedError()
    
    @property
    def depth(self) -> int:
        '''Gets the height of this texture, for none-3D texture it\'s always 1.'''
        raise NotImplementedError()
    
    @property
    def u_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @u_wrap.setter
    def u_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @property
    def v_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @v_wrap.setter
    def v_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @property
    def w_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @w_wrap.setter
    def w_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @property
    def minification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for minification.'''
        raise NotImplementedError()
    
    @minification.setter
    def minification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for minification.'''
        raise NotImplementedError()
    
    @property
    def magnification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @magnification.setter
    def magnification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @property
    def mipmap(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @mipmap.setter
    def mipmap(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @property
    def scroll(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @scroll.setter
    def scroll(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scale of the UV coordinate.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scale of the UV coordinate.'''
        raise NotImplementedError()
    

class ITextureDecoder:
    '''External texture decoder should implement this interface for decoding.'''
    
    def decode(self, stream : io._IOBase, reverse_y : bool) -> aspose.threed.render.TextureData:
        '''Decode texture from stream, return null if failed to decode.
        
        :param stream: Texture data source stream
        :param reverse_y: Flip the texture
        :returns: Decoded texture data or null if not supported.'''
        raise NotImplementedError()
    

class ITextureEncoder:
    '''External texture encoder should implement this interface for encoding.'''
    
    def encode(self, texture : aspose.threed.render.TextureData, stream : io._IOBase) -> None:
        '''Encode texture data into stream
        
        :param texture: The texture data to be encoded
        :param stream: The output stream'''
        raise NotImplementedError()
    
    @property
    def file_extension(self) -> str:
        '''File extension name(without dot) of the this encoder'''
        raise NotImplementedError()
    

class ITextureUnit:
    ''':py:class:`aspose.threed.render.ITextureUnit` represents a texture in the memory that shared between GPU and CPU and can be sampled by the shader,
    where the :py:class:`aspose.threed.shading.Texture` only represents a reference to an external file.
    More details can be found https://en.wikipedia.org/wiki/Texture_mapping_unit'''
    
    @property
    def type(self) -> aspose.threed.render.TextureType:
        '''Gets the type of this texture unit.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of this texture.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of this texture.'''
        raise NotImplementedError()
    
    @property
    def depth(self) -> int:
        '''Gets the height of this texture, for none-3D texture it\'s always 1.'''
        raise NotImplementedError()
    
    @property
    def u_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @u_wrap.setter
    def u_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s U coordinate.'''
        raise NotImplementedError()
    
    @property
    def v_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @v_wrap.setter
    def v_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s V coordinate.'''
        raise NotImplementedError()
    
    @property
    def w_wrap(self) -> aspose.threed.shading.WrapMode:
        '''Gets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @w_wrap.setter
    def w_wrap(self, value : aspose.threed.shading.WrapMode) -> None:
        '''Sets the wrap mode for texture\'s W coordinate.'''
        raise NotImplementedError()
    
    @property
    def minification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for minification.'''
        raise NotImplementedError()
    
    @minification.setter
    def minification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for minification.'''
        raise NotImplementedError()
    
    @property
    def magnification(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @magnification.setter
    def magnification(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for magnification.'''
        raise NotImplementedError()
    
    @property
    def mipmap(self) -> aspose.threed.shading.TextureFilter:
        '''Gets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @mipmap.setter
    def mipmap(self, value : aspose.threed.shading.TextureFilter) -> None:
        '''Sets the filter mode for mipmap.'''
        raise NotImplementedError()
    
    @property
    def scroll(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @scroll.setter
    def scroll(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scroll of the UV coordinate.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> aspose.threed.utilities.Vector2:
        '''Gets the scale of the UV coordinate.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : aspose.threed.utilities.Vector2) -> None:
        '''Sets the scale of the UV coordinate.'''
        raise NotImplementedError()
    

class IVertexBuffer(IBuffer):
    '''The vertex buffer holds the polygon vertex data that will be sent to rendering pipeline'''
    
    @overload
    def load_data(self, mesh : aspose.threed.entities.TriMesh) -> None:
        '''Load vertex data from :py:class:`aspose.threed.entities.TriMesh`'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, array : System.Array) -> None:
        '''Load data from array'''
        raise NotImplementedError()
    
    @overload
    def load_data(self, data : List[int]) -> None:
        '''Load the data into current buffer'''
        raise NotImplementedError()
    
    @property
    def vertex_declaration(self) -> aspose.threed.utilities.VertexDeclaration:
        '''Gets the vertex declaration'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Size of this buffer in bytes'''
        raise NotImplementedError()
    

class InitializationException:
    '''Exceptions in render pipeline initialization'''
    
    @overload
    def __init__(self) -> None:
        '''Initialize an :py:class:`aspose.threed.render.InitializationException` instance'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, msg : str) -> None:
        '''Initialize an :py:class:`aspose.threed.render.InitializationException` instance with specified exception message.'''
        raise NotImplementedError()
    

class PixelMapping:
    
    @property
    def stride(self) -> int:
        '''Bytes of pixels in a row.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Rows of the pixels'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Columns of the pixels'''
        raise NotImplementedError()
    
    @property
    def data(self) -> List[int]:
        '''The mapped bytes of pixels.'''
        raise NotImplementedError()
    

class PostProcessing(aspose.threed.A3DObject):
    '''The post-processing effects'''
    
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
    def input(self) -> aspose.threed.render.ITextureUnit:
        '''Input of this post-processing'''
        raise NotImplementedError()
    
    @input.setter
    def input(self, value : aspose.threed.render.ITextureUnit) -> None:
        '''Input of this post-processing'''
        raise NotImplementedError()
    

class PushConstant:
    '''A utility to provide data to shader through push constant.'''
    
    def __init__(self) -> None:
        '''Constructor of the :py:class:`aspose.threed.render.PushConstant`'''
        raise NotImplementedError()
    
    @overload
    def write(self, mat : aspose.threed.utilities.FMatrix4) -> aspose.threed.render.PushConstant:
        '''Write the matrix to the constant
        
        :param mat: The matrix to write'''
        raise NotImplementedError()
    
    @overload
    def write(self, n : int) -> aspose.threed.render.PushConstant:
        '''Write a int value to the constant'''
        raise NotImplementedError()
    
    @overload
    def write(self, f : float) -> aspose.threed.render.PushConstant:
        '''Write a float value to the constant'''
        raise NotImplementedError()
    
    @overload
    def write(self, vec : aspose.threed.utilities.FVector4) -> aspose.threed.render.PushConstant:
        '''Write a 4-component vector to the constant'''
        raise NotImplementedError()
    
    @overload
    def write(self, vec : aspose.threed.utilities.FVector3) -> aspose.threed.render.PushConstant:
        '''Write a 3-component vector to the constant'''
        raise NotImplementedError()
    
    @overload
    def write(self, x : float, y : float, z : float, w : float) -> aspose.threed.render.PushConstant:
        '''Write a 4-component vector to the constant'''
        raise NotImplementedError()
    
    def commit(self, stage : aspose.threed.render.ShaderStage, command_list : aspose.threed.render.ICommandList) -> aspose.threed.render.PushConstant:
        '''Commit prepared data to graphics pipeline.'''
        raise NotImplementedError()
    

class RenderFactory:
    '''RenderFactory creates all resources that represented in rendering pipeline.'''
    
    @overload
    def create_render_texture(self, parameters : aspose.threed.render.RenderParameters, targets : int, width : int, height : int) -> aspose.threed.render.IRenderTexture:
        '''Create a render target that renders to the texture
        
        :param parameters: Render parameters to create the render texture
        :param targets: How many color output targets
        :param width: The width of the render texture
        :param height: The height of the render texture'''
        raise NotImplementedError()
    
    @overload
    def create_render_texture(self, parameters : aspose.threed.render.RenderParameters, width : int, height : int) -> aspose.threed.render.IRenderTexture:
        '''Create a render target contains 1 targets that renders to the texture
        
        :param parameters: Render parameters to create the render texture
        :param width: The width of the render texture
        :param height: The height of the render texture'''
        raise NotImplementedError()
    
    @overload
    def create_texture_unit(self, texture_type : aspose.threed.render.TextureType) -> aspose.threed.render.ITextureUnit:
        '''Create a texture unit that can be accessed by shader.
        
        :param texture_type: Type of the texture'''
        raise NotImplementedError()
    
    @overload
    def create_texture_unit(self) -> aspose.threed.render.ITextureUnit:
        '''Create a 2D texture unit that can be accessed by shader.'''
        raise NotImplementedError()
    
    def create_descriptor_set(self, shader : aspose.threed.render.ShaderProgram) -> aspose.threed.render.IDescriptorSet:
        '''Create the descriptor set for specified shader program.
        
        :param shader: The shader program
        :returns: A new descriptor set instance'''
        raise NotImplementedError()
    
    def create_cube_render_texture(self, parameters : aspose.threed.render.RenderParameters, width : int, height : int) -> aspose.threed.render.IRenderTexture:
        '''Create a render target contains 1 cube texture
        
        :param parameters: Render parameters to create the render texture
        :param width: The width of the render texture
        :param height: The height of the render texture'''
        raise NotImplementedError()
    
    def create_render_window(self, parameters : aspose.threed.render.RenderParameters, handle : aspose.threed.render.WindowHandle) -> aspose.threed.render.IRenderWindow:
        '''Create a render target that renders to the native window.
        
        :param parameters: Render parameters to create the render window
        :param handle: The handle of the window to render'''
        raise NotImplementedError()
    
    def create_vertex_buffer(self, declaration : aspose.threed.utilities.VertexDeclaration) -> aspose.threed.render.IVertexBuffer:
        '''Create an :py:class:`aspose.threed.render.IVertexBuffer` instance to store polygon\'s vertex information.'''
        raise NotImplementedError()
    
    def create_index_buffer(self) -> aspose.threed.render.IIndexBuffer:
        '''Create an :py:class:`aspose.threed.render.IIndexBuffer` instance to store polygon\'s face information.'''
        raise NotImplementedError()
    
    def create_shader_program(self, shader_source : aspose.threed.render.ShaderSource) -> aspose.threed.render.ShaderProgram:
        '''Create a :py:class:`aspose.threed.render.ShaderProgram` object
        
        :param shader_source: The source code of the shader'''
        raise NotImplementedError()
    
    def create_pipeline(self, shader : aspose.threed.render.ShaderProgram, render_state : aspose.threed.render.RenderState, vertex_declaration : aspose.threed.utilities.VertexDeclaration, draw_operation : aspose.threed.render.DrawOperation) -> aspose.threed.render.IPipeline:
        '''Create a preconfigured graphics pipeline with preconfigured shader/render state/vertex declaration and draw operations.
        
        :param shader: The shader used in the rendering
        :param render_state: The render state used in the rendering
        :param vertex_declaration: The vertex declaration of input vertex data
        :param draw_operation: Draw operation
        :returns: A new pipeline instance'''
        raise NotImplementedError()
    
    def create_uniform_buffer(self, size : int) -> aspose.threed.render.IBuffer:
        '''Create a new uniform buffer in GPU side with pre-allocated size.
        
        :param size: The size of the uniform buffer
        :returns: The uniform buffer instance'''
        raise NotImplementedError()
    

class RenderParameters:
    '''Describe the parameters of the render target'''
    
    def __init__(self, double_buffering : bool, color_bits : int, depth_bits : int, stencil_bits : int) -> None:
        '''Initialize an instance of :py:class:`aspose.threed.render.PixelFormat`'''
        raise NotImplementedError()
    
    @property
    def double_buffering(self) -> bool:
        '''Gets whether double buffer is used.'''
        raise NotImplementedError()
    
    @double_buffering.setter
    def double_buffering(self, value : bool) -> None:
        '''Sets whether double buffer is used.'''
        raise NotImplementedError()
    
    @property
    def color_bits(self) -> int:
        '''Gets how many bits will be used by color buffer.'''
        raise NotImplementedError()
    
    @color_bits.setter
    def color_bits(self, value : int) -> None:
        '''Sets how many bits will be used by color buffer.'''
        raise NotImplementedError()
    
    @property
    def depth_bits(self) -> int:
        '''Gets how many bits will be used by depth buffer.'''
        raise NotImplementedError()
    
    @depth_bits.setter
    def depth_bits(self, value : int) -> None:
        '''Sets how many bits will be used by depth buffer.'''
        raise NotImplementedError()
    
    @property
    def stencil_bits(self) -> int:
        '''Gets how many bits will be used in stencil buffer.'''
        raise NotImplementedError()
    
    @stencil_bits.setter
    def stencil_bits(self, value : int) -> None:
        '''Sets how many bits will be used in stencil buffer.'''
        raise NotImplementedError()
    

class RenderResource:
    '''The abstract class of all render resources
    All render resources will be disposed when the renderer is released.
    Classes like :py:class:`aspose.threed.entities.Mesh`/:py:class:`aspose.threed.shading.Texture` will have a corresponding RenderResource'''
    

class RenderState:
    '''Render state for building the pipeline
    The changes made on render state will not affect the created pipeline instances.'''
    
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.render.RenderState`'''
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.threed.render.RenderState) -> int:
        '''Compare the render state with another instance
        
        :param other: Another render state to compare'''
        raise NotImplementedError()
    
    @property
    def blend(self) -> bool:
        '''Enable or disable the fragment blending.'''
        raise NotImplementedError()
    
    @blend.setter
    def blend(self, value : bool) -> None:
        '''Enable or disable the fragment blending.'''
        raise NotImplementedError()
    
    @property
    def blend_color(self) -> aspose.threed.utilities.FVector4:
        '''Gets the blend color where used in :py:attr:`aspose.threed.render.BlendFactor.CONSTANT_COLOR`'''
        raise NotImplementedError()
    
    @blend_color.setter
    def blend_color(self, value : aspose.threed.utilities.FVector4) -> None:
        '''Sets the blend color where used in :py:attr:`aspose.threed.render.BlendFactor.CONSTANT_COLOR`'''
        raise NotImplementedError()
    
    @property
    def source_blend_factor(self) -> aspose.threed.render.BlendFactor:
        '''Gets how the color is blended.'''
        raise NotImplementedError()
    
    @source_blend_factor.setter
    def source_blend_factor(self, value : aspose.threed.render.BlendFactor) -> None:
        '''Sets how the color is blended.'''
        raise NotImplementedError()
    
    @property
    def destination_blend_factor(self) -> aspose.threed.render.BlendFactor:
        '''Gets how the color is blended.'''
        raise NotImplementedError()
    
    @destination_blend_factor.setter
    def destination_blend_factor(self, value : aspose.threed.render.BlendFactor) -> None:
        '''Sets how the color is blended.'''
        raise NotImplementedError()
    
    @property
    def cull_face(self) -> bool:
        '''Enable or disable cull face'''
        raise NotImplementedError()
    
    @cull_face.setter
    def cull_face(self, value : bool) -> None:
        '''Enable or disable cull face'''
        raise NotImplementedError()
    
    @property
    def cull_face_mode(self) -> aspose.threed.render.CullFaceMode:
        '''Gets which face will be culled.'''
        raise NotImplementedError()
    
    @cull_face_mode.setter
    def cull_face_mode(self, value : aspose.threed.render.CullFaceMode) -> None:
        '''Sets which face will be culled.'''
        raise NotImplementedError()
    
    @property
    def front_face(self) -> aspose.threed.render.FrontFace:
        '''Gets which order is front face.'''
        raise NotImplementedError()
    
    @front_face.setter
    def front_face(self, value : aspose.threed.render.FrontFace) -> None:
        '''Sets which order is front face.'''
        raise NotImplementedError()
    
    @property
    def depth_test(self) -> bool:
        '''Enable or disable the depth test.'''
        raise NotImplementedError()
    
    @depth_test.setter
    def depth_test(self, value : bool) -> None:
        '''Enable or disable the depth test.'''
        raise NotImplementedError()
    
    @property
    def depth_mask(self) -> bool:
        '''Enable or disable the depth writing.'''
        raise NotImplementedError()
    
    @depth_mask.setter
    def depth_mask(self, value : bool) -> None:
        '''Enable or disable the depth writing.'''
        raise NotImplementedError()
    
    @property
    def depth_function(self) -> aspose.threed.render.CompareFunction:
        '''Gets the compare function used in depth test'''
        raise NotImplementedError()
    
    @depth_function.setter
    def depth_function(self, value : aspose.threed.render.CompareFunction) -> None:
        '''Sets the compare function used in depth test'''
        raise NotImplementedError()
    
    @property
    def stencil_test(self) -> bool:
        '''Enable or disable the stencil test.'''
        raise NotImplementedError()
    
    @stencil_test.setter
    def stencil_test(self, value : bool) -> None:
        '''Enable or disable the stencil test.'''
        raise NotImplementedError()
    
    @property
    def stencil_reference(self) -> int:
        '''Gets the reference value for the stencil test.'''
        raise NotImplementedError()
    
    @stencil_reference.setter
    def stencil_reference(self, value : int) -> None:
        '''Sets the reference value for the stencil test.'''
        raise NotImplementedError()
    
    @property
    def stencil_mask(self) -> int:
        '''Gets the mask that is ANDed with the both reference and stored stencil value when test is done.'''
        raise NotImplementedError()
    
    @stencil_mask.setter
    def stencil_mask(self, value : int) -> None:
        '''Sets the mask that is ANDed with the both reference and stored stencil value when test is done.'''
        raise NotImplementedError()
    
    @property
    def stencil_front_face(self) -> aspose.threed.render.StencilState:
        '''Gets the stencil state for front face.'''
        raise NotImplementedError()
    
    @property
    def stencil_back_face(self) -> aspose.threed.render.StencilState:
        '''Gets the stencil state for back face.'''
        raise NotImplementedError()
    
    @property
    def scissor_test(self) -> bool:
        '''Enable or disable scissor test'''
        raise NotImplementedError()
    
    @scissor_test.setter
    def scissor_test(self, value : bool) -> None:
        '''Enable or disable scissor test'''
        raise NotImplementedError()
    
    @property
    def polygon_mode(self) -> aspose.threed.render.PolygonMode:
        '''Gets the polygon\'s render mode.'''
        raise NotImplementedError()
    
    @polygon_mode.setter
    def polygon_mode(self, value : aspose.threed.render.PolygonMode) -> None:
        '''Sets the polygon\'s render mode.'''
        raise NotImplementedError()
    

class Renderer:
    '''The context about renderer.'''
    
    def clear_cache(self) -> None:
        '''Manually clear the cache.
        Aspose.3D will cache some objects like materials/geometries into internal types that compatible with the render pipeline.
        This should be manually called when scene has major changes.'''
        raise NotImplementedError()
    
    def get_post_processing(self, name : str) -> aspose.threed.render.PostProcessing:
        '''Gets a built-in post-processor that supported by the renderer.'''
        raise NotImplementedError()
    
    def execute(self, post_processing : aspose.threed.render.PostProcessing, result : aspose.threed.render.IRenderTarget) -> None:
        '''Execute an post processing on specified render target'''
        raise NotImplementedError()
    
    @staticmethod
    def create_renderer() -> aspose.threed.render.Renderer:
        '''Creates a new :py:class:`aspose.threed.render.Renderer` with default profile.'''
        raise NotImplementedError()
    
    def register_entity_renderer(self, renderer : aspose.threed.render.EntityRenderer) -> None:
        '''Register the entity renderer for specified entity'''
        raise NotImplementedError()
    
    def render(self, render_target : aspose.threed.render.IRenderTarget) -> None:
        '''Render the specified target'''
        raise NotImplementedError()
    
    @property
    def shader_set(self) -> aspose.threed.render.ShaderSet:
        '''Gets the shader set that used to render the scene'''
        raise NotImplementedError()
    
    @shader_set.setter
    def shader_set(self, value : aspose.threed.render.ShaderSet) -> None:
        '''Sets the shader set that used to render the scene'''
        raise NotImplementedError()
    
    @property
    def variables(self) -> aspose.threed.render.RendererVariableManager:
        '''Access to the internal variables used for rendering'''
        raise NotImplementedError()
    
    @property
    def preset_shaders(self) -> aspose.threed.render.PresetShaders:
        '''Gets the preset shader set'''
        raise NotImplementedError()
    
    @preset_shaders.setter
    def preset_shaders(self, value : aspose.threed.render.PresetShaders) -> None:
        '''Sets the preset shader set'''
        raise NotImplementedError()
    
    @property
    def render_factory(self) -> aspose.threed.render.RenderFactory:
        '''Gets the factory to build render-related objects.'''
        raise NotImplementedError()
    
    @property
    def asset_directories(self) -> System.Collections.Generic.List`1[[System.String]]:
        '''Directories that stored external assets'''
        raise NotImplementedError()
    
    @property
    def post_processings(self) -> System.Collections.Generic.IList`1[[Aspose.ThreeD.Render.PostProcessing]]:
        '''Active post-processing chain'''
        raise NotImplementedError()
    
    @property
    def enable_shadows(self) -> bool:
        '''Gets whether to enable shadows.'''
        raise NotImplementedError()
    
    @enable_shadows.setter
    def enable_shadows(self, value : bool) -> None:
        '''Sets whether to enable shadows.'''
        raise NotImplementedError()
    
    @property
    def render_target(self) -> aspose.threed.render.IRenderTarget:
        '''Specify the render target that the following render operations will be performed on.'''
        raise NotImplementedError()
    
    @property
    def node(self) -> aspose.threed.Node:
        '''Gets the :py:attr:`aspose.threed.render.Renderer.node` instance used to provide world transform matrix.'''
        raise NotImplementedError()
    
    @node.setter
    def node(self, value : aspose.threed.Node) -> None:
        '''Sets the :py:attr:`aspose.threed.render.Renderer.node` instance used to provide world transform matrix.'''
        raise NotImplementedError()
    
    @property
    def frustum(self) -> aspose.threed.entities.Frustum:
        '''Gets the frustum that used to provide view matrix.'''
        raise NotImplementedError()
    
    @frustum.setter
    def frustum(self, value : aspose.threed.entities.Frustum) -> None:
        '''Sets the frustum that used to provide view matrix.'''
        raise NotImplementedError()
    
    @property
    def render_stage(self) -> aspose.threed.render.RenderStage:
        '''Gets the current render stage.'''
        raise NotImplementedError()
    
    @property
    def material(self) -> aspose.threed.shading.Material:
        '''Gets the material that used to provide material information used by shaders.'''
        raise NotImplementedError()
    
    @material.setter
    def material(self, value : aspose.threed.shading.Material) -> None:
        '''Sets the material that used to provide material information used by shaders.'''
        raise NotImplementedError()
    
    @property
    def shader(self) -> aspose.threed.render.ShaderProgram:
        '''Gets the shader instance used for rendering the geometry.'''
        raise NotImplementedError()
    
    @shader.setter
    def shader(self, value : aspose.threed.render.ShaderProgram) -> None:
        '''Sets the shader instance used for rendering the geometry.'''
        raise NotImplementedError()
    
    @property
    def fallback_entity_renderer(self) -> aspose.threed.render.EntityRenderer:
        '''Gets the fallback entity renderer when the entity has no special renderer defined.'''
        raise NotImplementedError()
    
    @fallback_entity_renderer.setter
    def fallback_entity_renderer(self, value : aspose.threed.render.EntityRenderer) -> None:
        '''Sets the fallback entity renderer when the entity has no special renderer defined.'''
        raise NotImplementedError()
    

class RendererVariableManager:
    '''This class manages variables used in rendering'''
    
    @property
    def world_time(self) -> float:
        '''Time in seconds'''
        raise NotImplementedError()
    
    @property
    def shadow_caster(self) -> aspose.threed.utilities.FVector3:
        '''Position of shadow caster in world coordinate system'''
        raise NotImplementedError()
    
    @shadow_caster.setter
    def shadow_caster(self, value : aspose.threed.utilities.FVector3) -> None:
        '''Position of shadow caster in world coordinate system'''
        raise NotImplementedError()
    
    @property
    def shadowmap(self) -> aspose.threed.render.ITextureUnit:
        '''The depth texture used for shadow mapping'''
        raise NotImplementedError()
    
    @shadowmap.setter
    def shadowmap(self, value : aspose.threed.render.ITextureUnit) -> None:
        '''The depth texture used for shadow mapping'''
        raise NotImplementedError()
    
    @property
    def matrix_light_space(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for light space transformation'''
        raise NotImplementedError()
    
    @matrix_light_space.setter
    def matrix_light_space(self, value : aspose.threed.utilities.FMatrix4) -> None:
        '''Matrix for light space transformation'''
        raise NotImplementedError()
    
    @property
    def matrix_view_projection(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for view and projection transformation.'''
        raise NotImplementedError()
    
    @property
    def matrix_world_view_projection(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for world view and projection transformation'''
        raise NotImplementedError()
    
    @property
    def matrix_world(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for world transformation'''
        raise NotImplementedError()
    
    @property
    def matrix_world_normal(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for converting normal from object to world space.'''
        raise NotImplementedError()
    
    @property
    def matrix_projection(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for projection transformation'''
        raise NotImplementedError()
    
    @matrix_projection.setter
    def matrix_projection(self, value : aspose.threed.utilities.FMatrix4) -> None:
        '''Matrix for projection transformation'''
        raise NotImplementedError()
    
    @property
    def matrix_view(self) -> aspose.threed.utilities.FMatrix4:
        '''Matrix for view transformation'''
        raise NotImplementedError()
    
    @matrix_view.setter
    def matrix_view(self, value : aspose.threed.utilities.FMatrix4) -> None:
        '''Matrix for view transformation'''
        raise NotImplementedError()
    
    @property
    def camera_position(self) -> aspose.threed.utilities.FVector3:
        '''Camera\'s position in world coordinate system'''
        raise NotImplementedError()
    
    @camera_position.setter
    def camera_position(self, value : aspose.threed.utilities.FVector3) -> None:
        '''Camera\'s position in world coordinate system'''
        raise NotImplementedError()
    
    @property
    def depth_bias(self) -> float:
        '''Depth bias for shadow mapping, default value is 0.001'''
        raise NotImplementedError()
    
    @depth_bias.setter
    def depth_bias(self, value : float) -> None:
        '''Depth bias for shadow mapping, default value is 0.001'''
        raise NotImplementedError()
    
    @property
    def viewport_size(self) -> aspose.threed.utilities.FVector2:
        '''Size of viewport, measured in pixel'''
        raise NotImplementedError()
    
    @property
    def world_ambient(self) -> aspose.threed.utilities.FVector3:
        '''Ambient color defined in viewport.'''
        raise NotImplementedError()
    

class SPIRVSource(ShaderSource):
    '''The compiled shader in SPIR-V format.'''
    
    def __init__(self) -> None:
        '''Constructor of SPIR-V based shader sources.'''
        raise NotImplementedError()
    
    @property
    def maximum_descriptor_sets(self) -> int:
        '''Maximum descriptor sets, default value is 10'''
        raise NotImplementedError()
    
    @maximum_descriptor_sets.setter
    def maximum_descriptor_sets(self, value : int) -> None:
        '''Maximum descriptor sets, default value is 10'''
        raise NotImplementedError()
    
    @property
    def compute_shader(self) -> List[int]:
        '''Gets the source code of the compute shader.'''
        raise NotImplementedError()
    
    @compute_shader.setter
    def compute_shader(self, value : List[int]) -> None:
        '''Sets the source code of the compute shader.'''
        raise NotImplementedError()
    
    @property
    def geometry_shader(self) -> List[int]:
        '''Gets the source code of the geometry shader.'''
        raise NotImplementedError()
    
    @geometry_shader.setter
    def geometry_shader(self, value : List[int]) -> None:
        '''Sets the source code of the geometry shader.'''
        raise NotImplementedError()
    
    @property
    def vertex_shader(self) -> List[int]:
        '''Gets the source code of the vertex shader'''
        raise NotImplementedError()
    
    @vertex_shader.setter
    def vertex_shader(self, value : List[int]) -> None:
        '''Sets the source code of the vertex shader'''
        raise NotImplementedError()
    
    @property
    def fragment_shader(self) -> List[int]:
        '''Gets the source code of the fragment shader.'''
        raise NotImplementedError()
    
    @fragment_shader.setter
    def fragment_shader(self, value : List[int]) -> None:
        '''Sets the source code of the fragment shader.'''
        raise NotImplementedError()
    

class ShaderException:
    '''Shader related exceptions'''
    
    def __init__(self, message : str) -> None:
        '''Constructor of :py:class:`aspose.threed.render.ShaderException`'''
        raise NotImplementedError()
    

class ShaderProgram:
    '''The shader program'''
    

class ShaderSet:
    '''Shader programs for each kind of materials'''
    
    def __init__(self) -> None:
        '''Construct the instance of :py:class:`aspose.threed.render.ShaderSet`'''
        raise NotImplementedError()
    
    @property
    def lambert(self) -> aspose.threed.render.ShaderProgram:
        '''Gets the shader that used to render the lambert material'''
        raise NotImplementedError()
    
    @lambert.setter
    def lambert(self, value : aspose.threed.render.ShaderProgram) -> None:
        '''Sets the shader that used to render the lambert material'''
        raise NotImplementedError()
    
    @property
    def phong(self) -> aspose.threed.render.ShaderProgram:
        '''Gets the shader that used to render the phong material'''
        raise NotImplementedError()
    
    @phong.setter
    def phong(self, value : aspose.threed.render.ShaderProgram) -> None:
        '''Sets the shader that used to render the phong material'''
        raise NotImplementedError()
    
    @property
    def pbr(self) -> aspose.threed.render.ShaderProgram:
        '''Gets the shader that used to render the PBR material'''
        raise NotImplementedError()
    
    @pbr.setter
    def pbr(self, value : aspose.threed.render.ShaderProgram) -> None:
        '''Sets the shader that used to render the PBR material'''
        raise NotImplementedError()
    
    @property
    def fallback(self) -> aspose.threed.render.ShaderProgram:
        '''Gets the fallback shader when required shader is unavailable'''
        raise NotImplementedError()
    
    @fallback.setter
    def fallback(self, value : aspose.threed.render.ShaderProgram) -> None:
        '''Sets the fallback shader when required shader is unavailable'''
        raise NotImplementedError()
    

class ShaderSource:
    '''The source code of shader'''
    

class ShaderVariable:
    '''Shader variable'''
    
    @overload
    def __init__(self, name : str) -> None:
        '''Constructor of :py:class:`aspose.threed.render.ShaderVariable`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, name : str, shader_stage : aspose.threed.render.ShaderStage) -> None:
        '''Constructor of :py:class:`aspose.threed.render.ShaderVariable`
        
        :param shader_stage: Which shader stage will this variable be used'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this variable'''
        raise NotImplementedError()
    

class StencilState:
    '''Stencil states per face.'''
    
    @property
    def compare(self) -> aspose.threed.render.CompareFunction:
        '''Gets the compare function used in stencil test'''
        raise NotImplementedError()
    
    @compare.setter
    def compare(self, value : aspose.threed.render.CompareFunction) -> None:
        '''Sets the compare function used in stencil test'''
        raise NotImplementedError()
    
    @property
    def fail_action(self) -> aspose.threed.render.StencilAction:
        '''Gets the stencil action when stencil test fails.'''
        raise NotImplementedError()
    
    @fail_action.setter
    def fail_action(self, value : aspose.threed.render.StencilAction) -> None:
        '''Sets the stencil action when stencil test fails.'''
        raise NotImplementedError()
    
    @property
    def depth_fail_action(self) -> aspose.threed.render.StencilAction:
        '''Gets the stencil action when stencil test pass but depth test fails.'''
        raise NotImplementedError()
    
    @depth_fail_action.setter
    def depth_fail_action(self, value : aspose.threed.render.StencilAction) -> None:
        '''Sets the stencil action when stencil test pass but depth test fails.'''
        raise NotImplementedError()
    
    @property
    def pass_action(self) -> aspose.threed.render.StencilAction:
        '''Gets the stencil action when both stencil test and depth test passes.'''
        raise NotImplementedError()
    
    @pass_action.setter
    def pass_action(self, value : aspose.threed.render.StencilAction) -> None:
        '''Sets the stencil action when both stencil test and depth test passes.'''
        raise NotImplementedError()
    

class TextureCodec:
    '''Class to manage encoders and decoders for textures.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @staticmethod
    def get_supported_encoder_formats() -> List[str]:
        '''Gets all supported encoder formats'''
        raise NotImplementedError()
    
    @staticmethod
    def register_codec(codec : aspose.threed.render.ITextureCodec) -> None:
        '''Register a set of texture encoders and decoders'''
        raise NotImplementedError()
    
    @staticmethod
    def encode(texture : aspose.threed.render.TextureData, stream : io._IOBase, format : str) -> None:
        '''Encode texture data into stream using specified format
        
        :param texture: The texture to be encoded
        :param stream: The output stream
        :param format: The image format of encoded data, like png/jpg'''
        raise NotImplementedError()
    
    @staticmethod
    def decode(stream : io._IOBase, reverse_y : bool) -> aspose.threed.render.TextureData:
        '''Decode texture data from stream'''
        raise NotImplementedError()
    

class TextureData(aspose.threed.A3DObject):
    '''This class contains the raw data and format definition of a texture.'''
    
    @overload
    def __init__(self, width : int, height : int, stride : int, bytes_per_pixel : int, pixel_format : aspose.threed.render.PixelFormat, data : List[int]) -> None:
        '''Constructor of :py:class:`aspose.threed.render.TextureData`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, width : int, height : int, pixel_format : aspose.threed.render.PixelFormat) -> None:
        '''Constructs a new :py:class:`aspose.threed.render.TextureData` and allocate pixel data.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self) -> None:
        '''Constructor of :py:class:`aspose.threed.render.TextureData`'''
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
    def save(self, stream : io._IOBase, format : str) -> None:
        '''Save texture data into specified image format
        
        :param stream: The stream that holds the saved image
        :param format: Image format, usually file extension'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str) -> None:
        '''Save texture data into image file
        
        :param file_name: The file name of where the image will be saved.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str, format : str) -> None:
        '''Save texture data into image file
        
        :param file_name: The file name of where the image will be saved.
        :param format: Image format of the output file.'''
        raise NotImplementedError()
    
    @overload
    def map_pixels(self, map_mode : aspose.threed.render.PixelMapMode) -> aspose.threed.render.PixelMapping:
        '''Map all pixels for read/write
        
        :param map_mode: Map mode'''
        raise NotImplementedError()
    
    @overload
    def map_pixels(self, map_mode : aspose.threed.render.PixelMapMode, format : aspose.threed.render.PixelFormat) -> aspose.threed.render.PixelMapping:
        '''Map all pixels for read/write in given pixel format
        
        :param map_mode: Map mode
        :param format: Pixel format'''
        raise NotImplementedError()
    
    @overload
    def map_pixels(self, rect : aspose.threed.utilities.Rect, map_mode : aspose.threed.render.PixelMapMode, format : aspose.threed.render.PixelFormat) -> aspose.threed.render.PixelMapping:
        '''Map pixels addressed by rect for reading/writing in given pixel format
        
        :param rect: The area of pixels to be accessed
        :param map_mode: Map mode
        :param format: Pixel format
        :returns: Returns a mapping object, it should be disposed when no longer needed.'''
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
    def from_stream(stream : io._IOBase) -> aspose.threed.render.TextureData:
        '''Load a texture from stream'''
        raise NotImplementedError()
    
    @staticmethod
    def from_file(file_name : str) -> aspose.threed.render.TextureData:
        '''Load a texture from file'''
        raise NotImplementedError()
    
    def transform_pixel_format(self, pixel_format : aspose.threed.render.PixelFormat) -> None:
        '''Transform pixel\'s layout to new pixel format.
        
        :param pixel_format: Destination pixel format'''
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
    def data(self) -> List[int]:
        '''Raw bytes of pixel data'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Number of horizontal pixels'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Number of vertical pixels'''
        raise NotImplementedError()
    
    @property
    def stride(self) -> int:
        '''Number of bytes of a scanline.'''
        raise NotImplementedError()
    
    @property
    def bytes_per_pixel(self) -> int:
        '''Number of bytes of a pixel'''
        raise NotImplementedError()
    
    @property
    def pixel_format(self) -> aspose.threed.render.PixelFormat:
        '''The pixel\'s format'''
        raise NotImplementedError()
    

class Viewport:
    '''A :py:class:`aspose.threed.render.IRenderTarget` contains at least one viewport for rendering the scene.'''
    
    @property
    def frustum(self) -> aspose.threed.entities.Frustum:
        '''Gets the camera of this :py:class:`aspose.threed.render.Viewport`'''
        raise NotImplementedError()
    
    @frustum.setter
    def frustum(self, value : aspose.threed.entities.Frustum) -> None:
        '''Sets the camera of this :py:class:`aspose.threed.render.Viewport`'''
        raise NotImplementedError()
    
    @property
    def enabled(self) -> bool:
        '''Enable or disable this viewport.'''
        raise NotImplementedError()
    
    @enabled.setter
    def enabled(self, value : bool) -> None:
        '''Enable or disable this viewport.'''
        raise NotImplementedError()
    
    @property
    def render_target(self) -> aspose.threed.render.IRenderTarget:
        '''Gets the render target that created this viewport.'''
        raise NotImplementedError()
    
    @property
    def area(self) -> aspose.threed.utilities.RelativeRectangle:
        '''Gets the area of the viewport in render target.'''
        raise NotImplementedError()
    
    @area.setter
    def area(self, value : aspose.threed.utilities.RelativeRectangle) -> None:
        '''Sets the area of the viewport in render target.'''
        raise NotImplementedError()
    
    @property
    def z_order(self) -> int:
        '''Gets the Z-order of the viewport.'''
        raise NotImplementedError()
    
    @z_order.setter
    def z_order(self, value : int) -> None:
        '''Sets the Z-order of the viewport.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.threed.utilities.Vector3:
        '''Gets the background color of the viewport.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.threed.utilities.Vector3) -> None:
        '''Sets the background color of the viewport.'''
        raise NotImplementedError()
    
    @property
    def depth_clear(self) -> float:
        '''Gets the depth value used when clear the viewport with depth buffer bit set.'''
        raise NotImplementedError()
    
    @depth_clear.setter
    def depth_clear(self, value : float) -> None:
        '''Sets the depth value used when clear the viewport with depth buffer bit set.'''
        raise NotImplementedError()
    

class WindowHandle:
    '''Encapsulated window handle for different platforms.'''
    

class BlendFactor:
    '''Blend factor specify pixel arithmetic.'''
    
    ZERO : BlendFactor
    '''The blend factor is vec4(0)'''
    ONE : BlendFactor
    '''The blend factor is vec4(1)'''
    SRC_COLOR : BlendFactor
    '''The blend factor is src.rgba'''
    ONE_MINUS_SRC_COLOR : BlendFactor
    '''The blend factor is vec4(1) - src.rgba'''
    DST_COLOR : BlendFactor
    '''The blend factor is dst.rgba'''
    ONE_MINUS_DST_COLOR : BlendFactor
    '''The blend factor is vec4(1) - dst.rgba'''
    SRC_ALPHA : BlendFactor
    '''The blend factor is vec4(src.a)'''
    ONE_MINUS_SRC_ALPHA : BlendFactor
    '''The blend factor is vec4(1 - src.a)'''
    DST_ALPHA : BlendFactor
    '''The blend factor is vec4(dst.a)'''
    ONE_MINUS_DST_ALPHA : BlendFactor
    '''The blend factor is vec4(1 - dst.a)'''
    CONSTANT_COLOR : BlendFactor
    '''The blend factor is c where c is specified in :py:attr:`aspose.threed.render.RenderState.blend_color`'''
    ONE_MINUS_CONSTANT_COLOR : BlendFactor
    '''The blend factor is vec4(1) - c where c is specified in :py:attr:`aspose.threed.render.RenderState.blend_color`'''
    CONSTANT_ALPHA : BlendFactor
    '''The blend factor is vec4(c.a) where c is specified in :py:attr:`aspose.threed.render.RenderState.blend_color`'''
    ONE_MINUS_CONSTANT_ALPHA : BlendFactor
    '''The blend factor is vec4(1 - c.a) where c is specified in :py:attr:`aspose.threed.render.RenderState.blend_color`'''
    SRC_ALPHA_SATURATE : BlendFactor
    '''The blend factor is min(src.a, 1 - dst.a)'''

class CompareFunction:
    '''The compare function used in depth/stencil testing.'''
    
    NEVER : CompareFunction
    '''Never passes'''
    LESS : CompareFunction
    '''Pass if the incoming value is less than the stored value.'''
    EQUAL : CompareFunction
    '''Pass if the incoming value is equal to the stored value.'''
    L_EQUAL : CompareFunction
    '''Pass if the incoming value is less than or equal to the stored value.'''
    GREATER : CompareFunction
    '''Pass if the incoming value is greater than the stored value.'''
    NOT_EQUAL : CompareFunction
    '''Pass if the incoming value is not equal to the stored value.'''
    G_EQUAL : CompareFunction
    '''Pass if the incoming value is greater than or equal to the stored value.'''
    ALWAYS : CompareFunction
    '''Always passes'''

class CubeFace:
    '''Each face of the cube map texture'''
    
    POSITIVE_X : CubeFace
    '''The +X face'''
    NEGATIVE_X : CubeFace
    '''The -X face'''
    POSITIVE_Y : CubeFace
    '''The +Y face'''
    NEGATIVE_Y : CubeFace
    '''The -Y face'''
    POSITIVE_Z : CubeFace
    '''The +Z face'''
    NEGATIVE_Z : CubeFace
    '''The -Z face'''

class CullFaceMode:
    '''What face to cull'''
    
    BACK : CullFaceMode
    '''Only back faces are culled'''
    FRONT : CullFaceMode
    '''Only front faces are culled'''
    BOTH : CullFaceMode
    '''Both back/front faces are culled, doesn\'t affect line/point rendering.'''

class DrawOperation:
    '''The primitive types to render'''
    
    POINTS : DrawOperation
    '''Points'''
    LINES : DrawOperation
    '''Lines'''
    LINE_STRIP : DrawOperation
    '''Line strips'''
    TRIANGLES : DrawOperation
    '''Triangles'''
    TRIANGLE_STRIP : DrawOperation
    '''Triangle strips'''
    TRIANGLE_FAN : DrawOperation
    '''Triangle fan'''

class EntityRendererFeatures:
    '''The extra features that the entity renderer will provide'''
    
    DEFAULT : EntityRendererFeatures
    '''No extra features'''
    FRAME_BEGIN : EntityRendererFeatures
    '''The :py:class:`aspose.threed.render.EntityRenderer` will watch for FrameBegin callback before rendering each scene frame'''
    FRAME_END : EntityRendererFeatures
    '''The :py:class:`aspose.threed.render.EntityRenderer` will watch for FrameBegin callback after rendering each scene frame'''
    SHADOWMAP : EntityRendererFeatures
    '''This renderer can work in shadowmap mode'''

class FrontFace:
    '''Define front- and back-facing polygons'''
    
    CLOCKWISE : FrontFace
    '''Clockwise order is front face'''
    COUNTER_CLOCKWISE : FrontFace
    '''Counter-clockwise order is front face'''

class IndexDataType:
    '''The data type of the elements in :py:class:`aspose.threed.render.IIndexBuffer`'''
    
    INT32 : IndexDataType
    '''The index buffer\'s elements are 32bit int'''
    INT16 : IndexDataType
    '''The index buffer\'s elements are 16bit int'''

class PixelFormat:
    '''The pixel\'s format used in texture unit.'''
    
    UNKNOWN : PixelFormat
    '''Unknown pixel format.'''
    L8 : PixelFormat
    '''8-bit pixel format, all bits luminance.'''
    L16 : PixelFormat
    '''16-bit pixel format, all bits luminance.'''
    A8 : PixelFormat
    '''8-bit pixel format, all bits alpha.'''
    A4L4 : PixelFormat
    '''8-bit pixel format, 4 bits alpha, 4 bits luminance.'''
    BYTE_LA : PixelFormat
    '''2 byte pixel format, 1 byte luminance, 1 byte alpha'''
    R5G6B5 : PixelFormat
    '''16-bit pixel format, 5 bits red, 6 bits green, 5 bits blue.'''
    B5G6R5 : PixelFormat
    '''16-bit pixel format, 5 bits red, 6 bits green, 5 bits blue.'''
    R3G3B2 : PixelFormat
    '''8-bit pixel format, 2 bits blue, 3 bits green, 3 bits red.'''
    A4R4G4B4 : PixelFormat
    '''16-bit pixel format, 4 bits for alpha, red, green and blue.'''
    A1R5G5B5 : PixelFormat
    '''16-bit pixel format, 5 bits for blue, green, red and 1 for alpha.'''
    R8G8B8 : PixelFormat
    '''24-bit pixel format, 8 bits for red, green and blue.'''
    B8G8R8 : PixelFormat
    '''24-bit pixel format, 8 bits for blue, green and red.'''
    A8R8G8B8 : PixelFormat
    '''32-bit pixel format, 8 bits for alpha, red, green and blue.'''
    A8B8G8R8 : PixelFormat
    '''32-bit pixel format, 8 bits for blue, green, red and alpha.'''
    B8G8R8A8 : PixelFormat
    '''32-bit pixel format, 8 bits for blue, green, red and alpha.'''
    R8G8B8A8 : PixelFormat
    '''32-bit pixel format, 8 bits for red, green, blue and alpha.'''
    X8R8G8B8 : PixelFormat
    '''32-bit pixel format, 8 bits for red, 8 bits for green, 8 bits for blue like A8R8G8B8, but alpha will get discarded'''
    X8B8G8R8 : PixelFormat
    '''32-bit pixel format, 8 bits for blue, 8 bits for green, 8 bits for red like A8B8G8R8, but alpha will get discarded'''
    A2R10G10B10 : PixelFormat
    '''32-bit pixel format, 2 bits for alpha, 10 bits for red, green and blue.'''
    A2B10G10R10 : PixelFormat
    '''32-bit pixel format, 10 bits for blue, green and red, 2 bits for alpha.'''
    DXT1 : PixelFormat
    '''DDS (DirectDraw Surface) DXT1 format.'''
    DXT2 : PixelFormat
    '''DDS (DirectDraw Surface) DXT2 format.'''
    DXT3 : PixelFormat
    '''DDS (DirectDraw Surface) DXT3 format.'''
    DXT4 : PixelFormat
    '''DDS (DirectDraw Surface) DXT4 format.'''
    DXT5 : PixelFormat
    '''DDS (DirectDraw Surface) DXT5 format.'''
    FLOAT16_R : PixelFormat
    '''16-bit pixel format, 16 bits (float) for red'''
    FLOAT16_RGB : PixelFormat
    '''48-bit pixel format, 16 bits (float) for red, 16 bits (float) for green, 16 bits (float) for blue'''
    FLOAT16_RGBA : PixelFormat
    '''64-bit pixel format, 16 bits (float) for red, 16 bits (float) for green, 16 bits (float) for blue, 16 bits (float) for alpha'''
    FLOAT32_R : PixelFormat
    '''32-bit pixel format, 32 bits (float) for red'''
    FLOAT32_RGB : PixelFormat
    '''96-bit pixel format, 32 bits (float) for red, 32 bits (float) for green, 32 bits (float) for blue'''
    FLOAT32_RGBA : PixelFormat
    '''128-bit pixel format, 32 bits (float) for red, 32 bits (float) for green, 32 bits (float) for blue, 32 bits (float) for alpha'''
    FLOAT16_GR : PixelFormat
    '''32-bit, 2-channel s10e5 floating point pixel format, 16-bit green, 16-bit red'''
    FLOAT32_GR : PixelFormat
    '''64-bit, 2-channel floating point pixel format, 32-bit green, 32-bit red'''
    DEPTH : PixelFormat
    '''Depth texture format.'''
    SHORT_RGBA : PixelFormat
    '''64-bit pixel format, 16 bits for red, green, blue and alpha'''
    SHORT_GR : PixelFormat
    '''32-bit pixel format, 16-bit green, 16-bit red'''
    SHORT_RGB : PixelFormat
    '''48-bit pixel format, 16 bits for red, green and blue'''
    R32_UINT : PixelFormat
    '''32-bit pixel format, 32 bits red (unsigned int).'''
    R32G32_UINT : PixelFormat
    '''64-bit pixel format, 32 bits red (unsigned int), 32 bits blue (unsigned int).'''
    R32G32B32A32_UINT : PixelFormat
    '''128-bit pixel format, 32 bits red (unsigned int), 32 bits blue (unsigned int), 32 bits green (unsigned int), 32 bits alpha (unsigned int).'''
    R8 : PixelFormat
    '''8-bit pixel format, all bits red.'''
    G8 : PixelFormat
    '''8-bit pixel format, all bits green.'''
    B8 : PixelFormat
    '''8-bit pixel format, all bits blue.'''

class PixelMapMode:
    
    READ_ONLY : PixelMapMode
    '''The pixels are mapped only for reading.'''
    READ_WRITE : PixelMapMode
    '''The pixels are mapped for both reading and writing.'''
    WRITE_ONLY : PixelMapMode
    '''The pixels are mapped only for writing.'''

class PolygonMode:
    '''The polygon rasterization mode'''
    
    POINT : PolygonMode
    '''Polygon control points are drawn as points.'''
    LINE : PolygonMode
    '''Boundary edges of the polygon are drawn as line segments.'''
    FILL : PolygonMode
    '''The interior of the polygon is filled.'''

class PresetShaders:
    '''This defines the preset internal shaders used by the renderer.'''
    
    DEFAULT : PresetShaders
    '''Use the default shaders for phong/lambert/pbr materials'''
    CUSTOMIZED : PresetShaders
    '''User\'s customized shader set'''

class RenderQueueGroupId:
    '''The group id of render queue'''
    
    BACKGROUND : RenderQueueGroupId
    '''Render queue for background'''
    SKIES : RenderQueueGroupId
    '''Render queue for skies'''
    GEOMETRIES : RenderQueueGroupId
    '''Render queue for geometries'''
    MAIN : RenderQueueGroupId
    '''Render queue for main'''
    OPAQUE : RenderQueueGroupId
    '''Render queue for opaque objects'''
    OVERLAY : RenderQueueGroupId
    '''Render queue for overlays'''

class RenderStage:
    '''The render stage'''
    
    IDLE : RenderStage
    '''Renderer is idle'''
    SHADOW_MAP : RenderStage
    '''Renderer is rendering a shadow map'''
    SCENE : RenderStage
    '''Renderer is rendering the scene'''
    POST_PROCESSING : RenderStage
    '''Renderer is rendering post processing effects.'''

class ShaderStage:
    '''Shader stage'''
    
    VERTEX_SHADER : ShaderStage
    '''Vertex shader'''
    FRAGMENT_SHADER : ShaderStage
    '''Fragment shader'''
    GEOMETRY_SHADER : ShaderStage
    '''Geometry shader'''
    COMPUTE_SHADER : ShaderStage
    '''Compute shader'''

class StencilAction:
    '''The stencil test actions'''
    
    KEEP : StencilAction
    '''Keep the current value'''
    ZERO : StencilAction
    '''Sets the stencil buffer value to 0'''
    REPLACE : StencilAction
    '''Sets the stencil buffer to ref where defined in :py:attr:`aspose.threed.render.RenderState.stencil_reference`'''
    INCREMENT : StencilAction
    '''Increments the current stencil buffer value, clamps to maximum value.'''
    INCREMENT_WRAP : StencilAction
    '''Increments the current stencil buffer value and wrap it to zero when it reaches maximum value.'''
    DECREMENT : StencilAction
    '''Increments the current stencil buffer value, clamps to 0.'''
    DECREMENT_WRAP : StencilAction
    '''Decrements the current stencil buffer value and wrap it to maximum value when it reaches zero.'''
    INVERT : StencilAction
    '''Bit-wise inverts the current stencil buffer value.'''

class TextureType:
    '''The type of the :py:class:`aspose.threed.render.ITextureUnit`'''
    
    TEXTURE_1D : TextureType
    '''1-dimensional texture'''
    TEXTURE_2D : TextureType
    '''2-dimensional texture'''
    TEXTURE_3D : TextureType
    '''3-dimensional texture'''
    CUBE_MAP : TextureType
    '''Cube map texture contains 6 2d textures'''
    ARRAY_2D : TextureType
    '''Multiple set of 2d textures'''

