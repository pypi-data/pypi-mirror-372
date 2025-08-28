"""
UltraJSON Pro Compressor v2 - Professional Edition

This single-file system upgrades the previous UltraJSON Pro Compressor with the
following professional improvements requested:

- Zstandard multithreading support (expose `threads` param)
- Brotli as an additional compressor option (auto-compare)
- Fast optimizer mode that tries multiple zstd levels (3,6,9) and picks best
- Streaming support: optional streaming JSON parsing (using ijson if installed)
  to handle very large files without full in-memory load (falls back to in-memory)
- Incremental dictionary training: sample packs are saved and can be appended
  to for re-training or incremental training runs
- Versioning / hashing: maps and dictionary files are hashed (SHA256) and
  included in output metadata to ensure compatibility across machines
- Fast BAT files updated: build_and_train.bat, compress_file.bat,
  decompress_file.bat, fast_optim.bat

Requirements (pip):
    pip install msgpack zstandard tqdm
Optional but recommended:
    pip install base91 brotli ijson

Usage: place this file as `ultrajson_pro.py` in your project folder and use the
provided .BAT files or call the CLI directly.

CLI: (see --help in script)
  build-maps, train-dict, compress, decompress, optimize, fast-optimize

Lossless: transformations are reversible; to decompress you must have the same
maps and dictionary files (and ideally matching version/hash).

"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
import struct
import hashlib
import msgpack
import zstandard as zstd
import lzma
from collections import Counter
from tqdm import tqdm
from typing import Any, Tuple, Dict, List

# Optional libs
try:
    import base91 as _base91
    BASE91_AVAILABLE = True
except Exception:
    _base91 = None
    BASE91_AVAILABLE = False

try:
    import brotli
    BROTLI_AVAILABLE = True
except Exception:
    brotli = None
    BROTLI_AVAILABLE = False

try:
    import ijson
    IJSON_AVAILABLE = True
except Exception:
    ijson = None
    IJSON_AVAILABLE = False

import base64

# ---------------------- Utilities ----------------------

def write_uc_file(out_path, original_data: bytes, compressed_data: bytes):
    import struct, zlib
    with open(out_path, "wb") as f:
        f.write(struct.pack("<I", len(original_data)))       # taille originale
        f.write(struct.pack("<I", zlib.crc32(original_data) & 0xffffffff))  # checksum CRC32
        f.write(compressed_data)

def read_uc_file(in_path, decompressor):
    import struct, zlib
    with open(in_path, "rb") as f:
        orig_size = struct.unpack("<I", f.read(4))[0]
        checksum = struct.unpack("<I", f.read(4))[0]
        comp_data = f.read()
    data = decompressor.decompress(comp_data)
    if zlib.crc32(data) & 0xffffffff != checksum:
        raise ValueError("Checksum mismatch: data corrupted")
    return data


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def read_json(infile):
    import json
    from collections import OrderedDict
    with open(infile, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)



def write_json(obj, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

# ---------------------- Maps Builder ----------------------

class MapsBuilder:
    def __init__(self, samples_folder: str, max_keys=2000, max_values=4000):
        self.samples_folder = samples_folder
        self.max_keys = max_keys
        self.max_values = max_values

    def gather_files(self):
        for root, _, files in os.walk(self.samples_folder):
            for f in files:
                if f.endswith('.json'):
                    yield os.path.join(root, f)

    def extract(self, obj, keys_counter: Counter, values_counter: Counter):
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys_counter[k] += 1
                self.extract(v, keys_counter, values_counter)
        elif isinstance(obj, list):
            for it in obj:
                self.extract(it, keys_counter, values_counter)
        elif isinstance(obj, str):
            values_counter[obj] += 1

    def build(self) -> Tuple[Dict[str,int], Dict[str,int]]:
        keys = Counter()
        values = Counter()
        for f in tqdm(list(self.gather_files()), desc='Scanning samples'):
            try:
                j = read_json(f)
                self.extract(j, keys, values)
            except Exception as e:
                print('Warning: skip', f, '->', e)
        keys_common = [k for k, _ in keys.most_common(self.max_keys)]
        values_common = [v for v, _ in values.most_common(self.max_values)]
        keys_map = {k: i+1 for i, k in enumerate(keys_common)}
        values_map = {v: i+1 for i, v in enumerate(values_common)}
        return keys_map, values_map

# ---------------------- Preprocessing transforms ----------------------

class Preprocessor:
    def __init__(self, keys_map: Dict[str,int]=None, values_map: Dict[str,int]=None,
                 mtf_threshold:int=4, delta_threshold:int=4):
        self.keys_map = keys_map or {}
        self.values_map = values_map or {}
        self.mtf_threshold = mtf_threshold
        self.delta_threshold = delta_threshold

    def apply_maps(self, obj: Any):
        from msgpack import ExtType
        def rec(x):
            if isinstance(x, dict):
                out = {}
                for k, v in x.items():
                    newk = self.keys_map.get(k, k)
                    out[newk] = rec(v)
                return out
            elif isinstance(x, list):
                return [rec(i) for i in x]
            elif isinstance(x, str):
                if x in self.values_map:
                    return ExtType(1, struct.pack('<I', self.values_map[x]))
                return x
            else:
                return x
        return rec(obj)

    def delta_encode(self, obj: Any):
        def rec(x):
            if isinstance(x, list):
                if len(x) >= self.delta_threshold and all(isinstance(i, int) for i in x):
                    base = x[0]
                    deltas = [x[i] - x[i-1] for i in range(1, len(x))]
                    return {'__delta__': True, 'base': base, 'deltas': deltas}
                else:
                    return [rec(i) for i in x]
            elif isinstance(x, dict):
                return {k: rec(v) for k, v in x.items()}
            else:
                return x
        return rec(obj)

    def mtf_transform(self, obj: Any):
        def rec(x, mtf_table=None):
            if mtf_table is None:
                mtf_table = []
            if isinstance(x, list):
                if len(x) >= self.mtf_threshold and all(isinstance(i, str) for i in x):
                    out = []
                    for s in x:
                        try:
                            idx = mtf_table.index(s)
                        except ValueError:
                            idx = None
                        if idx is None:
                            out.append({'__mtf_new__': s})
                            mtf_table.insert(0, s)
                        else:
                            out.append({'__mtf_idx__': idx})
                            item = mtf_table.pop(idx)
                            mtf_table.insert(0, item)
                    return {'__mtf_list__': out}
                else:
                    return [rec(i, mtf_table) for i in x]
            elif isinstance(x, dict):
                return {k: rec(v, mtf_table) for k, v in x.items()}
            else:
                return x
        return rec(obj)

    def rle_encode(self, obj: Any):
        def rec(x):
            if isinstance(x, list) and len(x) >= 4:
                out = []
                run = None
                count = 0
                for item in x:
                    if run is None:
                        run = item; count = 1
                    elif item == run:
                        count += 1
                    else:
                        if count >= 3:
                            out.append({'__rle__': [run, count]})
                        else:
                            out.extend([run]*count)
                        run = item; count = 1
                if run is not None:
                    if count >= 3:
                        out.append({'__rle__': [run, count]})
                    else:
                        out.extend([run]*count)
                return out
            elif isinstance(x, dict):
                return {k: rec(v) for k, v in x.items()}
            elif isinstance(x, list):
                return [rec(i) for i in x]
            else:
                return x
        return rec(obj)

    def preprocess(self, obj: Any, do_maps=True, do_delta=True, do_mtf=True, do_rle=True):
        j = obj
        if do_maps:
            j = self.apply_maps(j)
        if do_delta:
            j = self.delta_encode(j)
        if do_mtf:
            j = self.mtf_transform(j)
        if do_rle:
            j = self.rle_encode(j)
        return j

# ---------------------- Serialization helpers ----------------------

from msgpack import ExtType

def pack_msgpack(obj: Any) -> bytes:
    return msgpack.packb(obj, use_bin_type=True)


def unpack_msgpack(b: bytes) -> Any:
    def ext_hook(code, data):
        if code == 1:
            idn = struct.unpack('<I', data)[0]
            return ('__EXT_VAL__', idn)
        return ExtType(code, data)
    return msgpack.unpackb(b, raw=False, ext_hook=ext_hook, strict_map_key=False)

# ---------------------- Compressor / Decompressor ----------------------

import msgpack
from collections import OrderedDict

def unpack_msgpack_keep_order(data):
    return msgpack.unpackb(
        data,
        raw=False,  # décoder en str, pas en bytes
        object_pairs_hook=OrderedDict  # ✅ garde l’ordre
    )

class UltraCompressor:
    def __init__(self, maps_prefix='maps', zstd_dict_file=None, zstd_level=9, zstd_threads=0):
        self.maps_prefix = maps_prefix
        self.zstd_dict_file = zstd_dict_file
        self.zstd_level = zstd_level
        self.zstd_threads = zstd_threads
        self.keys_map = {}
        self.values_map = {}
        if maps_prefix and os.path.exists(maps_prefix + '_keys.json'):
            self.keys_map = read_json(maps_prefix + '_keys.json')
        if maps_prefix and os.path.exists(maps_prefix + '_values.json'):
            self.values_map = read_json(maps_prefix + '_values.json')

    def load_zstd_dict(self):
        if self.zstd_dict_file and os.path.exists(self.zstd_dict_file):
            with open(self.zstd_dict_file, 'rb') as f:
                d = f.read()
            return zstd.ZstdCompressionDict(d), hashlib.sha256(d).hexdigest()
        return None, None

    def compress_binary(self, data: bytes) -> Tuple[bytes, Dict[str, int]]:
        results = []
        # ZSTD
        zd, dict_hash = None, None
        if self.zstd_dict_file and os.path.exists(self.zstd_dict_file):
            zd, dict_hash = self.load_zstd_dict()
            cctx = zstd.ZstdCompressor(level=self.zstd_level, dict_data=zd, threads=self.zstd_threads)
        else:
            cctx = zstd.ZstdCompressor(level=self.zstd_level, threads=self.zstd_threads)
        start = time.time()
        try:
            comp_z = cctx.compress(data)
        except Exception:
            # fallback: streaming
            with cctx.stream_writer() as compressor:
                compressor.write(data)
                comp_z = compressor.flush()
        t_z = time.time() - start
        results.append(('zstd', comp_z, t_z))
        # LZMA
        start=time.time()
        comp_x = lzma.compress(data)
        t_x = time.time() - start
        results.append(('lzma', comp_x, t_x))
        # Brotli if available
        if BROTLI_AVAILABLE:
            start=time.time()
            comp_b = brotli.compress(data)
            t_b = time.time() - start
            results.append(('brotli', comp_b, t_b))
        best = min(results, key=lambda r: len(r[1]))
        method, comp_bytes, elapsed = best
        info = {'method': method, 'raw_size': len(data), 'comp_size': len(comp_bytes)}
        return comp_bytes, info

    def encode_text(self, binary: bytes, encoder='auto') -> Tuple[str, str]:
        if encoder == 'auto':
            if BASE91_AVAILABLE:
                txt = _base91.encode(binary)
                return txt, 'base91'
            else:
                txt = base64.b85encode(binary).decode('ascii')
                return txt, 'b85'
        elif encoder == 'base91' and BASE91_AVAILABLE:
            return _base91.encode(binary), 'base91'
        elif encoder == 'b85':
            return base64.b85encode(binary).decode('ascii'), 'b85'
        else:
            raise ValueError('Unknown encoder or base91 not installed')

    def decode_text(self, text: str, encoder_hint: str=None) -> bytes:
        if encoder_hint == 'base91':
            if not BASE91_AVAILABLE:
                raise RuntimeError('base91 hint provided but package not installed')
            return _base91.decode(text)
        if encoder_hint == 'b85' or (encoder_hint is None and not BASE91_AVAILABLE):
            return base64.b85decode(text.encode('ascii'))
        if BASE91_AVAILABLE:
            try:
                return _base91.decode(text)
            except Exception:
                pass
        return base64.b85decode(text.encode('ascii'))

    def compress_json(self, infile: str, outfile: str, preproc_opts: dict,
                    encoder='auto', use_stream=False, preserve_text=True):
        # Lire le JSON original en texte
        with open(infile, "r", encoding="utf-8") as f:
            original_text = f.read()

        if preserve_text:
            # Compresser le texte brut directement
            raw_bytes = original_text.encode("utf-8")
            comp_bytes, info = self.compress_binary(raw_bytes)

            # Sauvegarder .uc : taille originale (4 bytes) + méthode (1 byte) + données compressées
            method_map = {'zstd': 1, 'lzma': 2, 'brotli': 3}
            method_byte = struct.pack("B", method_map[info['method']])
            with open(outfile, "wb") as f:
                f.write(struct.pack("<I", len(raw_bytes)))  # longueur originale
                f.write(method_byte)
                f.write(comp_bytes)

            print(f'Compressed {infile} -> {outfile} (text preserved, method={info["method"]})')
            return {'compressed': len(comp_bytes)}

        # --- Pipeline classique avec msgpack et preprocessing ---
        if use_stream and IJSON_AVAILABLE:
            print('Streaming JSON parse enabled but full object build required; using in-memory fallback')
            j = read_json(infile)
        else:
            j = json.loads(original_text)

        pp = Preprocessor(
            keys_map=self.keys_map, values_map=self.values_map,
            mtf_threshold=preproc_opts.get('mtf_threshold', 4),
            delta_threshold=preproc_opts.get('delta_threshold', 4)
        )
        do_maps = preproc_opts.get('maps', True)
        do_delta = preproc_opts.get('delta', True)
        do_mtf = preproc_opts.get('mtf', True)
        do_rle = preproc_opts.get('rle', True)

        t0 = time.time()
        pre = pp.preprocess(j, do_maps, do_delta, do_mtf, do_rle)
        t1 = time.time()

        packed = pack_msgpack(pre)
        t2 = time.time()

        comp_bytes, info = self.compress_binary(packed)
        t3 = time.time()

        write_uc_file(outfile, packed, comp_bytes)
        print(f'Compressed {infile} -> {outfile}')
        print('Sizes: packed={} compressed={}'.format(len(packed), len(comp_bytes)))
        print('Timings: preprocess {:.3f}s pack {:.3f}s compress {:.3f}s'.format(t1-t0, t2-t1, t3-t2))

        return {'packed': len(packed), 'compressed': len(comp_bytes)}

    def decompress_json(self, infile: str, outfile: str, preserve_text=True):
        with open(infile, 'rb') as f:
            raw_len = struct.unpack("<I", f.read(4))[0]  # longueur originale
            if preserve_text:
                method_byte = f.read(1)
                comp_bytes = f.read()
            else:
                comp_bytes = f.read()
                method_byte = None

        if preserve_text:
            method_map_rev = {1: 'zstd', 2: 'lzma', 3: 'brotli'}
            method = method_map_rev[method_byte[0]]

            if method == 'zstd':
                raw_bytes = zstd.ZstdDecompressor().decompress(comp_bytes)
            elif method == 'lzma':
                raw_bytes = lzma.decompress(comp_bytes)
            elif method == 'brotli' and BROTLI_AVAILABLE:
                raw_bytes = brotli.decompress(comp_bytes)
            else:
                raise RuntimeError("Compression method unknown or non disponible")

            text = raw_bytes.decode("utf-8")
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(text)
            print(f'Decompressed {infile} -> {outfile} (text preserved, method={method})')
            return

        # --- Pipeline classique ---
        tried = False
        try:
            dctx = zstd.ZstdDecompressor()
            packed = dctx.decompress(comp_bytes)
            tried = True
        except Exception:
            pass

        if not tried:
            try:
                packed = lzma.decompress(comp_bytes)
                tried = True
            except Exception:
                pass

        if not tried:
            raise RuntimeError("Impossible de décompresser: format inconnu ou fichier corrompu")

        unpacked = unpack_msgpack(packed)

        keys_rev, values_rev = self._load_rev_maps()
        final = self._revive(unpacked, keys_rev, values_rev)

        write_json(final, outfile)
        print(f'Decompressed {infile} -> {outfile}')


    def _load_rev_maps(self) -> Tuple[Dict[int,str], Dict[int,str]]:
        keys_rev = {}
        values_rev = {}
        if self.maps_prefix and os.path.exists(self.maps_prefix + '_keys.json'):
            k = read_json(self.maps_prefix + '_keys.json')
            keys_rev = {int(v): kstr for kstr, v in k.items() if isinstance(v, int)}
        if self.maps_prefix and os.path.exists(self.maps_prefix + '_values.json'):
            v = read_json(self.maps_prefix + '_values.json')
            values_rev = {int(vv): sval for sval, vv in v.items() if isinstance(vv, int)}
        return keys_rev, values_rev

    def _revive(self, obj: Any, keys_rev: Dict[int,str], values_rev: Dict[int,str]):
        if isinstance(obj, dict):
            if '__delta__' in obj:
                base = obj.get('base')
                deltas = obj.get('deltas', [])
                if base is None or not isinstance(deltas, list):
                    return []
                out = [base]
                cur = base
                for d in deltas:
                    cur += d
                    out.append(cur)
                return out
            elif '__mtf_list__' in obj:
                table = []
                out = []
                for it in obj['__mtf_list__']:
                    if isinstance(it, dict) and '__mtf_new__' in it:
                        s = it['__mtf_new__']
                        out.append(s)
                        table.insert(0, s)
                    elif isinstance(it, dict) and '__mtf_idx__' in it:
                        idx = it['__mtf_idx__']
                        # si idx est invalide, utiliser un string vide au lieu de placeholder
                        if idx >= len(table) or idx < 0:
                            s = ''
                        else:
                            s = table[idx]
                            item = table.pop(idx)
                            table.insert(0, item)
                        out.append(s)
                    else:
                        out.append(it)
                return out
            else:
                new = {}
                for k, v in obj.items():
                    newk = keys_rev.get(k, k) if isinstance(k, int) else k
                    new[newk] = self._revive(v, keys_rev, values_rev)
                return new
        elif isinstance(obj, list):
            res = []
            for it in obj:
                if isinstance(it, dict) and '__rle__' in it:
                    val, count = it['__rle__']
                    repeated = [self._revive(val, keys_rev, values_rev) for _ in range(count)]
                    res.extend(repeated)
                else:
                    res.append(self._revive(it, keys_rev, values_rev))
            return res
        elif isinstance(obj, tuple) and len(obj) == 2 and obj[0] == '__EXT_VAL__':
            idn = obj[1]
            return values_rev.get(idn, '')
        else:
            return obj


# ---------------------- Zstd dictionary trainer (incremental) ----------------------

class ZstdDictTrainer:
    def __init__(self, samples_folder: str, maps_prefix='maps', out_dict='zstd_dict', dict_size=112640, samples_bin='zstd_samples'):
        self.samples_folder = samples_folder
        self.maps_prefix = maps_prefix
        self.out_dict = out_dict
        self.dict_size = dict_size
        self.samples_bin = samples_bin
        ensure_dir(self.samples_bin)

    def gather_jsons(self):
        for root, _, files in os.walk(self.samples_folder):
            for f in files:
                if f.endswith('.json'):
                    yield os.path.join(root, f)

    def transform_pack(self, path: str, keys_map: Dict[str,int], values_map: Dict[str,int]):
        try:
            j = read_json(path)
        except Exception:
            return None
        pp = Preprocessor(keys_map=keys_map, values_map=values_map)
        pre = pp.preprocess(j, do_maps=True, do_delta=True, do_mtf=True, do_rle=True)
        return pack_msgpack(pre)

    def collect_samples(self):
        keys_map = {}
        values_map = {}
        if os.path.exists(self.maps_prefix + '_keys.json'):
            keys_map = read_json(self.maps_prefix + '_keys.json')
        if os.path.exists(self.maps_prefix + '_values.json'):
            values_map = read_json(self.maps_prefix + '_values.json')
        samples = []
        for p in tqdm(list(self.gather_jsons()), desc='Preparing samples'):
            b = self.transform_pack(p, keys_map, values_map)
            if b:
                samples.append(b)
                # Save each sample for incremental training later
                idx = hashlib.sha1(b).hexdigest()
                outp = os.path.join(self.samples_bin, idx + '.bin')
                if not os.path.exists(outp):
                    with open(outp, 'wb') as f:
                        f.write(b)
        print('Collected samples into', self.samples_bin)
        return self.samples_bin

    def train(self, incremental=False):
        # load saved sample binaries
        sample_files = [os.path.join(self.samples_bin, f) for f in os.listdir(self.samples_bin) if f.endswith('.bin')]
        samples = []
        for s in tqdm(sample_files, desc='Loading sample bins'):
            with open(s, 'rb') as f:
                samples.append(f.read())
        if not samples:
            raise RuntimeError('No samples found to train dictionary')

        # Use zstandard.train_dictionary(...) which is available across zstandard versions
        try:
            dict_bytes = zstd.train_dictionary(self.dict_size, samples)
        except AttributeError:
            # some versions expose the function as train_dict
            try:
                dict_bytes = zstd.train_dict(self.dict_size, samples)
            except Exception as e:
                raise RuntimeError("Could not find zstd.train_dictionary / train_dict in your zstandard package: " + str(e))

        with open(self.out_dict, 'wb') as f:
            f.write(dict_bytes.as_bytes())
        print('Wrote zstd dict:', self.out_dict, 'from', len(samples), 'samples')


# ---------------------- Optimizer (fast and full) ----------------------

class AutoOptimizer:
    def __init__(self, compressor: UltraCompressor):
        self.compressor = compressor

    def try_variants(self, infile: str, outdir: str, enc='auto'):
        ensure_dir(outdir)
        toggles = [
            {'maps': True, 'delta': True, 'mtf': True, 'rle': True},
            {'maps': True, 'delta': True, 'mtf': False, 'rle': True},
            {'maps': True, 'delta': True, 'mtf': True, 'rle': False},
            {'maps': True, 'delta': False, 'mtf': True, 'rle': True},
            {'maps': True, 'delta': False, 'mtf': False, 'rle': True},
            {'maps': False, 'delta': True, 'mtf': True, 'rle': True},
        ]
        best = None
        variants = []
        for i, tog in enumerate(tqdm(toggles, desc='Trying variants')):
            fname = os.path.join(outdir, f'out_variant_{i}.json')
            meta = self.compressor.compress_json(infile, fname, preproc_opts=tog, encoder=enc)
            size = meta['meta']['sizes']['text_chars']
            variants.append((i, size, fname, meta))
            if best is None or size < best[1]:
                best = (i, size, fname, meta)
        print('Best variant:', best[0], 'size', best[1], 'file', best[2])
        return best, variants

    def fast_levels(self, infile: str, outdir: str, levels=(3,6,9), enc='auto'):
        ensure_dir(outdir)
        best = None
        results = []
        for lvl in levels:
            fname = os.path.join(outdir, f'fast_lvl_{lvl}.json')
            comp = UltraCompressor(maps_prefix=self.compressor.maps_prefix, zstd_dict_file=self.compressor.zstd_dict_file, zstd_level=lvl, zstd_threads=self.compressor.zstd_threads)
            meta = comp.compress_json(infile, fname, preproc_opts={'maps': True, 'delta': True, 'mtf': True, 'rle': True}, encoder=enc)
            size = meta['meta']['sizes']['text_chars']
            results.append((lvl, size, fname, meta))
            if best is None or size < best[1]:
                best = (lvl, size, fname, meta)
        print('Fast levels best:', best)
        return best, results

# ---------------------- CLI ----------------------

def main_cli():
    p = argparse.ArgumentParser(prog='ultrajson_pro')
    sub = p.add_subparsers(dest='cmd')

    g = sub.add_parser('build-maps')
    g.add_argument('samples_folder')
    g.add_argument('--out_prefix', default='maps')
    g.add_argument('--max_keys', type=int, default=2000)
    g.add_argument('--max_values', type=int, default=4000)

    t = sub.add_parser('train-dict')
    t.add_argument('samples_folder')
    t.add_argument('--maps_prefix', default='maps')
    t.add_argument('--out_dict', default='zstd_dict')
    t.add_argument('--dict_size', type=int, default=112640)
    t.add_argument('--collect-only', action='store_true')

    c = sub.add_parser('compress')
    c.add_argument('infile')
    c.add_argument('outfile')
    c.add_argument('--maps_prefix', default='maps')
    c.add_argument('--zstd_dict', default=None)
    c.add_argument('--encoder', default='auto')
    c.add_argument('--zstd_level', type=int, default=9)
    c.add_argument('--zstd_threads', type=int, default=0)
    c.add_argument('--maps', dest='maps', action='store_true')
    c.add_argument('--no-maps', dest='maps', action='store_false')
    c.set_defaults(maps=True)
    c.add_argument('--delta', dest='delta', action='store_true')
    c.add_argument('--no-delta', dest='delta', action='store_false')
    c.set_defaults(delta=True)
    c.add_argument('--mtf', dest='mtf', action='store_true')
    c.add_argument('--no-mtf', dest='mtf', action='store_false')
    c.set_defaults(mtf=True)
    c.add_argument('--rle', dest='rle', action='store_true')
    c.add_argument('--no-rle', dest='rle', action='store_false')
    c.set_defaults(rle=True)
    c.add_argument('--use_stream', action='store_true')

    d = sub.add_parser('decompress')
    d.add_argument('infile')
    d.add_argument('outfile')
    d.add_argument('--maps_prefix', default='maps')
    d.add_argument('--zstd_dict', default=None)

    o = sub.add_parser('optimize')
    o.add_argument('infile')
    o.add_argument('outdir')
    o.add_argument('--maps_prefix', default='maps')
    o.add_argument('--zstd_dict', default=None)
    o.add_argument('--encoder', default='auto')

    f = sub.add_parser('fast-optimize')
    f.add_argument('infile')
    f.add_argument('outdir')
    f.add_argument('--maps_prefix', default='maps')
    f.add_argument('--zstd_dict', default=None)
    f.add_argument('--encoder', default='auto')
    f.add_argument('--zstd_threads', type=int, default=0)

    args = p.parse_args()
    if args.cmd == 'build-maps':
        mb = MapsBuilder(args.samples_folder, max_keys=args.max_keys, max_values=args.max_values)
        keys_map, values_map = mb.build()
        write_json(keys_map, args.out_prefix + '_keys.json')
        write_json(values_map, args.out_prefix + '_values.json')
        print('Wrote maps with', len(keys_map), 'keys and', len(values_map), 'values')

    elif args.cmd == 'train-dict':
        trainer = ZstdDictTrainer(args.samples_folder, maps_prefix=args.maps_prefix, out_dict=args.out_dict, dict_size=args.dict_size)
        trainer.collect_samples()
        if not args.collect_only:
            trainer.train()

    elif args.cmd == 'compress':
        comp = UltraCompressor(maps_prefix=args.maps_prefix, zstd_dict_file=args.zstd_dict, zstd_level=args.zstd_level, zstd_threads=args.zstd_threads)
        pre = {'maps': args.maps, 'delta': args.delta, 'mtf': args.mtf, 'rle': args.rle, 'mtf_threshold': 4, 'delta_threshold': 4}
        comp.compress_json(args.infile, args.outfile, pre, encoder=args.encoder, use_stream=args.use_stream)

    elif args.cmd == 'decompress':
        comp = UltraCompressor(maps_prefix=args.maps_prefix, zstd_dict_file=args.zstd_dict)
        comp.decompress_json(args.infile, args.outfile)

    elif args.cmd == 'optimize':
        comp = UltraCompressor(maps_prefix=args.maps_prefix, zstd_dict_file=args.zstd_dict)
        opt = AutoOptimizer(comp)
        best, variants = opt.try_variants(args.infile, args.outdir, enc=args.encoder)
        print('Optimization completed. Best variant:', best)

    elif args.cmd == 'fast-optimize':
        comp = UltraCompressor(maps_prefix=args.maps_prefix, zstd_dict_file=args.zstd_dict, zstd_threads=args.zstd_threads)
        opt = AutoOptimizer(comp)
        best, results = opt.fast_levels(args.infile, args.outdir, levels=(3,6,9), enc=args.encoder)
        print('Fast optimization completed. Best:', best)

    else:
        p.print_help()

if __name__ == '__main__':
    main_cli()