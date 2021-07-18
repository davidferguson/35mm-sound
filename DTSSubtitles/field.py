from utils import get_header
from consts import ASCII_TYPE, INT_TYPE, WIDTH_SCALE
from consts import HEADER_HEADER_VAL, HEADER_UNKNOWN1_VAL, HEADER_UNKNOWN2_VAL, HEADER_ZOOM_VAL, HEADER_DTS_VAL
from consts import INDEX_HEADER_VAL
from consts import PICHEADER_HEADER_VAL, PICHEADER_OFFSET_PLUS_VAL, PICHEADER_COUNT_MULTIPLE_VAL, PICHEADER_EXTRA_VAL

class Field():
    def __init__(self, name, offset, size, type=INT_TYPE):
        self.name = name
        self.offset = offset
        self.size = size
        self.type = type


class FieldGroup():
    def set_headers(self, headers):
        self.headers = headers
        self.data = {}
        self.pos = -1
    
    def read_file(self, f):
        self.pos = f.tell()
        for header in self.headers:
            f.seek(self.pos + header.offset)
            self.data[header.name] = get_header(f, header)
    
    def print_data(self):
        for name, value in self.data.items():
            print('%s: %s' % (name, value))
    
    def check_data(self):
        pass
