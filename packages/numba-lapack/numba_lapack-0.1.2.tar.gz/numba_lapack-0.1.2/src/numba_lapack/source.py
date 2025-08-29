# numba_lapack.py
from __future__ import annotations
import ctypes
import importlib
import re
from typing import Dict, List, Tuple, Optional

import numpy as np

from numba import types
from numba.extending import intrinsic, get_cython_function_address
from numba.core import cgutils
from numba.core.errors import TypingError
from llvmlite import ir as llir
from llvmlite import binding as llvm


# ========= Utilities to read __pyx_capi__ and parse capsule signatures =========

# Access PyCapsule name (contains the cdecl signature string)
_PyCapsule_GetName = ctypes.pythonapi.PyCapsule_GetName
_PyCapsule_GetName.restype = ctypes.c_char_p
_PyCapsule_GetName.argtypes = [ctypes.py_object]

def _list_capsules(modname: str) -> Dict[str, str]:
    """Return {symbol_name: signature_string} for module.__pyx_capi__."""
    mod = importlib.import_module(modname)
    capi = getattr(mod, "__pyx_capi__", {})
    out = {}
    for name, capsule in capi.items():
        sig_bytes = _PyCapsule_GetName(capsule)
        sig = sig_bytes.decode("utf-8") if sig_bytes else ""
        # Some signatures include extra info like "function ..."; keep only "ret(args)"
        m = re.search(r"^[^(]+\([^)]*\)", sig)
        out[name] = (m.group(0) if m else sig)
    return out


# Map base tokens to (Numba type, LLVM type builder)
# For scalars, we’ll make LLVM types on demand (for complex, use Numba’s).
_BASE_TO_NUMBA = {
    "void": None,
    "char": types.uint8,           # pass as uint8; for char* we take its address
    "signed char": types.int8,
    "unsigned char": types.uint8,
    "short": types.int16,
    "unsigned short": types.uint16,
    "int": types.int32,
    "unsigned int": types.uint32,
    "long": types.int64,           # LAPACK uses int, but keep long mapping
    "unsigned long": types.uint64,
    "long long": types.int64,
    "unsigned long long": types.uint64,
    "size_t": types.uintp,
    "float": types.float32,
    "double": types.float64,
    "__pyx_t_float_complex":  types.complex64,
    "__pyx_t_double_complex": types.complex128,
}

def _ll_from_numba(ctx, nb):
    if nb == types.uint8:  return llir.IntType(8)
    if nb == types.int8:   return llir.IntType(8)
    if nb == types.uint16: return llir.IntType(16)
    if nb == types.int16:  return llir.IntType(16)
    if nb == types.uint32: return llir.IntType(32)
    if nb == types.int32:  return llir.IntType(32)
    if nb == types.uint64: return llir.IntType(64)
    if nb == types.int64:  return llir.IntType(64)
    if nb == types.uintp:  return ctx.get_value_type(types.uintp)
    if nb == types.float32: return llir.FloatType()
    if nb == types.float64: return llir.DoubleType()
    if nb == types.complex64:  return ctx.get_value_type(types.complex64)   # {f32,f32}
    if nb == types.complex128: return ctx.get_value_type(types.complex128)  # {f64,f64}
    raise KeyError(f"Unsupported Numba type for LLVM mapping: {nb}")

class ArgSpec:
    __slots__ = ("base", "nb_base", "ptr_depth", "is_const")

    def __init__(self, base: str, nb_base: types.Type, ptr_depth: int, is_const: bool):
        self.base = base
        self.nb_base = nb_base
        self.ptr_depth = ptr_depth
        self.is_const = is_const

    def __repr__(self):
        c = "const " if self.is_const else ""
        stars = "*" * self.ptr_depth
        return f"{c}{self.base}{stars}"

class FuncSig:
    __slots__ = ("name", "restype", "restype_nb", "args", "raw_sig")

    def __init__(self, name: str, restype: str, restype_nb: Optional[types.Type],
                 args: List[ArgSpec], raw_sig: str):
        self.name = name
        self.restype = restype
        self.restype_nb = restype_nb
        self.args = args
        self.raw_sig = raw_sig

def _nb_from_token(tok: str) -> Optional[types.Type]:
    """
    Map a base token from the capsule to a Numba scalar type.
    Handles plain C names and Cython's module-local typedefs like:
      __pyx_t_5scipy_6linalg_11cython_blas_d (double)
      __pyx_t_5scipy_6linalg_11cython_blas_s (float)
      __pyx_t_5scipy_6linalg_11cython_blas_c (complex64)
      __pyx_t_5scipy_6linalg_11cython_blas_z (complex128)
    """
    tok = tok.strip()
    if tok in _BASE_TO_NUMBA:
        return _BASE_TO_NUMBA[tok]

    if tok.startswith("__pyx_t_"):
        # Try exact complex names first (already handled above), then suffix
        if tok.endswith("_d"):
            return types.float64
        if tok.endswith("_s"):
            return types.float32
        if tok.endswith("_c"):
            return types.complex64
        if tok.endswith("_z"):
            return types.complex128
        # Some Cython builds expose just "__pyx_t_float_complex"/"...double_complex" (already mapped)
        if "float_complex" in tok:
            return types.complex64
        if "double_complex" in tok:
            return types.complex128
        # Unknown typedef
        return None
    return None

def _normalize(tok: str) -> str:
    return " ".join(tok.strip().split())

def _parse_base_and_ptr(part: str) -> Tuple[str, int, bool]:
    """
    Parse e.g. 'const double *' or '__pyx_t_..._d *' -> (base_token, ptr_depth, is_const).
    """
    s = part.strip()
    is_const = "const" in s
    s = s.replace("const", "")
    # collapse multiple spaces
    s = _normalize(s)
    # count stars (ptr depth)
    ptr_depth = s.count("*")
    base = _normalize(s.replace("*", ""))
    return base, ptr_depth, is_const

def _parse_signature(name: str, sig: str) -> Optional[FuncSig]:
    """
    Accept both 'ret(args)' and 'ret (*)(args)' capsule names from Cython.
    Map base tokens via _nb_from_token (supports __pyx_t_* typedefs).
    """
    s = sig.strip()
    l, r = s.find("("), s.rfind(")")
    if l == -1 or r == -1 or r < l:
        return None

    ret_full = _normalize(s[:l])  # may contain '(*'
    args_str = s[l + 1 : r].strip()

    # Strip optional function-pointer marker from return part: 'double (*' -> 'double'
    ret_str = _normalize(ret_full.split("(*", 1)[0]) if "(*" in ret_full else ret_full

    # Return type
    ret_nb = _nb_from_token(ret_str)
    if ret_nb is None and ret_str != "void":
        return None  # unsupported return

    args: List[ArgSpec] = []
    if args_str and args_str != "void":
        parts = [a.strip() for a in args_str.split(",") if a.strip()]
        for raw in parts:
            base, ptr_depth, is_const = _parse_base_and_ptr(raw)
            nb = _nb_from_token(base)
            if nb is None:
                return None
            args.append(ArgSpec(base, nb, ptr_depth, is_const))

    return FuncSig(name, ret_str, ret_nb, args, sig)

def _is_cptr_to(ty, base):
    return isinstance(ty, types.CPointer) and ty.dtype == base

# ========= Lowering helpers =========

def _to_i32_signed(builder, v):
    i32 = llir.IntType(32)
    if isinstance(v.type, llir.IntType):
        if v.type.width < 32: return builder.sext(v, i32)
        if v.type.width > 32: return builder.trunc(v, i32)
        return v
    return builder.ptrtoint(v, i32)

def _to_i32_n(builder, v):
    i64 = llir.IntType(64)
    i32 = llir.IntType(32)
    if isinstance(v.type, llir.IntType):
        v64 = builder.zext(v, i64) if v.type.width < 64 else (builder.trunc(v, i64) if v.type.width > 64 else v)
        return builder.trunc(v64, i32)
    return builder.ptrtoint(v, i32)

def _alloca_ptr_to_value(ctx, builder, val, nb_type):
    ll_ty = ctx.get_value_type(nb_type)
    ptr   = cgutils.alloca_once(builder, ll_ty)
    builder.store(val, ptr)
    return ptr

def _coerce_scalar_to(ctx, builder, val, src_nb, dst_nb):
    """
    Cast LLVM value 'val' (Numba type src_nb) into LLVM type for dst_nb.
    Handles Integer<->Integer and Float<->Float; Complex must match exactly.
    """
    ll_dst = ctx.get_value_type(dst_nb)

    # Exact match
    if src_nb == dst_nb:
        return val

    # Integer -> Integer
    if isinstance(src_nb, types.Integer) and isinstance(dst_nb, types.Integer):
        # llvmlite integer types have .width (bits)
        src_ll = val.type
        if not isinstance(src_ll, llir.IntType):
            # In practice src is IntType here
            return builder.bitcast(val, ll_dst)
        if src_ll.width < ll_dst.width:
            return builder.sext(val, ll_dst) if src_nb.signed else builder.zext(val, ll_dst)
        elif src_ll.width > ll_dst.width:
            return builder.trunc(val, ll_dst)
        else:
            # same width, signedness difference is a no-op in LLVM IR
            return val

    # Float -> Float
    if isinstance(src_nb, types.Float) and isinstance(dst_nb, types.Float):
        if isinstance(dst_nb, types.Float) and dst_nb.bitwidth > src_nb.bitwidth:
            return builder.fpext(val, ll_dst)
        else:
            return builder.fptrunc(val, ll_dst)

    # Allow Integer -> uint8 (char)
    if isinstance(src_nb, types.Integer) and dst_nb == types.uint8:
        src_ll = val.type
        if isinstance(src_ll, llir.IntType) and src_ll.width > 8:
            return builder.trunc(val, ll_dst)
        elif isinstance(src_ll, llir.IntType) and src_ll.width < 8:
            return builder.zext(val, ll_dst)
        else:
            return val

    # Complex must match exactly at this layer (no implicit promotion)
    if dst_nb in (types.complex64, types.complex128):
        return val  # rely on typing to have enforced same complex type

    # Fallback: bitcast if sizes match, else raise
    if hasattr(val.type, 'width') and hasattr(ll_dst, 'width') and val.type.width == ll_dst.width:
        return builder.bitcast(val, ll_dst)

    raise TypingError(f"Cannot coerce {src_nb} to {dst_nb}")


# ========= Expose data_ptr intrinsic (portable equivalent of x.ctypes.data) =========

@intrinsic
def data_ptr(typingctx, arr_ty):
    # Return a typed pointer: CPointer(dtype)
    if not isinstance(arr_ty, types.Array):
        raise TypingError("data_ptr expects a NumPy array")
    res = types.CPointer(arr_ty.dtype)
    sig = res(arr_ty)
    def codegen(ctx, builder, signature, args):
        (aval,) = args
        arr = cgutils.create_struct_proxy(signature.args[0])(ctx, builder, value=aval)
        # arr.data is already a pointer to the element type; bitcast just in case
        ll_res = ctx.get_value_type(res)
        p = arr.data
        if p.type != ll_res:
            p = builder.bitcast(p, ll_res)
        return p
    return sig, codegen

@intrinsic
def byref(typingctx, val_ty):
    # Allocate 1 slot in the entry block, store the scalar, return CPointer(val_ty)
    ok = val_ty in (types.float32, types.float64, types.complex64, types.complex128,
                    types.int32, types.int64, types.uint8, types.boolean)
    if not ok:
        raise TypeError(f"byref: unsupported scalar type {val_ty}")
    res = types.CPointer(val_ty)
    sig = res(val_ty)
    def codegen(ctx, builder, signature, args):
        (val,) = args
        ll_val = ctx.get_value_type(val_ty)
        slot = cgutils.alloca_once(builder, ll_val)  # entry-block alloca
        builder.store(val, slot)
        # slot already has pointer type to ll_val
        ll_res = ctx.get_value_type(res)
        return builder.bitcast(slot, ll_res) if slot.type != ll_res else slot
    return sig, codegen

# ========= Generator: make one UNSAFE intrinsic per Cython symbol =========

def _register_symbol(modname: str, cname: str, alias: str):
    """Register 'alias' -> address of 'modname.cname' (cache-safe symbol)."""
    try:
        addr = int(get_cython_function_address(modname, cname))
        llvm.add_symbol(alias, addr)
        return True
    except Exception:
        return False

def _llvm_ptr_type(ctx, nb_base: types.Type, depth: int):
    ll = _ll_from_numba(ctx, nb_base)
    for _ in range(depth):
        ll = llir.PointerType(ll)
    return ll

def _mk_intrinsic(func: FuncSig, alias_name: str):
    """
    Create and return an @intrinsic callable UNSAFE wrapper with the *same*
    name as the Cython function (e.g., 'daxpy', 'dgemm', 'dgesv', ...).

    Typing rules:
      - For pointer args (depth==1): accept uintp (address) OR a scalar castable to base
      - For pointer args (depth>1): require uintp
      - For non-pointers: exact base scalar
    """
    fname = func.name
    fargs = func.args
    fret  = func.restype_nb  # None for void
    nargs = len(fargs)

    # ---------- the actual typing/lowering core (works on a tuple of arg types) ----------
    def _intr_core(typingctx, *argtys):
        if len(argtys) != nargs:
            raise TypingError(f"{fname}: expected {nargs} arguments, got {len(argtys)}")

        norm_arg_nbt = []
        for i, (aty, spec) in enumerate(zip(argtys, fargs)):
            if spec.ptr_depth == 0:
                if aty != spec.nb_base:
                    raise TypingError(f"{fname}: arg {i} must be {spec.nb_base}, got {aty}")
                norm_arg_nbt.append(aty)
            else:
                # pointer parameter
                if spec.ptr_depth == 1:
                    ok = False

                    # 1) typed pointer to the right base
                    if _is_cptr_to(aty, spec.nb_base):
                        ok = True

                    # 2) ndarray buffer of the right base
                    if not ok and isinstance(aty, types.Array) and aty.dtype == spec.nb_base:
                        ok = True

                    # 3) by-value scalar (we'll alloca)
                    if not ok:
                        if isinstance(spec.nb_base, types.Integer):
                            ok = isinstance(aty, types.Integer)
                        elif isinstance(spec.nb_base, types.Float):
                            ok = isinstance(aty, types.Float)
                        elif spec.nb_base == types.uint8:
                            ok = isinstance(aty, types.Integer)  # flags
                        elif spec.nb_base in (types.complex64, types.complex128):
                            ok = (aty == spec.nb_base)

                    # 4) raw address (uintp) — backwards compat
                    if not ok and aty == types.uintp:
                        ok = True

                    if not ok:
                        raise TypingError(
                            f"{fname}: arg {i} must be CPointer[{spec.nb_base}], "
                            f"or ndarray[{spec.nb_base}] (buffer), "
                            f"or a scalar castable to {spec.nb_base}, "
                            f"or uintp (raw address)"
                        )
                    norm_arg_nbt.append(aty)
                else:
                    if aty != types.uintp:
                        raise TypingError(f"{fname}: arg {i} must be uintp for pointer depth {spec.ptr_depth}")
                    norm_arg_nbt.append(aty)

        ret_nb = fret if fret is not None else types.void
        sig = ret_nb(*norm_arg_nbt)

        def codegen(ctx, builder, signature, args):
            # Build callee function type with original C pointer/value layout
            ll_params = []
            for spec in fargs:
                if spec.ptr_depth == 0:
                    ll_params.append(_ll_from_numba(ctx, spec.nb_base))
                else:
                    ll_params.append(_llvm_ptr_type(ctx, spec.nb_base, spec.ptr_depth))
            ll_ret = llir.VoidType() if fret is None else _ll_from_numba(ctx, fret)
            fnty   = llir.FunctionType(ll_ret, ll_params, False)
            callee = cgutils.get_or_insert_function(builder.module, fnty, name=alias_name)

            # Prepare call args
            ll_call_args = []
            for (spec, arg_val, aty) in zip(fargs, args, signature.args):
                if spec.ptr_depth == 0:
                    ll_call_args.append(arg_val)
                else:
                    if _is_cptr_to(aty, spec.nb_base):
                        # already the right typed pointer; cast to the callee's exact pointer type if needed
                        ll_ptr_needed = _llvm_ptr_type(ctx, spec.nb_base, spec.ptr_depth)
                        p = arg_val
                        if p.type != ll_ptr_needed:
                            p = builder.bitcast(p, ll_ptr_needed)
                        ll_call_args.append(p)

                    elif isinstance(aty, types.Array) and aty.dtype == spec.nb_base:
                        # pass array data pointer
                        arr = cgutils.create_struct_proxy(aty)(ctx, builder, value=arg_val)
                        ll_ptr_needed = _llvm_ptr_type(ctx, spec.nb_base, spec.ptr_depth)
                        p = arr.data
                        if p.type != ll_ptr_needed:
                            p = builder.bitcast(p, ll_ptr_needed)
                        ll_call_args.append(p)

                    elif aty == types.uintp:
                        # raw address -> typed pointer
                        ll_ptr_needed = _llvm_ptr_type(ctx, spec.nb_base, spec.ptr_depth)
                        ll_uintp = ctx.get_value_type(types.uintp)
                        addr = arg_val
                        if isinstance(addr.type, llir.IntType) and addr.type.width != ll_uintp.width:
                            addr = builder.zext(addr, ll_uintp) if addr.type.width < ll_uintp.width else builder.trunc(addr, ll_uintp)
                        ll_call_args.append(builder.inttoptr(addr, ll_ptr_needed))

                    else:
                        # by-value scalar: coerce, alloca, pass address
                        coerced = _coerce_scalar_to(ctx, builder, arg_val, aty, spec.nb_base)
                        ptr = _alloca_ptr_to_value(ctx, builder, coerced, spec.nb_base)
                        ll_call_args.append(ptr)

            res = builder.call(callee, ll_call_args)
            return ctx.get_constant_null(types.void) if fret is None else res

        return sig, codegen

    # ---------- build a fixed-arity @intrinsic wrapper to avoid *args on the Python def ----------
    # We manufacture:  @intrinsic  def _intr_fixed(typingctx, a0, a1, ... a{n-1}): return _intr_core(typingctx, a0, a1, ...)
    scope = {'intrinsic': intrinsic, '_intr_core': _intr_core}
    params = ", ".join([f"a{i}_ty" for i in range(nargs)])
    call   = ", ".join([f"a{i}_ty" for i in range(nargs)])
    src = (
        f"@intrinsic\n"
        f"def _intr_fixed(typingctx, {params}):\n"
        f"    return _intr_core(typingctx, {call})\n"
    )
    exec(src, scope)
    intr = scope['_intr_fixed']
    intr.__name__ = fname
    intr.__doc__  = f"UNSAFE intrinsic for {fname} (from SciPy Cython C-API). Parsed: {func.raw_sig}"
    return intr


# ========= Public API: auto-discover & export UNSAFE wrappers =========

def _discover_and_generate(verbose: bool = False):
    """
    Scan cython_blas and cython_lapack, register symbols, and create
    UNSAFE intrinsics exported in this module's globals, using the same
    names as SciPy (e.g. daxpy, dgemm, dgesv, ...).
    """
    created = 0
    skipped = []

    for modname in ("scipy.linalg.cython_blas", "scipy.linalg.cython_lapack"):
        try:
            caps = _list_capsules(modname)
        except Exception as e:
            if verbose:
                print(f"[numba_lapack] Failed to read {modname}: {e}")
            continue

        for cname, sig in caps.items():
            # 1) parse
            func = _parse_signature(cname, sig)
            if func is None:
                skipped.append((modname, cname, sig, "parse-failed"))
                continue

            # 2) register a stable alias for JIT linking
            alias = f"pybridge_{cname}"
            if not _register_symbol(modname, cname, alias):
                skipped.append((modname, cname, sig, "add_symbol-failed"))
                continue

            # 3) create the intrinsic and export it under its BLAS/LAPACK name
            try:
                intr = _mk_intrinsic(func, alias)
                globals()[cname] = intr
                created += 1
            except Exception as e:
                skipped.append((modname, cname, sig, f"gen-failed: {e}"))
                continue

    if verbose:
        print(f"[numba_lapack] Created {created} UNSAFE functions; skipped {len(skipped)}")
        for row in skipped[:20]:
            print("  skipped:", row)
        if len(skipped) > 20:
            print(f"  ... ({len(skipped)-20} more)")

# Kick off generation at import
_discover_and_generate(verbose=False)
