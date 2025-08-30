import json
import subprocess
from pathlib import Path


def preprocess_headers(
    files: list[str],
    includes: list[str] = None,
    defines: dict[str, any] = None,
    output_dir: str = None,
    output_name: str = None,
    cwd: str = None,
) -> Path:
    """
    Preprocess multiple C headers into a single `.i` file using Clang

        `clang -E -P -x c {header}`

    Parameters:
        files (List[str]): Header files to include
        includes (List[str], optional): Additional include directories (`-I`)
        output_dir (str, optional): Directory to store the generated `.i` file. Defaults to current directory
        output_name (str, optional): Base name (without extension) for the output `.h`/`.i` files
        defines (list[str], optional): List of macro definitions (`-D`). Currently unused
        cwd (str, optional): Directory in which to run the Clang process

    Returns:
        Path: Path to the generated preprocessed `.i` file
    """
    includes = includes or []
    output_dir = Path(output_dir or ".").resolve()
    output_name = output_name or "header"

    output_dir.mkdir(parents=True, exist_ok=True)
    header_file = output_dir / f"{output_name}.h"
    output_file = output_dir / f"{output_name}.i"

    # create header file
    with open(header_file, "w") as f:
        content = [f'#include "{file}"' for file in files]
        f.write("\n".join(content))

    cmd = ["clang"]  # invoke the Clang compiler
    cmd += ["-E"]  # run only the preprocessor stage
    # cmd += ["-P"]  # suppress #line directives in output for cleaner result
    cmd += ["-x", "c"]  # explicitly set the language to C

    for path in includes:
        cmd += ["-I", path]

    if defines:
        for marco, value in defines.items():
            cmd += ["-D", f"{marco}={value}" if value else marco]

    cmd += [str(header_file)]
    cmd += ["-o", str(output_file)]

    res = subprocess.run(cmd, capture_output=True, cwd=cwd)
    if res.returncode != 0:
        print("\n" + " ".join(cmd) + "\n")
        raise RuntimeError(res.stderr.decode())

    return output_file


def generate_ast_dict(input_file: str, output_dir: str = None, cwd: str = None) -> dict:
    """
    Convert a preprocessed C file (.i) to Clang AST in JSON format

        `clang -Xclang -ast-dump=json -fsyntax-only header.i -x c`

    Parameters:
        input_file (str): Path to the `.i` file to process
        cwd (str, optional): Working directory for running Clang

    Returns:
        Path: Path to the generated `.json` AST file
    """
    input_file = Path(input_file).resolve()

    cmd = ["clang"]  # invoke the Clang compiler
    cmd += ["-Xclang", "-ast-dump=json"]  # request Clang to dump the AST in JSON format
    cmd += ["-fsyntax-only"]  # only check syntax; do not generate code
    cmd += [str(input_file)]  # input preprocessed C file (.i)
    cmd += ["-x", "c"]  # explicitly set the language to C

    res = subprocess.run(cmd, capture_output=True, cwd=cwd)
    if res.returncode != 0:
        print("\n" + " ".join(cmd) + "\n")
        raise RuntimeError(res.stderr.decode())

    content = res.stdout.decode()
    ast = json.loads(content)

    if output_dir is not None:
        with open(Path(output_dir) / f"{input_file.stem}.json", "w") as f:
            f.write(content)

    return ast
