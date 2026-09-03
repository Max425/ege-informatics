# Задача: максимальный квадрат расстояния между двумя точками.
# Версия 1 — перебор всех пар. Простая и заведомо правильная, но медленная.
# Сложность O(N^2): при N = 200000 это ~2*10^10 пар, десятки минут. Не сдаётся.
# Нужна как эталон для проверки быстрых версий.

import sys

data = sys.stdin.buffer.read().split()
n = int(data[0])

points = []
for i in range(n):
    x = int(data[1 + 2 * i])
    y = int(data[2 + 2 * i])
    points.append((x, y))

best = 0
for i in range(n):
    for j in range(i + 1, n):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        d2 = dx * dx + dy * dy
        if d2 > best:
            best = d2

# если точка одна, внутренний цикл не выполнится ни разу и best останется 0
print(best)
