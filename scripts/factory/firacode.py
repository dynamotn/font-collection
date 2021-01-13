"""Specification of font ligatures from FiraCode"""
CHAR_DICT = {
    'equal': '=',
    'greater': '>',
}
LIGATURES = [
    {
        # >=
        'name': 'greater_equal.liga',
        'chars': ['greater', 'equal'],
    },
    {
        # =>
        'name': 'equal_greater.liga',
        'chars': ['equal', 'greater'],
    },
]
