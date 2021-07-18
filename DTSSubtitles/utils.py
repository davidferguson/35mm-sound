from consts import ASCII_TYPE, INT_TYPE, ENDIAN, ASCII_ENCODING

def get_header(f, header):
    # we assume the file is already seeked to the correct point
    raw = f.read(header.size)

    # decode it appropriately
    if header.type == INT_TYPE:
        return int.from_bytes(raw, ENDIAN)
    elif header.type == ASCII_TYPE:
        return raw.decode(ASCII_ENCODING)
    else:
        raise ValueError('Unknown type for field: "%s"' % header.type)