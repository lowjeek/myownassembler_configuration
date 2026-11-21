; Инициализация массива [9, -4, 12] по адресам 100–102.
LOAD 9
WRITE 100
LOAD -4
WRITE 101
LOAD 12
WRITE 102

; Копирование в 200–202. READ заменяет значение аккумулятора.
LOAD 100
READ 0
WRITE 200
LOAD 100
READ 1
WRITE 201
LOAD 100
READ 2
WRITE 202
