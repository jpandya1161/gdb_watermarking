import pandas as pd
import uuid
import random
import matplotlib.pyplot as plt
import itertools
import time
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
            # self.db_summary = {"node_types": [{"labels": ["Company"]}]}

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
        self.group_min_len = int(input("Enter group min length: "))
        self.group_max_len = int(input("Enter group max length: "))

    def select_fields(self):
        for node_type, nodes in self.data_dict.items():
            # if node_type.lower() == "company":
            print(f"For Node type: {node_type}, \n")
            self.analyze_keys(nodes)
            required_fields = input("Enter the required fields: ").split(" ")
            optional_fields = input("Enter the optional fields: ").split(" ")
            watermark_cover_field = input("Enter the watermark cover field: ")
            self.fields_dict[node_type] = (required_fields, optional_fields, watermark_cover_field)

    def get_private_key(self):
        return self.private_key

    def watermark(self):
        for node_type, nodes in self.data_dict.items():
            embed = Embed(nodes, node_type=node_type, private_key=self.get_private_key())
            embed.embed(required_fields=self.fields_dict[node_type][0], optional_fields=self.fields_dict[node_type][1],
                        watermark_cover_field=self.fields_dict[node_type][2], min_group_length=self.group_min_len, max_group_length=self.group_max_len)
            self.wm_data_dict[node_type] = embed.watermarked_data
            self.wm_secret[node_type] = embed.watermarked_nodes_dict

    def print_watermark_secret(self):
        print("\n PRINTING WATERMARK SECRET: ")
        print(self.private_key)
        print(self.wm_secret)

    def generate_fake_data(self):
        # TODO: fake to real ratio
        for node_type, wm_data in self.wm_data_dict.items():
            if node_type.lower() == "company":
                num_fake_data = int(input(f"For {node_type}, Enter the number of fake data: "))
                ratio = float(input(f"For {node_type}, Enter the real-to-fake ratio between 0 and 1: "))
                fake_data_company = FakeDataCompany()
                fake_data = fake_data_company.create_random_company_data_with_real(num_fake_data, wm_data, ratio)
                self.fake_data[node_type] = fake_data
            
            # if node_type.lower() == "person":
            #     fake_data_company = FakeDataPerson()
            #     fake_data = fake_data_company.create_random_company_data_with_real(num_fake_data, wm_data, ratio)
            #     self.fake_data[node_type] = fake_data
            
            # if node_type.lower() == "property":
            #     fake_data_company = FakeDataProperty()
            #     fake_data = fake_data_company.create_random_company_data_with_real(num_fake_data, wm_data, ratio)
            #     self.fake_data[node_type] = fake_data

            # if node_type.lower() == "recipient":
            #     fake_data_company = FakeDataRecipient()
            #     fake_data = fake_data_company.create_random_company_data_with_real(num_fake_data, wm_data, ratio)
            #     self.fake_data[node_type] = fake_data

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
    
    def verify_group_parameters(self, node_type="Company"):
        min_group_sizes = [5, 6, 7, 8, 9, 10]
        max_group_sizes = [25, 50, 75, 100, 125, 150, 175, 200]
        pseudonode_count = []
        combinations = list(itertools.product(min_group_sizes, max_group_sizes))
        times = []
        x = []
        y = []

        data = self.data_dict[node_type]
        embed = Embed(data, node_type=node_type)

        for comb in combinations:
            min_group_length, max_group_length = comb
            start = time.time()
            embed.embed(required_fields=self.fields_dict[node_type][0], optional_fields=self.fields_dict[node_type][1],
                        watermark_cover_field=self.fields_dict[node_type][2], min_group_length=min_group_length, 
                        max_group_length=max_group_length)
            end = time.time()
            times.append(end - start)
            pseudonode_count.append(len(embed.watermarked_nodes_dict.keys()))
            x.append(min_group_length)
            y.append(max_group_length)

        # Uncomment for the plot
        # fig = plt.figure()
        # ax =fig.add_subplot(111, projection="3d")
        # sc = ax.scatter(x, y, pseudonode_count, c=pseudonode_count, cmap="viridis")
        # ax.set_xlabel("Minimum Group Size")
        # ax.set_ylabel("Maximum Group Size")
        # ax.set_zlabel("Number of Pseudonodes")
        # plt.colorbar(sc)
        sorted_xy = sorted(zip(pseudonode_count, times), key=lambda pair: pair[0])  # Sort by x
        x_sorted, y_sorted = zip(*sorted_xy)

        plt.figure(figsize=(10, 6))
        plt.plot(x_sorted, y_sorted, marker='o', color='g')

        # Adding labels and title
        plt.title('Effect on Performance vs Pseudonode Count')
        plt.xlabel('Pseudonode Count')
        plt.ylabel('Time taken for Watermarking in seconds')
        plt.grid(True)
        plt.show()

        # ax2 = fig.add_subplot(122)
        # ax2.plot(pseudonode_count, times, marker='o', color='g')
        # ax2.set_xlabel('Pseudonode Count')
        # ax2.set_ylabel('Time taken for Watermarking')
        # ax2.set_title('Effect on Performance vs Pseudonode Count')
        # ax2.legend()

        # Show the plots
        # plt.tight_layout()
        plt.show()

    def perform_insertion_attack(self, node_type, ratios):
        """
        Perform insertion attack with varying real-to-fake ratios and time validation.
        """
        results = []
        for ratio in ratios:
            # Generate fake data for the specified ratio
            print(f"Testing insertion attack with ratio: {ratio}")
            fake_data_company = FakeDataCompany()
            self.fake_data[node_type] = fake_data_company.create_random_company_data_with_real(
                num_entries=len(self.wm_data_dict[node_type]),
                original_data=self.wm_data_dict[node_type],
                ratio=ratio
            )

            # Start the timer
            start_time = time.time()

            # Validate watermarks
            validate = Validate(
                data=self.fake_data[node_type], 
                node_type=node_type, 
                private_key=self.private_key
            )
            result = validate.validate_watermark(
                wm_id_dict=self.wm_secret[node_type], 
                watermark_cover_field=self.fields_dict[node_type][2]
            )

            # End the timer
            elapsed_time = time.time() - start_time

            # Store results
            results.append({
                "ratio": ratio,
                "validation_result": result,
                "time_taken": elapsed_time
            })

            print(f"Ratio: {ratio}, Validation Result: {'Success' if result else 'Failed'}, Time Taken: {elapsed_time:.4f} seconds")

        return results

    # def verify_insertion(self):
    #     """
    #     Verify watermark robustness under insertion attacks with varying ratios.
    #     """
    #     ratios = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    #     node_type = "Company"  # Adjust if needed for other node types

    #     results = self.perform_insertion_attack(node_type=node_type, ratios=ratios)

    #     # Display results in a readable format
    #     print("\nInsertion Attack Results:")
    #     for result in results:
    #         print(f"Ratio: {result['ratio']}, Validation: {result['validation_result']}, Time: {result['time_taken']:.4f}s")

    def verify_insertion(self):
        """
        Verify watermark robustness under insertion attacks with varying ratios and plot the results.
        """
        ratios = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        node_type = "Company"  # Adjust if needed for other node types

        results = self.perform_insertion_attack(node_type=node_type, ratios=ratios)

        # Extract data for plotting
        insertion_ratios = [result['ratio'] for result in results]
        validation_results = [1 if result['validation_result'] else 0 for result in results]
        times_taken = [result['time_taken'] for result in results]

        # Plotting the results
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot the validation results (success or failure)
        ax1.plot(insertion_ratios, validation_results, marker='o', color='b', label='Validation Result', linestyle='-', linewidth=2)
        ax1.set_xlabel('Real-to-Fake Ratio')
        ax1.set_ylabel('Validation Result (1: Success, 0: Failure)', color='b')
        ax1.set_title('Effect of Insertion Attack on Watermark Validation')
        ax1.tick_params(axis='y', labelcolor='b')

        # Creating a second y-axis to plot time taken
        ax2 = ax1.twinx()
        ax2.plot(insertion_ratios, times_taken, marker='x', color='r', label='Time Taken', linestyle='--', linewidth=2)
        ax2.set_ylabel('Time Taken (Seconds)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        # Adding grid, labels, and legend
        fig.tight_layout()
        ax1.grid(True)
        fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
        
        plt.show()

        # Display results in a readable format
        print("\nInsertion Attack Results:")
        for result in results:
            print(f"Ratio: {result['ratio']}, Validation: {result['validation_result']}, Time: {result['time_taken']:.4f}s")
    
    
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
        # self.verify_deletion()
        # self.verify_group_parameters()
        self.verify_insertion()

if __name__ == "__main__":    
    driver = Driver()    
    driver.execute()
