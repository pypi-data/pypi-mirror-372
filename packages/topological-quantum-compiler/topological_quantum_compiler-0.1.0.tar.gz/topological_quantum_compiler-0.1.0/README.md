# Topological Quantum Compiler (TQC)

[![PyPI version](https://badge.fury.io/py/topological-quantum-compiler.svg)](https://badge.fury.io/py/topological-quantum-compiler)
[![CI](https://github.com/krish567366/TQC/workflows/CI/badge.svg)](https://github.com/krish567366/TQC/actions)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://krish567366.github.io/TQC)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The first universal compiler for quantum computers based on topological principles.**

TQC moves beyond fragile gate-based quantum operations by compiling quantum algorithms into fault-tolerant braiding operations of anyonic quasiparticles. This revolutionary approach promises inherently stable quantum computation through topological protection.

## 🌟 Key Features

- **Topological Compilation**: Translate quantum circuits into anyonic braid operations
- **Fault Tolerance**: Inherent error protection through topological properties
- **Multiple Anyon Types**: Support for Fibonacci, Ising, and other anyonic systems
- **Advanced Simulation**: Efficient tensor network simulation of many-anyon systems
- **Optimization**: Solovay-Kitaev-style approximation algorithms for braid optimization
- **Visualization**: Generate beautiful braid diagrams and topological visualizations

## 🚀 Quick Start

```python
from tqc import TopologicalCompiler, FibonacciAnyons
from qiskit import QuantumCircuit

# Create a simple quantum circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Compile to topological braids
compiler = TopologicalCompiler(anyon_type=FibonacciAnyons())
braid_program = compiler.compile(qc)

# Simulate the braided computation
result = braid_program.simulate(shots=1000)
print(f"Measurement results: {result.counts}")

# Visualize the braid
braid_program.visualize_braid(output="bell_state_braid.svg")
```

## 📦 Installation

```bash
# Via pip
pip install topological-quantum-compiler

# Via poetry
poetry add topological-quantum-compiler

# Development installation
git clone https://github.com/krish567366/TQC.git
cd TQC
poetry install
```

## 🔬 What Makes TQC Revolutionary

Traditional quantum computers suffer from:

- **Fragile qubits** sensitive to environmental noise
- **High error rates** requiring extensive error correction
- **Limited coherence times** constraining algorithm complexity

TQC solves these problems by encoding quantum information in the **topological properties** of anyonic braids, which are:

- **Naturally fault-tolerant** - protected by energy gaps
- **Stable against local perturbations** - only global changes affect computation
- **Scalable** - complexity grows polynomially with system size

## 📚 Documentation

- [Installation Guide](https://krish567366.github.io/TQC/installation/)
- [Quick Start Tutorial](https://krish567366.github.io/TQC/quickstart/)
- [API Reference](https://krish567366.github.io/TQC/api/)
- [Advanced Examples](https://krish567366.github.io/TQC/tutorials/)

## 🎯 Example Applications

```python
# VQE with topological compilation
from tqc.algorithms import TopologicalVQE
from tqc.chemistry import H2Molecule

molecule = H2Molecule(bond_length=0.74)
vqe = TopologicalVQE(molecule, anyon_type="fibonacci")
energy = vqe.run()

# Quantum machine learning with anyonic features
from tqc.ml import AnyonicFeatureMap

feature_map = AnyonicFeatureMap(n_qubits=4, anyon_type="ising")
quantum_kernel = feature_map.to_kernel()
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Created by Krishna Bajpai (krishna@krishnabajpai.me)
- Based on groundbreaking research in topological quantum computation
- Inspired by the work of Kitaev, Freedman, and other pioneers in the field
- Built on the shoulders of excellent libraries like Qiskit, JAX, and NumPy

## 📞 Support

- 📖 [Documentation](https://krish567366.github.io/TQC)
- 🐛 [Issue Tracker](https://github.com/krish567366/TQC/issues)
- 💬 [Discussions](https://github.com/krish567366/TQC/discussions)
- 📧 Contact: Krishna Bajpai <krishna@krishnabajpai.me>

---

*"The future of quantum computing is topological."* - Krishna Bajpai, TQC Creator
