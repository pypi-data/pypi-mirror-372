# What does "VRE language" mean?

This is a [Domain-Specific Language (DSL)](https://en.wikipedia.org/wiki/Domain-specific_language) to be used in a [Virtual Research Environment](https://en.wikipedia.org/wiki/Virtual_research_environment) in the [VirtMat projects](https://www.materials.kit.edu/virtmat_current_projects.php). This means it is a computer language using domain-specific notations and abstractions rather than such commonly used in general purpose languages such as Python. For example, in our DSL there are no for-loops and classes (that are used in Python) and no workflows and workflow node objects (used in workflow DSLs). But we have objects such as atoms and molecules and semantics to perform specific operations on these.

# Requirements

## Domain concepts

The DSL totally depends on how we define our domain. In this VRE language, we define our domain as *materials modelling* domain that is a subdomain of *scientific computing* and has subdomains such as *atomistic modeling* and *molecular modeling*. Particularly, support of physical units by the language is a common concept for all these domains. Nevertheless, these domains can still be defined in different ways. Therefore, we base *our domain definition* on a set of use cases. We generally look at [this repository](https://gitlab.kit.edu/kit/virtmat-tools/virtmat-models-and-data-analyses) for relevant use cases to define our domain. **You are welcome to contribute with further uses cases to the further development of the VRE language.** To get involved, please fork [the use case repository](https://gitlab.kit.edu/kit/virtmat-tools/virtmat-models-and-data-analyses), add your use case and create a merge request.

## Requirements from the community and the target platform

Apart from the domain-specific notations, our VRE language has to satisfy further requirements:

1. Support a full life cycle of modeling, simulation and data analysis. A model should be accessible and extensible dynamically, at any time. This is what we call *persistence* and *dynamics* of the model. To satisfy this requirement, we connect the interpreter to a workflow management system equipped with a database.
2. Use [Jupyter](https://jupyter.org/) as a front-end system. This poses a challenge for models with persistence and on the other hand a new Jupyter kernel with the VRE language interpreter has to be developed.
3. Make the complex workflow management systems and HPC systems / batch systems *transparent*. This is not obvious and also not trivial to implement. Particularly, notations in the program code about the granularity (which statements belong to the same workflow node) and the computing resources needed (such as computing time, number of CPUs, memory, disk space, ...) are necessary for computational performance or other practical reasons but difficult to hide completely from the language.
4. Use Python as a language for the interpreter. This is due to the fact that a plenty of libraries (APIs) for Python in the domain already exist: the [Atomic Simulation Environment (ASE)](https://wiki.fysik.dtu.dk/ase/), [Python Materials Genomics (Pymatgen)](https://pymatgen.org/) and [PyIron](https://pyiron.org/), to name only a few. These libraries cover the most relevant aspects of their domains but still are used in the general-purpose language Python. The use of Python implies in turn that a workflow management system and system of physical units providing Python APIs are required.

# Development status

The current developement status of the VRE language is *beta*.

If you are interested, you can have a look at the [issues](https://gitlab.kit.edu/kit/virtmat-tools/vre-language/-/issues) and even start contributing by forking and creating merge requests.

If you want to use workflows for modeling and data analysis using Python in Jupyter you can start testing the [VRE middleware](https://gitlab.kit.edu/kit/virtmat-tools/vre-middleware) that is currently in *beta* state.

# Documentation

An installation guide and comprehensive documentation is provided on [these pages](https://vre-language.readthedocs.io).

# Support

If you need support or have any questions about VRE Language please write a message to virtmat-tools@lists.kit.edu.
