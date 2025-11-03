# Create an empty list to store employee records
employees = []

# Ask how many employees to add
n = int(input("How many employee records do you want to add? "))

# Collect employee data dynamically
for i in range(n):
    print(f"\nEnter details for Employee {i+1}:")
    name = input("Name: ")
    age = int(input("Age: "))
    department = input("Department: ")
    designation = input("Designation: ")
    salary = float(input("Salary: "))

    # Create dictionary for each employee
    employee = {
        "name": name,
        "age": age,
        "department": department,
        "designation": designation,
        "salary": salary
    }

    # Add to list
    employees.append(employee)

# Print all employee details
print("\nAll Employee Records:")
print("---------------------")
for idx, emp in enumerate(employees, start=1):
    print(f"\nEmployee {idx}:")
    for key, value in emp.items():
        print(f"{key.capitalize():<15}: {value}")
