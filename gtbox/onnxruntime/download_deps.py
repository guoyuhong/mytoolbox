import argparse
import os
import subprocess
import sys
import platform
import time
import hashlib
import threading

HOME = os.path.expanduser('~')
DEPS = os.path.join(HOME, ".gtbox/onnxruntime/deps")
SAVE = os.path.join(HOME, ".gtbox/onnxruntime/deps_save")


def run_cmd(cmd, timeout):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output_lines = []

    def stdout_thread():
        nonlocal output_lines
        for line in proc.stdout:
            output_lines.append(line)

    def stderr_thread():
        nonlocal output_lines
        for line in proc.stderr:
            output_lines.append(line)

    prev_count = 0
    thread1 = threading.Thread(target=stdout_thread)
    thread2 = threading.Thread(target=stderr_thread)
    thread1.start()
    thread2.start()
    tik = 0
    last_valid_tik = 0
    while True:
        time.sleep(1)
        tik += 1
        cur = len(output_lines)
        if cur != prev_count:
            for i in range(prev_count, cur):
                print(output_lines[i].decode().rstrip())
            last_valid_tik = tik
            prev_count = cur
        elif proc.poll() is not None:
            break
        if last_valid_tik - tik > timeout:
            proc.kill()
            return 1

    return proc.returncode


class DepItem:

    def __init__(self, name, url, sha1):
        self.name = name
        self.url = url
        self.sha1 = sha1

    def __repr__(self) -> str:
        return f"{self.name}:{self.url}:{self.sha1}"


def parse_deps(resource_file):
    resource_map = {}
    with open(resource_file, "r") as fin:
        for line in fin:
            line = line.strip()
            if "protoc-" in line:
                continue
            if platform.system() != "Windows" and ("win32" in line
                                                   or "win64" in line):
                continue
            if platform.machine() == "x86_64" and "aarch_64" in line:
                continue
            if line.startswith("#"):
                continue
            segs = line.split(";")
            if len(segs) != 3:
                continue
            resource_map[segs[0]] = DepItem(segs[0], segs[1], segs[2])
    return resource_map


def download_deps(resource_map, timeout):
    may_have_diff_sha1 = ["curl"]
    for key in resource_map:
        item = resource_map[key]
        local_dir = os.path.join(DEPS,
                                 f"{key}-subbuild/{key}-populate-prefix/src")
        os.system(f"mkdir -p {local_dir}")
        local_file = os.path.join(local_dir, os.path.split(item.url)[-1])
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            # Check the sha1.
            with open(local_file, "rb") as f:
                bytes = f.read()  # read entire file as bytes
                readable_hash = hashlib.sha1(bytes).hexdigest()
                if readable_hash == item.sha1:
                    print(f"{local_file} exists, skip.")
                    continue
                elif key in may_have_diff_sha1:
                    continue
        cmd = f"wget -c {item.url} -O {local_file} --no-check-certificate"
        print(f"Running: {cmd}")
        retries = 5
        for i in range(retries):
            code = run_cmd(cmd.split(), float(timeout))
            if code != 0:
                if i + 1 == retries:
                    print(f"{i}:Run {cmd} failed")
                    os.system(f"rm -rf {local_file}")
                    sys.exit(1)
                else:
                    print("Retrying...")
            else:
                # Succeed.
                break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="Base dirs for dependencies")
    parser.add_argument("-t",
                        "--timeout",
                        default="5",
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
    parser.add_argument(
        "-f",
        "--file",
        default="",
        help=
        'The deps.txt file, if not provide, it assumes PWD the root of ORT.')
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
    if len(args.file) == 0:
        dep_file = os.path.join(os.getcwd(), "cmake/deps.txt")
    else:
        dep_file = args.file
    if not os.path.exists(dep_file):
        raise Exception(f"{dep_file} does not exist! " +
                        "Go to ORT git root or parse by --file")
    resource_map = parse_deps(dep_file)
    download_deps(resource_map, args.timeout)
    if args.dir is None:
        return
    name_change_map = {
        "json": "nlohmann_json",
    }
    if os.path.exists(SAVE):
        print(f"{SAVE} exists, copy from {SAVE} to {args.dir}")
        assert os.system(f"mkdir -p {args.dir}") == 0
        assert os.system(f"cp -rf {SAVE}/* {args.dir}/") == 0
    else:
        for key in resource_map:
            if key in name_change_map:
                use_key = name_change_map[key]
            else:
                use_key = key
            src = os.path.join(DEPS,
                               f"{key}-subbuild/{key}-populate-prefix/src")
            dst = os.path.join(
                args.dir, f"{use_key}-subbuild/{use_key}-populate-prefix/src")
            assert os.system(f"mkdir -p {dst}") == 0
            print(f"cp -r {src}/* {dst}")
            assert os.system(f"cp -r {src}/* {dst}") == 0


if __name__ == "__main__":
    main()
