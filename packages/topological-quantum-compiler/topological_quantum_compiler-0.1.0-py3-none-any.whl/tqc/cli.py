"""Command-line interface for the Topological Quantum Compiler."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from tqc import TopologicalCompiler, create_compiler, get_supported_anyons
from tqc.anyons import get_anyon_type
from tqc.braids import BraidWord, BraidGenerator, BraidDirection
from tqc._version import __version__


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def compile_qasm_file(filepath: str, anyon_type: str, 
                     optimization_level: int, output_file: Optional[str]) -> None:
    """Compile a QASM file to braid sequences."""
    from qiskit import QuantumCircuit
    
    try:
        # Load quantum circuit
        circuit = QuantumCircuit.from_qasm_file(filepath)
        print(f"Loaded quantum circuit with {circuit.num_qubits} qubits and {len(circuit.data)} gates")
        
        # Create compiler
        compiler = create_compiler(anyon_type, optimization_level=optimization_level)
        
        # Compile circuit
        print(f"Compiling with {anyon_type} anyons...")
        result = compiler.compile(circuit)
        
        # Display results
        print(f"\nCompilation Results:")
        print(f"  Original gates: {result.compilation_stats['original_gates']}")
        print(f"  Compiled braids: {len(result.braid_program)}")
        print(f"  Estimated fidelity: {result.fidelity_estimate:.4f}")
        print(f"  Braid sequence: {result.braid_program}")
        
        # Save results if requested
        if output_file:
            save_results(result, output_file)
            print(f"\nResults saved to {output_file}")
            
    except Exception as e:
        print(f"Error compiling circuit: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_mode() -> None:
    """Run interactive compilation mode."""
    print("Topological Quantum Compiler - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit\n")
    
    # Default settings
    anyon_type = "fibonacci"
    optimization_level = 1
    n_strands = 4
    
    compiler = create_compiler(anyon_type, optimization_level=optimization_level)
    current_braid = BraidWord([], n_strands)
    
    while True:
        try:
            command = input("tqc> ").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "help":
                print_help()
            elif command.startswith("set anyon"):
                new_type = command.split()[-1]
                if new_type in get_supported_anyons():
                    anyon_type = new_type
                    compiler = create_compiler(anyon_type, optimization_level=optimization_level)
                    print(f"Anyon type set to: {anyon_type}")
                else:
                    print(f"Unsupported anyon type. Supported: {get_supported_anyons()}")
            elif command.startswith("add braid"):
                parts = command.split()
                if len(parts) >= 3:
                    try:
                        index = int(parts[2])
                        direction = BraidDirection.OVER
                        if len(parts) > 3 and parts[3].lower() in ['under', 'inv', '-1']:
                            direction = BraidDirection.UNDER
                        
                        gen = BraidGenerator(index, direction)
                        current_braid.append(gen)
                        print(f"Added generator: {gen}")
                    except ValueError:
                        print("Invalid braid index")
                else:
                    print("Usage: add braid <index> [over|under]")
            elif command == "show braid":
                print(f"Current braid: {current_braid}")
                print(f"Length: {len(current_braid)}")
            elif command == "clear braid":
                current_braid = BraidWord([], n_strands)
                print("Braid cleared")
            elif command == "optimize":
                optimized = compiler.optimizer.optimize(current_braid)
                print(f"Optimized: {len(current_braid)} -> {len(optimized)} braids")
                current_braid = optimized
            elif command == "simulate":
                if len(current_braid) > 0:
                    result = compiler.simulator.simulate(current_braid, shots=1000)
                    print(f"Simulation results: {result.counts}")
                    print(f"Simulation time: {result.simulation_time:.3f}s")
                else:
                    print("No braid to simulate")
            elif command == "visualize":
                if len(current_braid) > 0:
                    svg = current_braid.visualize()
                    filename = "interactive_braid.svg"
                    with open(filename, 'w') as f:
                        f.write(svg)
                    print(f"Braid diagram saved to {filename}")
                else:
                    print("No braid to visualize")
            elif command.startswith("strands"):
                parts = command.split()
                if len(parts) > 1:
                    try:
                        n_strands = int(parts[1])
                        current_braid = BraidWord([], n_strands)
                        print(f"Number of strands set to: {n_strands}")
                    except ValueError:
                        print("Invalid number of strands")
                else:
                    print(f"Current strands: {n_strands}")
            else:
                print(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")


def print_help() -> None:
    """Print help text for interactive mode."""
    help_text = """
Available commands:
  help                    - Show this help
  quit/exit              - Exit interactive mode
  
  set anyon <type>       - Set anyon type (fibonacci, ising)
  strands [n]            - Set/show number of strands
  
  add braid <i> [dir]    - Add braid generator σᵢ (dir: over/under)
  show braid             - Show current braid sequence
  clear braid            - Clear current braid
  
  optimize               - Optimize current braid
  simulate               - Simulate current braid
  visualize              - Save braid diagram as SVG
"""
    print(help_text)


def save_results(result, filename: str) -> None:
    """Save compilation results to file."""
    with open(filename, 'w') as f:
        f.write(f"Topological Quantum Compiler Results\n")
        f.write(f"====================================\n\n")
        f.write(f"Original Circuit:\n")
        f.write(f"  Qubits: {result.original_circuit.num_qubits}\n")
        f.write(f"  Gates: {result.compilation_stats['original_gates']}\n\n")
        f.write(f"Compilation:\n")
        f.write(f"  Anyon type: {result.braid_program.metadata.get('anyon_type', 'Unknown')}\n")
        f.write(f"  Braids: {len(result.braid_program)}\n")
        f.write(f"  Fidelity: {result.fidelity_estimate:.6f}\n")
        f.write(f"  Optimization time: {result.compilation_stats.get('optimization_time', 0):.3f}s\n\n")
        f.write(f"Braid Sequence:\n")
        f.write(f"  {result.braid_program}\n\n")
        f.write(f"Anyon Mapping:\n")
        for qubit, anyon in result.anyon_mapping.items():
            f.write(f"  Qubit {qubit} -> Anyon {anyon}\n")


def benchmark_mode(anyon_type: str, max_qubits: int) -> None:
    """Run benchmarking tests."""
    print(f"TQC Benchmarking - {anyon_type} anyons, up to {max_qubits} qubits")
    print("=" * 60)
    
    from qiskit import QuantumCircuit
    import time
    
    compiler = create_compiler(anyon_type)
    
    for n_qubits in range(2, max_qubits + 1):
        # Create test circuit
        qc = QuantumCircuit(n_qubits)
        for i in range(n_qubits):
            qc.h(i)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        
        # Time compilation
        start_time = time.time()
        result = compiler.compile(qc)
        compile_time = time.time() - start_time
        
        # Time simulation
        start_time = time.time()
        sim_result = compiler.simulator.simulate(result.braid_program, shots=100)
        sim_time = time.time() - start_time
        
        print(f"{n_qubits:2d} qubits: {len(result.braid_program):4d} braids, "
              f"compile: {compile_time:6.3f}s, simulate: {sim_time:6.3f}s, "
              f"fidelity: {result.fidelity_estimate:.3f}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Topological Quantum Compiler - Compile quantum circuits to anyonic braids",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tqc-cli circuit.qasm                    # Compile QASM file with Fibonacci anyons
  tqc-cli -a ising -o 2 circuit.qasm     # Use Ising anyons with optimization level 2
  tqc-cli --interactive                   # Start interactive mode
  tqc-cli --benchmark --max-qubits 6     # Run benchmarks up to 6 qubits
        """
    )
    
    parser.add_argument('--version', action='version', version=f'TQC {__version__}')
    
    parser.add_argument('file', nargs='?', 
                       help='QASM file to compile (required unless using --interactive or --benchmark)')
    
    parser.add_argument('-a', '--anyon-type', 
                       choices=get_supported_anyons(),
                       default='fibonacci',
                       help='Type of anyons to use (default: fibonacci)')
    
    parser.add_argument('-o', '--optimization-level',
                       type=int, choices=[0, 1, 2, 3],
                       default=1,
                       help='Optimization level 0-3 (default: 1)')
    
    parser.add_argument('--output', '-f',
                       help='Save compilation results to file')
    
    parser.add_argument('--interactive', '-i',
                       action='store_true',
                       help='Start interactive compilation mode')
    
    parser.add_argument('--benchmark', '-b',
                       action='store_true',
                       help='Run benchmarking tests')
    
    parser.add_argument('--max-qubits',
                       type=int, default=8,
                       help='Maximum qubits for benchmarking (default: 8)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    print(f"Topological Quantum Compiler v{__version__}")
    print(f"Using {args.anyon_type} anyons\n")
    
    if args.interactive:
        interactive_mode()
    elif args.benchmark:
        benchmark_mode(args.anyon_type, args.max_qubits)
    elif args.file:
        compile_qasm_file(args.file, args.anyon_type, 
                         args.optimization_level, args.output)
    else:
        parser.print_help()
        print("\nError: Must specify input file, --interactive, or --benchmark")
        sys.exit(1)


if __name__ == '__main__':
    main()
