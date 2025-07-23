import os
import subprocess
import uuid
from typing import List, Generator, Union

from tree_sitter import Parser, Node
import tree_sitter_cpp as tscpp
import tree_sitter_go as tsgo
import tree_sitter_java as tsjava
import tree_sitter_typescript as tsts
import tree_sitter_rust as tsrust
import ast

# Map GitHub repo names to their top-level folder names on disk
repo_to_top_folder = {
    # Python
    "django/django": "django",
    "sphinx-doc/sphinx": "sphinx",
    "scikit-learn/scikit-learn": "scikit-learn",
    "sympy/sympy": "sympy",
    "pytest-dev/pytest": "pytest",
    "matplotlib/matplotlib": "matplotlib",
    "astropy/astropy": "astropy",
    "pydata/xarray": "xarray",
    "mwaskom/seaborn": "seaborn",
    "psf/requests": "requests",
    "pylint-dev/pylint": "pylint",
    "pallets/flask": "flask",
    # Java
    "skylot/jadx": "jadx",
    "apache/dubbo": "dubbo",
    "apache/commons-lang": "commons-lang",
    "reactivex/rxjava": "rxjava",
    "googlecontainertools/jib": "jib",
    "netflix/eureka": "eureka",
    "apache/camel": "camel",
    "mockito/mockito": "mockito",
    "google/gson": "gson",
    "fasterxml/jackson-core": "jackson-core",
    "fasterxml/jackson-databind": "jackson-databind",
    "fasterxml/jackson-dataformat-xml": "jackson-dataformat-xml",
    "elastic/logstash": "logstash",
    "alibaba/fastjson2": "fastjson2",
    # Go
    "etcd-io/etcd": "etcd",
    "gin-gonic/gin": "gin",
    "zeromicro/go-zero": "go-zero",
    "grpc/grpc-go": "grpc-go",
    "cli/cli": "cli",
    "go-gorm/gorm": "gorm",
    # Rust
    "nushell/nushell": "nushell",
    "serde-rs/serde": "serde",
    "sharkdp/bat": "bat",
    "sharkdp/fd": "fd",
    "tokio-rs/tokio": "tokio",
    "rayon-rs/rayon": "rayon",
    "tokio-rs/bytes": "bytes",
    "tokio-rs/tracing": "tracing",
    "BurntSushi/ripgrep": "ripgrep",
    "clap-rs/clap": "clap",
    # Typescript/JavaScript
    "darkreader/darkreader": "darkreader",
    "vuejs/vue": "vue",
    "vuejs/core": "core",
    "mui/material-ui": "material-ui",
    "anuraghazra/github-readme-stats": "github-readme-stats",
    "Kong/insomnia": "insomnia",
    "axios/axios": "axios",
    "sveltejs/svelte": "svelte",
    "expressjs/express": "express",
    "preactjs/preact": "preact",
    "iamkun/dayjs": "dayjs",
    # Cpp
    "fmtlib/fmt": "fmt",
    "nlohmann/json": "json",
    "catchorg/Catch2": "Catch2",
    "simdjson/simdjson": "simdjson",
    "yhirose/cpp-httplib": "cpp-httplib",
    # C
    "jqlang/jq": "jq",
    "redis/redis": "redis",
    "facebook/zstd": "zstd",
    "valkey-io/valkey": "valkey",
    "ponylang/ponyc": "ponyc",
    # **Your local repos**
    "multi-swe-bench/validation-dataset": "validation-dataset",
    "multi-swe-bench/MagentLess": "MagentLess",
}


def checkout_commit(repo_path: str, commit_id: str) -> None:
    """Checkout the specified commit in the given local git repository."""
    try:
        subprocess.run(
            ["git", "-C", repo_path, "checkout", commit_id],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Git checkout failed at {repo_path}@{commit_id}: {e}")


def clone_repo(repo_name: str, repo_playground: str) -> None:
    """
    “Clone” by copying your already-cloned `repo/<top_folder>` into a fresh playground.
    Expects that you've run e.g. `git clone https://github.com/fmtlib/fmt.git repo/fmt`.
    """
    dir_name = repo_to_top_folder[repo_name]
    src = os.path.join("repo", dir_name)
    dest = os.path.join(repo_playground, dir_name)

    print(f"⮕ Copying repo/{dir_name} → {dest}")
    try:
        subprocess.run(
            ["cp", "-r", src, dest],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Error copying {repo_name}: {e}")
        raise


def get_project_structure_from_scratch(
    repo_name: str,
    commit_id: str,
    instance_id: str,
    repo_playground: str,
) -> dict:
    # 1) Make a fresh playground/<uuid>
    pg = os.path.join(repo_playground, str(uuid.uuid4()))
    os.makedirs(pg, exist_ok=False)

    # 2) Copy in your local repo/<top_folder>
    clone_repo(repo_name, pg)

    # 3) Checkout the exact commit
    top = os.path.join(pg, repo_to_top_folder[repo_name])
    checkout_commit(top, commit_id)

    # 4) Parse the directory into a JSON-able structure
    structure = create_structure(top)

    # 5) Cleanup (remove the copied folder)
    subprocess.run(["rm", "-rf", top], check=True)

    return {
        "repo": repo_name,
        "base_commit": commit_id,
        "structure": structure,
        "instance_id": instance_id,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Below here: your parsing helpers (unchanged)
# ────────────────────────────────────────────────────────────────────────────────

def parse_python_file(file_path: str, file_content: str = None):
    if file_content is None:
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
        except Exception as e:
            print(f"[!] Could not read {file_path}: {e}")
            return [], [], []
    try:
        tree = ast.parse(file_content)
    except Exception as e:
        print(f"[!] AST parse error {file_path}: {e}")
        return [], [], file_content.splitlines()

    classes, funcs, seen = [], [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            pass
        elif isinstance(node, ast.FunctionDef):
            pass
    return classes, funcs, file_content.splitlines()


def parse_cpp_file(file_path: str, file_content: str = None):
    if file_content is None:
        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
        except Exception as e:
            print(f"[!] Could not read {file_path}: {e}")
            return [], [], []
    
    # For now, just return empty classes and functions, but include the text
    # This will allow the localization to work while we fix the tree-sitter issue
    return [], [], file_content.splitlines()


def traverse(node: Node) -> Generator[Node, None, None]:
    cursor = node.walk()
    visited = False
    while True:
        if not visited:
            yield cursor.node
            if not cursor.goto_first_child():
                visited = True
        elif cursor.goto_next_sibling():
            visited = False
        elif not cursor.goto_parent():
            break


def get_child(node: Node, type_name: str, skip: int = 0) -> Union[Node, None]:
    for child in node.children:
        if child.type == type_name:
            if skip == 0:
                return child
            skip -= 1
    return None


def get_name(node: Node, type_name: str = 'identifier') -> str:
    c = get_child(node, type_name)
    return c.text.decode('utf-8') if c else ''


def check_file_ext(file_name: str, language: str) -> bool:
    exts = {
        'cpp': ['h','hpp','c','cpp','cc','cxx'],
        'typescript': ['ts','js'],
    }
    return any(file_name.lower().endswith(f'.{e}') for e in exts.get(language, []))


def create_structure(directory_path: str) -> dict:
    structure = {}
    for root, _, files in os.walk(directory_path):
        rel = os.path.relpath(root, directory_path)
        node = structure
        if rel != ".":
            for part in rel.split(os.sep):
                node = node.setdefault(part, {})
        for fn in files:
            fp = os.path.join(root, fn)
            if fn.endswith('.py'):
                cls, funcs, text = parse_python_file(fp)
                node[fn] = {'classes': cls, 'functions': funcs, 'text': text}
            elif check_file_ext(fn, 'cpp'):
                cls, funcs, text = parse_cpp_file(fp)
                node[fn] = {'classes': cls, 'functions': funcs, 'text': text}
            else:
                node[fn] = {}
    return structure
