#!/usr/bin/env python
# coding: utf-8

# In[1]:
import networkx as nx
from decorator import decorator
import os
import pandas as pd
from _pytest import warnings
from IPython.core.getipython import get_ipython

# get_ipython().run_line_magic('run', 'functions/cytoscapeFunctions')
# get_ipython().run_line_magic('run', 'functions/edgeFunctions')


# In[2]:


import numpy as np



# In[4]:


# random necessary functions

def create_random_state(random_state=None):
    """Returns a numpy.random.RandomState instance depending on input.
    Parameters
    ----------
    random_state : int or RandomState instance or None  optional (default=None)
        If int, return a numpy.random.RandomState instance set with seed=int.
        if numpy.random.RandomState instance, return it.
        if None or numpy.random, return the global random number generator used
        by numpy.random.
    """
    import numpy as np

    if random_state is None or random_state is np.random:
        return np.random.mtrand._rand
    if isinstance(random_state, np.random.RandomState):
        return random_state
    if isinstance(random_state, int):
        return np.random.RandomState(random_state)
    msg = (
        f"{random_state} cannot be used to generate a numpy.random.RandomState instance"
    )
    raise ValueError(msg)

def _process_params(G, center, dim):
    # Some boilerplate code.
    import numpy as np

    if not isinstance(G, nx.Graph):
        empty_graph = nx.Graph()
        empty_graph.add_nodes_from(G)
        G = empty_graph

    if center is None:
        center = np.zeros(dim)
    else:
        center = np.asarray(center)

    if len(center) != dim:
        msg = "length of center coordinates must match dimension of layout"
        raise ValueError(msg)

    return G, center

class PythonRandomInterface:
    def __init__(self, rng=None):
        try:
            import numpy as np
        except ImportError:
            msg = "numpy not found, only random.random available."
            warnings.warn(msg, ImportWarning)

        if rng is None:
            self._rng = np.random.mtrand._rand
        else:
            self._rng = rng

    def random(self):
        return self._rng.random_sample()

    def uniform(self, a, b):
        return a + (b - a) * self._rng.random_sample()

    def randrange(self, a, b=None):
        return self._rng.randint(a, b)

    def choice(self, seq):
        return seq[self._rng.randint(0, len(seq))]

    def gauss(self, mu, sigma):
        return self._rng.normal(mu, sigma)

    def shuffle(self, seq):
        return self._rng.shuffle(seq)

    #    Some methods don't match API for numpy RandomState.
    #    Commented out versions are not used by NetworkX

    def sample(self, seq, k):
        return self._rng.choice(list(seq), size=(k,), replace=False)

    def randint(self, a, b):
        return self._rng.randint(a, b + 1)

    #    exponential as expovariate with 1/argument,
    def expovariate(self, scale):
        return self._rng.exponential(1 / scale)

    #    pareto as paretovariate with 1/argument,
    def paretovariate(self, shape):
        return self._rng.pareto(shape)


#    weibull as weibullvariate multiplied by beta,
#    def weibullvariate(self, alpha, beta):
#        return self._rng.weibull(alpha) * beta
#
#    def triangular(self, low, high, mode):
#        return self._rng.triangular(low, mode, high)
#
#    def choices(self, seq, weights=None, cum_weights=None, k=1):
#        return self._rng.choice(seq

def random_state(random_state_index):
    """Decorator to generate a numpy.random.RandomState instance.
    Argument position `random_state_index` is processed by create_random_state.
    The result is a numpy.random.RandomState instance.
    Parameters
    ----------
    random_state_index : int
        Location of the random_state argument in args that is to be used to
        generate the numpy.random.RandomState instance. Even if the argument is
        a named positional argument (with a default value), you must specify
        its index as a positional argument.
    Returns
    -------
    _random_state : function
        Function whose random_state keyword argument is a RandomState instance.
    Examples
    --------
    Decorate functions like this::
       @np_random_state(0)
       def random_float(random_state=None):
           return random_state.rand()
       @np_random_state(1)
       def random_array(dims, random_state=1):
           return random_state.rand(*dims)
    See Also
    --------
    py_random_state
    """

    @decorator
    def _random_state(func, *args, **kwargs):
        # Parse the decorator arguments.
        try:
            random_state_arg = args[random_state_index]
        except TypeError as e:
            raise nx.NetworkXError("random_state_index must be an integer") from e
        except IndexError as e:
            raise nx.NetworkXError("random_state_index is incorrect") from e

        # Create a numpy.random.RandomState instance
        random_state = create_random_state(random_state_arg)

        # args is a tuple, so we must convert to list before modifying it.
        new_args = list(args)
        new_args[random_state_index] = random_state
        return func(*new_args, **kwargs)

    return _random_state

def rescale_layout(pos, scale=1):
    """Returns scaled position array to (-scale, scale) in all axes.
    The function acts on NumPy arrays which hold position information.
    Each position is one row of the array. The dimension of the space
    equals the number of columns. Each coordinate in one column.
    To rescale, the mean (center) is subtracted from each axis separately.
    Then all values are scaled so that the largest magnitude value
    from all axes equals `scale` (thus, the aspect ratio is preserved).
    The resulting NumPy Array is returned (order of rows unchanged).
    Parameters
    ----------
    pos : numpy array
        positions to be scaled. Each row is a position.
    scale : number (default: 1)
        The size of the resulting extent in all directions.
    Returns
    -------
    pos : numpy array
        scaled positions. Each row is a position.
    See Also
    --------
    rescale_layout_dict
    """
    # Find max length over all dimensions
    lim = 0  # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:, i] -= pos[:, i].mean()
        lim = max(abs(pos[:, i]).max(), lim)
    # rescale to (-scale, scale) in all directions, preserves aspect
    if lim > 0:
        for i in range(pos.shape[1]):
            pos[:, i] *= scale / lim
    return pos


# In[5]:


@random_state(10)
def fruchterman_reingold_layout_edit(
    G,
    k=None,
    pos=None,
    fixed=None,
    iterations=50,
    threshold=1e-4,
    weight="weight",
    scale=1,
    center=None,
    dim=2,
    seed=None,
    pretendIterations=None,
    stop = None
):
    """Position nodes using Fruchterman-Reingold force-directed algorithm.
    The algorithm simulates a force-directed representation of the network
    treating edges as springs holding nodes close, while treating nodes
    as repelling objects, sometimes called an anti-gravity force.
    Simulation continues until the positions are close to an equilibrium.
    There are some hard-coded values: minimal distance between
    nodes (0.01) and "temperature" of 0.1 to ensure nodes don't fly away.
    During the simulation, `k` helps determine the distance between nodes,
    though `scale` and `center` determine the size and place after
    rescaling occurs at the end of the simulation.
    Fixing some nodes doesn't allow them to move in the simulation.
    It also turns off the rescaling feature at the simulation's end.
    In addition, setting `scale` to `None` turns off rescaling.
    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.
    k : float (default=None)
        Optimal distance between nodes.  If None the distance is set to
        1/sqrt(n) where n is the number of nodes.  Increase this value
        to move nodes farther apart.
    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        random initial positions.
    fixed : list or None  optional (default=None)
        Nodes to keep fixed at initial position.
        ValueError raised if `fixed` specified and `pos` not.
    iterations : int  optional (default=50)
        Maximum number of iterations taken
    threshold: float optional (default = 1e-4)
        Threshold for relative error in node position changes.
        The iteration stops if the error is below this threshold.
    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  If None, then all edge weights are 1.
    scale : number or None (default: 1)
        Scale factor for positions. Not used unless `fixed is None`.
        If scale is None, no rescaling is performed.
    center : array-like or None
        Coordinate pair around which to center the layout.
        Not used unless `fixed is None`.
    dim : int
        Dimension of layout.
    seed : int, RandomState instance or None  optional (default=None)
        Set the random state for deterministic node layouts.
        If int, `seed` is the seed used by the random number generator,
        if numpy.random.RandomState instance, `seed` is the random
        number generator,
        if None, the random number generator is the RandomState instance used
        by numpy.random.
    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node
    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.spring_layout(G)
    # The same using longer but equivalent function name
    >>> pos = nx.fruchterman_reingold_layout(G)
    """
    import numpy as np

    G, center = _process_params(G, center, dim)
    
#     if pretendIterations is None:
#         pretendIterations = iterations
    
    if fixed is not None:
        if pos is None:
            raise ValueError("nodes are fixed without positions given")
        for node in fixed:
            if node not in pos:
                raise ValueError("nodes are fixed without positions given")
        nfixed = {node: i for i, node in enumerate(G)}
        fixed = np.asarray([nfixed[node] for node in fixed])

    if pos is not None:
        # Determine size of existing domain to adjust initial positions
        dom_size = max(coord for pos_tup in pos.values() for coord in pos_tup)
        if dom_size == 0:
            dom_size = 1
        pos_arr = seed.rand(len(G), dim) * dom_size + center

        for i, n in enumerate(G):
            if n in pos:
                pos_arr[i] = np.asarray(pos[n])
    else:
        pos_arr = None
        dom_size = 1

    if len(G) == 0:
        return {}
    if len(G) == 1:
        return {nx.utils.arbitrary_element(G.nodes()): center}

#     try:
#         # Sparse matrix
#         if len(G) < 500:  # sparse solver for large graphs
#             raise ValueError
#         A = nx.to_scipy_sparse_matrix(G, weight=weight, dtype="f")
#         if k is None and fixed is not None:
#             # We must adjust k by domain size for layouts not near 1x1
#             nnodes, _ = A.shape
#             k = dom_size / np.sqrt(nnodes)
#         pos = _sparse_fruchterman_reingold(
#             A, k, pos_arr, fixed, iterations, threshold, dim, seed
#         )
#     except ValueError:
    A = nx.to_numpy_array(G, weight=weight)
    if k is None and fixed is not None:
        # We must adjust k by domain size for layouts not near 1x1
        nnodes, _ = A.shape
        k = dom_size / np.sqrt(nnodes) 
#             what is k and dom_size
    pos = _fruchterman_reingold_edit(
        A, k, pos_arr, fixed, iterations, threshold, dim, seed, pretendIterations, stop
    )
    if fixed is None and scale is not None:
        pos = rescale_layout(pos, scale=scale) + center
    pos = dict(zip(G, pos))
    return pos


spring_layout = fruchterman_reingold_layout_edit


# In[6]:


@random_state(7)
def _fruchterman_reingold_edit(
    A, k=None, pos=None, fixed=None, iterations=50, threshold=1e-4, dim=2, seed=None, pretendIterations = None, stop = None
):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    import numpy as np

    try:
        nnodes, _ = A.shape
    except AttributeError as e:
        msg = "fruchterman_reingold() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg) from e
    
    if pretendIterations is None:
        pretendIterations = iterations
        
    if stop is None:
        stop = iterations
    
    if pos is None:
        # random initial positions
        pos = np.asarray(seed.rand(nnodes, dim), dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos = pos.astype(A.dtype)

    # optimal distance between nodes
    if k is None:
        k = np.sqrt(1.0 / nnodes)
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    # We need to calculate this in case our fixed positions force our domain
    # to be much bigger than 1x1
    if (iterations != 0):
        t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1])) * 0.1 * (float(pretendIterations)/iterations)
    # simple cooling scheme.
#     linearly step down by dt on each iteration so last iteration is size dt.
        dt = t / float(iterations + 1)
    delta = np.zeros((pos.shape[0], pos.shape[0], pos.shape[1]), dtype=A.dtype)
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(stop):
        # matrix of difference between points
        delta = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        # distance between points
        distance = np.linalg.norm(delta, axis=-1)
        # enforce minimum distance of 0.01
        np.clip(distance, 0.01, None, out=distance)
        # displacement "force"
        displacement = np.einsum(
            "ijk,ij->ik", delta, (k * k / distance ** 2 - A * distance / k)
        )
        # update positions
        length = np.linalg.norm(displacement, axis=-1)
        length = np.where(length < 0.01, 0.1, length)
        delta_pos = np.einsum("ij,i->ij", displacement, t / length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed] = 0.0
        pos += delta_pos
        # cool temperature
        t -= dt
        err = np.linalg.norm(delta_pos) / nnodes
        if err < threshold*(float(pretendIterations)/iterations):
            break
    return pos

