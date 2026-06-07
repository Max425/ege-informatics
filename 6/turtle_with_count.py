from turtle import *

color("black", "red")
tracer(0)  # чтобы сразу увидеть результат
left(90)  # поворачиваем в начальное положение
begin_fill()

# рисуем фигуру
k = 40
for i in range(3):
    forward(111 * k)
    right(120)

# считаем точки
end_fill()
canvas = getcanvas()
cnt = 0
for y in range(-120 * k, 120 * k, k):
    for x in range(-120 * k, 120 * k, k):
        item = canvas.find_overlapping(x, y, x, y)
        if len(item) == 1 and item[0] == 5:
            cnt += 1
print(cnt)
