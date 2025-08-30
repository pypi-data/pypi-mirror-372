"""Test suite for the TQC core functionality."""

import pytest
import numpy as np
from typing import List

from tqc.anyons import FibonacciAnyons, IsingAnyons, get_anyon_type
from tqc.braids import BraidWord, BraidGenerator, BraidDirection, create_braid_from_permutation
from tqc.compiler import TopologicalCompiler
from tqc.simulation import AnyonicSimulator, AnyonicState
from tqc.optimization import BraidOptimizer


class TestAnyons:
    """Test anyon types and their algebraic properties."""
    
    def test_fibonacci_anyon_creation(self):
        """Test Fibonacci anyon initialization."""
        fib = FibonacciAnyons()
        assert fib.name == "Fibonacci"
        assert abs(fib.quantum_dimension - (1 + np.sqrt(5))/2) < 1e-10
        assert set(fib.get_labels()) == {"I", "τ"}
    
    def test_fibonacci_fusion_rules(self):
        """Test Fibonacci fusion rules."""
        fib = FibonacciAnyons()
        
        # Identity fusion
        assert fib.fusion_rules("I", "I") == {"I": 1.0}
        assert fib.fusion_rules("I", "τ") == {"τ": 1.0}
        assert fib.fusion_rules("τ", "I") == {"τ": 1.0}
        
        # Non-trivial fusion
        tau_tau = fib.fusion_rules("τ", "τ")
        assert set(tau_tau.keys()) == {"I", "τ"}
        assert tau_tau["I"] == 1.0
        assert tau_tau["τ"] == 1.0
    
    def test_fibonacci_f_matrices(self):
        """Test Fibonacci F-matrices."""
        fib = FibonacciAnyons()
        
        # Trivial F-matrices
        f_trivial = fib.f_matrix("I", "I", "I", "I")
        assert f_trivial.shape == (1, 1)
        assert f_trivial[0, 0] == 1.0
        
        # Non-trivial F-matrix
        f_nontrivial = fib.f_matrix("τ", "τ", "τ", "τ")
        assert f_nontrivial.shape == (2, 2)
        
        # Check unitarity
        assert np.allclose(f_nontrivial @ f_nontrivial.conj().T, np.eye(2))
    
    def test_fibonacci_r_matrices(self):
        """Test Fibonacci R-matrices (braiding phases)."""
        fib = FibonacciAnyons()
        
        # Trivial braiding with identity
        assert fib.r_matrix("I", "I") == 1.0
        assert fib.r_matrix("I", "τ") == 1.0
        assert fib.r_matrix("τ", "I") == 1.0
        
        # Non-trivial braiding
        r_tau_tau = fib.r_matrix("τ", "τ")
        expected = np.exp(-4j * np.pi / 5)
        assert abs(r_tau_tau - expected) < 1e-10
    
    def test_ising_anyons(self):
        """Test Ising anyon properties."""
        ising = IsingAnyons()
        assert ising.name == "Ising"
        assert abs(ising.quantum_dimension - np.sqrt(2)) < 1e-10
        assert set(ising.get_labels()) == {"I", "σ", "ψ"}
    
    def test_ising_fusion_rules(self):
        """Test Ising fusion rules."""
        ising = IsingAnyons()
        
        # Key fusion rules
        assert ising.fusion_rules("ψ", "ψ") == {"I": 1.0}
        assert ising.fusion_rules("σ", "ψ") == {"σ": 1.0}
        assert ising.fusion_rules("ψ", "σ") == {"σ": 1.0}
        
        sigma_sigma = ising.fusion_rules("σ", "σ")
        assert set(sigma_sigma.keys()) == {"I", "ψ"}
    
    def test_anyon_validation(self):
        """Test anyon label validation."""
        fib = FibonacciAnyons()
        
        # Valid labels
        fib.validate_labels(["I", "τ"])
        
        # Invalid labels
        with pytest.raises(ValueError):
            fib.validate_labels(["I", "invalid"])
    
    def test_anyon_factory(self):
        """Test anyon factory function."""
        fib = get_anyon_type("fibonacci")
        assert isinstance(fib, FibonacciAnyons)
        
        ising = get_anyon_type("ising")
        assert isinstance(ising, IsingAnyons)
        
        with pytest.raises(ValueError):
            get_anyon_type("unknown")


class TestBraids:
    """Test braid group operations."""
    
    def test_braid_generator_creation(self):
        """Test creating braid generators."""
        gen = BraidGenerator(0, BraidDirection.OVER)
        assert gen.index == 0
        assert gen.direction == BraidDirection.OVER
        assert str(gen) == "σ_0"
        
        inv_gen = BraidGenerator(1, BraidDirection.UNDER)
        assert str(inv_gen) == "σ_1^(-1)"
    
    def test_braid_generator_inverse(self):
        """Test braid generator inversion."""
        gen = BraidGenerator(0, BraidDirection.OVER)
        inv = gen.inverse()
        assert inv.index == 0
        assert inv.direction == BraidDirection.UNDER
        
        # Double inverse
        double_inv = inv.inverse()
        assert double_inv.index == gen.index
        assert double_inv.direction == gen.direction
    
    def test_braid_word_creation(self):
        """Test creating braid words."""
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(1, BraidDirection.UNDER)
        ]
        braid = BraidWord(generators, 3)
        
        assert len(braid) == 2
        assert braid.n_strands == 3
        assert str(braid) == "σ_0 σ_1^(-1)"
    
    def test_braid_word_operations(self):
        """Test braid word operations."""
        gen1 = BraidGenerator(0, BraidDirection.OVER)
        gen2 = BraidGenerator(1, BraidDirection.OVER)
        
        braid1 = BraidWord([gen1], 3)
        braid2 = BraidWord([gen2], 3)
        
        # Concatenation
        product = braid1 * braid2
        assert len(product) == 2
        assert product.generators == [gen1, gen2]
        
        # Extension
        braid1.extend(braid2)
        assert len(braid1) == 2
    
    def test_braid_inverse(self):
        """Test braid word inversion."""
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(1, BraidDirection.UNDER)
        ]
        braid = BraidWord(generators, 3)
        
        inv_braid = braid.inverse()
        assert len(inv_braid) == 2
        
        # Inverse should reverse order and flip directions
        assert inv_braid.generators[0].index == 1
        assert inv_braid.generators[0].direction == BraidDirection.OVER
        assert inv_braid.generators[1].index == 0
        assert inv_braid.generators[1].direction == BraidDirection.UNDER
    
    def test_braid_simplification(self):
        """Test basic braid simplification."""
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(0, BraidDirection.UNDER),  # Cancels with previous
            BraidGenerator(1, BraidDirection.OVER)
        ]
        braid = BraidWord(generators, 3)
        
        simplified = braid.simplify()
        assert len(simplified) == 1
        assert simplified.generators[0].index == 1
    
    def test_braid_permutation(self):
        """Test braid to permutation conversion."""
        # σ_0 swaps strands 0 and 1
        gen = BraidGenerator(0, BraidDirection.OVER)
        braid = BraidWord([gen], 3)
        
        perm = braid.to_permutation()
        assert perm == [1, 0, 2]
    
    def test_permutation_to_braid(self):
        """Test creating braid from permutation."""
        # Swap first two elements
        perm = [1, 0, 2]
        braid = create_braid_from_permutation(perm)
        
        assert len(braid) == 1
        assert braid.generators[0].index == 0
        
        # Verify it produces the correct permutation
        assert braid.to_permutation() == perm
    
    def test_braid_validation(self):
        """Test braid word validation."""
        # Invalid generator index
        with pytest.raises(ValueError):
            BraidWord([BraidGenerator(2, BraidDirection.OVER)], 2)
        
        # Invalid strand count
        with pytest.raises(ValueError):
            BraidWord([], 1)


class TestCompiler:
    """Test the topological compiler."""
    
    def test_compiler_creation(self):
        """Test compiler initialization."""
        fib = FibonacciAnyons()
        compiler = TopologicalCompiler(fib)
        
        assert compiler.anyon_type is fib
        assert compiler.optimization_level == 1
        assert compiler.target_fidelity == 0.99
    
    def test_compile_simple_circuit(self):
        """Test compiling a simple quantum circuit."""
        from qiskit import QuantumCircuit
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        
        compiler = TopologicalCompiler(FibonacciAnyons())
        result = compiler.compile(qc)
        
        assert isinstance(result.braid_program, BraidWord)
        assert result.fidelity_estimate > 0
        assert len(result.anyon_mapping) == 2
        assert result.compilation_stats['original_gates'] == 3  # H, CX, measure
    
    def test_compile_with_invalid_circuit(self):
        """Test compiler error handling."""
        from qiskit import QuantumCircuit
        
        # Empty circuit
        qc = QuantumCircuit(0)
        compiler = TopologicalCompiler(FibonacciAnyons())
        
        with pytest.raises(ValueError):
            compiler.compile(qc)
    
    def test_optimization_levels(self):
        """Test different optimization levels."""
        from qiskit import QuantumCircuit
        
        qc = QuantumCircuit(2)
        for _ in range(5):  # Add some gates
            qc.h(0)
            qc.cx(0, 1)
        
        # Test different optimization levels
        for level in [0, 1, 2, 3]:
            compiler = TopologicalCompiler(FibonacciAnyons(), optimization_level=level)
            result = compiler.compile(qc)
            assert isinstance(result.braid_program, BraidWord)


class TestSimulation:
    """Test anyonic simulation."""
    
    def test_anyonic_state_creation(self):
        """Test creating anyonic states."""
        fib = FibonacciAnyons()
        state = AnyonicState(fib, 3, ["I", "τ", "I"])
        
        assert state.n_anyons == 3
        assert state.anyon_labels == ["I", "τ", "I"]
        assert state.dim > 0
        assert np.allclose(np.sum(np.abs(state.amplitudes)**2), 1.0)
    
    def test_anyonic_state_braiding(self):
        """Test applying braids to anyonic states."""
        fib = FibonacciAnyons()
        state = AnyonicState(fib, 3, ["I", "I", "I"])
        
        # Apply a braid generator
        gen = BraidGenerator(0, BraidDirection.OVER)
        initial_labels = state.anyon_labels.copy()
        
        state.apply_braid(gen)
        
        # Check that labels were swapped
        assert state.anyon_labels[0] == initial_labels[1]
        assert state.anyon_labels[1] == initial_labels[0]
        assert state.anyon_labels[2] == initial_labels[2]
    
    def test_anyonic_measurement(self):
        """Test measurement of anyonic states."""
        fib = FibonacciAnyons()
        state = AnyonicState(fib, 2, ["I", "I"])
        
        outcome, probability = state.measure()
        assert isinstance(outcome, str)
        assert 0 <= probability <= 1
        
        # After measurement, state should be normalized
        assert np.allclose(np.sum(np.abs(state.amplitudes)**2), 1.0)
    
    def test_simulator_creation(self):
        """Test creating anyonic simulator."""
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        assert simulator.anyon_type is fib
    
    def test_simulation_execution(self):
        """Test running simulations."""
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        # Create simple braid
        gen = BraidGenerator(0, BraidDirection.OVER)
        braid = BraidWord([gen], 2)
        braid.metadata['anyon_labels'] = ["I", "I"]
        
        result = simulator.simulate(braid, shots=100)
        
        assert isinstance(result.counts, dict)
        assert result.total_shots == 100
        assert result.simulation_time > 0
        assert 'n_braids' in result.metadata
    
    def test_statevector_simulation(self):
        """Test statevector simulation."""
        fib = FibonacciAnyons()
        simulator = AnyonicSimulator(fib)
        
        gen = BraidGenerator(0, BraidDirection.OVER)
        braid = BraidWord([gen], 2)
        braid.metadata['anyon_labels'] = ["I", "I"]
        
        final_state = simulator.simulate_statevector(braid)
        
        assert isinstance(final_state, AnyonicState)
        assert final_state.n_anyons == 2


class TestOptimization:
    """Test braid optimization algorithms."""
    
    def test_optimizer_creation(self):
        """Test creating braid optimizer."""
        fib = FibonacciAnyons()
        optimizer = BraidOptimizer(fib)
        
        assert optimizer.anyon_type is fib
        assert optimizer.target_fidelity == 0.99
    
    def test_basic_optimization(self):
        """Test basic braid optimization."""
        fib = FibonacciAnyons()
        optimizer = BraidOptimizer(fib)
        
        # Create braid with obvious simplification
        generators = [
            BraidGenerator(0, BraidDirection.OVER),
            BraidGenerator(0, BraidDirection.UNDER),
            BraidGenerator(1, BraidDirection.OVER)
        ]
        braid = BraidWord(generators, 3)
        
        optimized = optimizer.optimize(braid, strategy='greedy')
        
        # Should be simplified
        assert len(optimized) < len(braid)
    
    def test_rotation_approximation(self):
        """Test rotation approximation with braids."""
        fib = FibonacciAnyons()
        optimizer = BraidOptimizer(fib)
        
        # Approximate a rotation
        braid = optimizer.approximate_rotation('X', np.pi/4, 0)
        
        assert isinstance(braid, BraidWord)
        assert len(braid) > 0


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_compilation_pipeline(self):
        """Test complete compilation and simulation pipeline."""
        from qiskit import QuantumCircuit
        
        # Create test circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        
        # Compile to braids
        compiler = TopologicalCompiler(FibonacciAnyons())
        compilation_result = compiler.compile(qc)
        
        # Simulate braids
        simulation_result = compiler.simulator.simulate(
            compilation_result.braid_program,
            shots=1000
        )
        
        # Check results
        assert isinstance(simulation_result.counts, dict)
        assert simulation_result.total_shots == 1000
        assert compilation_result.fidelity_estimate > 0
    
    def test_different_anyon_types(self):
        """Test compilation with different anyon types."""
        from qiskit import QuantumCircuit
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        # Test with Fibonacci anyons
        fib_compiler = TopologicalCompiler(FibonacciAnyons())
        fib_result = fib_compiler.compile(qc)
        
        # Test with Ising anyons
        ising_compiler = TopologicalCompiler(IsingAnyons())
        ising_result = ising_compiler.compile(qc)
        
        # Both should produce valid results
        assert isinstance(fib_result.braid_program, BraidWord)
        assert isinstance(ising_result.braid_program, BraidWord)
    
    def test_large_circuit_handling(self):
        """Test handling of larger circuits."""
        from qiskit import QuantumCircuit
        
        # Create larger test circuit
        n_qubits = 4
        qc = QuantumCircuit(n_qubits)
        
        # Add various gates
        for i in range(n_qubits):
            qc.h(i)
        
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        
        qc.measure_all()
        
        compiler = TopologicalCompiler(FibonacciAnyons())
        result = compiler.compile(qc)
        
        assert len(result.braid_program) > 0
        assert len(result.anyon_mapping) == n_qubits
    
    def test_error_handling(self):
        """Test error handling in integration scenarios."""
        from qiskit import QuantumCircuit
        
        compiler = TopologicalCompiler(FibonacciAnyons())
        
        # Test with invalid circuit
        invalid_qc = QuantumCircuit(0)
        
        with pytest.raises(ValueError):
            compiler.compile(invalid_qc)


# Fixtures for testing
@pytest.fixture
def fibonacci_anyons():
    """Fixture providing Fibonacci anyons."""
    return FibonacciAnyons()


@pytest.fixture
def ising_anyons():
    """Fixture providing Ising anyons."""
    return IsingAnyons()


@pytest.fixture
def simple_braid():
    """Fixture providing a simple test braid."""
    generators = [
        BraidGenerator(0, BraidDirection.OVER),
        BraidGenerator(1, BraidDirection.UNDER)
    ]
    return BraidWord(generators, 3)


@pytest.fixture
def bell_circuit():
    """Fixture providing a Bell state circuit."""
    from qiskit import QuantumCircuit
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


if __name__ == '__main__':
    pytest.main([__file__])
