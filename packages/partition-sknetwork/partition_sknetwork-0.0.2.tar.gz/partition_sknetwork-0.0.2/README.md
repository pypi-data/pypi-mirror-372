# Graph Partition and Measures

Python code implementing 11 graph-aware measures (gam) for comparing graph partitions as well as a stable ensemble-based graph partition algorithm (ecg). This verion works with the sknetwork package. Versions for networkx and igraph are also available: partition-networkx, partition-igraph.

## Graph aware measures (gam)

The measures are respectively:
* 'rand': the RAND index
* 'jaccard': the Jaccard index
* 'mn': pairwise similarity normalized with the mean function
* 'gmn': pairwise similarity normalized with the geometric mean function
* 'min': pairwise similarity normalized with the minimum function
* 'max': pairwise similarity normalized with the maximum function

Each measure can be adjusted (recommended) or not, except for 'jaccard'.
Details can be found in: 

Valérie Poulin and François Théberge, "Comparing Graph Clusterings: Set Partition Measures vs. Graph-aware Measures",
    IEEE Transactions on Pattern Analysis and Machine Intelligence 43, 6 (2021) https://doi.org/10.1109/TPAMI.2020.3009862

## Ensemble clustering for graphs (ecg)

This is a good, stable graph partitioning algorithm. Details for ecg can be found in: 

Valérie Poulin and François Théberge, "Ensemble clustering for graphs: comparisons and applications", Appl Netw Sci 4, 51 (2019). 
    https://doi.org/10.1007/s41109-019-0162-z

# Example

We need to import the supplied Python file partition_sknetwork.

```pyhon
import sknetwork as sn
import partition_sknetwork as ps
```

Next, let's build a graph with communities.

```python
block_sizes = [100 for _ in range(10)]
g = sn.data.models.block_model(block_sizes, 0.1, 0.025, seed=42)

# Store the ground truth communities
labels = np.array([i for i,block_size in enumerate(block_sizes) for _ in range(block_size)])
```

Run Louvain and ecg:

```python
louvain = sn.clustering.Louvain(shuffle_nodes=True, random_state=42).fit_predict(g)
ecg = ps.ECG(random_state=42).fit_predict(g)
```

Finally, we show a few examples of measures we can compute with gam:

```python
print('Adjusted Graph-Aware Rand Index for Louvain:',ps.gam(g, labels, louvain))
print('Adjusted Graph-Aware Rand Index for ECG:',ps.gam(g, labels, ecg))
print('Jaccard Graph-Aware for Louvain:',ps.gam(g, labels, louvain, method="jaccard", adjusted=False))
print('Jaccard Graph-Aware for ECG:',ps.gam(g, labels, ecg, method="jaccard", adjusted=False))
```