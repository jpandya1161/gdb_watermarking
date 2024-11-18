# every node-type is analogous to a collection
# for every node type, create groups using min_len, max_len, total_collection_nodes
# group of documents
# manual analysis of the groups - select some fields from the documents
# borrow selected fields from the group of nodes to create pseudo nodes
# Company - companyNumber is the key, other attributes may or may not exist
# Person - everything seems to be a key
# Recipient - name and entityType
# Property - titleNumber
from py2neo import Graph
import random
import pandas as pd
from pandas import json_normalize
import hashlib

# Connect to the graph database (replace with your connection details)
# graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
# def get_all_nodes():
#     # Define a Cypher query to get all nodes with the label 'PERSON' and their properties
#     query = """
#     MATCH (n)
#     RETURN properties(n) AS properties
#     """
#
#     # Run the query and convert the results to a list of dictionaries
#     nodes = []
#     for record in graph.run(query):
#         person = {
#             "properties": dict(record["properties"])  # Node properties as a dictionary
#         }
#         nodes.append(person)
#
#     # `persons` will contain a list of dictionaries with each PERSON node's properties
#     return nodes

def create_groups_for_node(nodes_dict, min_length, max_length, total_length):
    groups = []
    remaining_records = total_length
    # print("HI")
    while groups == []:
        # print("HI")
        remaining_records = total_length
        while remaining_records > 0:
            # Set the max possible group size as the minimum of max_length or remaining_records
            max_possible_size = min(max_length, remaining_records)

            # print(min_length, max_possible_size)

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
                # else:
            #     return []  # Not possible to meet requirements

    return groups

def create_groups(dicts, group_sizes):
    grouped_dicts = []
    index = 0

    for size in group_sizes:
        group = dicts[index:index + size]  # Create a group of size 'size'
        grouped_dicts.append(group)
        index += size  # Move the index forward by 'size' for the next group

    return grouped_dicts

def create_pseudo_node(node_type, type_dicts_df, required_fields, optional_fields):
    pseudo_node = {}
    # pseudo_node = {"labels": node_type}
    # dicts_df = json_normalize(dicts, sep='_')
    # type_dicts_df = dicts_df[dicts_df['labels'] == node_type] # change the key as per the query

    for required_field in required_fields:
        req_fields_list = type_dicts_df[type_dicts_df[required_field].notna()][required_field].unique().tolist()
        req_field_val = random.choice(req_fields_list)
        pseudo_node[required_field] = req_field_val

    # search for all distinct values of the required fields and choose one for the pseudo-node

    # randomly decide on which optional fields to choose, search for all distinct values for each of the optional fields and then choose one
    opt_fields_num = random.randint(1, len(optional_fields))

    # Randomly choose the selected number of elements from the list (without duplicates)
    random_opt_fields = random.sample(optional_fields, opt_fields_num)

    for optional_field in random_opt_fields:
        opt_fields_list = type_dicts_df[type_dicts_df[optional_field].notna()][optional_field].unique().tolist()
        opt_field_val = random.choice(opt_fields_list)
        pseudo_node[optional_field] = opt_field_val

    return pseudo_node


dicts = [
    {"name": "John", "age": 30, "city": "New York", "occupation": "Engineer", "salary": 85000, "married": True},
    {"name": "Jane", "age": 25, "city": "Chicago", "occupation": "Designer", "hobby": "Photography"},
    {"name": "Alice", "age": 28, "city": "San Francisco", "salary": 92000, "married": False},
    {"name": "Bob", "age": 22, "occupation": "Student", "hobby": "Gaming"},
    {"name": "Charlie", "age": 35, "city": "Austin", "occupation": "Manager", "salary": 105000},
    {"name": "Dave", "age": 40, "city": "Boston", "occupation": "Consultant", "salary": 120000, "married": True, "hobby": "Golf"},
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
    {"name": "Rachel", "age": 30, "city": "Nashville", "occupation": "Event Planner", "married": True, "hobby": "Dancing"}
]

min_group_length = 1
max_group_length = 5
node_type = "PERSON"

group_sizes = create_groups_for_node(dicts, min_group_length, max_group_length, len(dicts))
groups = create_groups(dicts, group_sizes)
# print(groups)
list_dict = {f"{i}": sublist for i, sublist in enumerate(groups)}
print(list_dict)

group_wise_pseudo_nodes = {}
dicts_df = pd.DataFrame(dicts)
# required_fields and optional_fields are to be decided after the manual analysis

# after creating groups, create pseudo node for every group of every node type
for key, _ in list_dict.items():
    pseudo_node = create_pseudo_node(node_type, dicts_df, required_fields=["name", "age"], optional_fields=["occupation", "city", "married", "hobby"])
    group_wise_pseudo_nodes[key] = pseudo_node

print(group_wise_pseudo_nodes)

private_key = "e8d3cba12a8d4c3b9a12f4e7c5d1a8f2"
print(len(private_key))

# Watermarking:
# need private key, identity, field to be watermarked, fields used while watermarking

def watermark_pseudo_node(pseudo_node, private_key, watermark_identity, wm_attribute, attributes, max_num_fields):
    # wm_attribute is a numerical field of a pseudo-node
    # attributes is a list of all the attributes of the pseudo-node
    # watermark_identity = ?
    watermark_secret = watermark_identity + "".join(attributes) + private_key
    hashed_secret = hashlib.sha256(watermark_secret.encode("utf-8")).digest()
    hashed_secret_int = int.from_bytes(hashed_secret, byteorder="big") % max_num_fields
    pseudo_node[wm_attribute] = hashed_secret_int

    return pseudo_node


