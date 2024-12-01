import pandas as pd
import uuid
import random
import matplotlib.pyplot as plt
from db import DB
from embed import Embed
from validate import Validate
from fake_data_company import FakeDataCompany


class Driver:
    def __init__(self, uri="neo4j://localhost:7687", user="neo4j", password="Password"):
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
        self.private_key = uuid.uuid4().hex
        self.wm_data_dict = {}
        self.wm_secret = {}
        self.fake_data = {}

    def print_db_info(self):
        try:
            self.db.print_summary()

        except Exception as e:
            print(f"An error occurred: {e}")

    def select_node_type(self):
        node_type = input("Enter the node type: ")

        if node_type == "all":
            self.db_summary = {"node_types": [{"labels": ["Company"]}]}

            for node in self.db_summary["node_types"]:
                # print(node)
                nodes = self.db.query_nodes(node["labels"][0])
                nodes = [dict(node1["n"]) for node1 in nodes][:1000]

                new_nodes = []

                for one_node in nodes:
                    # [print(type(value)) for value in one_node.values()]
                    new_node = one_node
                    for key, value in one_node.items():
                        if isinstance(value, str):  # Check if the value is a string
                            # Try to convert to an integer or float
                            try:
                                one_node[key] = int(value)
                            except ValueError:
                                try:
                                    one_node[key] = float(value)
                                except ValueError:
                                    pass

                    new_nodes.append(new_node)

                self.data_dict[node["labels"][0]] = new_nodes

    def select_group_params(self):
        self.group_min_len = 1
        # int(input("Enter group min length: "))
        self.group_max_len = 5
        # int(input("Enter group max length: "))

    def select_fields(self):
        for node_type, nodes in self.data_dict.items():
            print(f"For Node type: {node_type}, \n")
            self.analyze_keys(nodes)
            required_fields = ["companyNumber"]
            # input("Enter the required fields: ").split(" ")
            optional_fields = ["mortgagesOutstanding", "category"]
            # input("Enter the optional fields: ").split(" ")
            watermark_cover_field = "company_id"
            # input("Enter the watermark cover field: ")
            self.fields_dict[node_type] = (required_fields, optional_fields, watermark_cover_field)

    def get_private_key(self):
        return self.private_key

    def watermark(self):
        for node_type, nodes in self.data_dict.items():
            embed = Embed(nodes, node_type=node_type, private_key=self.get_private_key())
            embed.embed(required_fields=self.fields_dict[node_type][0], optional_fields=self.fields_dict[node_type][1],
                        watermark_cover_field=self.fields_dict[node_type][2])
            self.wm_data_dict[node_type] = embed.watermarked_data
            self.wm_secret[node_type] = embed.watermarked_nodes_dict

    def print_watermark_secret(self):
        print("\n PRINTING WATERMARK SECRET: ")
        print(self.private_key)
        print(self.wm_secret)

    def generate_fake_data(self):
        # TODO: fake to real ratio
        for node_type, wm_data in self.wm_data_dict.items():
            num_fake_data = int(input(f"For {node_type}, Enter the number of fake data: "))
            ratio = float(input(f"For {node_type}, Enter the real-to-fake ratio between 0 and 1: "))
            if node_type.lower() == "company":
                fake_data_company = FakeDataCompany()
                fake_data = fake_data_company.create_random_company_data_with_real(num_fake_data, wm_data, ratio)
                self.fake_data[node_type] = fake_data

    def validate(self):
        counter = 0

        for node_type, nodes in self.wm_data_dict.items():
            validate = Validate(data=nodes, node_type=node_type, private_key=self.get_private_key())
            result = validate.validate_watermark(wm_id_dict=self.wm_secret[node_type],
                                                 watermark_cover_field=self.fields_dict[node_type][2])
            counter += 1 if result else 0

        if counter == len(self.data_dict.keys()):
            return True
        else:
            return False

    def verify_deletion(self):  # To preserve the original dataset
        deleted_nodes_percentage, valid_watermarks_detected = self.perform_deletion_attack(node_type="Company", step=2)

        # Plotting the results
        plt.figure(figsize=(10, 6))
        plt.plot(deleted_nodes_percentage, valid_watermarks_detected, marker='o', color='b')

        # Adding labels and title
        plt.title('Effect of Deletion Attack on Valid Watermarks Detection')
        plt.xlabel('Percentage of Deleted Nodes (%)')
        plt.ylabel('Number of Valid Watermarks Detected')
        plt.grid(True)
        plt.show()

    def perform_deletion_attack(self, node_type, step=1):
        """
        Perform deletion attack while tracking valid watermarks.
        """
        data = self.fake_data[node_type]
        total_records = len(data)
        deleted_nodes_percentage = []
        valid_watermarks_detected = []

        iterations = 0
        validate = Validate(data, node_type=node_type, private_key=self.private_key)
        while data and validate.validate_watermark(self.wm_secret[node_type], self.fields_dict[node_type][2]):
            # Randomly delete `step` records
            for _ in range(step):
                if data:
                    data.pop(random.randint(0, len(data) - 1))

            # Calculate the percentage of deleted nodes
            deleted_percentage = ((total_records - len(data)) / total_records) * 100
            deleted_nodes_percentage.append(deleted_percentage)

            # Validate watermarks in the remaining data
            valid_watermarks_records = validate.validate_watermark_all(self.wm_secret[node_type], self.fields_dict[node_type][2])
            valid_watermarks_detected.append(valid_watermarks_records)  # Append here

            iterations += 1
            print(f"Iteration {iterations}: Remaining records = {len(data)}, Valid Watermarks Detected = {valid_watermarks_records}")

        print(f"Watermark verification failed after {iterations} iterations.")
        return deleted_nodes_percentage, valid_watermarks_detected
    
    def verify_group_parameters(self):
        pass

    @staticmethod
    def analyze_keys(records):
        """Analyze keys present in all or only some of the records."""
        if not records:
            return "No records to analyze."

        print(records[0])
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(records)


        # Get keys present in all records
        common_keys = df.columns[df.notnull().all()].tolist()

        # Get keys not present in all records
        partial_keys = df.columns[df.isnull().any()].tolist()

        # Separate numerical and non-numerical keys
        numerical_keys = []
        # Identify numeric columns
        # numeric_keys = []

        for key in df.columns:
            # Get the first non-null value in the column
            first_valid = df[key].dropna().iloc[0] if not df[key].dropna().empty else None
            
            # Check its type
            if first_valid is not None:
                try:
                    # Attempt to convert it to float
                    float(first_valid)
                    numerical_keys.append(key)
                except Exception as e:
                    # Skip if conversion to float fails
                    pass


        non_numerical_keys = [key for key in df.columns if key not in numerical_keys]

        # Print the results
        print("Keys present in all records:", common_keys)
        print("Keys not present in all records:", partial_keys)
        print("Numerical keys:", numerical_keys)
        print("Non-numerical keys:", non_numerical_keys)

    def execute(self):
        self.print_db_info()
        self.select_node_type()
        self.select_group_params()
        self.select_fields()
        self.watermark()
        self.print_watermark_secret()
        self.generate_fake_data()
        print(f"Watermark Verified!" if self.validate() else "No Watermark Found!")
        self.verify_deletion()

if __name__ == "__main__":    
    driver = Driver()    
    driver.execute()
