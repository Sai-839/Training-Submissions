import numpy as np

def read_matrix(name = "Matrix"):
    rows = int(input(f"\nEnter no.of rows for Matrix-{name}:"))
    cols = int(input(f"\nEnter no.of columns for Matrix-{name}:"))

    print(f"\nEnter Matrix-{name} values, row by row (each row = {cols} numbers separated by spaces):")
    matrix = []
    for r in range (rows):
        while True:
            row = input(f"\nMatrix-{name} row {r+1}: ").split()
            if len(row) != cols:
                print(f"Please enter exactly {cols} numbers seperated by spaces.")
                continue
            try:
                matrix.append([float(x) for x in row])
                break
            except ValueError:
                print("Please enter numericals only.")
    return matrix

def multiplication(A, B):
    if len(A[0]) != len(B):
        raise ValueError("\nMatrix Multiplication is not possible!!"
                         f"Columns of Matrix-{A} must equal to rows of Matrix-{B}")
    result = []
    for i in range(len(A)):
        row = []
        for j in range(len(B[0])):
            cell = 0
            for k in range(len(B)):
                cell += A[i][k] * B[k][j]
            row.append(cell)
        result.append(row)

    return result

one = read_matrix("1")
two = read_matrix("2")

print("\nMatrix One:", one)
print("\nMatrix two:", two)

try:
    result = multiplication(one, two)
    print("\nResult of given matrices is:")
    for row in result:
        print(row)
except ValueError as e:
    print(e)

