import unittest

from hermes.hermes_cai.contrib.lm_prefix_utils import parse_character_definition, \
    NARRATOR_NAME

CHARACTER_NAME = "Character-Name"
USER_NAME = "User-Name"
AUTHORS = {
    "char": CHARACTER_NAME,
    "user": USER_NAME,
}


class TestParseCharacterDefinition(unittest.TestCase):
    def test_inject_placeholders(self):
        definition = """
{{char}} 1
{{user}} 2
{{random_user_1}} 3
{{random_user_2}} 4
{{some name}} 5
{{char}} 6
{{user}} 7
{{random_user_1}} 8
{{random_user_2}} 9
{{some name}} 6
        """
        v0, _ = parse_character_definition(definition, AUTHORS, version=0)
        v1, _ = parse_character_definition(definition, AUTHORS, version=1)
        self.assertEqual(v0, v1)

    def test_parse(self):
        test_cases = [
            {
                "name": "Empty description",
                "definition": "",
                "result": []
            },
            {
                "name": "Simple description",
                "definition": "Some description here",
                "result": [
                    {"src": NARRATOR_NAME, "text":  "Some description here"},
                ]
            },
            {
                "name": "Description with placeholders",
                "definition": "Some description here, {{char}} and {{user}}",
                "result": [
                    {"src": NARRATOR_NAME, "text": f"Some description here, {CHARACTER_NAME} and {USER_NAME}"},
                ]
            },
            {
                "name": "Simple dialog",
                "definition": "{{char}}: msg1\n{{user}}: msg2\n{{char}}: msg3\nEND_OF_DIALOG",
                "result": [
                    {"src": CHARACTER_NAME, "text": "msg1"},
                    {"src": USER_NAME, "text": "msg2"},
                    {"src": CHARACTER_NAME, "text": "msg3"},
                ]
            },
            {
                "name": "Multiple dialogs",
                "definition": "{{char}}: msg1\n{{user}}: msg2\n{{char}}: msg3\nEND_OF_DIALOG\n{{char}}: msg4\n{{user}}: msg5\n{{char}}: msg6\nEND_OF_DIALOG",
                "result": [
                    {"src": CHARACTER_NAME, "text": "msg1"},
                    {"src": USER_NAME, "text": "msg2"},
                    {"src": CHARACTER_NAME, "text": "msg3"},
                    {"src": CHARACTER_NAME, "text": "msg4"},
                    {"src": USER_NAME, "text": "msg5"},
                    {"src": CHARACTER_NAME, "text": "msg6"},
                ]
            },
            {
                "name": "Dialog without END_OF_DIALOG",
                "definition": "{{char}}: msg1\n{{user}}: msg2\n{{char}}: msg3",
                "result": [
                    {"src": NARRATOR_NAME, "text": f"{CHARACTER_NAME}: msg1\n{USER_NAME}: msg2\n{CHARACTER_NAME}: msg3"},
                ]
            },
            {
                "name": "Dialog and description",
                "definition": "{{char}}: msg1\n{{user}}: msg2\n{{char}}: msg3\nEND_OF_DIALOG\nSome description here",
                "result": [
                    {"src": CHARACTER_NAME, "text": "msg1"},
                    {"src": USER_NAME, "text": "msg2"},
                    {"src": CHARACTER_NAME, "text": "msg3"},
                    {"src": NARRATOR_NAME, "text": "Some description here"},
                ]
            },
            {
                "name": "Description and dialog",
                "definition": "Some description here\n{{char}}: msg1\n{{user}}: msg2\n{{char}}: msg3\nEND_OF_DIALOG",
                "result": [
                    {"src": NARRATOR_NAME, "text": "Some description here"},
                    {"src": CHARACTER_NAME, "text": "msg1"},
                    {"src": USER_NAME, "text": "msg2"},
                    {"src": CHARACTER_NAME, "text": "msg3"},
                ]
            },
            {
                "name": "Multilines",
                "definition": "\n\nSome description here\nEven more description\n\n{{char}}: msg1-1\nmsg1-2\n{{user}}: msg2-1\nmsg2-2\n\n{{char}}: msg3-1\nmsg3-2\nEND_OF_DIALOG\n\n",
                "result": [
                    {"src": NARRATOR_NAME, "text": "Some description here\nEven more description"},
                    {"src": CHARACTER_NAME, "text": "msg1-1\nmsg1-2"},
                    {"src": USER_NAME, "text": "msg2-1\nmsg2-2"},
                    {"src": CHARACTER_NAME, "text": "msg3-1\nmsg3-2"},
                ]
            },
            {
                "name": "Multilines for windows",
                "definition": "\r\n\r\nSome description here\r\nEven more description\r\n\r\n{{char}}: msg1-1\r\nmsg1-2\r\n{{user}}: msg2-1\r\nmsg2-2\r\n\r\n{{char}}: msg3-1\r\nmsg3-2\r\nEND_OF_DIALOG\r\n\r\n",
                "result": [
                    {"src": NARRATOR_NAME, "text": "Some description here\nEven more description"},
                    {"src": CHARACTER_NAME, "text": "msg1-1\nmsg1-2"},
                    {"src": USER_NAME, "text": "msg2-1\nmsg2-2"},
                    {"src": CHARACTER_NAME, "text": "msg3-1\nmsg3-2"},
                ]
            },
            {
                "name": "Complex",
                "definition": """
desc1
desc2
{{char}}: msg1-1
msg1-2

{{user}}:
msg2-1
msg2-2
{{char}}:
msg3-1

msg3-2
END_OF_DIALOG

desc4

desc5
{{char}}: msg4-1
msg4-2

{{user}}:
msg5-1
msg5-2
{{char}}:
msg6-1

msg6-2
END_OF_DIALOG
desc6
""",
                "result": [
                    {"src": NARRATOR_NAME, "text": "desc1\ndesc2"},
                    {"src": CHARACTER_NAME, "text": "msg1-1\nmsg1-2"},
                    {"src": USER_NAME, "text": "msg2-1\nmsg2-2"},
                    {"src": CHARACTER_NAME, "text": "msg3-1\nmsg3-2"},
                    {"src": NARRATOR_NAME, "text": "desc4\ndesc5"},
                    {"src": CHARACTER_NAME, "text": "msg4-1\nmsg4-2"},
                    {"src": USER_NAME, "text": "msg5-1\nmsg5-2"},
                    {"src": CHARACTER_NAME, "text": "msg6-1\nmsg6-2"},
                    {"src": NARRATOR_NAME, "text": "desc6"},
                ]
            },
        ]
        for case in test_cases:
            with self.subTest(case["name"]) as subtest:
                definition = case["definition"]
                expected = case["result"]
                v1, _ = parse_character_definition(definition, AUTHORS, version=1)
                self.assertEqual(v1, expected)


if __name__ == "__main__":
    unittest.main()
