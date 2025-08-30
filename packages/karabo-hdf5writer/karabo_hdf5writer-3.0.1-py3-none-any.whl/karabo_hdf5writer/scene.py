from karabo.common.scenemodel.api import (
    DisplayCommandModel, DisplayLabelModel, DisplayStateColorModel,
    DisplayTextLogModel, ErrorBoolModel, FixedLayoutModel, LabelModel,
    LineModel, SceneModel, TableElementModel, write_scene)


def get_scene(device_id):
    scene0 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=21,
        keys=[f"{device_id}.deviceId"],
        parent_component="DisplayComponent",
        width=331,
        x=10,
        y=30,
    )
    scene1 = DisplayStateColorModel(
        font_size=10,
        font_weight="normal",
        height=21,
        keys=[f"{device_id}.state"],
        parent_component="DisplayComponent",
        show_string=True,
        width=121,
        x=350,
        y=30,
    )
    scene2 = TableElementModel(
        height=171,
        keys=[f"{device_id}.dataSources"],
        klass="EditableTableElement",
        parent_component="EditableApplyLaterComponent",
        width=461,
        x=10,
        y=60,
    )
    scene3 = DisplayTextLogModel(
        height=221,
        keys=[f"{device_id}.status"],
        parent_component="DisplayComponent",
        width=281,
        x=200,
        y=280,
    )
    scene40 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=23,
        parent_component="DisplayComponent",
        text="Current Run #",
        width=96,
        x=10,
        y=380,
    )
    scene41 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=23,
        keys=[f"{device_id}.currentRunNumber"],
        parent_component="DisplayComponent",
        width=51,
        x=150,
        y=380,
    )
    scene42 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=25,
        parent_component="DisplayComponent",
        text="No warnings present",
        width=131,
        x=10,
        y=440,
    )
    scene43 = ErrorBoolModel(
        height=25,
        invert=True,
        keys=[f"{device_id}.warningsExist"],
        parent_component="DisplayComponent",
        width=31,
        x=170,
        y=440,
    )
    scene44 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=25,
        parent_component="DisplayComponent",
        text="Data not being truncated",
        width=151,
        x=10,
        y=470,
    )
    scene45 = ErrorBoolModel(
        height=25,
        invert=True,
        keys=[f"{device_id}.dataIsTruncated"],
        parent_component="DisplayComponent",
        width=31,
        x=170,
        y=470,
    )
    scene46 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=21,
        parent_component="DisplayComponent",
        text="# Devices",
        width=96,
        x=10,
        y=290,
    )
    scene47 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=21,
        keys=[f"{device_id}.numDevices"],
        parent_component="DisplayComponent",
        width=51,
        x=150,
        y=290,
    )
    scene48 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=23,
        parent_component="DisplayComponent",
        text="Current Sequence File #",
        width=138,
        x=10,
        y=410,
    )
    scene49 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=23,
        keys=[f"{device_id}.currentSequenceFileNumber"],
        parent_component="DisplayComponent",
        width=51,
        x=150,
        y=410,
    )
    scene410 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=21,
        parent_component="DisplayComponent",
        text="# Slow Properties",
        width=105,
        x=10,
        y=320,
    )
    scene411 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=21,
        keys=[f"{device_id}.numSlowProperties"],
        parent_component="DisplayComponent",
        width=51,
        x=150,
        y=320,
    )
    scene412 = LabelModel(
        font="Source Sans Pro,10,-1,5,50,0,0,0,0,0",
        foreground="#000000",
        height=21,
        parent_component="DisplayComponent",
        text="# Output Channels",
        width=111,
        x=10,
        y=350,
    )
    scene413 = DisplayLabelModel(
        font_size=10,
        font_weight="normal",
        height=21,
        keys=[f"{device_id}.numOutputChannels"],
        parent_component="DisplayComponent",
        width=51,
        x=150,
        y=350,
    )
    scene4 = FixedLayoutModel(
        height=205,
        width=191,
        x=10,
        y=290,
        children=[
            scene40,
            scene41,
            scene42,
            scene43,
            scene44,
            scene45,
            scene46,
            scene47,
            scene48,
            scene49,
            scene410,
            scene411,
            scene412,
            scene413,
        ],
    )
    scene5 = DisplayCommandModel(
        font_size=10,
        height=31,
        keys=[f"{device_id}.configure"],
        parent_component="DisplayComponent",
        width=76,
        x=10,
        y=240,
    )
    scene6 = DisplayCommandModel(
        font_size=10,
        height=31,
        keys=[f"{device_id}.monitor"],
        parent_component="DisplayComponent",
        width=121,
        x=100,
        y=240,
    )
    scene7 = DisplayCommandModel(
        font_size=10,
        height=31,
        keys=[f"{device_id}.record"],
        parent_component="DisplayComponent",
        width=131,
        x=230,
        y=240,
    )
    scene8 = DisplayCommandModel(
        font_size=10,
        height=31,
        keys=[f"{device_id}.ignore"],
        parent_component="DisplayComponent",
        width=91,
        x=380,
        y=240,
    )

    scene9 = LineModel(
        stroke="#000000", x=10, x1=10, x2=470, y=280, y1=280, y2=280)
    scene10 = DisplayCommandModel(
        font_size=10,
        height=34,
        keys=[f"{device_id}.reset"],
        parent_component="DisplayComponent",
        width=81,
        x=320,
        y=460,
    )
    scene = SceneModel(
        height=524,
        width=474,
        children=[
            scene0,
            scene1,
            scene2,
            scene3,
            scene4,
            scene5,
            scene6,
            scene7,
            scene8,
            scene9,
            scene10,
        ],
    )
    return write_scene(scene)
