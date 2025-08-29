from turtle import *

FORWARD = 0
RIGHT = 0
BACKWARD = 1
LEFT = 1


def star(
    draw: Turtle,
    size: float,
    pos: tuple[float, float] = None,
    ward=FORWARD,
    directions=RIGHT,
):
    pos = draw.pos() if pos is None else pos
    gomode = draw.backward if ward else draw.forward
    turnmode = draw.left if directions else draw.right

    draw.penup()
    draw.goto(pos[0], pos[1])
    draw.pendown()

    for _ in range(5):
        gomode(size)
        turnmode(144)


def reg_polygon(
    draw: Turtle,
    side: int,
    size: float,
    pos: tuple[float, float] = None,
    ward=FORWARD,
    directions=RIGHT,
):
    pos = draw.pos() if pos is None else pos
    gomode = draw.backward if ward else draw.forward
    turnmode = draw.left if directions else draw.right

    draw.penup()
    draw.goto(pos[0], pos[1])
    draw.pendown()

    for _ in range(side):
        gomode(size)
        turnmode(360 / side)


def rect(
    draw: Turtle,
    width: float,
    height: float,
    pos: tuple[float, float] = None,
    ward=FORWARD,
    directions=RIGHT,
):
    pos = draw.pos() if pos is None else pos
    gomode = draw.backward if ward else draw.forward
    turnmode = draw.left if directions else draw.right

    draw.penup()
    draw.goto(pos[0], pos[1])
    draw.pendown()

    for _ in range(2):
        gomode(width)
        turnmode(90)
        gomode(height)
        turnmode(90)


def square(
    draw: Turtle,
    size: float,
    pos: tuple[float, float] = None,
    ward=FORWARD,
    directions=RIGHT,
):
    rect(draw, size, size, pos, ward, directions)


def reg_polygon(
    draw: Turtle, *points: tuple[float, float], pos: tuple[float, float] = None
):
    pos = draw.pos() if pos is None else pos

    draw.penup()
    draw.goto(pos[0], pos[1])
    draw.pendown()

    for i in points:
        draw.goto(i[0], i[1])
