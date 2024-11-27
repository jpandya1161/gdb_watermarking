# every node-type is analogous to a collection
# for every node type, create groups using min_len, max_len, total_collection_nodes
# group of documents
# manual analysis of the groups - select some fields from the documents
# borrow selected fields from the group of nodes to create pseudo nodes
# Company - companyNumber is the key, other attributes may or may not exist
# Person - everything seems to be a key
# Recipient - name and entityType
# Property - titleNumber
import random
import pandas as pd
import hashlib
from itertools import chain


class Embed:
    def __init__(self, data, node_type, private_key="e8d3cba12a8d4c3b9a12f4e7c5d1a8f2", max_num_fields=1000):
        """

        :param data: A list of dictionaries containing the original data of a given node type
        """
        self.data = data
        self.data_df = pd.DataFrame(data)
        self.node_type = node_type
        self.private_key = private_key
        self.max_num_fields = max_num_fields
        self.watermarked_nodes_dict = {}
        self.watermarked_data = []

    def generate_group_partitions(self, min_length, max_length, total_length):
        groups = []

        while groups == []:
            remaining_records = total_length
            while remaining_records > 0:
                # Set the max possible group size as the minimum of max_length or remaining_records
                max_possible_size = min(max_length, remaining_records)

                try:

                    # Randomly choose a group size between min_length and max_possible_size
                    group_size = random.randint(min_length, max_possible_size)

                except ValueError:
                    break

                # Append the group size and reduce the remaining records
                groups.append(group_size)
                remaining_records -= group_size

                # Check if the remaining records would violate the constraints if left as a single group
                if remaining_records < min_length and remaining_records > 0:
                    # Adjust the last group to absorb the remainder if possible
                    if groups[-1] + remaining_records <= max_length:
                        groups[-1] += remaining_records
                        remaining_records = 0

        return groups

    def generate_groups(self, group_partitions):
        grouped_dicts = []
        index = 0

        for size in group_partitions:
            group = self.data[index:index + size]  # Create a group of size 'size'
            grouped_dicts.append(group)
            index += size  # Move the index forward by 'size' for the next group

        return grouped_dicts

    def generate_pseudo_node(self, required_fields, optional_fields):
        pseudo_node = {}
        # TODO: check if the node type information is present in the node
        # pseudo_node = {"labels": self.node_type}
        # dicts_df = json_normalize(dicts, sep='_')
        # type_dicts_df = dicts_df[dicts_df['labels'] == self.node_type] # change the key as per the query

        for required_field in required_fields:
            req_fields_list = self.data_df[self.data_df[required_field].notna()][required_field].unique().tolist()
            req_field_val = random.choice(req_fields_list)
            pseudo_node[required_field] = req_field_val

        # search for all distinct values of the required fields and choose one for the pseudo-node

        # randomly decide on which optional fields to choose, search for all distinct values for each of the optional fields and then choose one
        opt_fields_num = random.randint(0, len(optional_fields))

        # Randomly choose the selected number of elements from the list (without duplicates)
        random_opt_fields = random.sample(optional_fields, opt_fields_num)

        for optional_field in random_opt_fields:
            opt_fields_list = self.data_df[self.data_df[optional_field].notna()][optional_field].unique().tolist()
            opt_field_val = random.choice(opt_fields_list)
            pseudo_node[optional_field] = opt_field_val

        return pseudo_node

    def watermark_pseudo_node(self, pseudo_node, watermark_identity, watermark_id_field, attributes):
        # wm_attribute is a numerical field of a pseudo-node
        # attributes is a list of all the attributes of the pseudo-node
        # watermark_identity = ?
        watermark_secret = watermark_identity + "".join(attributes) + self.private_key
        hashed_secret = hashlib.sha256(watermark_secret.encode("utf-8")).digest()
        hashed_secret_int = int.from_bytes(hashed_secret, byteorder="big") % self.max_num_fields
        # pseudo_node["hashed_secret"] = hashed_secret_int
        pseudo_node[watermark_id_field] = watermark_identity

        return pseudo_node, hashed_secret_int

    def insert_pseudo_nodes(self, group_wise_pseudo_nodes, groups_dict):
        upper_limit = n = len(group_wise_pseudo_nodes)
        lower_limit = 1

        # Generate n unique random numbers
        watermark_id_list = random.sample(range(lower_limit, upper_limit + 1), n)

        # print("Unique random numbers:", unique_random_numbers)

        # Initialize an empty list to store the watermarked pseudo nodes
        watermarked_pseudo_nodes = []

        # Initialize a dictionary to store the mapping of unique random numbers to hashed watermarked values
        # id_list = {}

        # Iterate through the pseudo nodes, apply watermarking, and store mappings
        for i, node in enumerate(group_wise_pseudo_nodes):
            # Generate the watermarked node
            watermarked_node, hashed_secret_int = self.watermark_pseudo_node(
                group_wise_pseudo_nodes[node],
                str(watermark_id_list[i]),
                "company_id",
                [str(group_wise_pseudo_nodes[node]["age"])]
            )
            # Append the watermarked node to the list
            watermarked_pseudo_nodes.append(watermarked_node)

            # Map the unique random number to its corresponding watermarked value (hashed)
            self.watermarked_nodes_dict[watermark_id_list[i]] = hashed_secret_int  # Assuming `watermarked_node` is hashed

        # Print the resulting id_list
        # print("ID List:")
        # for key, value in self.watermarked_nodes_dict.items():
        #     print(f"Unique Random Number: {key}, Hashed Watermarked Value: {value}")

        # Append watermarked pseudo nodes to their respective groups in list_dict
        for key, group in groups_dict.items():
            # Retrieve the corresponding watermarked pseudo node
            watermarked_node = watermarked_pseudo_nodes[int(key)]

            # Add the watermarked node to the group
            group.append(watermarked_node)

        # Print the updated list_dict
        print("Updated list_dict with watermarked pseudo nodes:")
        for group_key, group_value in groups_dict.items():
            print(f"Group {group_key}: {group_value}")

        # Flatten the list using itertools.chain
        self.watermarked_data = list(chain(*groups_dict.values()))


    def embed(self, required_fields=("birthMonth", "birthYear"), optional_fields=("nationality", )):
        self.watermarked_nodes_dict = {}
        self.watermarked_data = []

        min_group_length = 1
        max_group_length = 5
        # node_type = "PERSON"

        group_partitions = self.generate_group_partitions(min_group_length, max_group_length, len(dicts))
        groups = self.generate_groups(group_partitions)
        # print(groups)
        groups_dict = {f"{i}": sublist for i, sublist in enumerate(groups)}
        print(groups_dict)

        group_wise_pseudo_nodes = {}
        # dicts_df = pd.DataFrame(dicts)
        # required_fields and optional_fields are to be decided after the manual analysis

        # after creating groups, create pseudo node for every group of every node type
        for key, _ in groups_dict.items():
            pseudo_node = self.generate_pseudo_node(required_fields=required_fields,
                                                    optional_fields=optional_fields)
            group_wise_pseudo_nodes[key] = pseudo_node

        print(group_wise_pseudo_nodes)

        self.insert_pseudo_nodes(group_wise_pseudo_nodes, groups_dict)


if __name__ == "__main__":
    dicts = [
        {"name": "John", "age": 30, "city": "New York", "occupation": "Engineer", "salary": 85000, "married": True},
        {"name": "Jane", "age": 25, "city": "Chicago", "occupation": "Designer", "hobby": "Photography"},
        {"name": "Alice", "age": 28, "city": "San Francisco", "salary": 92000, "married": False},
        {"name": "Bob", "age": 22, "occupation": "Student", "hobby": "Gaming"},
        {"name": "Charlie", "age": 35, "city": "Austin", "occupation": "Manager", "salary": 105000},
        {"name": "Dave", "age": 40, "city": "Boston", "occupation": "Consultant", "salary": 120000, "married": True,
         "hobby": "Golf"},
        {"name": "Eve", "age": 29, "occupation": "Artist", "hobby": "Painting"},
        {"name": "Frank", "age": 33, "city": "Seattle", "salary": 98000, "married": False},
        {"name": "Grace", "age": 24, "city": "Denver", "occupation": "Researcher", "married": True},
        {"name": "Hannah", "age": 31, "city": "Miami", "occupation": "Chef", "salary": 60000, "hobby": "Traveling"},
        {"name": "Ian", "age": 27, "city": "Dallas", "occupation": "Photographer", "salary": 45000},
        {"name": "Jill", "age": 26, "city": "Portland", "occupation": "Nurse", "married": False, "hobby": "Reading"},
        {"name": "Kyle", "age": 29, "city": "Los Angeles", "occupation": "Software Developer", "salary": 95000},
        {"name": "Laura", "age": 34, "city": "Houston", "occupation": "Analyst", "salary": 83000, "married": True},
        {"name": "Mark", "age": 36, "city": "Phoenix", "occupation": "Teacher", "hobby": "Cooking"},
        {"name": "Nina", "age": 23, "city": "Philadelphia", "salary": 72000, "married": False},
        {"name": "Oscar", "age": 32, "city": "San Diego", "occupation": "Architect", "salary": 88000, "married": True},
        {"name": "Paula", "age": 37, "city": "Atlanta", "occupation": "Lawyer", "salary": 140000, "hobby": "Hiking"},
        {"name": "Quinn", "age": 28, "city": "Orlando", "occupation": "Musician", "hobby": "Writing"},
        {"name": "Rachel", "age": 30, "city": "Nashville", "occupation": "Event Planner", "married": True,
         "hobby": "Dancing"}
    ]
    embed = Embed(data=dicts, node_type="PERSON")
    embed.embed(required_fields=["name", "age"], optional_fields=["city", "occupation"])
    print(embed.watermarked_data)


