from pluralizer import Pluralizer

pluralizer = Pluralizer()


def pluralize(word: str) -> str:
    """
    Pluralizes a word using the pluralizer library.
    """
    return pluralizer.pluralize(word)


def singularize(word: str) -> str:
    """
    Singularizes a word using the pluralizer library.
    """
    return pluralizer.singular(word)


def snake_case_to_upper_camel_case(snake_str: str) -> str:
    """
    Converts a snake_case string to UpperCamelCase.
    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)
