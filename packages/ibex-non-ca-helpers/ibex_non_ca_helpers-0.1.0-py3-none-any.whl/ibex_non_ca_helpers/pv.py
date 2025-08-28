from typing import Iterable


def waveform_to_string(data: Iterable[int | str]) -> str:
    output = ""
    for i in data:
        if i == 0:
            break
        if isinstance(i, str):
            output += i
        else:
            output += str(chr(i))
    return output
