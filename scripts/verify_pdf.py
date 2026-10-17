"""Verify PDF generation, stream decompression, and page statistics."""
import base64
import zlib

def verify():
    with open("docs/CrossPay_Master_Operational_Manual.pdf", "rb") as f:
        data = f.read()

    print(f"Total PDF size: {len(data)} bytes ({len(data)/1024:.2f} KB)")
    
    idx = 0
    p = 1
    total_bytes = 0
    while True:
        spos = data.find(b"stream\n", idx)
        if spos == -1:
            break
        spos += 7
        epos = data.find(b"endstream", spos)
        chunk = data[spos:epos].strip()
        decomp = zlib.decompress(base64.a85decode(chunk, adobe=True))
        total_bytes += len(decomp)
        has_header = b"CrossPay Master Operational Manual" in decomp
        has_footer = b"CONFIDENTIAL" in decomp
        has_page = b"Page " in decomp
        print(f"Page {p}: {len(decomp)} decompressed bytes | Header: {has_header} | Footer: {has_footer} | PageNum: {has_page}")
        p += 1
        idx = epos + 9

    print(f"Total uncompressed PDF content: {total_bytes} bytes ({total_bytes/1024:.2f} KB)")
    print("Verification completed successfully!")

if __name__ == "__main__":
    verify()
