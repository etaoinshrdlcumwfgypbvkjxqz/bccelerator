# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import itertools as _itertools
import typing as _typing

from .. import util as _util
from ..util import enums as _util_enums
from ..util import props as _util_props
from ..util import types as _util_types
from ..util import utils as _util_utils


class LinkModifierByName(_bpy.types.Operator):
    """Link modifiers from active modifier to modifiers of selected object(s) by name"""

    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar = "object.link_modifier_by_name"
    bl_label: _typing.ClassVar = "Link Modifier By Name"
    bl_options: _typing.ClassVar = {
        _util_enums.OperatorTypeFlag.REGISTER,
        _util_enums.OperatorTypeFlag.UNDO,
    }
    exclude_attrs: _typing.ClassVar = frozenset(
        {
            "__doc__",
            "__module__",
            "__slots__",
            "bl_rna",
            "rna_type",
            "is_active",
            "is_override_data",
            "name",
            "show_expanded",
            "type",
        }
    )

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _bpy.types.Context,
    ) -> bool:
        active_object = context.active_object
        return (
            active_object
            and active_object.modifiers.active
            and len(context.selected_objects) >= 2
        )

    def execute(  # type: ignore
        self,
        context: _bpy.types.Context,
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        modifiers = 0
        drivers = 0

        from_object = context.active_object
        from_modifier = from_object.modifiers.active
        modifier_name: _typing.Any = from_modifier.name
        modifier_type = _util_enums.ObjectModifierType(from_modifier.type)
        modifier_attrs = tuple(
            filter(lambda attr: attr not in self.exclude_attrs, dir(from_modifier))
        )
        for to_object in filter(
            lambda obj: obj != from_object and modifier_name in obj.modifiers,
            context.selected_objects,
        ):
            to_modifier = to_object.modifiers[modifier_name]
            if to_modifier.type == modifier_type:
                to_drivers = 0
                for modifier_attr in modifier_attrs:
                    data_path = f'modifiers["{modifier_name}"].{modifier_attr}'
                    if _util_utils.has_driver(to_object, data_path):
                        continue
                    try:
                        curves = to_object.driver_add(data_path)
                    except TypeError:
                        continue
                    if isinstance(curves, _typing.Collection):
                        multiple = True
                    else:
                        multiple = False
                        curves = (curves,)
                    for index, curve in enumerate(curves):
                        _util_utils.configure_driver(
                            curve.driver,
                            id_type=_util_enums.IDType.OBJECT,
                            id=from_object,
                            data_path=f"{data_path}[{index}]"
                            if multiple
                            else data_path,
                        )
                        curve.lock = True
                    to_drivers += len(curves)
                modifiers += 1
                drivers += to_drivers
                self.report(
                    {_util_enums.WMReport.INFO},
                    f'Linked modifier of "{to_object.name_full}" using {to_drivers} driver(s)',
                )
        self.report(
            {_util_enums.WMReport.INFO},
            f"Linked {modifiers} modifier(s) using {drivers} driver(s)",
        )
        return (
            {_util_enums.OperatorReturn.FINISHED}
            if drivers > 0
            else {_util_enums.OperatorReturn.CANCELLED}
        )


class ChangeLibraryOverrideEditable(_bpy.types.Operator):
    """Change editability of selected library override(s)"""

    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar = "outliner.liboverride_editable_operation"
    bl_label: _typing.ClassVar = "Change Library Override(s) Editability"
    bl_options: _typing.ClassVar = {
        _util_enums.OperatorTypeFlag.REGISTER,
        _util_enums.OperatorTypeFlag.UNDO,
    }

    editable: _typing.Annotated[
        bool,
        _bpy.props.BoolProperty,  # type: ignore
    ]
    selection_set_items: _typing.ClassVar = {
        "SELECTED": _util_props.enum_property_item(
            "SELECTED",
            "Selected",
            "Apply the operation over selected data-block(s) only",
            number=0,
        ),
        "CONTENT": _util_props.enum_property_item(
            "CONTENT",
            "Content",
            "Apply the operation over content of the selected item(s) only (the data-block(s) in their sub-tree(s))",
            number=1,
        ),
        "SELECTED_AND_CONTENT": _util_props.enum_property_item(
            "SELECTED_AND_CONTENT",
            "Selected & Content",
            "Apply the operation over selected data-block(s) and all their dependency(s)",
            number=2,
        ),
    }
    selection_set: _typing.Annotated[
        str,
        _bpy.props.EnumProperty,  # type: ignore
    ]

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _bpy.types.Context,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _util_enums.SpaceType.OUTLINER
            and any(id.override_library for id in context.selected_ids)
        )

    def execute(  # type: ignore
        self,
        context: _bpy.types.Context,
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed = 0

        if self.selection_set == "SELECTED":
            data = context.selected_ids
        elif self.selection_set == "CONTENT":

            def lamb(id: _bpy.types.ID) -> _typing.Iterable[_bpy.types.ID]:
                return (
                    _itertools.chain(_util.flatmap(lamb, id.children), id.objects)
                    if isinstance(id, _bpy.types.Collection)
                    else (id,)
                )

            data = _util.flatmap(lamb, context.selected_ids)
        elif self.selection_set == "SELECTED_AND_CONTENT":

            def lamb(id: _bpy.types.ID) -> _typing.Iterable[_bpy.types.ID]:
                return (
                    _itertools.chain(
                        (id,),
                        _util.flatmap(lamb, id.children),
                        id.objects,
                    )
                    if isinstance(id, _bpy.types.Collection)
                    else (id,)
                )

            data = _util.flatmap(lamb, context.selected_ids)
        else:
            self.report(
                {_util_enums.WMReport.ERROR_INVALID_INPUT},
                f'Invalid selection set "{self.selection_set}"',
            )
            return {_util_enums.OperatorReturn.CANCELLED}

        for datum in data:
            if datum.override_library:
                datum.override_library.is_system_override = not self.editable
                processed += 1
                self.report(
                    {_util_enums.WMReport.INFO},
                    f'Changed editability of library override "{datum.name_full}"',
                )

        self.report(
            {_util_enums.WMReport.INFO},
            f"Changed editability of {processed} data-block(s)",
        )
        return (
            {_util_enums.OperatorReturn.FINISHED}
            if processed > 0
            else {_util_enums.OperatorReturn.CANCELLED}
        )


ChangeLibraryOverrideEditable.__annotations__["editable"] = (
    _bpy.props.BoolProperty  # type: ignore
)(
    name="Editable",
    description="Editability",
    default=False,
    options={_util_enums.PropertyFlagEnum.SKIP_SAVE},
)
ChangeLibraryOverrideEditable.__annotations__["selection_set"] = (
    _bpy.props.EnumProperty  # type: ignore
)(
    name="Selection Set",
    items=ChangeLibraryOverrideEditable.selection_set_items.values(),  # type: ignore
    description="Over which part of the tree item(s) to apply the operation",
    default="SELECTED",
    options={_util_enums.PropertyFlagEnum.SKIP_SAVE},
)


class _LibraryOverrideEditableMenu(_bpy.types.Menu):
    __slots__: _typing.ClassVar = ()
    __editable: _typing.ClassVar[bool]

    def __init_subclass__(cls, editable: bool, **kwargs: _typing.Any):
        super().__init_subclass__(**kwargs)
        cls.__editable = editable
        cls.bl_idname = f'OUTLINER_MT_liboverride_editable_{"editable" if editable else "noneditable"}'  # type: ignore
        cls.bl_label = "Editable" if editable else "Non-Editable"  # type: ignore

    def draw(
        self,
        context: _bpy.types.Context | None,
    ):
        for selection_set in ChangeLibraryOverrideEditable.selection_set_items.values():
            op = self.layout.operator(
                ChangeLibraryOverrideEditable.bl_idname, text=selection_set[1]
            )
            setattr(op, "editable", self.__editable)
            setattr(op, "selection_set", selection_set[0])


@_util_types.draw_func_class
@_util_types.internal_operator(uuid="06211866-d898-46d8-b253-14e4cd41dd77")
class DrawFunc(_bpy.types.Operator):
    __slots__: _typing.ClassVar = ()

    editable_menu: _typing.ClassVar
    noneditable_menu: _typing.ClassVar
    editable_menu, noneditable_menu = (
        type(
            "",
            (_LibraryOverrideEditableMenu,),
            {
                "__annotations__": {
                    "__slots__": _typing.ClassVar,
                },
                "__slots__": (),
            },
            editable=editable,
        )
        for editable in (True, False)
    )

    __register: _typing.ClassVar
    __unregister: _typing.ClassVar
    __register, __unregister = _util_utils.register_classes_factory(
        (editable_menu, noneditable_menu)
    )

    @classmethod
    def register(cls):
        cls.__register()

    @classmethod
    def unregister(cls):
        cls.__unregister()

    @classmethod
    def VIEW3D_MT_make_links_draw_func(
        cls,
        self: _util_types.Drawer,
        context: _bpy.types.Context,
    ):
        self.layout.separator()
        self.layout.operator(LinkModifierByName.bl_idname)

    @classmethod
    def OUTLINER_MT_liboverride_draw_func(
        cls,
        self: _util_types.Drawer,
        context: _bpy.types.Context,
    ):
        self.layout.separator()
        self.layout.menu(cls.editable_menu.bl_idname)
        self.layout.menu(cls.noneditable_menu.bl_idname)


register, unregister = _util_utils.register_classes_factory(
    (
        LinkModifierByName,
        ChangeLibraryOverrideEditable,
        DrawFunc,
    )
)
