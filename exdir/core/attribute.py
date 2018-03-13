from enum import Enum
import ruamel_yaml as yaml
import os
import numpy as np
import exdir

from . import exdir_object as exob


def _quote_strings(value):
    if isinstance(value, str):
        return yaml.scalarstring.DoubleQuotedScalarString(value)
    else:
        try:
            new_result = {}
            for key, val in value.items():
                new_result[key] = _quote_strings(val)
            return new_result
        except AttributeError:
            pass
    return value


class Attribute(object):
    """Attribute class."""

    class Mode(Enum):
        ATTRIBUTES = 1
        METADATA = 2

    def __init__(self, parent, mode, io_mode, path=None, plugin_manager=None):
        self.parent = parent
        self.mode = mode
        self.io_mode = io_mode
        self.path = path or []
        self.plugin_manager = plugin_manager

    def __getitem__(self, name=None):
        attrs = self._open_or_create()

        meta = {}
        attribute_data = exdir.plugin_interface.AttributeData(attrs=attrs,
                                                              meta=meta)

        for plugin in self.plugin_manager.attribute_plugins.read_order:
            attribute_data = plugin.prepare_read(attribute_data)
            attrs = attribute_data.attrs
            meta.update(attribute_data.meta)

        for i in self.path:
            attrs = attrs[i]
        if name is not None:
            attrs = attrs[name]
        if isinstance(attrs, dict):
            return Attribute(
                self.parent, self.mode, self.io_mode, self.path + [name],
                plugin_manager=self.plugin_manager
            )
        else:
            return attrs

    def __setitem__(self, name, value):
        attrs = self._open_or_create()
        key = name
        sub_attrs = attrs

        for i in self.path:
            sub_attrs = sub_attrs[i]
        sub_attrs[key] = value

        self._set_data(attrs)

    def __contains__(self, name):
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return name in attrs

    def keys(self):
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.keys()

    def to_dict(self):
        attrs = self._open_or_create()
        for i in self.path:  # TODO check if this is necesary
            attrs = attrs[i]

        for plugin in self.plugin_manager.attribute_plugins.read_order:
            attrs = plugin.prepare_read(attrs)

        return attrs

    def items(self):
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.items()

    def values(self):
        attrs = self._open_or_create()
        for i in self.path:
            attrs = attrs[i]
        return attrs.values()

    def _set_data(self, attrs):
        if self.io_mode == exob.Object.OpenMode.READ_ONLY:
            raise IOError("Cannot write in read only ("r") mode")

        meta = {}
        attribute_data = exdir.plugin_interface.AttributeData(attrs=attrs,
                                                              meta=meta)

        for plugin in self.plugin_manager.attribute_plugins.write_order:
            attribute_data = plugin.prepare_write(attribute_data)

            if "required" in attribute_data.meta and attribute_data.meta["required"] is True:
                meta[plugin._plugin_module.name] = attribute_data.meta

        # QUESTION: Should we add plugin meta data to parent.meta here?

        meta_data_quoted = _quote_strings(attribute_data.attrs)

        with self.filename.open("w", encoding="utf-8") as meta_file:
            yaml.dump(
                meta_data_quoted,
                meta_file,
                default_flow_style=False,
                allow_unicode=True,
                Dumper=yaml.RoundTripDumper
            )

    # TODO only needs filename, make into free function
    def _open_or_create(self):
        attrs = {}
        if self.filename.exists():  # NOTE str for Python 3.5 support
            with self.filename.open("r", encoding="utf-8") as meta_file:
                attrs = yaml.safe_load(meta_file)
        return attrs

    def __iter__(self):
        for key in self.keys():
            yield key

    @property
    def filename(self):
        if self.mode == self.Mode.METADATA:
            return self.parent.meta_filename
        else:
            return self.parent.attributes_filename

    def __len__(self):
        return len(self.keys())

    def update(self, value):
        for key in value:
            self[key] = value[key]

    def __str__(self):
        string = ""
        for key in self:
            string += "{}: {},".format(key, self[key])
        return "Attribute({}, {{{}}})".format(self.parent.name, string)
