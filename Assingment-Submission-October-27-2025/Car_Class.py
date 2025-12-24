class Car:
    # Constructor (initializer)
    def __init__(self, make, model):
        self.make = make      # instance variable for car make
        self.model = model    # instance variable for car model

    # Method to display details
    def display_info(self):
        print(f"Car Make: {self.make}, Model: {self.model}")



# Creating objects (instances) of the Car class
car1 = Car("Toyota", "Camry")
car2 = Car("Tesla", "Model S")
car3 = Car("Rolce Royals", "Cummins")

# Accessing class method
car1.display_info()
car2.display_info()
