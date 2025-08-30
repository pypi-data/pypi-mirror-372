"""Core anyonic types and their algebraic structures."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FusionChannel(Enum):
    """Enumeration of possible fusion channels."""
    IDENTITY = "I"
    FIBONACCI = "τ"  # tau
    PSI = "ψ"
    SIGMA = "σ"


@dataclass(frozen=True)
class FusionRule:
    """Represents a fusion rule between anyons.
    
    Attributes:
        left: First anyon in fusion
        right: Second anyon in fusion  
        result: Possible fusion outcomes with coefficients
    """
    left: str
    right: str
    result: Dict[str, complex]
    
    def __post_init__(self) -> None:
        """Validate fusion rule after initialization."""
        if not self.result:
            raise ValueError("Fusion rule must have at least one outcome")
        
        # Check that coefficients sum to reasonable value (accounting for normalization)
        total = sum(abs(coeff)**2 for coeff in self.result.values())
        if abs(total) < 1e-10:
            raise ValueError("Fusion rule coefficients cannot all be zero")


class AnyonType(ABC):
    """Abstract base class for anyon types and their algebraic properties."""
    
    def __init__(self, name: str, quantum_dimension: float) -> None:
        """Initialize anyon type.
        
        Args:
            name: Human-readable name of the anyon type
            quantum_dimension: Quantum dimension of the anyon
            
        Raises:
            ValueError: If quantum dimension is not positive
        """
        if quantum_dimension <= 0:
            raise ValueError("Quantum dimension must be positive")
            
        self.name = name
        self.quantum_dimension = quantum_dimension
        self._fusion_rules: Dict[Tuple[str, str], FusionRule] = {}
        self._f_matrices: Dict[Tuple[str, str, str, str], np.ndarray] = {}
        self._r_matrices: Dict[Tuple[str, str], complex] = {}
        
        logger.info(f"Initialized {name} anyon type with dimension {quantum_dimension}")
    
    @abstractmethod
    def get_labels(self) -> List[str]:
        """Get all anyon labels for this type.
        
        Returns:
            List of string labels identifying each anyon species
        """
        pass
    
    @abstractmethod
    def fusion_rules(self, a: str, b: str) -> Dict[str, complex]:
        """Get fusion outcomes for two anyons.
        
        Args:
            a: First anyon label
            b: Second anyon label
            
        Returns:
            Dictionary mapping outcome labels to fusion coefficients
            
        Raises:
            ValueError: If anyon labels are invalid
        """
        pass
    
    @abstractmethod  
    def f_matrix(self, a: str, b: str, c: str, d: str) -> np.ndarray:
        """Get F-matrix for pentagon equation.
        
        The F-matrix relates different ways of associating triple fusion:
        (a ⊗ b) ⊗ c ≅ a ⊗ (b ⊗ c)
        
        Args:
            a, b, c, d: Anyon labels for the transformation
            
        Returns:
            Complex matrix representing the F-transformation
            
        Raises:
            ValueError: If transformation is not defined
        """
        pass
    
    @abstractmethod
    def r_matrix(self, a: str, b: str) -> complex:
        """Get R-matrix for braiding transformation.
        
        The R-matrix gives the phase for exchanging two anyons:
        a ⊗ b → b ⊗ a
        
        Args:
            a: First anyon label
            b: Second anyon label
            
        Returns:
            Complex phase for the braiding transformation
        """
        pass
    
    def validate_labels(self, labels: List[str]) -> None:
        """Validate that all labels are recognized anyon types.
        
        Args:
            labels: List of anyon labels to validate
            
        Raises:
            ValueError: If any label is not recognized
        """
        valid_labels = set(self.get_labels())
        for label in labels:
            if label not in valid_labels:
                raise ValueError(f"Invalid anyon label '{label}' for {self.name} anyons")


class FibonacciAnyons(AnyonType):
    """Fibonacci anyons - the simplest universal anyon type.
    
    Fibonacci anyons have two species: I (identity) and τ (tau).
    The fusion rule is: τ × τ = I + τ
    
    This is the most studied anyon type for topological quantum computation
    because it's universal for quantum computation and has relatively simple
    structure.
    """
    
    def __init__(self) -> None:
        # Golden ratio φ = (1 + √5)/2 ≈ 1.618
        phi = (1 + np.sqrt(5)) / 2
        super().__init__("Fibonacci", phi)
        
        # Precompute matrices for efficiency
        self._setup_matrices()
    
    def get_labels(self) -> List[str]:
        """Get Fibonacci anyon labels: ['I', 'τ']."""
        return ["I", "τ"]
    
    def fusion_rules(self, a: str, b: str) -> Dict[str, complex]:
        """Fibonacci fusion rules.
        
        Rules:
        - I × I = I
        - I × τ = τ × I = τ  
        - τ × τ = I + τ (both outcomes with equal weight)
        """
        self.validate_labels([a, b])
        
        if a == "I":
            return {b: 1.0}
        elif b == "I":
            return {a: 1.0}
        else:  # a == "τ" and b == "τ"
            return {"I": 1.0, "τ": 1.0}
    
    def f_matrix(self, a: str, b: str, c: str, d: str) -> np.ndarray:
        """F-matrices for Fibonacci anyons."""
        self.validate_labels([a, b, c, d])
        
        # Most F-matrices are trivial (1x1 identity)
        # The only non-trivial case is F^τ_{τ,τ,τ}
        if all(x == "τ" for x in [a, b, c, d]):
            phi = self.quantum_dimension
            inv_phi = 1 / phi
            return np.array([
                [inv_phi, np.sqrt(inv_phi)],
                [np.sqrt(inv_phi), -inv_phi]
            ], dtype=complex)
        else:
            return np.array([[1.0]], dtype=complex)
    
    def r_matrix(self, a: str, b: str) -> complex:
        """R-matrices (braiding phases) for Fibonacci anyons."""
        self.validate_labels([a, b])
        
        if a == "I" or b == "I":
            return 1.0
        else:  # Both are τ
            # R^τ_τ = exp(-4πi/5) for Fibonacci anyons
            return np.exp(-4j * np.pi / 5)
    
    def _setup_matrices(self) -> None:
        """Precompute and cache matrices for performance."""
        # Cache commonly used F-matrices
        labels = self.get_labels()
        for a in labels:
            for b in labels:
                for c in labels:
                    for d in labels:
                        key = (a, b, c, d)
                        self._f_matrices[key] = self.f_matrix(a, b, c, d)
        
        # Cache R-matrices  
        for a in labels:
            for b in labels:
                key = (a, b)
                self._r_matrices[key] = self.r_matrix(a, b)


class IsingAnyons(AnyonType):
    """Ising anyons - related to the 2D Ising model at criticality.
    
    Ising anyons have three species: I (identity), σ (sigma), ψ (psi).
    Key fusion rules:
    - σ × σ = I + ψ
    - σ × ψ = σ  
    - ψ × ψ = I
    """
    
    def __init__(self) -> None:
        # Ising anyons have quantum dimension √2 for σ
        super().__init__("Ising", np.sqrt(2))
        self._setup_matrices()
    
    def get_labels(self) -> List[str]:
        """Get Ising anyon labels: ['I', 'σ', 'ψ']."""
        return ["I", "σ", "ψ"]
    
    def fusion_rules(self, a: str, b: str) -> Dict[str, complex]:
        """Ising anyon fusion rules."""
        self.validate_labels([a, b])
        
        # Identity rules
        if a == "I":
            return {b: 1.0}
        elif b == "I":
            return {a: 1.0}
        # σ fusion rules
        elif a == "σ" and b == "σ":
            return {"I": 1.0, "ψ": 1.0}
        elif (a == "σ" and b == "ψ") or (a == "ψ" and b == "σ"):
            return {"σ": 1.0}
        # ψ × ψ = I
        elif a == "ψ" and b == "ψ":
            return {"I": 1.0}
        else:
            raise ValueError(f"Invalid fusion: {a} × {b}")
    
    def f_matrix(self, a: str, b: str, c: str, d: str) -> np.ndarray:
        """F-matrices for Ising anyons."""
        self.validate_labels([a, b, c, d])
        
        # Most are trivial, key non-trivial case is F^σ_{σ,σ,σ}
        if all(x == "σ" for x in [a, b, c, d]):
            return np.array([
                [1/np.sqrt(2), 1/np.sqrt(2)],
                [1/np.sqrt(2), -1/np.sqrt(2)]
            ], dtype=complex)
        else:
            return np.array([[1.0]], dtype=complex)
    
    def r_matrix(self, a: str, b: str) -> complex:
        """R-matrices for Ising anyons."""
        self.validate_labels([a, b])
        
        if a == "I" or b == "I":
            return 1.0
        elif a == "ψ" or b == "ψ":
            return -1.0  # Fermion exchange
        else:  # Both σ
            return np.exp(1j * np.pi / 8)  # σ braiding phase
    
    def _setup_matrices(self) -> None:
        """Precompute matrices."""
        labels = self.get_labels()
        for a in labels:
            for b in labels:
                for c in labels:
                    for d in labels:
                        key = (a, b, c, d)
                        self._f_matrices[key] = self.f_matrix(a, b, c, d)
        
        for a in labels:
            for b in labels:
                key = (a, b)
                self._r_matrices[key] = self.r_matrix(a, b)


def get_anyon_type(name: str) -> AnyonType:
    """Factory function to create anyon type by name.
    
    Args:
        name: Name of anyon type ('fibonacci', 'ising', etc.)
        
    Returns:
        Instance of the requested anyon type
        
    Raises:
        ValueError: If anyon type is not recognized
        
    Example:
        >>> from tqc.anyons import get_anyon_type
        >>> fib = get_anyon_type('fibonacci')
        >>> print(fib.quantum_dimension)
        1.618...
    """
    name_lower = name.lower()
    
    if name_lower == "fibonacci":
        return FibonacciAnyons()
    elif name_lower == "ising":
        return IsingAnyons()
    else:
        supported = ["fibonacci", "ising"]
        raise ValueError(f"Unknown anyon type '{name}'. Supported types: {supported}")


# Convenient aliases
FibAnyons = FibonacciAnyons  # Common abbreviation
