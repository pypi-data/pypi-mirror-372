from multiprocessing import Pool
from typing import Callable, Iterable, List, Optional, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def parallel_map(
    func: Callable[[T], R],
    items: Iterable[T],
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
) -> List[R]:
    """
    Performs parallel mapping of a function over an iterable using multiple processes.

    Args:
        func: The function to apply to each item
        items: Iterable of items to process
        num_workers: Number of worker processes (defaults to number of CPU cores)
        chunk_size: Size of chunks to send to each worker (defaults to len(items)/num_workers)

    Returns:
        List of results in the same order as the input items

    Example:
        >>> def square(x): return x * x
        >>> parallel_map(square, range(10))
        [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    """
    with Pool(processes=num_workers) as pool:
        results = pool.map(func, items, chunksize=chunk_size)
    return list(results)
