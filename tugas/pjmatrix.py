matrix = [list(map(int, input().split())) for _ in range(3)]
n = int(input()) % 8

outer = [
    matrix[0][0], matrix[0][1], matrix[0][2],
    matrix[1][2], matrix[2][2], matrix[2][1],
    matrix[2][0], matrix[1][0]
]

outer = outer[-n:] + outer[:-n]

matrix[0][0], matrix[0][1], matrix[0][2] = outer[0], outer[1], outer[2]
matrix[1][2], matrix[2][2] = outer[3], outer[4]
matrix[2][1], matrix[2][0] = outer[5], outer[6]
matrix[1][0] = outer[7]

for row in matrix:
    print(*row)
