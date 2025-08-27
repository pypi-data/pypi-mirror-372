mpiprof.py: Profiler for MPI python programs
============================================

Enables:

1. using cProfile on each launched MPI process.
2. measuring the communication overhead of your MPI setup.

mpiprof provides two complementary pieces:

1. A drop-in wrapper for cProfile that you can invoke as a module,
   ``mpiexec -n 4 python3 -m mpiprof your_script.py arg1 arg2``.
   This writes a separate .pstats file for each rank.

2. An optional ``MPIProfiler`` class that wraps a ``mpi4py.MPI.Comm`` and
   records basic timing/count statistics of MPI calls and where they came from.
   You can write the results to disk by calling ``write_statistics()``.

Installation
------------

- From pypi::

    pip install mpiprof

- From a local checkout, by cloning this repository::

    git clone https://github.com/JohannesBuchner/mpiprof.py
    cd mpiprof.py/
    pip install .

Requirements
------------
- Python 3.8+
- mpi4py
- An MPI runtime if you plan to launch under mpiexec/srun/etc.

Usage: per-rank cProfile runner
-------------------------------
Run your script under mpiexec (or srun) using the module form:

- ``mpiexec -n 4 python3 -m mpiprof your_script.py arg1 arg2``

This writes one profile file per rank named ``mpiprof.<rank>.pstats``
in the current working directory.

Options:

- ``-o / --outfile`` sets the output path or pattern (default:
  ``mpiprof.{rank}.pstats``). The literal substring ``{rank}`` will be
  replaced with the MPI rank.

Signal handling:

- mpiprof installs SIGINT and SIGTERM handlers to dump the profile
  before exiting, so Ctrl-C or a clean termination should still produce
  output. If the MPI launcher escalates to SIGKILL immediately, no tool
  can save a profile.

Usage: MPIProfiler for mpi4py
-----------------------------
The ``MPIProfiler`` wraps a communicator and measures wall-clock time
and call counts for common blocking MPI calls. It is intentionally
lightweight and safe to leave in production runs (low overhead on the
measured calls). Nonblocking calls are counted but not timed precisely
(the time recorded is call overhead, not the transfer time).

Example:

.. code-block:: python

    from mpi4py import MPI
    from mpiprof import MPIProfiler

    comm = MPIProfiler(MPI.COMM_WORLD)

    # Your MPI code as usual, using comm instead of MPI.COMM_WORLD:
    rank = comm.Get_rank()
    size = comm.Get_size()
    data = rank

    # Simple collective
    total = comm.allreduce(data, op=MPI.SUM)

    # Point-to-point
    if rank == 0:
        comm.send(b"hello", dest=1, tag=0)
    elif rank == 1:
        msg = comm.recv(source=0, tag=0)

    # Write stats at the end (one file per rank)
    comm.write_statistics()  # default name: mpiprof.stats.<rank>.json

Notes:

- The wrapper exposes common methods (e.g., ``send``, ``recv``, ``bcast``,
  ``reduce``, ``allreduce``, ``gather``, ``scatter``, ``barrier``) and
  forwards any other attributes to the underlying communicator. It tries
  to be case-insensitive to match mpi4py idioms (both ``Send`` and
  ``send`` are supported).

- For nonblocking operations (``Isend``, ``Irecv``), the wrapper records
  the call count but cannot attribute data transfer time unless you also
  wrap and time ``Wait``/``Waitall``. A simple ``wait`` wrapper is
  provided to time individual requests returned by the wrapper.

Rank detection
--------------
The runner tries to detect the rank via common environment variables:

- ``OMPI_COMM_WORLD_RANK``, ``PMIX_RANK`` (Open MPI)
- ``PMI_RANK`` (MPICH, Intel MPI)
- ``MV2_COMM_WORLD_RANK`` (MVAPICH2)
- ``SLURM_PROCID`` (scheduler fallback)
- default: 0 if none found

Output files
------------
- Runner: ``mpiprof.<rank>.pstats`` (or the pattern you set with ``-o``).
  You can analyze it with ``pstats`` or tools like ``snakeviz``:

  - ``python3 -m pstats mpiprof.0.pstats``
  - ``snakeviz mpiprof.0.pstats``

- MPIProfiler: ``mpiprof.stats.<rank>.json`` with operation counts and
  total wall-clock time per operation.

Limitations
-----------
- The runner cannot save profiles if the process is killed by SIGKILL.
- MPIProfiler’s accounting for nonblocking calls is approximate unless
  you consistently call ``wait``/``waitall`` on the requests returned
  by the wrapper’s nonblocking methods.

License
-------
MIT

