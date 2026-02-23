import string


base62 = list(string.digits + string.ascii_uppercase + string.ascii_lowercase)

def convert_to_shortcode(no: int):
    """converts integer to shortcode(base62)"""
    values = []

    while no > 0:
        rem = no % 62        
        no = int(no / 62)
        
        values.append(base62[rem])

    return "".join(reversed(values))


def decode_shortcode(code: str):
    """decode shortcode(base-62) to integer(base-10)"""
    total = 0

    values = [] 
    for item in code:
        values.append(base62.index(item))

    index = len(values) - 1
    for item in values:
        total += item * (62 ** index)
        index -= 1
        
    return total

