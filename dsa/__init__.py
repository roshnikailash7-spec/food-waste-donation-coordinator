"""
Data Structures and Algorithms (DSA) Package
Custom from-scratch implementations for Food Waste Reduction and Donation Coordinator.
No built-in priority queues (heapq), deques, or built-in sort/bisect are used.
"""

from .min_heap import MinHeap
from .hash_table import HashTable
from .linked_list import SinglyLinkedList
from .queue import Queue
from .stack import Stack
from .graph import Graph
from .merge_sort import merge_sort
from .binary_search import (
    binary_search_exact,
    binary_search_range,
    binary_search_closest
)

__all__ = [
    "MinHeap",
    "HashTable",
    "SinglyLinkedList",
    "Queue",
    "Stack",
    "Graph",
    "merge_sort",
    "binary_search_exact",
    "binary_search_range",
    "binary_search_closest",
]
