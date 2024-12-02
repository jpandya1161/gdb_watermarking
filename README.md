# Graph Database Watermarking with Pseudo-Nodes

![Python](https://img.shields.io/badge/python-3.12-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-Database-green)


## Overview

This project implements a novel watermarking technique for graph databases, embedding ownership indicators within the graph structure using pseudo-nodes. The method ensures data integrity and provenance without compromising database performance. It is resilient to ownership attacks and provides an efficient way of verifying data authenticity through watermark extraction.

The system utilizes Neo4j for graph database management and is implemented in Python 3.12. The process involves creating a fake graph that mimics the original, and using a private key to match embedded pseudo-nodes, proving the authenticity of the data.

## Features

- **Pseudo-Node Watermarking**: Embeds ownership markers into the graph structure using pseudo-nodes, maintaining operational integrity.
- **Attack Resilience**: Protects against ownership attacks such as guessing and deletion attacks.
- **Efficient Watermark Extraction**: Verifies data ownership by matching pseudo-nodes with a private key, without compromising performance.
- **Graph Database Verification**: Uses Neo4j as the graph database for storing and querying data.

## Requirements

- Python 3.12 or higher
- Neo4j
- Libraries:
  - `py2neo`
  - `pandas`
  - `hashlib`

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/graph-watermarking.git
cd graph-watermarking
```

## Install dependencies
```bash
pip install -r requirements.txt
```
OR
```bash
python3.12 -m pipenv shell
pip install -r requirements.txt
```

## Set up Neo4j

1. **Download and Install Neo4j**  
   - Download Neo4j from its [official website](https://neo4j.com/download/).  
   - Follow the installation instructions for your operating system.  

2. **Install Plugins**  
   - Install the APOC plugin for advanced procedures.  
   - Enable the plugin by adding the following lines to the `neo4j.conf` file:  
     ```plaintext
     dbms.security.procedures.unrestricted=apoc.*
     dbms.security.procedures.allowlist=apoc.*
     ```

3. **Set Up the Database**  
   - Start the Neo4j database server.  
   - Access the Neo4j browser at `http://localhost:7474`.  
   - Set up the database credentials (default username: `neo4j`). Update the password as prompted.  

4. **Using Py2neo for Queries**  
   - Install Py2neo using the following command:  
     ```bash
     pip install py2neo
     ```
   - Update the connection details in your Python scripts to match your Neo4j database credentials.  
   - Example connection code:  
     ```python
     from py2neo import Graph
     graph = Graph("neo4j://localhost:7687", auth=("<Your Username>", "<Your Password>"))

     ```

## Import Dataset:

Please download the [UKCompanies dataset](https://neo4j.com/graphgists/35a813ba-ea10-4165-9065-84f8802cbae8/) and import in Neo4j by following the import instructions in the same link.

## Usage

One the dataset import has been verified, please run the following script in the virtual environment:

```bash
python3 driver.py
```

1. The script will first print the database summary and information useful for schema analysis in this project.
2. The script will first prompt you to select the node types. Please select type "all" to watermark all node types.
3. Then you will be prompted to choose the minimum group size and maximum group size for pseudo node generation.
4. Now, for all node types, you must select the required and optional fields for the pseudo nodes. Remember, the required fields must be numerical. Optional fields can be numerical.
5. After this, the program will watermark the pseudo nodes and insert them back into the original data. The script will print the Watermark Secret: Private Key K and the watermarked node IDs along with the hashed secret.
6. Then you will be asked to generate the number of total nodes in suspected fake data.
7. You will prompted for real-to-fake data ratio between 0 and 1. Here, the real data has the watermarked nodes.
8. After this, the watermark validation script will run to search for watermarks in the suspected data.

## Evaluation

![Fig. 1: Embedding Performance](images%2Fdb_wm_embedding_time.png)
*Fig. 1: Embedding Performance*


![Fig. 2: Pseudo Node Group Parameters](images%2Fdb_wm_group_params.png)
*Fig. 2: Pseudo Node Group Parameters*


![Fig. 3: Simulating Deletion Attack](images%2Fdb_wm_deletion.png)
*Fig. 3: Simulating Deletion Attack*


![Fig. 4: Simulating Insertion Attack](images%2Fdb_wm_insertion_attack.png)
*Fig. 4: Simulating Insertion Attack*

