import random
from faker import Faker
from embed import *

# Initialize Faker for generating fake data
fake = Faker()

# Expanded lists for cities and occupations for fake data generation
cities = [
    "New York", "Los Angeles", "Chicago", "San Francisco", "Austin", "Boston", "Seattle", "Denver", "Miami",
    "Dallas", "Portland", "Houston", "Phoenix", "Philadelphia", "San Diego", "Atlanta", "Orlando", "Nashville"
]

occupations = [
    "Engineer", "Designer", "Artist", "Manager", "Consultant", "Chef", "Photographer", "Nurse",
    "Software Developer", "Researcher", "Teacher", "Architect", "Analyst", "Lawyer", "Musician",
    "Event Planner"
]

# Function to generate random data with 10% original data and 90% fake data
def create_random_data_with_real(num_entries, original_data, cities, occupations):
    random_data = []
    original_data_count = int(num_entries * 0.1)  # 10% of the data will be real
    fake_data_count = num_entries - original_data_count  # 90% will be fake

    # Add 10% real data
    for _ in range(original_data_count):
        real_entry = random.choice(original_data)
        random_data.append(real_entry)

    # Add 90% fake data
    for _ in range(fake_data_count):
        fake_entry = {
            "name": fake.first_name(),
            "age": random.randint(18, 60),
            "city": random.choice(cities),
            "occupation": random.choice(occupations),
            "salary": random.randint(40, 150) * 1000,  # Salary in thousands
            "married": random.choice([True, False]),
            "hobby": random.choice(["Photography", "Reading", "Traveling", "Cooking", "Hiking", "Gaming", "Dancing"])
        }
        random_data.append(fake_entry)

    return random_data

# Generate 10,000 randomized data entries mixing both fake and real data
randomized_data = create_random_data_with_real(1000, full_data, cities, occupations)

print(len(randomized_data))
# Print first 5 entries to check
for entry in randomized_data[:5]:  # print only the first 5 for brevity
    print(entry)


def validate_watermark_ids(records, id_list, private_key, watermark_identity, max_num_fields):
    # Convert id_list to a set for fast membership checks
    id_set = set(str(key) for key in id_list)  # Use set to avoid duplicates and improve lookup speed

    # Iterate over each record in the list with its index (record number)
    for index, record in enumerate(records):
        # Ensure the record has a 'watermark_id'
        if 'watermark_id' in record:
            watermark_id = str(record['watermark_id'])
            if watermark_id in id_set:
                record_hash = watermark_pseudo_node(record, private_key, str(watermark_id), [str(record["age"])],
                                                    max_num_fields)

                # print("watermark_id", watermark_id)
                # print("generated hashed secret", record_hash["hashed_secret"])
                # print("expected hashed secret", id_list[int(watermark_id)])
                if record_hash['hashed_secret'] == id_list[int(watermark_id)]:
                    print("Valid watermark")
                    break
            else:
                print("No Valid watermark")


# Example usage
validate_watermark_ids(randomized_data, id_list, private_key, watermark_identity, max_num_fields)