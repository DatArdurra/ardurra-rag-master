import csv

def update_telemetry():
    # Read the existing values
    with open(r"C:\Users\apevida\Documents\Human_Resources_App\ardurra-rag-master\app\backend\core\telemetry.csv", 'r') as f:
        reader = csv.reader(f)
        row = next(reader)  # get the first line
        values = [int(x) for x in row]  # convert to integers

    # Increment the first or second value
    values[0] += 1  # increment first value
    # values[1] += 1  # uncomment to increment second value instead

    # Write the updated values back
    with open(r"C:\Users\apevida\Documents\Human_Resources_App\ardurra-rag-master\app\backend\core\telemetry.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(values)