import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--install",
                        dest='install',
                        action='store_true',
                        help='Whether to install the lint env.')
    parser.add_argument("-d",
                        "--diff",
                        dest='diff',
                        action='store_true',
                        help='Whether only show the diff without applying.')
    args = parser.parse_args()
    source = "https://mirrors.aliyun.com/pypi/simple/"
    if args.install:
        requires = os.path.join(
            os.path.split(__file__)[0], "requirements-dev.txt")
        assert os.system(
            f"{sys.executable} -m pip install -r {requires} -i {source}") == 0
        assert os.system(
            f"{sys.executable} -m pip install lintrunner lintrunner-adapters -i {source}"
        ) == 0
        assert os.system("lintrunner init")
    if args.diff:
        assert os.system(
            "lintrunner --force-color --all-files --tee-json=lint.json -v"
        ) == 0
    else:
        # Directly apply.
        assert os.system("lintrunner -a") == 0


if __name__ == "__main__":
    main()
