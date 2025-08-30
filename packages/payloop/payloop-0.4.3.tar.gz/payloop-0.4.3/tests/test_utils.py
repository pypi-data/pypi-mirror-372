from payloop._utils import bytes_to_json, merge_chunk


def test_merge_chunk():
    merged = merge_chunk({}, {"a": 1, "b": [1, 2], "c": {"x": "foo"}})
    merged = merge_chunk(merged, {"b": [3], "c": {"y": "bar"}, "d": 5})
    merged = merge_chunk(merged, {"a": 2, "c": {"x": "baz"}})

    assert merged == {"a": 2, "b": [1, 2, 3], "c": {"x": "baz", "y": "bar"}, "d": 5}


def test_bytes_to_json():
    assert bytes_to_json(
        {
            b"name": b"John",
            "info": {
                b"age": 30,
                b"email": b"john@example.com",
                "tags": [b"friend", b"developer"],
            },
            "body": b'{"abc": "def"}',
        }
    ) == {
        "body": {"abc": "def"},
        "info": {
            "age": 30,
            "email": "john@example.com",
            "tags": [
                "friend",
                "developer",
            ],
        },
        "name": "John",
    }
