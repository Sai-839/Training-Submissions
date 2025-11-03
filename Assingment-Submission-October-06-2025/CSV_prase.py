import csv

with open(r"C:\Users\saisu\Desktop\KeyPixel\Training-Submissions\Assingment-Submission-October-06-2025\Temp test.csv", mode="r") as file:
    reader = csv.reader(file)
   
    for row in reader:
        print(row)
