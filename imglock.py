from PIL import Image
import numpy as np
import argparse, hashlib, os

def _load_image(path):
    img = Image.open(path)
    if img.mode not in ("L", "RGB", "RGBA"):
        img = img.convert("RGB")
    return img, np.array(img, dtype=np.uint8)

def _save_image(arr, ref_img, out_path):
    out = Image.fromarray(arr.astype(np.uint8), mode=ref_img.mode)
    out.save(out_path)
    return out_path

def _derive_seed(key_str: str) -> int:
    h = hashlib.sha256(key_str.encode("utf-8")).digest()[:8]
    return int.from_bytes(h, "big")

def _keystream(shape, seed):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=shape, dtype=np.uint8)

def op_add(arr, key):
    if isinstance(key, int):
        return (arr + key) % 256
    else:
        ks = _keystream(arr.shape, _derive_seed(key))
        return (arr + ks) % 256

def inv_add(arr, key):
    if isinstance(key, int):
        return (arr - key) % 256
    else:
        ks = _keystream(arr.shape, _derive_seed(key))
        return (arr - ks) % 256

def op_xor(arr, key):
    if isinstance(key, int):
        return arr ^ np.uint8(key)
    else:
        ks = _keystream(arr.shape, _derive_seed(key))
        return arr ^ ks

def inv_xor(arr, key):
    return op_xor(arr, key)

def op_swap(arr, _):
    return arr[::-1, ::-1]

inv_swap = op_swap

OPS = {
    "add": (op_add, inv_add),
    "xor": (op_xor, inv_xor),
    "swap": (op_swap, inv_swap),
}

def parse_key(s):
    try:
        v = int(s)
        return v
    except ValueError:
        return s

def process(in_path, out_path, mode, ops, key_str):
    img, arr = _load_image(in_path)
    key = parse_key(key_str)

    if mode == "encrypt":
        pipeline = ops
    elif mode == "decrypt":
        pipeline = ops[::-1]
    else:
        raise ValueError("Mode must be encrypt or decrypt")

    res = arr
    for op_name in pipeline:
        fwd, inv = OPS[op_name]
        if mode == "encrypt":
            res = fwd(res, key)
        else:
            res = inv(res, key)
    return _save_image(res, img, out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image encryption/decryption tool using pixel manipulation")
    parser.add_argument("mode", choices=["encrypt", "decrypt"])
    parser.add_argument("-i", "--input", required=True, help="Input image path")
    parser.add_argument("-o", "--output", required=True, help="Output image path")
    parser.add_argument("--ops", default="swap,xor", help="Comma-separated ops (add,xor,swap)")
    parser.add_argument("--key", default="123", help="Key (integer or string)")

    args = parser.parse_args()
    ops_list = [s.strip() for s in args.ops.split(",")]
    out_path = process(args.input, args.output, args.mode, ops_list, args.key)
    print(f"{args.mode.capitalize()}ed -> {out_path}")
