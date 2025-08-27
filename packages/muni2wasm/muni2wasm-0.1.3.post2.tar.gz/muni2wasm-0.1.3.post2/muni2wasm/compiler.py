#!/usr/bin/env python3
"""
compile.py

Handles full pipeline from .mun → WAT → WASM, and WASM execution.
"""
import sys
import logging
import tempfile
import os
from pathlib import Path

from wabt import Wabt
from wasmtime import Memory, Store, Linker, Module

from .lexer import tokenize
from .parser import Parser
from .codegen_wat import CodeGen
from .semantics import SemanticChecker
from .environment import register_host_functions
from .importer import import_standard_lib, inline_file_imports


_wabt = Wabt(skip_update=True)



def dump_hex(mem: Memory, store: Store, start=0, length=128):
    u8 = mem.data_ptr(store)
    b = bytes(u8[start:start+length])
    for off in range(0, len(b), 16):
        row = b[off:off+16]
        hexs = ' '.join(f'{x:02x}' for x in row)
        print(f'{start+off:08x}: {hexs}')



def compile_to_wat(source: str, input_path: str) -> str:
    tokens = tokenize(source)
    ast = Parser(tokens).parse()

    ast, lib_seen = import_standard_lib(ast)  # type: ignore
    ast, _ = inline_file_imports(ast, Path(input_path).parent, lib_seen)

    SemanticChecker(ast).check()
    return CodeGen(ast).gen()


def compile_file(input_path: str, output_path: str) -> None:
    inp = Path(input_path)
    out = Path(output_path)
    src = inp.read_text(encoding="utf-8")
    wat = compile_to_wat(src, input_path=input_path)

    out.parent.mkdir(parents=True, exist_ok=True)
    ext = out.suffix.lower()

    if ext == ".wat":
        out.write_text(wat, encoding="utf-8")
        logging.info(f"Generated {out}")
        return

    if ext == ".wasm":
        # write out a temp .wat file so Wabt can read it
        with tempfile.NamedTemporaryFile("w+", suffix=".wat", delete=False) as tmp:
            tmp.write(wat)
            tmp.flush()
            tmp_path = tmp.name

        try:
            # use WABT to convert
            _wabt.wat_to_wasm(tmp_path, output=str(out))
        except Exception as e:
            logging.error(f"WABT conversion failed: {e}")
            os.remove(tmp_path)
            sys.exit(1)

        os.remove(tmp_path)
        logging.info(f"Generated {out}")
        return


    logging.error("Output must end with .wat or .wasm")
    sys.exit(1)


def run_wasm(wasm_path: str) -> None:
    wasm = Path(wasm_path)
    if not wasm.exists():
        logging.error(f"File not found: {wasm}")
        sys.exit(1)

    store = Store()
    linker = Linker(store.engine)

    memory_ref = register_host_functions(linker, store)

    module = Module.from_file(store.engine, str(wasm))
    instance = linker.instantiate(store, module)

    exports = instance.exports(store)
    mem_extern = exports.get("memory")
    if mem_extern is None or not isinstance(mem_extern, Memory):
        logging.error("Module has no valid `memory` export")
        sys.exit(1)
    memory_ref["mem"] = mem_extern
    


    main_fn = exports.get("main")
    if main_fn is None:
        logging.error("No 'main' export found in module.")
        sys.exit(1)

    main_fn(store)  # type: ignore
