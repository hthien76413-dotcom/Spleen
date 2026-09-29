"""Post-process the generated protocol: strip <w:highlightCs/> from every XML part.

Usage:  python3 finish_protocol.py [protocol_raw.docx] ["../Systematic review protocol - PROSPERO draft.docx"]

Run after `node build_protocol.js` (which writes protocol_raw.docx to the current
directory, or to the directory given as its first argument).
"""
import re
import sys
import zipfile

src = sys.argv[1] if len(sys.argv) > 1 else "protocol_raw.docx"
dst = sys.argv[2] if len(sys.argv) > 2 else "../Systematic review protocol - PROSPERO draft.docx"

zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.endswith(".xml"):
        data = re.sub(rb"<w:highlightCs[^>]*/>", b"", data)
    zout.writestr(item, data)
zout.close()
