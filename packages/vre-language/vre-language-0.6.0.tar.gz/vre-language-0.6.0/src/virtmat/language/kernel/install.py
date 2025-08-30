"""utility module to install the custom texts/textm jupyter kernel"""
import argparse
import json
import os
import shutil
import sys
from tempfile import TemporaryDirectory
from jupyter_client.kernelspec import KernelSpecManager

kernel_json = {
    "argv": [sys.executable, "-m", "virtmat.language.kernel", "-f", "{connection_file}"],
    "display_name": "textS/textM",
    "language": "text"
}


def install_my_kernel_spec(user=True, prefix=None):
    """create the kernel JSON file and install it"""
    with TemporaryDirectory() as temp_dir:
        os.chmod(temp_dir, 0o755)  # Starts off as 700, not user readable
        with open(os.path.join(temp_dir, 'kernel.json'), 'w', encoding='utf-8') as f:
            json.dump(kernel_json, f, sort_keys=True)
        # Use logo files from kernel root directory
        cur_path = os.path.dirname(os.path.realpath(__file__))
        for logo in ['logo-32x32.png', 'logo-64x64.png']:
            try:
                shutil.copy(os.path.join(cur_path, logo), temp_dir)
            except FileNotFoundError:
                print("Custom logo files not found. Default logos will be used.")
        KernelSpecManager().install_kernel_spec(temp_dir, 'texts', user=user, prefix=prefix)


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


def main(argv=None):
    """main function in module"""
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', action='store_true',
                    help="Install to the per-user kernels registry. Default if not root.")
    ap.add_argument('--sys-prefix', action='store_true',
                    help="Install to sys.prefix (e.g. a virtualenv or conda env)")
    ap.add_argument('--prefix',
                    help="Install to the given prefix. "
                         "Kernelspec will be installed in {PREFIX}/share/jupyter/kernels/")
    args = ap.parse_args(argv)

    if args.sys_prefix:
        args.prefix = sys.prefix
    if not args.prefix and not _is_root():
        args.user = True

    install_my_kernel_spec(user=args.user, prefix=args.prefix)


if __name__ == '__main__':
    main()
