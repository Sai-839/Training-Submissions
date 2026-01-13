import numpy as np

zeros = int(input("enter no.of zeros to be printed:"))
ones = int(input("enter no.of ones to be printed:"))

zeros_array = np.zeros(zeros, dtype = int)
ones_array = np.ones(ones, dtype = int)

print("One Dimensional Array of zeros and ones are as follows:")
print("--------------")

print(zeros_array)
print(ones_array)

zeros_2d = np.zeros((zeros, zeros), dtype = int)
ones_2d = np.ones((ones, ones), dtype = int)

print("Two Dimensional Array of zeros and ones are as follows:")
print("--------------")

print(zeros_2d)
print(ones_2d)

combined = np.array([np.zeros(zeros, dtype = int), np.ones(ones, dtype = int)])

print("The combined one dimensional arrray of both zeros and ones array's is as follows:")
print("--------------")

print(combined)
