from __future__ import annotations

import caseconverter
import logging
import os
import sys
from functools import partial
from gi.repository import GLib, GObject, Gio, Gtk
from typing import Mapping, Sequence

from .element import BaseElement, ClosureElement, MenuElement, ObjectElement, SignalElement
from .template import Template
from .utils import validate_resource_path

logger = logging.getLogger(__name__)

try:
    from gi.types import GObjectMeta
except ImportError:
    # Fallback for older versions of PyGObject that do not have GObjectMeta
    logger.warning("GObjectMeta not found, using GObject.GObject as fallback.")
    GObjectMeta = type(GObject.GObject)


class TemplateMeta(GObjectMeta, type):
    """ A metaclass for constructing Gtk Widgets from an XML template definition.

    When defining a new class that inherits from TemplateMeta, you can specify the template using
    one of the following keyword arguments:

    `template_path`: The path to the XML template file.
    `template_resource`: The resource name of the XML template file.
    `template_string`: A string containing the XML template definition.
    """
    __template__: Template

    __template_resource__: str | None = None
    __template_string__: str | None = None
    __template_path__: str | None = None
    __template_methods__: dict[str, SignalElement | ClosureElement] = None
    __template_handlers__: dict[str, SignalElement | ClosureElement] = None
    __template_widgets__: dict[str, ObjectElement] = None

    def __new__(mcs, name: str, bases: tuple[type], dict_: dict[str, object], **kwargs):
        if '__gtype_name__' not in dict_:
            dict_['__gtype_name__'] = name

        cls = super(GObjectMeta, mcs).__new__(mcs, name, bases, dict_)
        mcs.load_template(cls, **kwargs)
        return cls

    def __init__(cls, name, bases, dict_, **kwargs):
        super().__init__(name, bases, dict_)
        cls.set_template(GLib.Bytes.new(cls.__template__.template))
        register_template(cls)

        ...

    @staticmethod
    def load_template(cls, **kwargs):
        if hasattr(cls, '__template__'):
            return cls

        template_bytes = None

        if template_string := kwargs.pop('template_string', getattr(cls, '__template_string__', None)):
            # Load the template from a string.
            if isinstance(template_string, str):
                template_string = template_string.encode('utf-8')
            template_bytes = GLib.Bytes.new(template_string)

        elif template_resource := kwargs.pop('template_resource', getattr(cls, '__template_resource__', None)):
            # Load the template from the resource with the given path.
            validate_resource_path(template_resource)
            template_bytes = Gio.resources_lookup_data(template_resource, Gio.ResourceLookupFlags.NONE)

        elif template_path := kwargs.pop('template_path', getattr(cls, '__template_path__', None)):
            # Load the template from the file with the given path.
            template_file = Gio.File.new_for_path(template_path)
            template_bytes = GLib.Bytes.new(template_file.load_contents()[1])

        if template_bytes is None:
            # No template data has been loaded yet, so we will try to find it automatically.
            try:
                # Get the path to the module file where the class is defined.
                module = sys.modules.get(cls.__module__)
                module_path, module_file = os.path.split(module.__file__)
                module_name, _ = os.path.splitext(module_file)

                converters = (str.lower, caseconverter.snakecase, caseconverter.pascalcase)
                names = {func(n) for n in (module_name, cls.__name__) for func in converters}

                # Look for possible template files based on the module name.
                extensions = ('ui', 'xml', 'glade')
                filenames = [os.path.join(module_path, os.path.extsep.join((name, ext)))
                             for ext in extensions for name in names]

                for filename in filter(os.path.isfile, filenames):
                    template_file = Gio.File.new_for_path(filename)
                    template_bytes = GLib.Bytes.new(template_file.load_contents()[1])
                    break

                if template_bytes is None:
                    raise ValueError(f'No template found for {cls.__name__} in {module_path}. ')

            except Exception as e:
                raise e

        template = Template.from_bytes(template_bytes)
        setattr(cls, '__template__', template)
        return cls

    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def register_template(cls: Gtk.Widget):
    from gi.repository import Gtk

    bound_methods = {}
    bound_widgets = {}

    def bind_child(element: BaseElement):
        """ Bind a child to the template. """
        element_key = element.name = element.name or element.id_
        if element_key is None:
            logger.debug(f'Could not bind {element.element.tag} on {element.element.sourceline}, no id')

        if element_key in bound_widgets:
            raise KeyError(f"Duplicate widget ID '{element.name}' in template")

        bound_widgets[element_key] = element
        cls.bind_template_child_full(element.id_, element.internal, 0)

    def bind_callback(element: SignalElement | ClosureElement):
        """ Bind a callback to the template. """
        method = getattr(element, 'handler' if isinstance(element, SignalElement) else 'function')

        if method in bound_methods:
            logger.warning(f'{method} already bound to {bound_methods[method]}')
            return

        if not hasattr(cls, method):
            logger.warning(f'{method} not found in {cls}')
            return

        bound_methods[method] = element

    def bind_menu(element: MenuElement):
        """ Bind a menu element to the template. """
        if element.id_ is None:
            logger.debug(f'Could not bind {element.element.tag} on {element.element.sourceline}, no id')
            return

        if element.name in bound_widgets:
            logger.warning(f'{element.name} already bound to {bound_widgets[element.name]}')
            return

        bound_widgets[element.name] = element
        cls.bind_template_child_full(element.id_, False, 0)

    template = cls.__template__

    for bind_func, element_list in {
        bind_menu: template.menus.values(),
        bind_child: template.children.values(),
        bind_callback: [*template.signals.values(),
                        *template.closures.values()]
    }.items():
        for e in element_list:
            bind_func(e)

    cls.__template_methods__ = bound_methods
    cls.__template_widgets__ = bound_widgets

    if Gtk._version == '4.0':
        builder_scope = define_builder_scope()
        cls.set_template_scope(builder_scope())
    else:
        raise NotImplementedError(f'Gtk {Gtk._version} is unsupported. Please use Gtk 4.0 or later.')

    base_init_template = cls.init_template
    cls.__dontuse_ginstance_init__ = lambda s: init_template(s, cls, base_init_template)
    cls.init_template = cls.__dontuse_ginstance_init__


def init_template(self, cls, base_init_template):
    self.init_template = lambda: None

    # if self.__class__ is not cls:
    #     raise TypeError(f"Invalid class '{self.__class__.__name__}' for template")

    self.__template_handlers__ = set()

    # logger.warning(f'{cls} init_template')
    base_init_template(self)

    for name, element in self.__template_widgets__.items():
        child = self.get_template_child(cls, element.id_)
        if child is not None:
            # logger.debug(f'Binding {name} to {child}')
            setattr(self, name, child)

    for method, attr in self.__template_methods__.items():
        if method not in self.__template_handlers__:
            logger.warning(f'Missing template handler for method {method}')
            continue

    ...
    # try:
    #     base_init_template(self)
    # except Exception as err:
    #     logger.exception(str(err), exc_info=sys.exc_info(), stack_info=True, stacklevel=2)
    #     raise err


def extract_handler_and_args(obj_or_map, handler: SignalElement | ClosureElement):
    handler_name = handler.handler if isinstance(handler, SignalElement) else handler.function
    if isinstance(obj_or_map, Mapping):
        handler = obj_or_map.get(handler, None)
    else:
        handler = getattr(obj_or_map, handler_name)

    args = ()
    if isinstance(handler, Sequence):
        if len(handler) == 0:
            raise TypeError(f'Handler {handler} is empty')
        args = handler[1:]
        handler = handler[0]

    elif not callable(handler):
        raise TypeError(f'Handler {handler} is not callable')

    return handler, args


def define_builder_scope():
    from gi.repository import Gtk

    class BuilderScope(GObject.Object, Gtk.BuilderScope):
        def __init__(self, scope_object=None):
            super().__init__()
            self._scope_object = scope_object

        def do_create_closure(self, builder: Gtk.Builder,
                              func_name: str,
                              flags: Gtk.BuilderClosureFlags,
                              obj):
            current_object: TemplateMeta | GObject.Object = (builder.get_current_object()
                                                             or self._scope_object)
            if not self._scope_object:
                current_object = builder.get_current_object()

                # assert (hasattr(current_obj, '__template_methods__')
                #         and isinstance(current_obj.__template_methods__, dict))
                # assert (hasattr(current_obj, '__template_handlers__')
                #         and isinstance(current_obj.__template_handlers__, set))

                if func_name not in current_object.__template_methods__:
                    return

                current_object.__template_handlers__.add(func_name)
                handler_name = current_object.__template_methods__[func_name]

            else:
                current_object = self._scope_object
                handler_name = func_name
                raise NotImplementedError()

            if int(flags & Gtk.BuilderClosureFlags.SWAPPED):
                raise NotImplementedError('swapped closures are not implemented yet')

            handler, args = extract_handler_and_args(current_object, handler_name)

            p = partial(handler, *args)
            if obj is not None:
                p.keywords['swap_data'] = obj
            p.__gtk_template__ = True
            return p

    return BuilderScope
