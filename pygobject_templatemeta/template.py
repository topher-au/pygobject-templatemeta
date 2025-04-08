from __future__ import annotations

import dataclasses
import logging
from abc import ABCMeta
# from dataclasses import MISSING
from typing import Any, Callable, Type, TypeVar

from gi.repository import GLib, GObject, Gtk
from lxml import etree as ET
from lxml.etree import _Element as XMLElement

logger = logging.getLogger(__name__)
_T = TypeVar('_T')


class _MISSING_TYPE:
    ...


MISSING = _MISSING_TYPE()


def dataclass(*args, **kwargs) -> Callable[[Type[_T]], Type[_T]]:
    """ Overrides the default dataclass decorator to set init=False by default. """
    if 'init' not in kwargs:
        kwargs['init'] = False
    return dataclasses.dataclass(*args, **kwargs)


def field(*, default: _T = MISSING,
          default_factory: Callable[[], _T] = MISSING,
          name: str = None,
          required: bool = False):
    """ Overrides the default field function to add `name` and `required` attributes. """
    kwargs = {'metadata': {'name': name,
                           'required': required}}
    if default is not MISSING:
        kwargs['default'] = default
    if default_factory is not MISSING:
        kwargs['default_factory'] = default_factory
    field = dataclasses.field(**kwargs)
    return field


def get_attr_required(field_: dataclasses.field) -> bool:
    """ Returns whether the `required` flag is set for the given field. """
    return field_.metadata and field_.metadata.get('required', False)


def get_attr_name(field_: dataclasses.field) -> str:
    """ Return the `name` metadata for the given field. """
    if field_.metadata and (name := field_.metadata.get('name')):
        return name
    return field_.name


class ElementMeta(ABCMeta):
    element: object

    def __getattr__(cls, item: str):
        if fields := super().__getattribute__('__dataclass_fields__'):
            if item in fields:
                return lambda x: getattr(x, item)
        return super().__getattribute__(item)


# class FuckIt:
#     element: object

@dataclass
class BaseElement(metaclass=ElementMeta):
    def __init__(self, attributes: dict[str, object], element: XMLElement):
        self.__element = element
        for name, value in attributes.items():
            if name not in self.__dataclass_fields__:
                logger.warning(f'Element {element.tag} has unknown attribute {name}')
                continue
            attr_field = self.__dataclass_fields__[name]
            if get_attr_required(attr_field) and value is MISSING:
                raise AttributeError(name=get_attr_name(attr_field),
                                     obj=element)

            elif value is MISSING:
                if attr_field.default is MISSING:
                    if not callable(attr_field.default_factory):
                        continue
                    value = attr_field.default_factory()
                else:
                    value = attr_field.default

            setattr(self, name, value)

    @property
    def element(self) -> XMLElement:
        return self.__element

    @classmethod
    def get_attributes(cls, element: XMLElement) -> dict[str, Any]:
        """ Returns a dictionary of attributes for the given element.

        :param element: The element to get attributes from.
        :return: A dictionary of attributes for the given element.
        """
        attributes = {}
        for field_ in cls.__dataclass_fields__.values():
            name = get_attr_name(field_)
            value = element.get(name, MISSING)

            if value is MISSING:
                if get_attr_required(field_):
                    raise AttributeError(name, element)
                value = field_.default

            attributes[field_.name] = value
        return attributes

    @classmethod
    def from_element(cls, element: XMLElement) -> BaseElement:
        """ Returns an instance of the class from the given element.

        :param element: The element to create an instance from.
        :return: An instance of the class created from the given element.
        """
        return cls(cls.get_attributes(element), element=element)

    @classmethod
    def find_elements(cls, tree: XMLElement) -> list[XMLElement]:
        """ Returns a list of elements matching the class's template tags.

        :param tree: The XML tree to search for elements.
        :return: A list of elements matching the class's template tags.
        """
        if tags := getattr(cls, '__template_tags__', None):
            return [element for tag in tags
                    for element in tree.findall(f'.//{tag}')]
        return []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        # If the `tag` keyword is not provided, return
        if not (tag := kwargs.get('tag')):
            return

        # Create the `__template_tags__` attribute for the class if it doesn't exist
        if not hasattr(cls, '__template_tags__'):
            cls.__template_tags__ = []

        # If `tag` is a string, convert it to a list
        if isinstance(tag, str):
            tag = [tag]

        # Extend the `__template_tags__` list with the new tags
        cls.__template_tags__.extend(tag)

    def __getattr__(self, item: str):
        return getattr(type(self), item)

    @classmethod
    def parse_elements(cls, tree: XMLElement, key_attr: str) -> dict[str, _T]:
        """ Returns a dictionary of elements parsed from the given tree.

        :param tree: The XML tree to parse elements from.
        :param key_attr: The attribute to use as the key for the dictionary.
        :return: A dictionary of elements parsed from the given tree.
        """
        elements = {}
        for element in cls.find_elements(tree):
            element_obj = cls.from_element(element)
            element_key = getattr(element_obj, key_attr)
            if element_key is None:
                continue
            elements[element_key] = element_obj

        return elements


@dataclass(init=False)
class SignalElement(BaseElement, tag='signal'):
    """ Represents a <signal> element in the template XML. """
    name: str = field(required=True)
    handler: str = field(required=True)
    object: str | None = field(default=None)
    swapped: bool = field(default=False)
    after: bool = field(default=False)


@dataclass(init=False)
class ClosureElement(BaseElement, tag='closure'):
    """ Represents a <closure> element in the template XML. """
    function: str = field(required=True)
    type_: GObject.GType = field(name='type', required=True)


@dataclass(init=False)
class ObjectElement(BaseElement, tag='object'):
    """ Represents an <object> element in the template XML. """
    type_name: str = field(name='class', required=True)
    id_: str = field(default=None, name='id')
    name: str | None = field(default=None)
    internal: bool = field(default=False)

    @property
    def gtype(self) -> GObject.GType:
        return GObject.type_from_name(self.type_name)

    @property
    def type_(self) -> Type:
        return self.gtype.pytype


@dataclass(init=False)
class MenuElement(BaseElement, tag=['menu', 'submenu', 'section']):
    """ Represents a <menu> element in the template XML. """
    id_: str | None = field(default=None, name='id')
    domain: str | None = field(default=None)

    @property
    def name(self) -> str | None:
        return self.id_


@dataclass(init=True)
class Template:
    template: str = dataclasses.field(repr=False, hash=False, compare=False, kw_only=True)
    class_name: str = field(required=True)
    parent_type: Type[Gtk.Widget] = field(required=True)
    signals: dict[str, SignalElement] = field(default=None)
    closures: dict[str, ClosureElement] = field(default=None)
    children: dict[str, ObjectElement] = field(default=None)
    menus: dict[str, MenuElement] = field(default=None)

    @classmethod
    def from_string(cls, template_string: str) -> Template:
        """ Parse a Template from a string containing the GtkBuilder XML.

        :param template_string: The GtkBuilder XML for the template as a string.
        :return: The Template object parsed from the given XML.
        """
        tree: XMLElement = ET.fromstring(template_string)
        return cls.from_element_tree(tree)

    @classmethod
    def from_bytes(cls, template_bytes: GLib.Bytes) -> Template:
        """ Parse a Template from a string containing the GtkBuilder XML.

        :param template_bytes: The GtkBuilder XML for the template as a :class:`GLib.Bytes`.
        :return: The Template object parsed from the given XML.
        """
        template_data = template_bytes.get_data()
        tree: XMLElement = ET.fromstring(template_data)
        return cls.from_element_tree(tree)

    @classmethod
    def from_element_tree(cls, tree: XMLElement) -> Template:
        """ Parse a Template from a GtkBuilder XML tree.

        :param tree: The GtkBuilder XML tree to parse.
        :return: The Template object parsed from the given XML.
        """
        if (element := tree.find('.//template')) is None:
            # No <template> element was found
            raise KeyError('template')

        if (class_name := element.get('class')) is None:
            # The <template> element has no "class" attribute
            raise AttributeError('class')

        if (parent := element.get('parent')) is None:
            # The <template> element has no "parent" attribute
            raise AttributeError('parent')

        if (parent_type := GObject.type_from_name(parent)) is None:
            # Unable to resolve a GType from the parent type name
            raise RuntimeError(f'unresolved gtype for parent: {parent}')

        if not hasattr(parent_type, 'pytype') or parent_type.pytype is None:
            # Resolved GType has no associated Python type
            raise RuntimeError(f'unknown python type for parent gtype: {parent_type}')

        template = Template(class_name, parent_type.pytype,
                            SignalElement.parse_elements(tree, 'handler'),
                            ClosureElement.parse_elements(tree, 'function'),
                            ObjectElement.parse_elements(tree, 'id_'),
                            MenuElement.parse_elements(tree, 'id_'),
                            template=ET.tostring(tree))
        return template
