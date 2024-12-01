import random
from faker import Faker
from datetime import datetime, timedelta


class FakeDataCompany:
    def __init__(self):
        self.fake = Faker()
        # Expanded lists for fake data generation
        self.company_categories = ["Private Limited Company", "Public Limited Company", "LLC", "Sole Proprietorship", "Non-Profit", "Partnership"]
        self.sic_codes = [
            "64999 - Financial intermediation not elsewhere classified",
            "62020 - Information technology consultancy activities",
            "70100 - Activities of head offices",
            "49390 - Other passenger land transport",
            "73110 - Advertising agencies",
            "86210 - General medical practice activities"
        ]
        self.countries_of_origin = [
            "United Kingdom", "United States", "Germany", "France", "Canada", "Australia", "India", "Japan", "China", "Brazil"
        ]
        self.full_company_data = [
            {
                "companyNumber": "04179322",
                "name": "CURO TRANSATLANTIC LIMITED",
                "mortgagesOutstanding": 1,
                "countryOfOrigin": "United Kingdom",
                "incorporationDate": "2001-03-14",
                "category": "Private Limited Company",
                "SIC": "64999 - Financial intermediation not elsewhere classified",
                "status": "Active"
            },
            # Add more real company data here
        ]

# Function to generate random company data with 10% original data and 90% fake data
    def create_random_company_data_with_real(self, num_entries, original_data, ratio):
        random_data = []
        original_data_count = int(num_entries * ratio)  # 10% of the data will be real
        fake_data_count = num_entries - original_data_count  # 90% will be fake

        # Add 10% real data
        for _ in range(original_data_count):
            real_entry = random.choice(original_data)
            random_data.append(real_entry)

        # Add 90% fake data
        for _ in range(fake_data_count):
            fake_entry = {
                "companyNumber": self.fake.unique.random_number(digits=8),  # Random company number with 8 digits
                "name": self.fake.company(),  # Generate a fake company name
                "mortgagesOutstanding": random.randint(0, 5),  # Random number of mortgages
                "countryOfOrigin": random.choice(self.countries_of_origin),  # Random country of origin
                "incorporationDate": self.fake.date_between(start_date="-30y", end_date="today").strftime("%Y-%m-%d"),  # Random date
                "category": random.choice(self.company_categories),  # Random company category
                "SIC": random.choice(self.sic_codes),  # Random SIC code
                "status": random.choice(["Active", "Inactive"]),  # Random company status
                "company_id": random.randint(10, 100)
            }
            random_data.append(fake_entry)

        return random_data

# Sample original company data (this would come from an external source in a real scenario)


# Generate 1,000 randomized company data entries mixing both fake and real data
# randomized_company_data = create_random_company_data_with_real(1000, full_company_data, company_categories, sic_codes, countries_of_origin)

