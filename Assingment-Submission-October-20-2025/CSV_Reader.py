import csv, sys

PLACEHOLDER = '??NO DATA??' #To handel missing data

def read_and_print_csv(file_path):
    print(f"--- Task 1: Reading CSV File: {file_path} ---")
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
        
        print("Headers:", reader.fieldnames) #Gives Headers First
        
        for i, row in enumerate(reader, start=1):
            print(f"\nRow {i}:")
            for key, value in row.items():
                value = value.strip() or PLACEHOLDER
                print(f"  {key}: {value}")
                
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    print("\n")

if __name__ == "__main__":
    file_path = r'C:\Users\saisu\Desktop\KeyPixel\Training-Submissions\Assingment-Submission-October-20-2025\Temp test.csv'
    read_and_print_csv('file_path')