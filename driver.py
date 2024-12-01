import pandas as pd
import uuid
from db import DB
from embed import Embed
from validate import Validate
from fake_data_company import FakeDataCompany


class Driver:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.db = DB(uri, user, password)
        try:
            self.db.connect()
        except Exception as e:
            print(f"An error occurred: {e}")

        self.group_min_len = 0
        self.group_max_len = 0
        self.db_summary = self.db.fetch_summary()
        self.data_dict = {}
        self.fields_dict = {}

    def print_db_info(self):
        try:
            self.db.print_summary()

        except Exception as e:
            print(f"An error occurred: {e}")

    def select_node_type(self):
        node_type = input("Enter the node type")

        if node_type == "all":
            for node in self.db_summary["node_type"]:
                self.data_dict[node] = self.db.query_nodes(node)

    def select_group_params(self):
        self.group_min_len = int(input("Enter group min length: "))
        self.group_max_len = int(input("Enter group max length: "))

    def select_fields(self):
        for node_type, nodes in self.data_dict.items():
            print(f"For Node type: {node_type}, \n")
            self.analyze_keys(nodes)
            required_fields = input("Enter the required fields: ").split(" ")
            optional_fields = input("Enter the optional fields: ").split(" ")
            self.fields_dict[node_type] = (required_fields, optional_fields)

    def generate_private_key(self):
        return uuid.uuid4().hex

    def generate_fake_data(self):
        # TODO: fake to real ratio
        pass

    def validate(self):
        pass

    def verify_deletion(self):
        pass

    def verify_group_parameters(self):
        pass

    @staticmethod
    def analyze_keys(records):
        """Analyze keys present in all or only some of the records."""
        if not records:
            return "No records to analyze."

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(records)

        # Get keys present in all records
        common_keys = df.columns[df.notnull().all()].tolist()

        # Get keys not present in all records
        partial_keys = df.columns[df.isnull().any()].tolist()

        # Separate numerical and non-numerical keys
        numerical_keys = [key for key in df.columns if pd.to_numeric(df[key], errors='coerce').notnull().all()]
        non_numerical_keys = [key for key in df.columns if key not in numerical_keys]

        # Print the results
        print("Keys present in all records:", common_keys)
        print("Keys not present in all records:", partial_keys)
        print("Numerical keys:", numerical_keys)
        print("Non-numerical keys:", non_numerical_keys)




