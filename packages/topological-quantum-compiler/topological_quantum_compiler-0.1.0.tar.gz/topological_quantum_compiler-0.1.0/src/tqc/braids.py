"""Braid group operations and representations."""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union, Dict, Any
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import StringIO

logger = logging.getLogger(__name__)


class BraidDirection(Enum):
    """Direction of braid crossing."""
    OVER = 1    # Positive crossing (σᵢ)
    UNDER = -1  # Negative crossing (σᵢ⁻¹)


@dataclass(frozen=True)
class BraidGenerator:
    """A single braid generator σᵢ or σᵢ⁻¹.
    
    Represents the exchange of strands i and i+1 in an n-strand braid.
    
    Attributes:
        index: Which pair of strands to exchange (0-indexed)
        direction: Whether this is σᵢ (OVER) or σᵢ⁻¹ (UNDER)
        
    Example:
        >>> gen = BraidGenerator(0, BraidDirection.OVER)  # σ₀
        >>> inv_gen = BraidGenerator(0, BraidDirection.UNDER)  # σ₀⁻¹
    """
    index: int
    direction: BraidDirection = BraidDirection.OVER
    
    def __post_init__(self) -> None:
        """Validate generator after creation."""
        if self.index < 0:
            raise ValueError("Braid generator index must be non-negative")
    
    def inverse(self) -> "BraidGenerator":
        """Get the inverse of this generator.
        
        Returns:
            BraidGenerator with opposite direction
        """
        opposite_dir = (BraidDirection.UNDER if self.direction == BraidDirection.OVER 
                       else BraidDirection.OVER)
        return BraidGenerator(self.index, opposite_dir)
    
    def __str__(self) -> str:
        """String representation of the generator."""
        if self.direction == BraidDirection.OVER:
            return f"σ_{self.index}"
        else:
            return f"σ_{self.index}^(-1)"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"BraidGenerator({self.index}, {self.direction.name})"


@dataclass
class BraidWord:
    """A word in the braid group B_n.
    
    Represents a sequence of braid generators that can be applied to
    a set of n strands. This is the fundamental data structure for
    representing braided computations.
    
    Attributes:
        generators: Sequence of braid generators
        n_strands: Number of strands in the braid
        metadata: Optional metadata (anyon labels, etc.)
    """
    generators: List[BraidGenerator] = field(default_factory=list)
    n_strands: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate braid word after creation."""
        if self.n_strands < 2:
            raise ValueError("Braid must have at least 2 strands")
        
        # Validate all generators are valid for this braid
        for gen in self.generators:
            if gen.index >= self.n_strands - 1:
                raise ValueError(
                    f"Generator σ_{gen.index} invalid for {self.n_strands}-strand braid"
                )
    
    def append(self, generator: BraidGenerator) -> None:
        """Add a generator to the end of the braid word.
        
        Args:
            generator: Braid generator to append
            
        Raises:
            ValueError: If generator index is too large for this braid
        """
        if generator.index >= self.n_strands - 1:
            raise ValueError(
                f"Generator σ_{generator.index} invalid for {self.n_strands}-strand braid"
            )
        self.generators.append(generator)
        logger.debug(f"Appended {generator} to braid word")
    
    def extend(self, other: "BraidWord") -> None:
        """Concatenate another braid word to this one.
        
        Args:
            other: BraidWord to concatenate
            
        Raises:
            ValueError: If braids have different numbers of strands
        """
        if other.n_strands != self.n_strands:
            raise ValueError("Cannot concatenate braids with different strand counts")
        
        self.generators.extend(other.generators)
        logger.debug(f"Extended braid word with {len(other.generators)} generators")
    
    def inverse(self) -> "BraidWord":
        """Compute the inverse of this braid word.
        
        The inverse is obtained by reversing the sequence and taking
        the inverse of each generator.
        
        Returns:
            New BraidWord representing the inverse braid
        """
        inv_generators = [gen.inverse() for gen in reversed(self.generators)]
        return BraidWord(inv_generators, self.n_strands, self.metadata.copy())
    
    def __mul__(self, other: "BraidWord") -> "BraidWord":
        """Multiply (concatenate) two braid words.
        
        Args:
            other: BraidWord to multiply with
            
        Returns:
            New BraidWord representing the product
        """
        if other.n_strands != self.n_strands:
            raise ValueError("Cannot multiply braids with different strand counts")
        
        result = BraidWord(
            self.generators + other.generators,
            self.n_strands,
            {**self.metadata, **other.metadata}
        )
        return result
    
    def __len__(self) -> int:
        """Get the length (number of generators) of the braid word."""
        return len(self.generators)
    
    def __str__(self) -> str:
        """String representation of the braid word."""
        if not self.generators:
            return "e"  # Identity braid
        
        return " ".join(str(gen) for gen in self.generators)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"BraidWord({len(self.generators)} generators, {self.n_strands} strands)"
    
    def simplify(self) -> "BraidWord":
        """Apply basic simplification rules to reduce braid word length.
        
        Applies:
        1. σᵢ σᵢ⁻¹ = e (generator-inverse cancellation)
        2. σᵢ⁻¹ σᵢ = e 
        
        Returns:
            Simplified BraidWord (new instance)
        """
        simplified_gens = []
        
        for gen in self.generators:
            # Check if we can cancel with the previous generator
            if (simplified_gens and 
                simplified_gens[-1].index == gen.index and
                simplified_gens[-1].direction != gen.direction):
                # Cancellation: σᵢ σᵢ⁻¹ = e
                simplified_gens.pop()
                logger.debug(f"Cancelled {simplified_gens[-1] if simplified_gens else 'empty'} with {gen}")
            else:
                simplified_gens.append(gen)
        
        result = BraidWord(simplified_gens, self.n_strands, self.metadata.copy())
        
        if len(result) < len(self):
            logger.info(f"Simplified braid from {len(self)} to {len(result)} generators")
        
        return result
    
    def to_permutation(self) -> List[int]:
        """Convert braid word to the permutation it induces on strand labels.
        
        Returns:
            List where result[i] is the final position of strand i
            
        Example:
            >>> braid = BraidWord([BraidGenerator(0, BraidDirection.OVER)], 3)
            >>> braid.to_permutation()
            [1, 0, 2]  # Strands 0 and 1 are swapped
        """
        perm = list(range(self.n_strands))
        
        for gen in self.generators:
            i = gen.index
            # Swap positions i and i+1
            perm[i], perm[i + 1] = perm[i + 1], perm[i]
        
        return perm
    
    def visualize(self, filename: Optional[str] = None, 
                  show_labels: bool = True,
                  colormap: str = "tab10") -> str:
        """Generate a visual representation of the braid.
        
        Creates an SVG diagram showing the braiding pattern with
        over/under crossings clearly marked.
        
        Args:
            filename: If provided, save SVG to this file
            show_labels: Whether to show anyon labels
            colormap: Matplotlib colormap for strand colors
            
        Returns:
            SVG markup as string
        """
        if not self.generators:
            # Empty braid - just parallel strands
            return self._draw_trivial_braid(filename, show_labels, colormap)
        
        # Set up the plot
        fig, ax = plt.subplots(1, 1, figsize=(len(self.generators) + 2, self.n_strands))
        ax.set_xlim(0, len(self.generators) + 1)
        ax.set_ylim(0, self.n_strands - 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Colors for different strands
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, self.n_strands))
        
        # Track strand positions
        positions = np.arange(self.n_strands, dtype=float)
        
        # Draw initial vertical strands
        for i in range(self.n_strands):
            ax.plot([0, 0.2], [positions[i], positions[i]], 
                   color=colors[i], linewidth=3, solid_capstyle='round')
        
        # Draw each crossing
        for step, gen in enumerate(self.generators):
            x_start = step + 0.2
            x_end = step + 0.8
            x_mid = (x_start + x_end) / 2
            
            i, j = gen.index, gen.index + 1
            y_i, y_j = positions[i], positions[j]
            
            if gen.direction == BraidDirection.OVER:
                # i goes over j
                self._draw_crossing(ax, x_start, x_end, y_i, y_j, 
                                  colors[i], colors[j], over_strand=0)
            else:
                # i goes under j  
                self._draw_crossing(ax, x_start, x_end, y_i, y_j,
                                  colors[i], colors[j], over_strand=1)
            
            # Update positions after crossing
            positions[i], positions[j] = positions[j], positions[i]
            colors[i], colors[j] = colors[j], colors[i]
        
        # Draw final vertical segments
        final_x = len(self.generators) + 0.8
        for i in range(self.n_strands):
            ax.plot([final_x, final_x + 0.2], [positions[i], positions[i]],
                   color=colors[i], linewidth=3, solid_capstyle='round')
        
        # Add labels if requested
        if show_labels and 'anyon_labels' in self.metadata:
            labels = self.metadata['anyon_labels']
            for i, label in enumerate(labels):
                ax.text(-0.1, i, label, ha='right', va='center', fontsize=12)
                final_pos = int(np.where(positions == i)[0][0])
                ax.text(final_x + 0.3, final_pos, label, ha='left', va='center', fontsize=12)
        
        plt.title(f"Braid: {str(self)}", fontsize=14)
        plt.tight_layout()
        
        # Save or return SVG
        if filename:
            plt.savefig(filename, format='svg', bbox_inches='tight')
            logger.info(f"Braid diagram saved to {filename}")
        
        # Convert to SVG string
        svg_buffer = StringIO()
        plt.savefig(svg_buffer, format='svg', bbox_inches='tight')
        svg_content = svg_buffer.getvalue()
        
        plt.close(fig)
        return svg_content
    
    def _draw_crossing(self, ax, x_start: float, x_end: float, 
                      y1: float, y2: float, color1, color2, over_strand: int) -> None:
        """Draw a single crossing with proper over/under visualization."""
        x_vals = np.linspace(x_start, x_end, 50)
        
        # Parametric curves for the crossing strands
        y1_vals = y1 + (y2 - y1) * (x_vals - x_start) / (x_end - x_start)  
        y2_vals = y2 + (y1 - y2) * (x_vals - x_start) / (x_end - x_start)
        
        if over_strand == 0:
            # Strand 1 goes over strand 2
            # Draw strand 2 first (under)
            ax.plot(x_vals, y2_vals, color=color2, linewidth=3, solid_capstyle='round')
            # Draw strand 1 on top with a gap
            mid_idx = len(x_vals) // 2
            gap = 3
            ax.plot(x_vals[:mid_idx-gap], y1_vals[:mid_idx-gap], 
                   color=color1, linewidth=3, solid_capstyle='round')
            ax.plot(x_vals[mid_idx+gap:], y1_vals[mid_idx+gap:], 
                   color=color1, linewidth=3, solid_capstyle='round')
        else:
            # Strand 2 goes over strand 1
            ax.plot(x_vals, y1_vals, color=color1, linewidth=3, solid_capstyle='round')
            mid_idx = len(x_vals) // 2
            gap = 3
            ax.plot(x_vals[:mid_idx-gap], y2_vals[:mid_idx-gap], 
                   color=color2, linewidth=3, solid_capstyle='round')
            ax.plot(x_vals[mid_idx+gap:], y2_vals[mid_idx+gap:], 
                   color=color2, linewidth=3, solid_capstyle='round')
    
    def _draw_trivial_braid(self, filename: Optional[str], 
                           show_labels: bool, colormap: str) -> str:
        """Draw a trivial (empty) braid as parallel lines."""
        fig, ax = plt.subplots(1, 1, figsize=(3, self.n_strands))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, self.n_strands - 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, self.n_strands))
        
        for i in range(self.n_strands):
            ax.plot([0.2, 1.8], [i, i], color=colors[i], linewidth=3, solid_capstyle='round')
        
        if show_labels and 'anyon_labels' in self.metadata:
            labels = self.metadata['anyon_labels']
            for i, label in enumerate(labels):
                ax.text(0.1, i, label, ha='right', va='center', fontsize=12)
                ax.text(1.9, i, label, ha='left', va='center', fontsize=12)
        
        plt.title("Identity Braid", fontsize=14)
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, format='svg', bbox_inches='tight')
        
        svg_buffer = StringIO()
        plt.savefig(svg_buffer, format='svg', bbox_inches='tight')
        svg_content = svg_buffer.getvalue()
        
        plt.close(fig)
        return svg_content


def create_braid_from_permutation(perm: List[int]) -> BraidWord:
    """Create a braid word that realizes a given permutation.
    
    Uses the bubble sort algorithm to construct a minimal-length
    braid word for the given permutation.
    
    Args:
        perm: Target permutation as a list
        
    Returns:
        BraidWord that induces the given permutation
        
    Example:
        >>> braid = create_braid_from_permutation([1, 0, 2])
        >>> str(braid)
        'σ_0'
    """
    n = len(perm)
    if n < 2:
        return BraidWord([], n)
    
    # Validate permutation
    if sorted(perm) != list(range(n)):
        raise ValueError("Invalid permutation: must be a rearrangement of 0..n-1")
    
    generators = []
    current = list(range(n))
    
    # Bubble sort to generate braid word
    while current != perm:
        for i in range(n - 1):
            if current[i] > current[i + 1]:
                # Need to swap positions i and i+1
                generators.append(BraidGenerator(i, BraidDirection.OVER))
                current[i], current[i + 1] = current[i + 1], current[i]
                break
    
    return BraidWord(generators, n)
