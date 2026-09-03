# Версия 3 — итоговая: выпуклая оболочка + вращающиеся калиперы.
# Оболочка строится за O(N log N) (основное время — сортировка),
# калиперы проходят по ней за O(h), потому что указатель j не откатывается назад.
# Проходит все 30 тестов, самый тяжёлый — 0.37 с.

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


# знак говорит, куда повернули в точке a, идя o -> a -> b
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def dist2(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


# нижняя часть оболочки: идём слева направо
lower = []
for p in points:
    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
        lower.pop()
    lower.append(p)

# верхняя часть: идём справа налево
upper = []
for p in reversed(points):
    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
        upper.pop()
    upper.append(p)

# склеиваем, у каждой половины убираем последнюю точку (она же первая у другой)
hull = lower[:-1] + upper[:-1]
m = len(hull)

# все точки на одной прямой: многоугольника нет, ответ — крайние точки
if m < 3:
    print(dist2(points[0], points[-1]))
    sys.exit()

# вращающиеся калиперы
best = 0
j = 1
for i in range(m):
    a = hull[i]
    b = hull[(i + 1) % m]
    # двигаем j, пока следующая вершина дальше от прямой a-b, чем текущая
    while cross(a, b, hull[(j + 1) % m]) > cross(a, b, hull[j]):
        j = (j + 1) % m
    c = hull[j]
    best = max(best, dist2(a, c), dist2(b, c))

print(best)
