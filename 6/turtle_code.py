import turtle

turtle.tracer(0)  # чтобы сразу увидеть результат
turtle.left(90)  # поворачиваем в начальное положение

# рисуем фигуру
k = 40
for i in range(7):
    turtle.forward(10 * k)
    turtle.right(120)

# рисуем точки
turtle.penup()
for x in range(-k, k):
    for y in range(-k, k):
        turtle.goto(x * k, y * k)
        turtle.dot(5)

turtle.done()  # чтобы рисунок не закрывался
