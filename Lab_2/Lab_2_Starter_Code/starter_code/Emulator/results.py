# Prompt the user to enter 5 values
values = []
for i in range(5):
    while True:
        try:
            value = float(input(f"Enter value {i+1}: "))
            values.append(value)
            break
        except ValueError:
            print("Please enter a valid number.")

# Calculate the mean
mean = sum(values) / len(values)

# Calculate the standard deviation
variance = sum((i - mean) ** 2 for i in values) / len(values)
std_deviation = variance ** 0.5

print(f"Mean: {mean}")
print(f"Standard Deviation: {std_deviation}")