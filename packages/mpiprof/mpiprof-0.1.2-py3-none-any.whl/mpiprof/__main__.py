#!/usr/bin/env python3
import sys, os, runpy, cProfile, signal, atexit
import argparse

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="python -m mpiprof",
        description="Per-rank cProfile runner for MPI-launched Python programs."
    )
    parser.add_argument(
        "-o", "--outfile",
        default=os.environ.get("MPIPROF_OUT", "mpiprof.{rank}.pstats"),
        help="Output file or pattern (default: mpiprof.{rank}.pstats). "
             "Use {rank} to insert the MPI rank."
    )
    parser.add_argument(
        "script",
        help="Path to the Python script to run under profiling"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to the script (prefix with -- to stop parsing)"
    )

    if not argv:
        parser.print_help(sys.stderr)
        return 2

    # Allow: python -m mpiprof -o out -- script.py args...
    # argparse will include leading '--' in args; strip a single leading '--' if present.
    # We parse once, then clean args.
    ns = parser.parse_args(argv)
    rank = os.environ.get('OMPI_COMM_WORLD_RANK', os.environ.get('PMIX_RANK',
        os.environ.get('PMI_RANK', os.environ.get('MV2_COMM_WORLD_RANK',
        os.environ.get('SLURM_PROCID', "0")))))
    outfile = ns.outfile.replace('{rank}', rank)
    script = ns.script
    if ns.args and ns.args[0] == "--":
        args = [script] + list(ns.args)[1:]
    else:
        args = [script] + list(ns.args)
    sys.argv = args  # pass original args to the target script

    pr = cProfile.Profile()
    dumped = {"done": False}

    def dump_and_exit(code=0):
        if dumped["done"]:
            # Avoid double-dump from atexit + signal
            sys.exit(code)
        dumped["done"] = True
        try:
            pr.disable()
        except Exception:
            pass
        try:
            pr.dump_stats(outfile)
        except Exception as e:
            try:
                sys.stderr.write(f"Failed to dump profile to {outfile}: {e}\n")
            except Exception:
                pass
        sys.exit(code)

    def _sig_handler(signum, frame):
        # 130 for SIGINT, 143 for SIGTERM, like shells do
        print("got signal:", signum)
        dump_and_exit(130 if signum == signal.SIGINT else 143)

    # Dump on normal interpreter shutdown too
    atexit.register(lambda: dump_and_exit(0))

    # Install handlers early
    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    pr.enable()
    # Run the target script as __main__
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        # Respect the script's exit code; still dump the profile
        code = e.code if isinstance(e.code, int) else 0
        dump_and_exit(code)
    except BaseException:
        # Ensure the profile is dumped before propagating
        import traceback
        traceback.print_exc()
        dump_and_exit(1)
        

if __name__ == "__main__":
    raise SystemExit(main())
