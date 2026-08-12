from src.normalizer import normalize, split_words


def test_lowercase_and_punctuation_are_ignored():
    assert normalize("To be or not to be, that is the question.") == (
        "to be or not to be that is the question"
    )


def test_number_of_spaces_does_not_matter():
    assert normalize("be,   that") == normalize("be, that") == normalize("be that")


def test_punctuation_does_not_leave_a_double_space():
    assert normalize("hello , world") == "hello world"


def test_tabs_and_newlines_become_a_single_space():
    assert normalize("hello\t\nworld") == "hello world"


def test_split_words():
    assert split_words("to be or not") == ["to", "be", "or", "not"]
