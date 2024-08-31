import grpc
import mapReduce_pb2
import mapReduce_pb2_grpc
import random
import numpy as np
from concurrent import futures
import matplotlib.pyplot as plt
import threading
import time

# random.seed(0)
def custom_print(*args, **kwargs):
    try:
        # Convert all arguments to strings
        printed_data = ' '.join(map(str, args))

        # Print to console using built-in print function
        built_in_print(*args, **kwargs)

        # Write to file
        with open('dump.txt', 'a') as file:
            file.write(printed_data + '\n')
    except Exception as e:
        # In case of any error, print the exception message to console using built-in print function
        built_in_print(f"Error occurred while printing: {e}")

# Replace the built-in print function with the custom one
built_in_print = print
print = custom_print

N = 10  # number of iterations
M = 5   # number of mappers
R = 3   # number of reducers
K = 2   # number of centroids
mapper_nodes = [f'localhost:5005{i}' for i in range(M)]
reducer_nodes = [f'localhost:5006{i}' for i in range(R)]

mapper_response = {}
reducer_response = {}

class Master(mapReduce_pb2_grpc.MapReduceServicer):
    centroids= []
    mapper_stubs = []
    reducer_stubs = []

    def __init__(self):
        # setup grpc clients
        for i in range(M):
            channel = grpc.insecure_channel(mapper_nodes[i])
            stub = mapReduce_pb2_grpc.MapReduceStub(channel)
            self.mapper_stubs.append(stub)
            
        for i in range(R):
            channel = grpc.insecure_channel(reducer_nodes[i])
            stub = mapReduce_pb2_grpc.MapReduceStub(channel)
            self.reducer_stubs.append(stub)       

        # initialize centroids
        with open('points.txt', 'r') as f:
            points = f.readlines()
            points = [point.strip() for point in points]
            points = [eval(point) for point in points]
        self.centroids = random.sample(points, K) 
        self.response_lock = threading.Lock()
        

    def send_map_request(self, i, tasks):
        request = mapReduce_pb2.MapRequest(
            id=i,
            start=tasks[i],
            end=tasks[i+1],
            centroids=str(self.centroids),
            r=R
        )

        try:
            response = self.mapper_stubs[i].Map(request)
            with self.response_lock:
                mapper_response[i] = response
            if response.success:
                print(f"Mapper {i} finished successfully")
            else:
                print(f"Mapper {i} failed, retrying")
                time.sleep(1)                
                self.send_map_request(i, tasks)
        except grpc.RpcError as e:
            print(f"Error sending Map request to Mapper {i}: {e}")
            time.sleep(1)
            self.send_map_request(i, tasks)

    def send_reduce_request(self, i, mapper_nodes):
        request = mapReduce_pb2.ReduceRequest(
            id=i,
            mapper_nodes=str(mapper_nodes),
        )

        try:
            response = self.reducer_stubs[i].Reduce(request)
            with self.response_lock:
                reducer_response[i] = response
            if response.success:
                print(f"Reducer {i} finished successfully")
            else:
                print(f"Reducer {i} failed, retrying")
                time.sleep(1)
                self.send_reduce_request(i, mapper_nodes)
        except grpc.RpcError as e:
            print(f"Error sending Reduce request to Reducer {i}: {e}")
            time.sleep(1)
            self.send_reduce_request(i, mapper_nodes)
        # time.sleep(1)

    def Map(self, request, context):
        print("\nSending Map request to mappers")

        with open('points.txt', 'r') as f:
            points = f.readlines()
        num_lines = len(points)
        tasks = [i for i in range(0, num_lines+1, num_lines // M)]
        if tasks[-1] != num_lines:
            tasks[-1] = num_lines
        print(tasks)

        threads = []
        for i in range(M):
            thread = threading.Thread(target=self.send_map_request, args=(i, tasks))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def Reduce(self, request, context):
        print("\nSending Reduce request to reducers")

        received_centroids = []

        threads = []
        for i in range(R):
            thread = threading.Thread(target=self.send_reduce_request, args=(i, mapper_nodes))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        with self.response_lock:
            for i in range(R):
                if i in reducer_response:
                    response = reducer_response[i]
                    received_centroids.extend(eval(response.centroids))

        print(f"\nReceived centroids: ", *received_centroids, sep='\n')
        
        updated_centroids = []
        for i in range(K):
            values = [received_centroid[1] for received_centroid in received_centroids if received_centroid[0] == self.centroids[i]]
            updated_centroid = tuple(np.mean(values, axis=0))
            updated_centroids.append(updated_centroid)

        print(f"\nUpdated centroids: ", *updated_centroids, sep='\n')

        if self.centroids == updated_centroids:
            return True
        else:
            self.centroids = updated_centroids
            return False

    def start(self):
        print("Starting Master node")

        for i in range(N):
            print(f"\n\nIteration {i}")
            print(f"Centroids: ", *self.centroids, sep='\n')
            self.Map(None, None)
            # Wait for all mappers to finish
            while len(mapper_response) < M:
                time.sleep(1)
            isConverged = self.Reduce(None, None)
            if isConverged:
                print("\nConverged")
                break
            
        # write the final centroids to a file
        with open('centroids.txt', 'w') as f:
            for centroid in self.centroids:
                f.write(f"{centroid[0]},{centroid[1]}\n")
                
        print("Finished Master node")

        # plot the data points and centroids
        with open('points.txt', 'r') as f:
            points = f.readlines()
            points = [point.strip() for point in points]
            points = [eval(point) for point in points]
            points = np.array(points)
        centroids = np.array(self.centroids)
        plt.scatter(points[:, 0], points[:, 1], c='blue')
        plt.scatter(centroids[:, 0], centroids[:, 1], c='red')
        plt.show()

if __name__ == '__main__':
    N = int(input("Enter the maximum number of iterations: "))
    M = int(input("Enter the number of mappers: "))
    R = int(input("Enter the number of reducers: "))
    K = int(input("Enter the number of centroids: "))

    master = Master()
    master.start()