import pygame
from pygame import Color, Rect, Surface
from pygame.font import Font

import sys
from math import floor
from pyvectors import Vector2

pygame.init()
clock = pygame.time.Clock()

class Udim():
    size: float
    offset: int

    def __init__(self, size=0, offset=0):
        self.size = size
        self.offset = offset

    def __str__(self):
        return f"{self.size}, {self.offset}"

    def calc(self, absolute: int):
        return floor(absolute * self.size) + self.offset

class Udim2():
    x: Udim
    y: Udim

    def __init__(self, scaleX=0, offsetX=0, scaleY=0, offsetY=0):
        self.x, self.y = Udim(scaleX, offsetX), Udim(scaleY, offsetY)

    def __str__(self):
        return f"{self.x}; {self.y}"

    @classmethod
    def fromOffset(cls, offsetX: int, offsetY: int):
        return cls(0, offsetX, 0, offsetY)

    @classmethod
    def fromScale(cls, scaleX: float, scaleY: float):
        return cls(scaleX, 0, scaleY, 0)

    def calc(self, absolute: tuple):
        return self.x.calc(absolute[0]), self.y.calc(absolute[1])


class UIElement():
    absoluteSize: Vector2
    absolutePosition: Vector2

    enabled = True
    parent = None


class Frame(UIElement):
    position: Udim2
    size: Udim2
    color: Color

    actions: dict

    def __init__(self, position=Udim2(), size=Udim2.fromOffset(200, 50)):
        self.position = position
        self.size = size
        self.color = Color("white")

        self.actions = {}

    def bindToState(self, state: str, action):
        stateActions = self.actions.get(state)
        
        if stateActions is None:
            self.actions[state] = [action]
        else:
            stateActions.append(action)

    def executeActions(self):
        stateActions = self.actions.get(self.state)
        if stateActions:
            for action in stateActions:
                action()

    def calcRect(self, surface):
        parentSize = self.parent.absoluteSize.components
        posX, posY = self.position.calc(parentSize)
        scaleX, scaleY = self.size.calc(parentSize)
        
        return pygame.Rect(posX, posY, scaleX, scaleY)

    def setTransparency(self, transparency: int):
        alpha = floor(255*(1 - transparency))
        self.color.update(self.color.r, self.color.g, self.color.b, alpha)

    def draw(self, surface, rect: Rect):
        return pygame.draw.rect(surface, self.color, rect)

    def update(self, surface):
        rect = self.calcRect(surface)
        mX, mY = pygame.mouse.get_pos()

        if rect.collidepoint(mX, mY):
            self.state = "hovered"
        else:
            self.state = "idle"

        self.executeActions()

        return self.draw(surface, rect)


class TextLabel(Frame):
    text = "Hell0 w0rld"
    textColor: Color
    
    fontName = None
    fontSize = 12

    state = "idle"
    
    _cachedRender=("", None)

    def __init__(self, position=Udim2(), size=Udim2.fromOffset(200, 50)):
        Frame.__init__(self, position, size)
        self.font = pygame.font.Font(None, )
        self.textColor = Color("black")

    
    def draw(self, layer, rect):
        # Render font if text changed
        if self._cachedRender[0] != self.text:
            font = Font(self.fontName, self.fontSize)
            render = font.render(self.text, True, self.textColor)
            self._cachedRender = (self.text, render)

        # Gets the text size and creates a rect centered from the background
        textWidth, textHeight = self._cachedRender[1].get_size()
        textRect = Rect(rect.centerx - textWidth/2, rect.centery - textHeight/2, textWidth, textHeight)

        # Draw background and text
        Frame.draw(self, layer, rect)
        layer.blit(self._cachedRender[1], textRect)

        return rect


class TextButton(TextLabel):
    def update(self, layer):
        rect = self.calcRect(layer)
        mx, my = pygame.mouse.get_pos()
        m1 = pygame.mouse.get_pressed()[0]
        mouseCollision = rect.collidepoint(mx, my)

        if (self.state == "activated" or self.state == "hold") and m1:
            self.state = "hold"

        elif mouseCollision and m1:
            self.state = "activated"
        
        elif mouseCollision and not m1:
            self.state = "hovered"
        
        else:
            self.state = "idle"

        self.executeActions()

        return self.draw(layer, rect)
        

class Panel(UIElement):
    enabled = True
    absoluteSize: Vector2
    elements: list

    def __init__(self, layer, elements):
        self.parent = layer
        self.absolutePosition = Vector2()
        self.absoluteSize = Vector2(layer.width, layer.height)
        self.elements = elements

        layer.panels.append(self)

        for elem in elements:
            elem.parent = self

    def sortElements(self):
        print("Sorted")

    def update(self):
        for elem in self.elements:
            
            if elem.enabled:
                elem.update(self.parent.surface)

class UILayer():
    width: int
    height: int
    surface: Surface

    panels: list

    def __init__(self, window: Surface):
        windowSize = window.get_size()
        self.width, self.height = windowSize
        self.surface = Surface(windowSize, pygame.SRCALPHA)

        self.panels = []

    def draw(self):
        self.surface.fill(Color(0, 0, 0, 0))

        for panel in self.panels:
            
            if panel.enabled:
                panel.update()



def exit():
    pygame.quit()
    sys.exit()


def main():
    ratio = 1200/1920
    WIDTH = 800
    HEIGHT = WIDTH*ratio
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    layer = UILayer(window)

    background_color = Color("black")

    panel1 = Panel(layer, [])
    panel2 = Panel(layer, [])
    panel2.enabled = False

    frame = Frame(position=Udim2.fromOffset(200, 0))
    textlabel = TextLabel(position=Udim2.fromOffset(400, 0))
    
    textbutton1 = TextButton()
    # print(text.size)
    textbutton1.fontSize = 40
    textbutton1.color = Color("white")
    textbutton1.textColor = Color("red")
    textbutton1.setTransparency(0)
    
    textbutton1.parent = panel1
    panel1.elements.append(textbutton1)

    textbutton2 = TextButton(position=Udim2.fromOffset(200, 50))
    textbutton2.fontSize = 40
    textbutton2.color = Color("white")
    textbutton2.textColor = Color("blue")
    textbutton2.setTransparency(0)
    
    textbutton2.parent = panel2
    panel2.elements.append(textbutton2)

    def togglePanels():
        panel1.enabled = not panel1.enabled
        panel2.enabled = not panel2.enabled

    textbutton1.bindToState("activated", togglePanels)
    textbutton2.bindToState("activated", togglePanels)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    return exit()
        
        window.fill(background_color)
        window.blit(layer.surface, (0, 0))

        
        layer.draw()
        
        
        pygame.display.flip()
        clock.tick(400)


if __name__=="__main__":
    main()
