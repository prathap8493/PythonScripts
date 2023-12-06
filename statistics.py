import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate('./config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def calculate_statistics_batchwise(batch_size=10):
    total_votes = 0
    correct_votes = 0
    country_stats = {}
    region_stats = {}

    
    # List of specified images to track
    specified_images = [
        "/AI/AI img 3.jpg",
        "/AI/AI img 4.jpg",
        "/AI/AI img 5.jpg",
        "/AI/AI img 6.jpg",
        "/AI/AI img 8.jpg",
        "/AI/AI img 9.jpg",
        "/AI/AI img 10.jpg",
        "/AI/AI img 11.jpg",
        "/AI/AI img 15.jpg",
        "/AI/AI img 16.jpg",
        "/AI/AI img 17.jpg",
        "/AI/AI img 18.jpg",
        "/Human /img 1.jpg",
        "/Human /img 3.jpg",
        "/Human /img 5.jpg",
        "/Human /img 6.jpg",
        "/Human /img 7.jpg",
        "/Human /img 8.jpg",
        "/Human /img 9.jpg",
        "/Human /img 10.jpg",
        "/Human /img 11.jpg",
        "/Human /img 15.jpg",
        "/Human /img 16.jpg",
        "/Human /img 17.jpg",

        "/AI/AI img 1.jpg",
        "/AI/AI img 2.jpg",
        "/AI/AI img 7.jpg",
        "/AI/AI img 12.jpg",
        "/AI/AI img 13.jpg",
        "/AI/AI img 14.jpg",
        "/AI/AI img 19.jpg",
        "/AI/AI img 20.jpg",
        "/Human /img 2.jpg",
        "/Human /img 4.jpg",
        "/Human /img 12.jpg",
        "/Human /img 13.jpg",
        "/Human /img 14.jpg",
        "/Human /img 18.jpg",
        "/Human /img 19.jpg",
        "/Human /img 20.jpg",

    ]

    # Initialize stats for specified images
    image_stats = {src: {'total_votes': 0, 'correct_votes': 0} for src in specified_images}

    def process_batch(start_after_doc=None):
        nonlocal total_votes, correct_votes

        # Create the query
        query = db.collection('user_responses').order_by(u'__name__').limit(batch_size)
        if start_after_doc:
            query = query.start_after(start_after_doc)

        # Execute the query
        docs = query.stream()
        last_doc = None
        for doc in docs:
            last_doc = doc
            doc_dict = doc.to_dict()
            image_data = doc_dict.get("imageData", [])
            country = doc_dict.get("country", "Unknown")
            region = doc_dict.get("region", "Unknown")

            # Initialize country and region stats if not exist
            if country not in country_stats:
                country_stats[country] = {'total_votes': 0, 'correct_votes': 0}
            if region not in region_stats:
                region_stats[region] = {'total_votes': 0, 'correct_votes': 0}

            # Increment total_votes and correct_votes for each response
            responses = len(image_data)
            total_votes += responses
            correct_responses = sum(1 for response in image_data if response.get("isCorrect"))
            correct_votes += correct_responses

            # Update country and region statistics
            country_stats[country]['total_votes'] += responses
            country_stats[country]['correct_votes'] += correct_responses
            region_stats[region]['total_votes'] += responses
            region_stats[region]['correct_votes'] += correct_responses

            # Update statistics for specified images
            for response in image_data:
                if response.get("src") in specified_images:
                    image_stats[response["src"]]['total_votes'] += 1
                    if response.get("isCorrect"):
                        image_stats[response["src"]]['correct_votes'] += 1

        return last_doc

    # Iterate through the collection in batches
    last_doc = None
    while True:
        last_doc = process_batch(start_after_doc=last_doc)
        if not last_doc:
            break

    # Calculate percentages
    correct_percentage = (correct_votes / total_votes) * 100 if total_votes > 0 else 0

    # Calculate percentages for each country and region
    for country in country_stats:
        country_total = country_stats[country]['total_votes']
        country_correct = country_stats[country]['correct_votes']
        country_stats[country]['percentage_correct'] = (country_correct / country_total) * 100 if country_total > 0 else 0

    for region in region_stats:
        region_total = region_stats[region]['total_votes']
        region_correct = region_stats[region]['correct_votes']
        region_stats[region]['percentage_correct'] = (region_correct / region_total) * 100 if region_total > 0 else 0

    # Calculate percentage for each specified image
    for src in image_stats:
        total = image_stats[src]['total_votes']
        correct = image_stats[src]['correct_votes']
        image_stats[src]['percentage_correct'] = (correct / total) * 100 if total > 0 else 0

    return total_votes, correct_percentage, country_stats, region_stats, image_stats

# Usage
total_votes, correct_percentage, country_stats, region_stats, image_stats = calculate_statistics_batchwise(batch_size=10)

# Write to a file
with open('statistics_output.txt', 'w') as file:
    file.write(f"Total Votes Polled: {total_votes}\n")
    file.write(f"Percentage Correct: {correct_percentage:.2f}%\n")
    file.write("Country Statistics:\n")
    for country, stats in country_stats.items():
        file.write(f"{country}: Total Votes - {stats['total_votes']}, Correct Votes - {stats['correct_votes']}, Percentage Correct - {stats['percentage_correct']:.2f}%\n")
    file.write("Region Statistics:\n")
    for region, stats in region_stats.items():
        file.write(f"{region}: Total Votes - {stats['total_votes']}, Correct Votes - {stats['correct_votes']}, Percentage Correct - {stats['percentage_correct']:.2f}%\n")
    file.write("black Statistics:\n")
    for src, stats in image_stats.items():
        file.write(f"{src}: Total Votes - {stats['total_votes']}, Correct Votes - {stats['correct_votes']}, Percentage Correct - {stats['percentage_correct']:.2f}%\n")

print("Statistics have been written to 'statistics_output.txt'")
