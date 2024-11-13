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


dicts = [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25},
    {"name": "Alice", "age": 28},
    {"name": "Bob", "age": 22},
    {"name": "Charlie", "age": 35},
    {"name": "Dave", "age": 40},
    {"name": "Eve", "age": 29},
    {"name": "Frank", "age": 33},
    {"name": "Grace", "age": 24}
]

print(create_groups(dicts, create_groups_for_node({}, 1, 3, len(dicts))))
