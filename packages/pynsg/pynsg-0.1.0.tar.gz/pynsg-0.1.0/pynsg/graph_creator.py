from argparse import ArgumentParser
import numpy as np
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


def read_fvecs(fname):
    """Load fvecs file into numpy array"""
    a = np.fromfile(fname, dtype=np.int32)
    if a.size == 0:
        raise FileNotFoundError(f"File {fname} is empty or not found")
    d = a[0]
    return a.reshape(-1, d + 1)[:, 1:].astype(np.float32)

def create_graph_file(filename: str, x, k, use_omp=True):
    if not HAS_FAISS:
        raise ImportError("faiss is required for HNSW graph generation")
    if use_omp:
        omp_threads = faiss.omp_get_max_threads()
        faiss.omp_set_num_threads(omp_threads)

    n, d = x.shape
    m = 32
    index = faiss.IndexHNSWFlat(d, m)
    index.hnsw.efConstruction = 200
    index.hnsw.efSearch = 128
    index.add(x)

    distances, neighbors = index.search(x, k + 1)

    for i in range(n):
        if neighbors[i, 0] != i:
            neighbors[i, -1] = i
    neighbors = neighbors[:, 1:]

    k = neighbors.shape[1]

    with open(filename, "wb") as f:
        f.write(np.uint32(k).tobytes())
        for i in range(n):
            f.write(np.uint32(i).tobytes())
            neighbors[i].astype(np.uint32).tofile(f)

def main():
	parser = ArgumentParser(
		prog='nnGraphMaker',
		description='Creates approximate nn graph using HNSW.',
	)
	parser.add_argument('-f', '--filename', required=True,
			help='Output filename for the graph.')
	parser.add_argument('-k', '--knn', type=int, required=True,
			help='Number of nearest neighbors to search for.')
	parser.add_argument('-i', '--input', required=True,
			help='Input vectors in fvecs file.')

	args = parser.parse_args()
	vecs = read_fvecs(args.input)
	create_graph_file(args.filename, vecs, args.knn)
if __name__ == '__main__':
   main() 
