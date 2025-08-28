from turtle import Turtle
import math as m
class TurtleQS:

  def __init__(self, limit = 10, screenWidth = 400, screenHeight = 400):
    """
    Initialize world coordinates and screen size. \n
    """
    self.screenWidth = screenWidth
    self.screenHeight = screenHeight
    self.t = Turtle()
    if limit > 10 or limit < 5:
      print(f"Setting grid limit: {10}")
      self.lx = 10 * -1
      self.ly = 10 * -1
      self.ux = 10
      self.uy = 10
    else:
      print(f"Setting grid limit: {limit}")
      self.lx = abs(limit) * -1
      self.ly = abs(limit) * -1
      self.ux = abs(limit)
      self.uy = abs(limit)

    if self.screenHeight < 100:
      self.screenHeight = 400
    if self.screenWidth < 100:
      self.screenWidth = 400

  def mainloop(self):
    self.t.screen.mainloop()

  def start(self, tracerOn = True, showGrid = True, speed = 1):
    """
    Draws coordinate plane if showGrid = True\n
    Set speed if you want to draw faster or slower (0: fastest, 1 -> 10; slowest -> fastest)\n
    Toggle tracer False, if you want to draw in background then refresh screen to view drawing.\n
    **If Tracer is off, will not refresh the screen. To see drawing use screenUpdate() before mainloop()**
    """
    screen = self.t.getscreen()
    screen.tracer(0)
    screen.setup(self.screenWidth, self.screenHeight)
    screen.bgcolor("white")
    screen.setworldcoordinates(self.lx, self.ly, self.ux, self.uy)
    self.t.speed(speed)  # Fastest speed

    if showGrid:
      self.drawGrid()

    screen.tracer(1 if tracerOn else 0)
    # self.t.screen.update()
    self.t.goto(0, 0)
    self.t.pendown()

    return self.t

  def drawGrid(self):
    grid = Turtle()  # separate turtle for grid
    grid.hideturtle()
    grid.penup()
    grid.speed(0)

    # Draw vertical lines + numbers
    x = self.lx
    for i in range((self.ux * 2) + 1):
        if i == ((self.ux * 2) / 2):
            grid.pencolor("red")
        else:
            grid.pencolor("black")

        # line
        grid.goto(x, self.uy)
        grid.pendown()
        grid.goto(x, self.ly)
        grid.penup()

        # label (skip origin because it clutters)
        # if x != 0:
        grid.goto(x, self.ly - 1)   # a little below x-axis
        grid.write(str(x), align="center", font=("Arial", 8, "normal"))

        x += 1

    # Draw horizontal lines + numbers
    y = self.ly
    for i in range((self.uy * 2) + 1):
        if i == (self.uy * 2) / 2:
            grid.pencolor("red")
        else:
            grid.pencolor("black")

        # line
        grid.goto(self.lx, y)
        grid.pendown()
        grid.goto(self.ux, y)
        grid.penup()

        # label (skip origin to avoid overlap)
        # if y != 0:
        grid.goto(self.lx - .2, y -.4)  # a little left of y-axis
        grid.write(str(y), align="right", font=("Arial", 8, "normal"))

        y += 1


  def screenUpdate(self):
    """
    Updates the screen. Useful when the tracer is off, should be used at the end of file before mainloop().
    Allows screen to update drawing. Great to use when using goto, forward, etc. to see the effect of methods.
    """
    self.t.screen.update()