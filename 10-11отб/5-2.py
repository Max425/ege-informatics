# Версия 2 — выпуклая оболочка, дальше перебор всех пар её вершин.
# Самая далёкая пара всегда лежит на оболочке, поэтому внутренние точки
# можно выбросить. На обычных данных оболочка крошечная (тест 21: из 182622
# точек остаётся 31 вершина) и решение летает.
# Слабое место: если точки лежат близко к окружности, внутренних почти нет и
# оболочка = почти всё множество. В тестах это 26 и 29 (84627 и 113446 вершин),
# на них решение не укладывается во время. Сдаёт 28 тестов из 30.

import sys

data = sys.stdin.buffer.read().split()
n = int(data[0])

# читаем точки и сразу выкидываем повторы
points = set()
for i in range(n):
    x = int(data[1 + 2 * i])
    y = int(data[2 + 2 * i])
    points.add((x, y))
points = sorted(points)

if len(points) < 2:
    print(0)
    sys.exit()


# знак говорит, куда повернули в точке a, идя o -> a -> b:
# > 0 налево, < 0 направо, = 0 три точки на одной прямой
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


# нижняя часть оболочки: идём слева направо, оставляем только левые повороты
lower = []
for p in points:
    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
        lower.pop()
    lower.append(p)

# верхняя часть: тот же код, но по списку задом наперёд
upper = []
for p in reversed(points):
    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
        upper.pop()
    upper.append(p)

# склеиваем; [:-1] убирает крайние точки, попавшие в обе половины
hull = lower[:-1] + upper[:-1]

# перебор всех пар, но только по вершинам оболочки
best = 0
for i in range(len(hull)):
    for j in range(i + 1, len(hull)):
        dx = hull[i][0] - hull[j][0]
        dy = hull[i][1] - hull[j][1]
        d2 = dx * dx + dy * dy
        if d2 > best:
            best = d2

print(best)
