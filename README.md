## Overview

This repository contains the main implementation for the paper:

**"A Comparative Study of Caching Approaches for Symbolic Regression via Genetic Programming"**

The project evaluates different caching strategies applied to symbolic regression using genetic programming.

---

## Features

* Implementation of multiple caching strategies
* Benchmarking of:

  * Overall runtime
  * Execution runtime of evaluation functions
  * Memory (RAM) usage (average and peak)
* Modular design for testing different cache configurations

---



## Parameter

* `cache_type`: Selects the caching strategy
  Available options: `LRU`, `FIFO`, `LFU`, `RR`, `SLRU`, `2Q`, `ARC`, `TinyLFU`


---

## Notes

* Ensure that datasets and experimental settings match those described in the paper for reproducibility.
* Results may vary depending on hardware and system configuration.


