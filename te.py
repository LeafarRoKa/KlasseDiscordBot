def flatten(dictionary: dict[str, str | dict]) -> dict[str, str]:
    key_string= ''
    while isinstance(dictionary, dict):
        for key, val in dictionary.items():
            if not val:
                val = ''
            if not key_string:
                key_string = key
            else:
                key_string+= f'/{key}'
            if type(val) != dict:
                return {key_string:val}
            else:
                dictionary=val
                
    return dictionary

print("Example:")
print(flatten({"key": "value"}))

# These "asserts" are used for self-checking
assert flatten({"key": "value"}) == {"key": "value"}
assert flatten({"key": {"deeper": {"more": {"enough": "value"}}}}) == {
    "key/deeper/more/enough": "value"
}
assert flatten({"empty": {}}) == {"empty": ""}
assert flatten(
    {
        "name": {"first": "One", "last": "Drone"},
        "job": "scout",
        "recent": {},
        "additional": {"place": {"zone": "1", "cell": "2"}},
    }
) == {
    "name/first": "One",
    "name/last": "Drone",
    "job": "scout",
    "recent": "",
    "additional/place/zone": "1",
    "additional/place/cell": "2",
}

print("The mission is done! Click 'Check Solution' to earn rewards!")
