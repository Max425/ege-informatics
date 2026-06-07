# Текстовый файл состоит из символов P, R, O, E, G – зашифрованное письмо Деду Морозу.
#
# Определите в прилагаемом файле максимальное количество идущих подряд символов, среди которых комбинация символов RO
# встречается ровно 21 раз, а комбинации символов ORO и ROR ни разу не встречаются.
# ответ - 814


f = open('24_12476.txt').readline()
left = 0
ro = oro = ror = 0
ans = 0

for right in range(len(f)):
    c = f[right]
    # добавляем правый символ, обновляем счётчики
    if right >= 1 and f[right-1] == 'R' and c == 'O':
        ro += 1
    if right >= 2 and f[right-2] == 'O' and f[right-1] == 'R' and c == 'O':
        oro += 1
    if right >= 2 and f[right-2] == 'R' and f[right-1] == 'O' and c == 'R':
        ror += 1

    # сжимаем окно слева пока условие нарушено
    while ro > 21 or oro > 0 or ror > 0:
        lc = f[left]
        if left + 1 < len(f) and lc == 'R' and f[left+1] == 'O':
            ro -= 1
        if left + 2 < len(f) and lc == 'O' and f[left+1] == 'R' and f[left+2] == 'O':
            oro -= 1
        if left + 2 < len(f) and lc == 'R' and f[left+1] == 'O' and f[left+2] == 'R':
            ror -= 1
        left += 1

    if ro == 21:
        ans = max(ans, right - left + 1)

print(ans)