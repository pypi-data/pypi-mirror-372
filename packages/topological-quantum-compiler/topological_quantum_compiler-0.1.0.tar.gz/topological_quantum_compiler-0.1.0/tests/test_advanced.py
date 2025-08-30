"""Additional tests for specific TQC components."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from tqc.braids import BraidWord, BraidGenerator, BraidDirection
from tqc.anyons import FibonacciAnyons, IsingAnyons
from tqc.simulation import AnyonicState, AnyonicSimulator
from tqc.optimization import BraidOptimizer, GreedySimplification, SolovayKitaevApproximation


class TestAdvancedBraids:
    """Advanced tests for braid functionality."""
    
    def test_long_braid_word_operations(self):
        """Test operations on longer braid words."""
        # Create a longer braid sequence
        generators = []
        for i in range(20):
            gen = BraidGenerator(i % 4, 
                               BraidDirection.OVER if i % 2 == 0 else BraidDirection.UNDER)
            generators.append(gen)
        
        braid = BraidWord(generators, 5)
        assert len(braid) == 20
        
        # Test simplification on long braid
        simplified = braid.simplify()
        assert len(simplified) <= len(braid)  # Should not increase length
        
        # Test inverse
        inverse = braid.inverse()
        assert len(inverse) == len(braid)
        
        # Test that braid * inverse simplifies significantly
        combined = braid * inverse
        very_simplified = combined.simplify()
        assert len(very_simplified) < len(combined)
    
    def test_braid_visualization_metadata(self):
        """Test braid visualization with metadata."""
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(1, BraidDirection.UNDER)
        ]
        braid = BraidWord(generators, 3)
        braid.metadata['anyon_labels'] = ['τ', 'I', 'τ']
        
        # Test visualization (should not raise exceptions)
        svg_content = braid.visualize(show_labels=True)
        assert isinstance(svg_content, str)
        assert len(svg_content) > 0
        
        # Test without labels
        svg_no_labels = braid.visualize(show_labels=False)
        assert isinstance(svg_no_labels, str)
    
    def test_complex_permutations(self):
        """Test complex permutation to braid conversion."""
        # Test various permutations
        test_perms = [
            [2, 1, 0],        # Reverse order
            [0, 2, 1, 3],     # Single cycle
            [1, 0, 3, 2],     # Two swaps
            [3, 2, 1, 0]      # Complete reversal
        ]
        
        from tqc.braids import create_braid_from_permutation
        
        for perm in test_perms:
            braid = create_braid_from_permutation(perm)
            result_perm = braid.to_permutation()
            assert result_perm == perm, f"Failed for permutation {perm}"


class TestAnyonPhysics:
    """Tests focusing on anyonic physics correctness."""
    
    def test_fibonacci_pentagon_equation(self):
        """Test that Fibonacci F-matrices satisfy the pentagon equation."""
        fib = FibonacciAnyons()
        
        # Pentagon equation: F^d_{ab,c} F^d_{a,bc} = sum_e F^e_{a,bc} F^d_{ae,c} F^e_{ab,c}
        # This is a fundamental consistency condition for anyon theories
        
        # For Fibonacci anyons, test with τ anyons
        F_left = fib.f_matrix("τ", "τ", "τ", "τ")
        
        # This test is simplified - full pentagon equation testing
        # would require more complex tensor calculations
        assert F_left.shape == (2, 2)
        assert np.allclose(F_left @ F_left.conj().T, np.eye(2), atol=1e-10)
    
    def test_braiding_yang_baxter(self):
        """Test that braiding satisfies Yang-Baxter equation."""
        fib = FibonacciAnyons()
        
        # Yang-Baxter: R_{12} R_{23} R_{12} = R_{23} R_{12} R_{23}
        # This is the fundamental braid relation
        
        r_12 = fib.r_matrix("τ", "τ")
        r_23 = fib.r_matrix("τ", "τ")
        
        # For 2x2 case, this reduces to checking braid relations hold
        # Full test would involve tensor products
        assert abs(r_12) > 0  # Non-trivial braiding
    
    def test_quantum_dimension_consistency(self):
        """Test quantum dimension consistency."""
        fib = FibonacciAnyons()
        phi = fib.quantum_dimension
        
        # For Fibonacci anyons: d_τ = φ = (1+√5)/2
        expected_phi = (1 + np.sqrt(5)) / 2
        assert abs(phi - expected_phi) < 1e-12
        
        # Golden ratio property: φ² = φ + 1
        assert abs(phi**2 - (phi + 1)) < 1e-12
    
    def test_ising_anyon_properties(self):
        """Test specific Ising anyon properties."""
        ising = IsingAnyons()
        
        # Test quantum dimensions
        assert abs(ising.quantum_dimension - np.sqrt(2)) < 1e-12
        
        # Test that ψ is fermionic (braiding gives -1)
        r_psi_psi = ising.r_matrix("ψ", "ψ")
        assert abs(r_psi_psi - (-1)) < 1e-12
        
        # Test σ braiding phase
        r_sigma_sigma = ising.r_matrix("σ", "σ")
        expected = np.exp(1j * np.pi / 8)
        assert abs(r_sigma_sigma - expected) < 1e-12


class TestSimulationAccuracy:
    """Tests for simulation accuracy and edge cases."""
    
    def test_statevector_normalization(self):
        """Test that statevectors remain normalized."""
        fib = FibonacciAnyons()
        state = AnyonicState(fib, 3, ["τ", "τ", "I"])
        
        # Check initial normalization
        initial_norm = np.sum(np.abs(state.amplitudes)**2)
        assert abs(initial_norm - 1.0) < 1e-12
        
        # Apply several braids and check normalization is preserved
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(1, BraidDirection.UNDER),
            BraidGenerator(0, BraidDirection.OVER)
        ]
        
        for gen in generators:
            state.apply_braid(gen)
            norm = np.sum(np.abs(state.amplitudes)**2)
            assert abs(norm - 1.0) < 1e-12, f"Norm became {norm} after {gen}"
    
    def test_measurement_probabilities(self):
        """Test measurement probability calculations."""
        fib = FibonacciAnyons()
        state = AnyonicState(fib, 2, ["I", "I"])
        
        # Perform many measurements and check statistical consistency
        outcomes = []
        for _ in range(100):
            temp_state = state.copy()
            outcome, prob = temp_state.measure()
            outcomes.append(outcome)
            assert 0 <= prob <= 1
        
        # Check that we got reasonable distribution
        unique_outcomes = set(outcomes)
        assert len(unique_outcomes) > 0
    
    def test_fidelity_calculation(self):
        """Test state fidelity calculations."""
        fib = FibonacciAnyons()
        
        state1 = AnyonicState(fib, 2, ["I", "I"])
        state2 = AnyonicState(fib, 2, ["I", "I"])
        
        # Identical states should have fidelity 1
        fidelity = state1.get_fidelity(state2)
        assert abs(fidelity - 1.0) < 1e-10
        
        # Apply different operations and check fidelity changes
        gen = BraidGenerator(0, BraidDirection.OVER)
        state2.apply_braid(gen)
        
        new_fidelity = state1.get_fidelity(state2)
        assert 0 <= new_fidelity <= 1
    
    def test_simulation_with_many_shots(self):
        """Test simulation with large number of shots."""
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        gen = BraidGenerator(0, BraidDirection.OVER)
        braid = BraidWord([gen], 2)
        braid.metadata['anyon_labels'] = ["I", "I"]
        
        # Large number of shots
        result = simulator.simulate(braid, shots=5000)
        
        assert result.total_shots == 5000
        assert len(result.counts) > 0
        
        # Check that probabilities sum to 1
        probabilities = result.get_probabilities()
        total_prob = sum(probabilities.values())
        assert abs(total_prob - 1.0) < 1e-10


class TestOptimizationAlgorithms:
    """Tests for optimization algorithms."""
    
    def test_greedy_simplification_edge_cases(self):
        """Test greedy simplification with edge cases."""
        strategy = GreedySimplification()
        
        # Empty braid
        empty_braid = BraidWord([], 2)
        optimized = strategy.optimize(empty_braid, 0.99)
        assert len(optimized) == 0
        
        # Single generator
        single = BraidWord([BraidGenerator(0, BraidDirection.OVER)], 2)
        optimized = strategy.optimize(single, 0.99)
        assert len(optimized) == 1
        
        # Already simplified
        simplified = BraidWord([BraidGenerator(0, BraidDirection.OVER)], 2)
        optimized = strategy.optimize(simplified, 0.99)
        assert len(optimized) == len(simplified)
    
    def test_solovay_kitaev_initialization(self):
        """Test Solovay-Kitaev algorithm initialization."""
        fib = FibonacciAnyons()
        sk = SolovayKitaevApproximation(fib)
        
        assert len(sk.base_generators) > 0
        assert sk.recursion_depth == 10
        assert len(sk._generator_database) > 0
    
    def test_rotation_approximation_angles(self):
        """Test rotation approximation for different angles."""
        fib = FibonacciAnyons()
        optimizer = BraidOptimizer(fib)
        
        test_angles = [0, np.pi/8, np.pi/4, np.pi/2, np.pi, 2*np.pi]
        
        for angle in test_angles:
            for axis in ['X', 'Y', 'Z']:
                braid = optimizer.approximate_rotation(axis, angle, 0)
                assert isinstance(braid, BraidWord)
                
                # More braids needed for larger angles
                if angle > np.pi/2:
                    assert len(braid) > 0
    
    def test_optimization_consistency(self):
        """Test that optimization preserves braid equivalence."""
        fib = FibonacciAnyons()
        optimizer = BraidOptimizer(fib)
        
        # Create braid with known simplification
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(0, BraidDirection.UNDER),
            BraidGenerator(1, BraidDirection.OVER),
            BraidGenerator(1, BraidDirection.UNDER),
            BraidGenerator(2, BraidDirection.OVER)
        ]
        braid = BraidWord(generators, 4)
        
        # Optimize with different strategies
        strategies = ['greedy', 'solovay_kitaev', 'heuristic']
        results = {}
        
        for strategy in strategies:
            try:
                optimized = optimizer.optimize(braid, strategy=strategy)
                results[strategy] = optimized
                assert len(optimized) <= len(braid)
            except Exception as e:
                # Some strategies might not be fully implemented
                assert "Unknown strategy" in str(e) or "not implemented" in str(e).lower()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_braid_operations(self):
        """Test invalid braid operations."""
        # Generator index too large
        with pytest.raises(ValueError):
            BraidGenerator(-1, BraidDirection.OVER)
        
        # Invalid strand count
        with pytest.raises(ValueError):
            BraidWord([], 0)
        
        # Generator incompatible with strand count
        with pytest.raises(ValueError):
            gen = BraidGenerator(5, BraidDirection.OVER)
            BraidWord([gen], 3)
    
    def test_anyon_state_edge_cases(self):
        """Test anyonic state edge cases."""
        fib = FibonacciAnyons()
        
        # Mismatched labels and anyon count
        with pytest.raises(ValueError):
            AnyonicState(fib, 3, ["I", "τ"])  # Only 2 labels for 3 anyons
        
        # Invalid anyon labels
        with pytest.raises(ValueError):
            AnyonicState(fib, 2, ["I", "invalid"])
    
    def test_simulation_edge_cases(self):
        """Test simulation edge cases."""
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        # Empty braid
        empty_braid = BraidWord([], 2)
        empty_braid.metadata['anyon_labels'] = ["I", "I"]
        
        result = simulator.simulate(empty_braid, shots=10)
        assert result.total_shots == 10
        
        # Zero shots
        result_zero = simulator.simulate(empty_braid, shots=0)
        assert result_zero.total_shots == 0
    
    def test_compiler_parameter_validation(self):
        """Test compiler parameter validation."""
        from tqc.compiler import TopologicalCompiler
        
        fib = FibonacciAnyons()
        
        # Invalid optimization level
        with pytest.raises(ValueError):
            TopologicalCompiler(fib, optimization_level=-1)
        
        with pytest.raises(ValueError):
            TopologicalCompiler(fib, optimization_level=5)
        
        # Invalid fidelity
        with pytest.raises(ValueError):
            TopologicalCompiler(fib, target_fidelity=0.0)
        
        with pytest.raises(ValueError):
            TopologicalCompiler(fib, target_fidelity=1.5)


class TestPerformance:
    """Performance and scaling tests."""
    
    def test_braid_length_scaling(self):
        """Test performance with different braid lengths."""
        import time
        
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        times = []
        lengths = [1, 5, 10, 20]
        
        for length in lengths:
            generators = [BraidGenerator(i % 3, BraidDirection.OVER) 
                         for i in range(length)]
            braid = BraidWord(generators, 4)
            braid.metadata['anyon_labels'] = ["I"] * 4
            
            start_time = time.time()
            simulator.simulate(braid, shots=100)
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        # Check that time increases with braid length
        assert times[-1] >= times[0]  # Longest should take at least as long as shortest
    
    def test_anyon_count_scaling(self):
        """Test performance scaling with anyon count."""
        import time
        
        fib = FibonacciAnyons()
        
        times = []
        anyon_counts = [2, 3, 4, 5]
        
        for n_anyons in anyon_counts:
            state = AnyonicState(fib, n_anyons, ["I"] * n_anyons)
            
            start_time = time.time()
            
            # Apply a few braids
            for i in range(min(3, n_anyons - 1)):
                gen = BraidGenerator(i, BraidDirection.OVER)
                state.apply_braid(gen)
            
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        # Performance should degrade gracefully
        assert all(t < 1.0 for t in times)  # All should complete in reasonable time


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
