"""Topological Quantum Compiler - A universal compiler based on anyonic braiding."""

from tqc._version import __version__
from tqc.compiler import TopologicalCompiler
from tqc.anyons import AnyonType, FibonacciAnyons, IsingAnyons
from tqc.braids import BraidWord, BraidGenerator
from tqc.simulation import AnyonicSimulator
from tqc.optimization import BraidOptimizer

__all__ = [
    "__version__",
    "TopologicalCompiler",
    "AnyonType",
    "FibonacciAnyons", 
    "IsingAnyons",
    "BraidWord",
    "BraidGenerator",
    "AnyonicSimulator",
    "BraidOptimizer",
]


def get_supported_anyons() -> list[str]:
    """Get list of supported anyon types.
    
    Returns:
        List of anyon type names supported by TQC.
        
    Example:
        >>> from tqc import get_supported_anyons
        >>> anyons = get_supported_anyons()
        >>> print(anyons)
        ['fibonacci', 'ising', 'su2_k3']
    """
    return ["fibonacci", "ising", "su2_k3"]


def create_compiler(anyon_type: str = "fibonacci", **kwargs) -> TopologicalCompiler:
    """Create a topological compiler with specified anyon type.
    
    Args:
        anyon_type: Type of anyons to use ('fibonacci', 'ising', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Configured TopologicalCompiler instance
        
    Raises:
        ValueError: If anyon_type is not supported
        
    Example:
        >>> from tqc import create_compiler
        >>> compiler = create_compiler('fibonacci')
        >>> print(compiler.anyon_type.name)
        Fibonacci
    """
    from tqc.anyons import get_anyon_type
    
    if anyon_type not in get_supported_anyons():
        raise ValueError(f"Unsupported anyon type: {anyon_type}")
    
    anyon_instance = get_anyon_type(anyon_type)
    return TopologicalCompiler(anyon_type=anyon_instance, **kwargs)
