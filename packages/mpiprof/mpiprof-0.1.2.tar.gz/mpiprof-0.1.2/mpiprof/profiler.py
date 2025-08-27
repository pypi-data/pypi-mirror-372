import time
import traceback

class MPIProfiler:
    """Call profiler for mpi4py."""
    def __init__(self, comm):
        """Initialise.

        Parameters
        ----------
        comm: object
            most likely, mpi4py.COMM_WORLD or a similar object
        """
        self.comm = comm
        self.rank = comm.Get_rank()
        self.statistics = {}  # To store call stack timings
        # Define the MPI functions to wrap
        self._mpi_methods = [
            'bcast', 'Bcast', 'gather', 'Gather', 'scatter', 'Scatter', 'allgather', 'Allgather', 'alltoall', 
            'Alltoall', 'Scatterv', 'Gatherv', 'Allgatherv', 'Alltoallv', 'Alltoallw',
            'Reduce_scatter', 'Scan', 'Exscan',
        ]
        # Wrap each MPI method
        for name in dir(self.comm):
            if not name.startswith('_'):
                setattr(self, name, getattr(self.comm, name))
        for method in self._mpi_methods:
            if hasattr(self.comm, method):
                original_method = getattr(self.comm, method)
                if callable(original_method):
                    wrapped_method = self._wrap_mpi_method(original_method, method)
                    setattr(self, method, wrapped_method)
        self.last_mpi_time = time.time()  # Last time an MPI call was completed
            
    def _get_call_stack(self):
        """Extract caller information."""
        frame_stack = traceback.extract_stack()
        # Return (filename, lineno) excluding this wrapper class's frames
        return [f'{frame.filename}:{frame.lineno}' for frame in frame_stack[:-2]]

    def _wrap_mpi_method(self, mpi_function, func_name):
        """Make forwarded which records call information."""
        def wrapper(*args, **kwargs):
            since_last_call = time.time() - self.last_mpi_time
            call_stack = self._get_call_stack()

            # Call the original MPI function
            start_time = time.time()
            result = mpi_function(*args, **kwargs)
            end_time = time.time()

            duration = end_time - start_time

            # Record statistics
            self._record_statistics(func_name, call_stack, duration, since_last_call)
            self.last_mpi_time = time.time()
            return result
        return wrapper

    def _record_statistics(self, func_name, call_stack, duration, since_last_call):
        """Store statistics for this type of call."""
        call_key = (func_name, tuple(call_stack))
        if call_key not in self.statistics:
            self.statistics[call_key] = {'count': 0, 'durations': 0, 'since_last_call': 0}
        self.statistics[call_key]['count'] += 1
        self.statistics[call_key]['durations'] += duration
        self.statistics[call_key]['since_last_call'] += since_last_call

    def write_statistics(self, prefix='MPIprofile.', suffix='.out'):
        """Write records to ascii file.
        
        Parameters
        ----------
        prefix: str
            Prefix of output file, before rank ID.
        suffix: str
            Suffix of output file, after rank ID.
        """
        start_time = time.time()
        mpi_time_total = 0
        non_mpi_time_total = 0
        # Write stats to file
        with open(f"{prefix}{self.rank}{suffix}", "w") as f:
            for call_key, data in sorted(self.statistics.items()):
                mpi_time_total += data['durations']
                non_mpi_time_total += data['since_last_call']
                func_name, call_stack = call_key
                durations = data['durations']
                count = data['count']
                since_last_calls = data['since_last_call']
                f.write(f"Function: {func_name}\n")
                f.write(f"Call stack: \n\t{"\n\t".join(call_stack)}\n")
                f.write(f"Number of calls: {count}\n")
                f.write(f"Duration During Call: {durations / count:.6f}s\n")
                f.write(f"Duration Before Call: {since_last_calls / count:.6f}s\n")
                f.write("\n")
            f.write(f"Total MPI Time: {mpi_time_total:.6f}s\n")
            f.write(f"Total Non-MPI Time: {non_mpi_time_total:.6f}s\n")
        end_time = time.time()

        # shift last call time, to subtract time spent in this function
        self.last_mpi_time += end_time - start_time
