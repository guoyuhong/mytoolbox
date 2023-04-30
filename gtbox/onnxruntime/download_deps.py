import argparse
import os
import subprocess
import sys

HOME = os.path.expanduser('~')
DEPS = os.path.join(HOME, ".gtbox/onnxruntime/deps")
SAVE = os.path.join(HOME, ".gtbox/onnxruntime/deps_save")
DEP_FILE = os.path.join(
    os.path.split(__file__)[0], "../data/onnxruntime/dep_map.txt")


def run_cmd(cmd, timeout=None):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        return (1, f"Timeout of {timeout} seconds", "")
    stdout = stdout.decode()
    stderr = stderr.decode()
    return (proc.returncode, stdout, stderr)


def download_deps(resource_file, timeout):
    resource_map = {}
    with open(resource_file, "r") as fin:
        for line in fin:
            line = line.strip()
            segs = line.split(",")
            if len(segs) != 2:
                continue
            local_dir = os.path.join(DEPS, segs[1])
            resource_map[segs[1]] = segs[0]
            os.system(f"mkdir -p {local_dir}")
            local_file = os.path.join(local_dir, os.path.split(segs[0])[-1])
            if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
                print(f"{local_file} exists, skip.")
                continue
            cmd = f"wget -c {segs[0]} -O {local_file}"
            print(f"Running: {cmd}")
            retries = 3
            for i in range(retries):
                code, stdout, stderr = run_cmd(cmd.split(), float(timeout))
                if code != 0:
                    if i + 1 == retries:
                        print(
                            f"{i}:Run {cmd} with stdout: {stdout}\nstderr: {stderr}"
                        )
                        os.system(f"rm -rf {local_file}")
                        sys.exit(1)
                    else:
                        print("Retrying...")
                else:
                    # Succeed.
                    break
    return resource_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="Base dirs for dependencies")
    parser.add_argument("-t",
                        "--timeout",
                        default="15",
                        help="Timeout time in secondes")
    parser.add_argument("-s",
                        "--save",
                        dest='save',
                        action='store_true',
                        help='Whether to save the files from --dir backward.')
    parser.add_argument("-c",
                        "--clean",
                        dest='clean',
                        action='store_true',
                        help='Clean the saved repo.')
    args = parser.parse_args()
    if args.clean:
        assert os.system(f"rm -rf {SAVE}") == 0
    if args.save:
        if len(args.dir) == 0:
            raise Exception(f"--save requires --dir to set")
        assert os.system(f"mkdir -p {SAVE}") == 0
        assert os.system(f"rm -rf {SAVE}/*") == 0
        assert os.system(f"cp -r {args.dir}/* {SAVE}/") == 0
        # Remove the CMakeCache.txt files.
        assert os.system(
            f"find {SAVE} -name CMakeCache.txt | xargs rm -rf") == 0
        sys.exit(0)
    resource_map = download_deps(DEP_FILE, args.timeout)
    if args.dir is None:
        return
    if os.path.exists(SAVE):
        print(f"{SAVE} exists, copy from {SAVE} to {args.dir}")
        assert os.system(f"mkdir -p {args.dir}") == 0
        assert os.system(f"cp -rf {SAVE}/* {args.dir}/") == 0
    else:
        for resource_dir in resource_map:
            src = os.path.join(DEPS, resource_dir)
            dst = os.path.join(args.dir, resource_dir)
            assert os.system(f"mkdir -p {dst}") == 0
            assert os.system(f"cp -r {src} {dst}") == 0


if __name__ == "__main__":
    main()
