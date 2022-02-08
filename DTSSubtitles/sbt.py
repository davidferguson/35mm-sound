from field import FieldGroup, Field
from PIL import Image

from consts import ASCII_TYPE, WIDTH_SCALE, PIL_BINARY_MODE
from consts import HEADER_HEADER_VAL, HEADER_UNKNOWN1_VAL, HEADER_UNKNOWN2_VAL, HEADER_ZOOM_VAL, HEADER_DTS_VAL
from consts import INDEX_HEADER_START, INDEX_HEADER_VAL
from consts import PICHEADER_HEADER_VAL, PICHEADER_OFFSET_PLUS_VAL, PICHEADER_COUNT_MULTIPLE_VAL, PICHEADER_EXTRA_VAL, PICHEADER_EXTRA_NOCOUNT_MASK, PICHEADER_EXTRA_COUNT_MASK, PICHEADER_EXTRA_LENGTH

class SbtHeader(FieldGroup):
    def __init__(self):
        self.set_headers([
            Field('header', 0, 3),
            Field('dts', 6, 3, ASCII_TYPE),
            Field('name', 9, 18, ASCII_TYPE),
            Field('studio', 69, 3, ASCII_TYPE),
            Field('serial', 79, 2),
            Field('language', 85, 3, ASCII_TYPE),
            Field('zoom', 96, 1),
            Field('unknown1', 91, 1),
            Field('unknown2', 113, 3),
       ])
    
    def check_data(self):
        assert self.data['header'] == HEADER_HEADER_VAL, ('Incorrect header value of %s, was expecting %s' % self.data['unknown0'], HEADER_HEADER_VAL)
        assert self.data['unknown1'] == HEADER_UNKNOWN1_VAL
        assert self.data['unknown2'] == HEADER_UNKNOWN2_VAL
        assert self.data['zoom'] == HEADER_ZOOM_VAL, ('Incorrect zoom value of %s, was expecting %s' % self.data['zoom'], HEADER_ZOOM_VAL)
        assert self.data['dts'] == HEADER_DTS_VAL, 'Incorrect DTS value of %s, was expecting %s' % (self.data['dts'], HEADER_DTS_VAL)


class SbtIndex(FieldGroup):
    def __init__(self):
        self.set_headers([
            Field('header', 0, 4),
            Field('offset', 4, 4),
            Field('startframe', 8, 3),
            Field('startreel', 11, 1),
            Field('endframe', 12, 3),
            Field('endreel', 15, 1)
        ])
    
    def is_index(self):
        return self.data['header'] == INDEX_HEADER_VAL
    
    def check_data(self):
        assert self.data['header'] == INDEX_HEADER_VAL, ('Incorrect header value of %s, was expecting %s' % self.data['header'], INDEX_HEADER_VAL)
        assert self.data['startreel'] <= self.data['endreel'], 'Start reel of %s is greater than end reel of %s' % (self.data['startreel'], self.data['endreel'])
        assert self.data['startreel'] < self.data['endreel'] or self.data['startframe'] < self.data['endframe'], 'Reels are the same, but start frame of %s is greater then end frame of %s' % (self.data['startframe'], self.data['endframe'])
    

class SbtPicHeader(FieldGroup):
    def __init__(self):
        self.set_headers([
            Field('header', 0, 4),
            Field('name', 4, 12, ASCII_TYPE),
            Field('offset', 16, 4),
            Field('startframe', 20, 3),
            Field('startreel', 23, 1),
            Field('endframe', 24, 3),
            Field('endreel', 27, 1),
            Field('horizontal', 28, 2),
            Field('vertical', 30, 2),
            Field('height', 32, 2),
            Field('width', 34, 2),
            Field('count', 36, 2),
            Field('extra', 38, 4)
        ])
    
    def read_file(self, f):
        super().read_file(f)
    
    def check_data(self):
        assert self.data['header'] == PICHEADER_HEADER_VAL, ('Incorrect header value of %s, was expecting %s' % self.data['header'], PICHEADER_HEADER_VAL)
        assert self.data['offset'] == self.pos + PICHEADER_OFFSET_PLUS_VAL, 'Offset of %s did not match expected of %s' % (self.data['offset'], self.pos + PICHEADER_OFFSET_PLUS_VAL)
        assert self.data['startreel'] <= self.data['endreel'], 'Start reel of %s is greater than end reel of %s' % (self.data['startreel'], self.data['endreel'])
        assert self.data['startreel'] < self.data['endreel'] or self.data['startframe'] < self.data['endframe'], 'Reels are the same, but start frame of %s is greater then end frame of %s' % (self.data['startframe'], self.data['endframe'])
        assert self.data['count'] * WIDTH_SCALE >= self.data['width'] * self.data['height'], 'Count x %s of %s is less than width x height of %s' % (WIDTH_SCALE, self.data['count'] * 8, self.data['width'] * self.data['height'])
        #assert self.data['count'] % PICHEADER_COUNT_MULTIPLE_VAL == 0, 'Count of %s is not a multiple of %s' % (self.data['count'], PICHEADER_COUNT_MULTIPLE_VAL)
        #assert self.data['extra'] & PICHEADER_EXTRA_NOCOUNT_MASK == PICHEADER_EXTRA_VAL
        #assert self.data['extra'] & PICHEADER_EXTRA_COUNT_MASK == self.data['count']
    
    def calculate_width(self):
        self.data['calculatedwidth'] = int(self.data['count'] / self.data['height'])
    
    def generate_img(self, f):
        self.calculate_width()
        f.seek(self.data['offset'] + PICHEADER_EXTRA_LENGTH)
        data = f.read(self.data['count'])
        img = Image.new(mode=PIL_BINARY_MODE, size=(self.data['calculatedwidth'] * WIDTH_SCALE, self.data['height']))
        offset = 0
        for y in range(0, self.data['height']):
            for x in range(0, self.data['calculatedwidth'] * WIDTH_SCALE, WIDTH_SCALE):
                byte = data[offset]
                offset += 1
                for i in range(0, 8):
                    bit = (byte >> (7 - i) & 0b1)
                    img.putpixel((x + i, self.data['height'] - y - 1), (bit))
        return img


class SbtFile():
    def __init__(self):
        pass
    
    def from_file(self, f):
        self.f = f
        self.__read_header()
        self.__read_indexes()

    def __read_header(self):
        self.sbt_header = SbtHeader()
        self.sbt_header.read_file(self.f)
        self.sbt_header.check_data()
    
    def __read_indexes(self):
        self.sbt_indexes = []
        count = 0
        self.f.seek(INDEX_HEADER_START)
        while True:
            # read in the index
            index = SbtIndex()
            index.read_file(self.f)

            # if not an index, stop looping, reset file pos
            if not index.is_index():
                self.f.seek(self.f.tell() - 16)
                break
            
            # otherwise, check and append the index
            index.check_data()
            self.sbt_indexes.append(index)
            count += 1
    
    def __read_picheaders(self):
        for index in self.sbt_indexes:
            self.f.seek(index.data['offset'])
            picheader = SbtPicHeader()
            picheader.read_file(self.f)
            picheader.check_data()
    
    def __get_sub_img_index(self, index):
        self.f.seek(index.data['offset'])
        picheader = SbtPicHeader()
        picheader.read_file(self.f)
        picheader.check_data()
        return picheader.generate_img(self.f)

    def print_info(self):
        film = self.sbt_header.data['name']
        code = self.sbt_header.data['serial']
        language = self.sbt_header.data['language']
        studio = self.sbt_header.data['studio']
        print('A DTS SBT file for film "%s", code %s, in language %s by studio %s' % (film, code, language, studio))
        num_subs = len(self.sbt_indexes)
        reels = (self.sbt_indexes[-1].data['endreel'] - self.sbt_indexes[0].data['startreel']) + 1
        print('There are %s subtile images across %s reels' % (num_subs, reels))
    
    def get_subs_img(self, startreel, startframe, endreel, endframe):
        for index in self.sbt_indexes:
            # skip past too low indexes
            if index.data['endreel'] < startreel or index.data['endframe'] < startframe:
                continue
            # stop after too high indexes
            if index.data['startreel'] > endreel or index.data['startframe'] > endframe:
                break
            # yield this img
            img = self.__get_sub_img_index(index)
            yield (img, index.data['startreel'], index.data['startframe'])
