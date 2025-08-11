from message_definition import AggregatedKind, MessageDefinition, MessageDefinitionField
from rosmsg2_serialization import MessageReader, MessageReaderOptions

from cdr import CdrWriter


def make_defs():
    enum_def = MessageDefinition(
        name="test/t2_test_msgs/FooEnum",
        aggregatedKind=AggregatedKind.MODULE,
        definitions=[
            MessageDefinitionField(
                type="uint32", name="ENUMERATOR1", isConstant=True, value=0
            ),
            MessageDefinitionField(
                type="uint32", name="ENUMERATOR2", isConstant=True, value=1
            ),
        ],
    )

    union_def = MessageDefinition(
        name="test/t2_test_msgs/FooUnion",
        aggregatedKind=AggregatedKind.UNION,
        switchType="test/t2_test_msgs/FooEnum",
        definitions=[
            MessageDefinitionField(type="int32", name="int_value", casePredicates=[0]),
            MessageDefinitionField(
                type="string", name="string_value", upperBound=32, casePredicates=[1]
            ),
        ],
    )

    root_def = MessageDefinition(
        name="test/t2_test_msgs/msg/Bar",
        definitions=[
            MessageDefinitionField(
                type="test/t2_test_msgs/FooUnion", name="union_value", isComplex=True
            )
        ],
    )

    # Ensure root struct comes before union definition for reader initialization
    return [enum_def, root_def, union_def]


def make_buffer():
    writer = CdrWriter()
    writer.uint32(1)  # discriminator ENUMERATOR2
    writer.string("contains a string")
    return writer.data


def test_union_discriminator_as_int():
    reader = MessageReader(make_defs())
    msg = reader.read_message(make_buffer())
    assert msg == {
        "union_value": {
            "discriminator": 1,
            "string_value": "contains a string",
        }
    }


def test_union_discriminator_as_string():
    options = MessageReaderOptions(enumsAsStrings=True)
    reader = MessageReader(make_defs(), options)
    msg = reader.read_message(make_buffer())
    assert msg == {
        "union_value": {
            "discriminator": "ENUMERATOR2",
            "string_value": "contains a string",
        }
    }
