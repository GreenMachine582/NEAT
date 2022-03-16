
__version__ = '1.1'
__date__ = '16/03/2022'

from pygame import font

font.init()


class Message(object):
    def __init__(self, text, pos, colour=(0, 0, 0), size=20, align=''):
        self.text = text
        self.pos = pos
        self.colour = colour
        self.size = size
        self.align = align
        self.font = 'freesansbold.ttf'

        self.text_surface = None
        self.text_rect = None

        self.generate()

    def generate(self, dims=None):
        padding = 0 if dims is None else (dims[0] / 2) - (self.text_rect[2] / 2)

        text_font = font.Font(self.font, self.size)
        self.text_surface = text_font.render(str(self.text), True, self.colour)
        self.text_rect = self.text_surface.get_rect()
        if self.align == "ml":
            self.text_rect.midleft = (int(self.pos[0] + padding), self.pos[1])
        elif self.align == "mr":
            self.text_rect.midright = (int(self.pos[0] - padding), self.pos[1])
        else:
            self.text_rect.center = self.pos

    def draw(self, window):
        window.blit(self.text_surface, self.text_rect)
