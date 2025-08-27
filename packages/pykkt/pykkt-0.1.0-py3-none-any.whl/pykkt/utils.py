from typing import Union

from .constants import STX


def compute_lrc(data):
    """
    Compute LRC as XOR of all bytes from length to the end (excluding STX and LRC itself).
    """
    lrc = 0
    for b in data:
        lrc ^= b
    return lrc


def build_message(cmd_code, params: Union[list[int], bytes] = b''):
    """
    Build the message byte array.
    - cmd_code: int, the command or response code.
    - params: bytes or list of ints, the parameters.
    Returns: bytes, the full message including STX and LRC.
    """
    if isinstance(params, list):
        params = bytes(params)
    elif not isinstance(params, bytes):
        raise ValueError("Params must be bytes or list of ints")

    data = cmd_code.to_bytes(1 + (cmd_code > 255), 'big') + params
    message = bytes([len(data)]) + data
    return STX + message + bytes([compute_lrc(message)])
