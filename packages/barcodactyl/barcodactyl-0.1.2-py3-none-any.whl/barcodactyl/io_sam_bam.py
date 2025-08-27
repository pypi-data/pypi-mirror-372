import os, sys
from collections import defaultdict
from typing import Dict
import pysam
from .detector import BarcodeDetector

FMT_MAP = {"sam": {"mode_in": "r", "mode_out": "w", "ext": ".sam"},
           "bam": {"mode_in": "rb", "mode_out": "wb", "ext": ".bam"}}

def _guess_rg_barcode(read: pysam.AlignedSegment, detector: BarcodeDetector) -> str:
    rg = read.get_tag("RG") if read.has_tag("RG") else None
    if rg:
        lab = detector.from_text(str(rg))
        if lab != detector.unassigned:
            return lab
    return detector.from_text(read.query_name or "")

def split_sam_bam(in_path: str, out_dir: str, prefix: str, detector: BarcodeDetector, out_format: str, quiet: bool = False) -> int:
    assert out_format in ("sam", "bam")
    os.makedirs(out_dir, exist_ok=True)
    fmt_in = "rb" if in_path.lower().endswith(".bam") else "r"
    fmt_out = FMT_MAP[out_format]["mode_out"]
    ext = FMT_MAP[out_format]["ext"]
    writers: Dict[str, pysam.AlignmentFile] = {}
    counts: Dict[str, int] = defaultdict(int)

    with pysam.AlignmentFile(in_path, fmt_in) as ih:
        header = ih.header.to_dict()
        def get_writer(label: str) -> pysam.AlignmentFile:
            fn = os.path.join(out_dir, f"{prefix}{label}{ext}")
            w = writers.get(label)
            if w is None:
                w = pysam.AlignmentFile(fn, fmt_out, header=header)
                writers[label] = w
            return w
        total = 0
        for read in ih.fetch(until_eof=True):
            label = _guess_rg_barcode(read, detector)
            w = get_writer(label)
            w.write(read)
            counts[label] += 1
            total += 1

    for w in writers.values():
        w.close()

    if not quiet:
        sys.stderr.write("\n=== Per-barcode counts ===\n")
        total2 = 0
        for k in sorted(counts):
            sys.stderr.write(f"{k}\t{counts[k]:,}\n")
            total2 += counts[k]
        sys.stderr.write(f"Total reads written:\t{total2:,}\n")
    return total
