import random
from faker import Faker
from embed import dicts  # Import the dicts from embed.py

# Initialize Faker for generating fake data
fake = Faker()

# Expanded lists for cities and occupations
cities = [
    "New York", "Los Angeles", "Chicago", "San Francisco", "Austin", "Boston", "Seattle", "Denver", "Miami",
    "Dallas", "Portland", "Houston", "Phoenix", "Philadelphia", "San Diego", "Atlanta", "Orlando", "Nashville"
]

occupations = [
    "Engineer", "Designer", "Artist", "Manager", "Consultant", "Chef", "Photographer", "Nurse", 
    "Software Developer", "Researcher", "Teacher", "Architect", "Analyst", "Lawyer", "Musician", 
    "Event Planner"
]

# Function to generate random data with a mix of fake and real entries
def create_random_data_with_real(num_entries, original_data, cities, occupations):
    random_data = []
    
    for _ in range(num_entries):
        if random.choice([True, False]):  # Randomly select between real or fake data
            # Adding fake data
            fake_entry = {}
            fake_entry['name'] = fake.first_name()
            fake_entry['age'] = random.randint(18, 60)
            fake_entry['city'] = random.choice(cities)
            fake_entry['occupation'] = random.choice(occupations)
            fake_entry['salary'] = random.randint(40, 150) * 1000  # Salary in thousands
            fake_entry['married'] = random.choice([True, False])
            fake_entry['hobby'] = random.choice(["Photography", "Reading", "Traveling", "Cooking", "Hiking", "Gaming", "Dancing"])
            random_data.append(fake_entry)
        else:
            # Adding real data from the imported dicts
            real_entry = random.choice(original_data)
            random_data.append(real_entry)
    
    return random_data

# Generate 10000 random data entries mixing both fake and real data
randomized_data = create_random_data_with_real(10000, dicts, cities, occupations)

# Print first 5 entries to check
for entry in randomized_data[:5]:  # print only the first 5 for brevity
    print(entry)
