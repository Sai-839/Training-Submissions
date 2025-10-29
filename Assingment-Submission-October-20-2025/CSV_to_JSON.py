import csv, json

csv_file_path = r"C:\Users\saisu\Desktop\KeyPixel\Training-Submissions\Assingment-Submission-October-20-2025\Unnamed.csv"
json_file_path = r"C:\Users\saisu\Desktop\KeyPixel\Training-Submissions\Assingment-Submission-October-20-2025\Unnamed.json"

def csv_to_json(csv_file_path, json_file_path, placeholder="?no data?"):
    data = []

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cleaned_row = {
                key: (value.strip() if value.strip() else placeholder)
                for key, value in row.items()
            }
            data.append(cleaned_row)

    with open(json_file_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Conversion successful! JSON saved to: {json_file_path}")

csv_to_json("Unnamed.csv", "Unnamed.json")
