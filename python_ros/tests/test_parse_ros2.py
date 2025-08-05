from python_ros.message_definition import MessageDefinition, MessageDefinitionField
from python_ros.rosmsg.parse import parse


def test_parses_single_field():
    assert parse("string name", ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[MessageDefinitionField(type="string", name="name")],
        )
    ]


def test_resolves_unqualified_names():
    message_definition = (
        "Point[] points\n" "===============\n" "MSG: geometry_msgs/Point\n" "float64 x"
    )
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(
                    type="geometry_msgs/Point",
                    name="points",
                    is_array=True,
                    is_complex=True,
                )
            ],
        ),
        MessageDefinition(
            name="geometry_msgs/Point",
            definitions=[MessageDefinitionField(type="float64", name="x")],
        ),
    ]


def test_normalizes_aliases():
    assert parse("char x\nbyte y", ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(type="uint8", name="x"),
                MessageDefinitionField(type="uint8", name="y"),
            ],
        )
    ]


def test_ignores_comment_lines():
    message_definition = (
        "# your first name goes here\n"
        "string first_name\n\n"
        "# last name here\n"
        "### foo bar baz?\n"
        "string last_name\n"
    )
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(type="string", name="first_name"),
                MessageDefinitionField(type="string", name="last_name"),
            ],
        )
    ]


def test_parses_variable_length_array():
    assert parse("string[] names", ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(type="string", name="names", is_array=True)
            ],
        )
    ]


def test_parses_fixed_length_array():
    assert parse("string[3] names", ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(
                    type="string", name="names", is_array=True, array_length=3
                )
            ],
        )
    ]


def test_parses_nested_complex_types():
    message_definition = (
        "string username\n"
        "Account account\n"
        "===============\n"
        "MSG: custom_type/Account\n"
        "string name\n"
        "uint16 id"
    )
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(type="string", name="username"),
                MessageDefinitionField(
                    type="custom_type/Account", name="account", is_complex=True
                ),
            ],
        ),
        MessageDefinition(
            name="custom_type/Account",
            definitions=[
                MessageDefinitionField(type="string", name="name"),
                MessageDefinitionField(type="uint16", name="id"),
            ],
        ),
    ]


def test_returns_constants():
    message_definition = (
        "uint32 FOO = 55\n"
        "int32 BAR=-11\n"
        "float32 BAZ= -32.25\n"
        "bool SOME_BOOLEAN = 0\n"
        "string FOO_STR = Foo\n"
        "int64 A = 0000000000000001"
    )
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(
                    type="uint32",
                    name="FOO",
                    is_constant=True,
                    value=55,
                    value_text="55",
                ),
                MessageDefinitionField(
                    type="int32",
                    name="BAR",
                    is_constant=True,
                    value=-11,
                    value_text="-11",
                ),
                MessageDefinitionField(
                    type="float32",
                    name="BAZ",
                    is_constant=True,
                    value=-32.25,
                    value_text="-32.25",
                ),
                MessageDefinitionField(
                    type="bool",
                    name="SOME_BOOLEAN",
                    is_constant=True,
                    value=False,
                    value_text="0",
                ),
                MessageDefinitionField(
                    type="string",
                    name="FOO_STR",
                    is_constant=True,
                    value="Foo",
                    value_text="Foo",
                ),
                MessageDefinitionField(
                    type="int64",
                    name="A",
                    is_constant=True,
                    value=1,
                    value_text="0000000000000001",
                ),
            ],
        )
    ]


def test_handles_python_boolean_values():
    message_definition = "bool ALIVE=True\n" "bool DEAD=False"
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(
                    type="bool",
                    name="ALIVE",
                    is_constant=True,
                    value=True,
                    value_text="True",
                ),
                MessageDefinitionField(
                    type="bool",
                    name="DEAD",
                    is_constant=True,
                    value=False,
                    value_text="False",
                ),
            ],
        )
    ]


def test_handles_type_names_for_fields():
    assert parse("time time", ros2=True) == [
        MessageDefinition(
            name=None, definitions=[MessageDefinitionField(type="time", name="time")]
        )
    ]

    assert parse("time time_ref", ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[MessageDefinitionField(type="time", name="time_ref")],
        )
    ]

    message_definition = (
        "true true\n" "===============\n" "MSG: custom/true\n" "bool false"
    )
    assert parse(message_definition, ros2=True) == [
        MessageDefinition(
            name=None,
            definitions=[
                MessageDefinitionField(type="custom/true", name="true", is_complex=True)
            ],
        ),
        MessageDefinition(
            name="custom/true",
            definitions=[MessageDefinitionField(type="bool", name="false")],
        ),
    ]
