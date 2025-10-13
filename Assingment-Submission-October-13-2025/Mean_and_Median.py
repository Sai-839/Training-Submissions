def calculate_mean_median(numbers):
    if not numbers:
        return None, None  # Handle empty list safely

    # Sort the list for median calculation
    numbers.sort()

    # Mean
    mean = sum(numbers) / len(numbers)

    # Median
    n = len(numbers)
    if n % 2 == 1:
        median = numbers[n // 2]
    else:
        median = (numbers[n // 2 - 1] + numbers[n // 2]) / 2

    return mean, median

# Reading numbers
data = list(map(int, input("Enter the numbers separated by space to calculate the mean and median: ").split()))
mean, median = calculate_mean_median(data)

print("Your Numbers :", data)
print(f"Mean: {mean}")
print(f"Median: {median}")
