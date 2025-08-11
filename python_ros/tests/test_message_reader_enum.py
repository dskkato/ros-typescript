from message_definition import MessageDefinition, MessageDefinitionField
from rosmsg2_serialization import MessageReader, MessageReaderOptions

from cdr import CdrWriter


def make_defs():
    enum_def = MessageDefinition(
        name="Color",
        definitions=[
            MessageDefinitionField(type="uint8", name="RED", isConstant=True, value=0),
            MessageDefinitionField(
                type="uint8", name="GREEN", isConstant=True, value=1
            ),
            MessageDefinitionField(type="uint8", name="BLUE", isConstant=True, value=2),
        ],
    )
    root_def = MessageDefinition(
        name="MyMsg",
        definitions=[
            MessageDefinitionField(type="Color", name="color"),
            MessageDefinitionField(type="Color", name="palette", isArray=True),
        ],
    )
    return [enum_def, root_def]


def make_buffer():
    writer = CdrWriter()
    writer.uint8(1)  # color = GREEN
    writer.sequenceLength(2)
    writer.uint8(0)  # palette[0] = RED
    writer.uint8(2)  # palette[1] = BLUE
    return writer.data


def test_enum_values_as_ints():
    reader = MessageReader(make_defs())
    msg = reader.read_message(make_buffer())
    assert msg == {"color": 1, "palette": [0, 2]}


def test_enum_values_as_strings():
    options = MessageReaderOptions(enumsAsStrings=True)
    reader = MessageReader(make_defs(), options)
    msg = reader.read_message(make_buffer())
    assert msg == {"color": "GREEN", "palette": ["RED", "BLUE"]}
