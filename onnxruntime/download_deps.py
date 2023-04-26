import argparse
import os
import subprocess
import sys


def run_cmd(cmd, timeout=None):
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(timeout=timeout)
    stdout = stdout.decode()
    stderr = stderr.decode()
    return (proc.returncode, stdout, stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", required=True, help="Base dirs for dependencies")
    parser.add_argument(
        "-t", "--timeout", default="15", help="Timeout time in secondes")
    args = parser.parse_args()
    with open(os.path.join(os.path.split(__file__)[0], "dep_map.txt")) as fin:
        for line in fin:
            line = line.strip()
            segs = line.split(",")
            if len(segs) != 2:
                continue
            local_dir = os.path.join(args.dir, segs[1])
            os.system(f"mkdir -p {local_dir}")
            local_file = os.path.join(local_dir, os.path.split(segs[0])[-1])
            if os.path.exists(local_file):
                print(f"{local_file} exists, skip.")
                continue
            cmd = f"wget -c {segs[0]} -O {local_file}"
            print(f"Running: {cmd}")
            retries = 3
            for i in range(retries):
                code, stdout, stderr = run_cmd(cmd.split(),
                                               float(args.timeout))
                if code != 0:
                    if i + 1 == retries:
                        print(
                            f"{i}:Run {cmd} with stdout: {stdout}\nstderr: {stderr}"
                        )
                        sys.exit(1)
                    else:
                        print("Retrying...")
                else:
                    # Succeed.
                    break


if __name__ == "__main__":
    main()
