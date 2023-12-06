# import json

# # Assuming the JSON data is stored in a file named 'data.json'
# file_path = 'data.json'

# def count_correct_guesses(file_path, correct_count):
#     try:
#         with open(file_path, 'r') as file:
#             data = json.load(file)

#         # Counting the number of users with the specified correct_count
#         count = sum(1 for item in data if item.get("correct_count") == str(correct_count))
#         return count
#     except FileNotFoundError:
#         return "File not found."
#     except json.JSONDecodeError:
#         return "Error decoding JSON."
#     except Exception as e:
#         return str(e)

# # Count how many people have correct_count=5
# result = count_correct_guesses(file_path, 1)
# print(result)



import json

def calculate_statistics_from_json(json_file, output_file):
    # Initialize statistics dictionaries
    country_stats = {}
    total_votes = 0
    total_correct = 0

    # Read and parse the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Process each entry in the JSON data
    for entry in data:
        country = entry.get('country', 'Unknown')
        incorrect_count = int(entry['incorrect_count'])
        correct_count = int(entry['correct_count'])
        country_total_votes = incorrect_count + correct_count

        # Update total votes and total correct votes
        total_votes += country_total_votes
        total_correct += correct_count

        # Initialize country stats if not exist
        if country not in country_stats:
            country_stats[country] = {'total_votes': 0, 'correct_votes': 0}

        # Update country statistics
        country_stats[country]['total_votes'] += country_total_votes
        country_stats[country]['correct_votes'] += correct_count

        # Check for None or empty country fields
        if country is None or country == "":
            print(f"Found an entry with no country specified: {entry}")

    # Calculate overall percentage correct
    percentage_correct = (total_correct / total_votes) * 100 if total_votes > 0 else 0

    # Write the results to a file
    with open(output_file, 'w') as f:
        f.write(f"Total Votes Polled: {total_votes}\n")
        f.write(f"Percentage Correct: {percentage_correct:.2f}%\n\n")
        f.write("Country Statistics:\n")
        f.write("--------------------\n\n")
        for country, stats in country_stats.items():
            country_total = stats['total_votes']
            country_correct = stats['correct_votes']
            country_percentage_correct = (country_correct / country_total) * 100 if country_total > 0 else 0
            f.write(f"{country}: Total Votes - {country_total}, Correct Votes - {country_correct}, Percentage Correct - {country_percentage_correct:.2f}%\n")

# Usage
json_file = 'dec6_data.json'  # Replace with your JSON file path
output_file = 'statistics_output2.txt'  # Output file name
calculate_statistics_from_json(json_file, output_file)

print("Statistics have been written to 'statistics_output.txt'")




