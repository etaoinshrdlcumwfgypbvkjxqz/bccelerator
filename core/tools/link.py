# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.props import (
    BoolProperty as _BoolProp,  # type: ignore
    EnumProperty as _EnumProp,  # type: ignore
)
from bpy.types import (
    Collection as _BCollect,
    Context as _Ctx,
    ID as _ID,
    Menu as _Menu,
    Operator as _Op,
)
from itertools import chain as _chain
from typing import (
    AbstractSet as _Set,
    Annotated as _Annotated,
    Any as _Any,
    Collection as _Collect,
    ClassVar as _ClassVar,
    Iterable as _Iter,
)

from ..util import flatmap as _flatmap
from ..util.enums import (
    IDType as _IDType,
    ObjectModifierType as _ObjModifierType,
    OperatorReturn as _OpReturn,
    OperatorTypeFlag as _OpTypeFlag,
    PropertyFlagEnum as _PropFlag,
    SpaceType as _SpaceType,
    WMReport as _WMReport,
)
from ..util.props import enum_property_item as _enum_prop_item
from ..util.types import (
    Drawer as _Drawer,
    draw_func_class as _draw_func_class,
    internal_operator as _int_op,
)
from ..util.utils import (
    configure_driver as _cfg_drv,
    has_driver as _has_drv,
    register_classes_factory as _reg_cls_fac,
)


class LinkModifierByName(_Op):
    """Link modifiers from active modifier to modifiers of selected object(s) by name"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "object.link_modifier_by_name"
    bl_label: _ClassVar = "Link Modifier By Name"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }
    exclude_attrs: _ClassVar = frozenset(
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
        context: _Ctx,
    ) -> bool:
        active_object = context.active_object
        return (
            active_object
            and active_object.modifiers.active
            and len(context.selected_objects) >= 2
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        modifiers = 0
        drivers = 0

        from_object = context.active_object
        from_modifier = from_object.modifiers.active
        modifier_name: _Any = from_modifier.name
        modifier_type = _ObjModifierType(from_modifier.type)
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
                    if _has_drv(to_object, data_path):
                        continue
                    try:
                        curves = to_object.driver_add(data_path)
                    except TypeError:
                        continue
                    if isinstance(curves, _Collect):
                        multiple = True
                    else:
                        multiple = False
                        curves = (curves,)
                    for index, curve in enumerate(curves):
                        _cfg_drv(
                            curve.driver,
                            id_type=_IDType.OBJECT,
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
                    {_WMReport.INFO},
                    f'Linked modifier of "{to_object.name_full}" using {to_drivers} driver(s)',
                )
        self.report(
            {_WMReport.INFO},
            f"Linked {modifiers} modifier(s) using {drivers} driver(s)",
        )
        return {_OpReturn.FINISHED} if drivers > 0 else {_OpReturn.CANCELLED}


class ChangeLibraryOverrideEditable(_Op):
    """Change editability of selected library override(s)"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "outliner.liboverride_editable_operation"
    bl_label: _ClassVar = "Change Library Override(s) Editability"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    editable: _Annotated[bool, _BoolProp]
    selection_set_items: _ClassVar = {
        "SELECTED": _enum_prop_item(
            "SELECTED",
            "Selected",
            "Apply the operation over selected data-block(s) only",
            number=0,
        ),
        "CONTENT": _enum_prop_item(
            "CONTENT",
            "Content",
            "Apply the operation over content of the selected item(s) only (the data-block(s) in their sub-tree(s))",
            number=1,
        ),
        "SELECTED_AND_CONTENT": _enum_prop_item(
            "SELECTED_AND_CONTENT",
            "Selected & Content",
            "Apply the operation over selected data-block(s) and all their dependency(s)",
            number=2,
        ),
    }
    selection_set: _Annotated[str, _EnumProp]

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _SpaceType.OUTLINER
            and any(id.override_library for id in context.selected_ids)
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0

        if self.selection_set == "SELECTED":
            data = context.selected_ids
        elif self.selection_set == "CONTENT":

            def lamb(id: _ID) -> _Iter[_ID]:
                return (
                    _chain(_flatmap(lamb, id.children), id.objects)
                    if isinstance(id, _BCollect)
                    else (id,)
                )

            data = _flatmap(lamb, context.selected_ids)
        elif self.selection_set == "SELECTED_AND_CONTENT":

            def lamb(id: _ID) -> _Iter[_ID]:
                return (
                    _chain(
                        (id,),
                        _flatmap(lamb, id.children),
                        id.objects,
                    )
                    if isinstance(id, _BCollect)
                    else (id,)
                )

            data = _flatmap(lamb, context.selected_ids)
        else:
            self.report(
                {_WMReport.ERROR_INVALID_INPUT},
                f'Invalid selection set "{self.selection_set}"',
            )
            return {_OpReturn.CANCELLED}

        for datum in data:
            if datum.override_library:
                datum.override_library.is_system_override = not self.editable
                processed += 1
                self.report(
                    {_WMReport.INFO},
                    f'Changed editability of library override "{datum.name_full}"',
                )

        self.report(
            {_WMReport.INFO},
            f"Changed editability of {processed} data-block(s)",
        )
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


ChangeLibraryOverrideEditable.__annotations__["editable"] = (_BoolProp)(
    name="Editable",
    description="Editability",
    default=False,
    options={_PropFlag.SKIP_SAVE},
)
ChangeLibraryOverrideEditable.__annotations__["selection_set"] = (_EnumProp)(
    name="Selection Set",
    items=ChangeLibraryOverrideEditable.selection_set_items.values(),  # type: ignore
    description="Over which part of the tree item(s) to apply the operation",
    default="SELECTED",
    options={_PropFlag.SKIP_SAVE},
)


class _LibOverrideEditableMenu(_Menu):
    __slots__: _ClassVar = ()
    __editable: _ClassVar[bool]

    def __init_subclass__(cls, editable: bool, **kwargs: _Any):
        super().__init_subclass__(**kwargs)
        cls.__editable = editable
        cls.bl_idname = f'OUTLINER_MT_liboverride_editable_{"editable" if editable else "noneditable"}'
        cls.bl_label = "Editable" if editable else "Non-Editable"

    def draw(
        self,
        context: _Ctx | None,
    ):
        for selection_set in ChangeLibraryOverrideEditable.selection_set_items.values():
            op = self.layout.operator(
                ChangeLibraryOverrideEditable.bl_idname, text=selection_set[1]
            )
            setattr(op, "editable", self.__editable)
            setattr(op, "selection_set", selection_set[0])


@_draw_func_class
@_int_op(uuid="06211866-d898-46d8-b253-14e4cd41dd77")
class DrawFunc(_Op):
    __slots__: _ClassVar = ()

    editable_menu: _ClassVar
    noneditable_menu: _ClassVar
    editable_menu, noneditable_menu = (
        type(
            "",
            (_LibOverrideEditableMenu,),
            {
                "__annotations__": {
                    "__slots__": _ClassVar,
                },
                "__slots__": (),
            },
            editable=editable,
        )
        for editable in (True, False)
    )

    __register: _ClassVar
    __unregister: _ClassVar
    __register, __unregister = _reg_cls_fac((editable_menu, noneditable_menu))

    @classmethod
    def register(cls):
        cls.__register()

    @classmethod
    def unregister(cls):
        cls.__unregister()

    @classmethod
    def VIEW3D_MT_make_links_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(LinkModifierByName.bl_idname)

    @classmethod
    def OUTLINER_MT_liboverride_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.menu(cls.editable_menu.bl_idname)
        self.layout.menu(cls.noneditable_menu.bl_idname)


register, unregister = _reg_cls_fac(
    (
        LinkModifierByName,
        ChangeLibraryOverrideEditable,
        DrawFunc,
    )
)
