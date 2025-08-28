from pathlib import Path
from .ultrajson_pro import UltraCompressor  # note le point, c'est un import relatif

def compress(infile: str, outfile: str):
    """Compresse un fichier JSON en .uc"""
    infile, outfile = Path(infile), Path(outfile)
    comp = UltraCompressor()
    comp.compress_json(str(infile), str(outfile), preproc_opts={}, preserve_text=True)
    return outfile

def decompress(infile: str, outfile: str):
    """Décompresse un fichier .uc en JSON"""
    infile, outfile = Path(infile), Path(outfile)
    comp = UltraCompressor()
    comp.decompress_json(str(infile), str(outfile), preserve_text=True)
    return outfile

__all__ = ['compress', 'decompress']