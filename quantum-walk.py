import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit.visualization import plot_histogram

script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'test_results/')

class BinomialTreeModel:
    def __init__(self, depth):
        self.depth = depth
        self.num_nodes = int((depth+1)*(depth+2)/2)
        self.position_qubits = depth
        self.graph = self._build_tree()

    def idx(self, i, j):
        return i*(i+1)//2 + j
    
    def _build_tree(self):
        G = nx.DiGraph()
        
        for i in range(self.depth):
            for j in range(i+1):
                curr_node = self.idx(i, j)
                down_node = self.idx(i+1, j)
                up_node = self.idx(i+1, j+1) 

                G.add_edge(curr_node, down_node)
                G.add_edge(curr_node, up_node)

        return G.to_undirected()
    
    def plot_binomial_tree(self, file_path=None):
        plt.figure(figsize=(12, 8))

        pos = {}
        for k in range(self.depth+1):
            for i in range(k+1):
                pos[self.idx(k,i)] = (i - k/2, -k)

        nx.draw(self.graph, pos, 
                node_color='lightblue',
                node_size=500,
                with_labels=True,
                font_size=8,
                font_weight='bold',
                arrows=False,
                edge_color='gray',
                width=2)
        
        plt.title(f'Binomial Tree (Depth={self.depth})\n'
                  f'Nodes={self.num_nodes}')
        plt.axis('off')
        plt.savefig(file_path, dpi=300, bbox_inches='tight')

    def decrement_gate(num_qubits):
        # Maps \ket{i} to \ket{i-1 mod N}
        qc = QuantumCircuit(num_qubits, name="Dec")
        qc.x(0)

        for i in range(num_qubits):
            for j in range(i):
                qc.x(j)
            qc.mcx(list(range(i)), i)
            for j in range(i):
                qc.x(j)
            qc.x(i)
                     
        return qc.to_gate()
    

    def quantum_walk_circuit(self, depth, steps, shots=1000):
        position_qubits = depth.bit_length()
    
        # Build circuit
        coin_register = QuantumRegister(1, 'coin')
        i_register = QuantumRegister(position_qubits, 'i')
        j_register = QuantumRegister(position_qubits, 'j')
        qc = QuantumCircuit(coin_register, i_register, j_register)

        # Initialize circuit
        value = depth
        for i in range(len(i_register)):
            if (value >> i) & 1:
                qc.x(i_register[i])
        qc.h(j_register)
        qc.barrier()

        # Perform quantum walk steps
        for step in range(steps):
            # Coin toss
            qc.h(coin_register)

            # Shift operator
            dec_i = self.decrement_gate(position_qubits)
            qc.append(dec_i, i_register)
            dec_j = self.decrement_gate(position_qubits)
            c_dec_j = dec_j.control(1)

            qc.append(c_dec_j, [coin_register[0]] + list(j_register))
            qc.barrier(label=f'step_{step}')

        if step%2==0:
            qc.h(coin_register)

        qc.measure_all()

        return qc
    
    def plot_results(qc, shots, title):
        simulator = AerSimulator()
        transpiled_qc = transpile(qc, simulator)
        results = simulator.run(transpiled_qc, shots=shots).result()
        counts = results.get_counts(transpiled_qc)

        return plot_histogram(counts, title=title)


class TrinomialTreeModel:
    def __init__(self, depth):
        self.depth = depth
        self.num_nodes = (depth+1)*(depth+1)
        self.position_qubits = depth
        self.graph = self._build_tree()

    def idx(self, i, j):
        return i*i + (j + i)
    
    def _build_tree(self):
        G = nx.DiGraph()
        for k in range(self.depth):
            for i in range(-k, k+1):
                curr_node = self.idx(k, i)
                down_node = self.idx(k+1, i-1)
                mid_node  = self.idx(k+1, i)
                up_node   = self.idx(k+1, i+1)

                G.add_edge(curr_node, down_node)
                G.add_edge(curr_node, mid_node)
                G.add_edge(curr_node, up_node)

        return G.to_undirected()
    
    def plot_trinomial_tree(self, file_path=None):
        plt.figure(figsize=(12, 8))
        
        pos = {}
        for k in range(self.depth+1):
            for i in range(-k, k+1):
                pos[self.idx(k, i)] = (i, -k)

        nx.draw(self.graph, pos, 
                node_color='lightblue',
                node_size=500,
                with_labels=True,
                font_size=8,
                font_weight='bold',
                arrows=False,
                edge_color='gray',
                width=2)
        
        plt.title(f'Binomial Tree (Depth={self.depth})\n'
                  f'Nodes={self.num_nodes}')
        plt.axis('off')
        plt.savefig(file_path, dpi=300, bbox_inches='tight')

    def quantum_walk_circuit(self):
        # TODO
        pass

if __name__ == "__main__":
    os.makedirs("test_results", exist_ok=True)

    print("Binomial Tree")
    binomial_walk = BinomialTreeModel(depth=6)
    print(f"Nodes: {binomial_walk.num_nodes}")
    binomial_walk.plot_binomial_tree(file_path=results_dir+'binomial_tree.png')
    
    print("Trinomial Tree")
    trinomial_walk = TrinomialTreeModel(depth=6)
    print(f"Nodes: {trinomial_walk.num_nodes}")
    trinomial_walk.plot_trinomial_tree(file_path=results_dir+'trinomial_tree_qiskit.png')
    