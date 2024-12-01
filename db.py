from py2neo import Graph

# TODO: add database fetch query function


class DB:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.graph = None

    def connect(self):
        """Establish a connection to the Neo4j database."""
        self.graph = Graph(self.uri, auth=(self.user, self.password))

    def disconnect(self):
        """Disconnect from the Neo4j database."""
        self.graph = None

    def fetch_summary(self):
        """Fetch a summary of the database, including node and edge types."""
        if not self.graph:
            raise ConnectionError("Database is not connected. Call connect() first.")

        # Fetch node types and their counts
        node_types_query = """
        MATCH (n)
        RETURN labels(n) AS labels, COUNT(n) AS count
        ORDER BY count DESC
        """
        node_types = self.graph.run(node_types_query).data()

        # Fetch edge types and their counts
        edge_types_query = """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship_type, COUNT(r) AS count
        ORDER BY count DESC
        """
        edge_types = self.graph.run(edge_types_query).data()

        # Prepare summary
        summary = {
            "node_types": node_types,
            "edge_types": edge_types
        }
        return summary

    def query_nodes(self, node_type):
        """Query all nodes of a specific type (label)."""
        if not self.graph:
            raise ConnectionError("Database is not connected. Call connect() first.")

        query = f"""
        MATCH (n:{node_type})
        RETURN n
        """
        results = self.graph.run(query).data()
        return results

    def print_summary(self):
        try:
            summary = self.fetch_summary()

            # Print summary
            print("Database Summary:")
            print("\nNode Types:")
            for node in summary["node_types"]:
                print(f"Labels: {node['labels']}, Count: {node['count']}")

            print("\nEdge Types:")
            for edge in summary["edge_types"]:
                print(f"Relationship Type: {edge['relationship_type']}, Count: {edge['count']}")

        except Exception as e:
            print(f"An error occurred: {e}")
