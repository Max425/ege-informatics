# условие задачи https://kpolyakov.spb.ru/school/ege/gen.php?action=viewTopic&topicId=6890

file = open('26-134.txt')
n, time = map(int, file.readline().split())
mas = []
for s in file:
    s = s.replace('G', '0').replace('W', '1').replace('M', '2')
    mas.append([int(x) for x in s.split()])
mas.sort()

queue, doctor = [], []
for t in range(time):

    # всех людей, что пришли - добавляем в очередь
    while t == mas[0][0]:
        queue.append(mas[0])
        mas = mas[1:]

    # сортируем очередь, в порядке преоритетов
    queue.sort(key=lambda x: (x[2], x[0]))

    # запускаем поситителя из очереди к врачу, если свободно
    if len(queue) != 0 and (len(doctor) == 0 or doctor[-1][1] <= t):
        queue[0][1] += t  # записываем время, когда уйдет посититель
        doctor.append(queue[0])
        queue = queue[1:]

print(len(doctor), len([x for x in doctor if x[2] == doctor[-1][2]]))
