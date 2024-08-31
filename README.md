# Distributed K-Means Clustering

This project implements a distributed K-Means clustering algorithm using the MapReduce framework. The system is built using Python and gRPC for communication between the master, mappers, and reducers.

## Components

### `master.py`
The master node coordinates the MapReduce process. It initializes the centroids, assigns tasks to mappers, and collects results from reducers.

Methods:
  - `start()`: Starts the MapReduce process.
  - `Map()`: Sends map requests to mappers.
  - `Reduce()`: Sends reduce requests to reducers.

### `mapper.py`
The mapper node processes a subset of data points, calculates the nearest centroid for each point, and partitions the results.

Methods:
  - `Map()`: Processes data points and calculates nearest centroids.
  - `partition()`: Partitions the output into smaller files.
  - `GetEntries()`: Retrieves partitioned entries for reducers.

### `reducer.py`
The reducer node collects and processes partitioned data from mappers, updates centroids, and writes the results

Methods:
  - `Reduce()`: Processes partitioned data and updates centroids.
  - `shuffle_and_sort()`: Collects and sorts data from mappers.
  - `reduce()`: Calculates updated centroids.

### `mapReduce.proto`
The protocol buffer file defines the gRPC service and message types for communication between the master, mappers, and reducers.


## Running the Project

### Prerequisites
- Python 3.x
- gRPC tools for Python

### Setup

```sh
# Install the required Python packages
pip install grpcio grpcio-tools numpy matplotlib

# Generate the gRPC code from the protobuf file:
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. mapReduce.proto
```


### Execution

```sh
# Start the master, mappers, and reducers
make
```

### Configuration
- Number of Iterations: N
- Number of Mappers: M
- Number of Reducers: R
- Number of Centroids: K

These parameters can be configured in the master.py file.

### Output
- **Centroids**: Final centroids are written to `centroids.txt`
- **Logs**: Execution logs are written to `dump.txt`
- **Partitions**: Intermediate partitions are stored in the `Mappers/` and `Reducers/` directories

### Notes
- Ensure that mappers and reducers run in parallel.
- The master node should not send the actual data points to mappers to avoid unnecessary network traffic.
- For more details on the implementation, refer to the comments in the source code and the todo.txt file.