import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, Preformatted

root = Path(__file__).resolve().parent
pdf_path = root / "Shifted_Slice_Writeup.pdf"

doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    leftMargin=40,
    rightMargin=40,
    topMargin=40,
    bottomMargin=40
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=colors.HexColor('#183455'),
    spaceAfter=8
)

h1_style = ParagraphStyle(
    'DocH1',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=colors.HexColor('#194b71'),
    spaceBefore=14,
    spaceAfter=6,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'DocH2',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#1e557b'),
    spaceBefore=10,
    spaceAfter=4,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor('#162437'),
    spaceAfter=6
)

meta_style = ParagraphStyle(
    'DocMeta',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#334155'),
    spaceAfter=4
)

caption_style = ParagraphStyle(
    'DocCaption',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor('#52677c'),
    spaceAfter=10
)

code_style = ParagraphStyle(
    'DocCode',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#e9f2f7'),
    backColor=colors.HexColor('#192b3f'),
    spaceBefore=4,
    spaceAfter=6
)

story = []

# Title & Metadata
story.append(Paragraph("Shifted Slice — WolvCTF 2026 Write-up", title_style))
story.append(Paragraph("<b>Author:</b> Hedi Fandouli (@hedifandouli3-hash) &nbsp;|&nbsp; <b>Category:</b> Web / Cryptography &nbsp;|&nbsp; <b>Points:</b> 500", meta_style))
story.append(Spacer(1, 8))

# Challenge Tile Image
tile_img = root / "images" / "challenge_tile_original.png"
if tile_img.exists():
    story.append(RLImage(str(tile_img), width=260, height=122))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Figure 1. WolvCTF 2026 challenge tile for Shifted Slice (500 pts, author: ayushmk).", caption_style))

# TL;DR
story.append(Paragraph("TL;DR", h1_style))
story.append(Paragraph(
    "The server issues authorization tickets to read slices of a serialized bundle. The fundamental flaw is in the authorization model: tickets authorize access to a <b>fixed byte range</b> (e.g., <code>bytes=112-175</code>) rather than binding to a specific logical record.<br/><br/>"
    "When requesting a ticket for <code>z-owned</code>, the server issued a ticket for byte offset 112–175. By manipulating public records and compacting the bundle, <code>m-sealed</code> (the secret record) was shifted into that exact byte range (112–175). Reusing the previously issued ticket on the modified bundle bypassed authorization and returned the 64 raw bytes of <code>m-sealed</code>.<br/><br/>"
    "Because the returned data was masked under a session keystream, I collected XOR difference vectors across 25 independent sessions against a known record structure. Intersecting the valid lowercase hexadecimal character constraints across all 25 sessions uniquely resolved the first 29 characters of the secret token, and the trailing 3 characters plus closing brace were resolved from invariant record framing:<br/>"
    "<b>wctf{2ad127e3d6d87a29e350f89b89c413a8}</b>",
    body_style
))

# 1. Quick Start
story.append(Paragraph("1. Offline Reproduction & Verification", h1_style))
story.append(Paragraph(
    "All reproduction scripts and difference vectors are self-contained and run with Python 3.9+ standard library:<br/>"
    "&bull; <code>python scripts/inspect_layout.py</code> &mdash; Compute bundle layout transitions<br/>"
    "&bull; <code>python scripts/solve_offline.py</code> &mdash; Derive candidate flag from deltas<br/>"
    "&bull; <code>python scripts/verify_offline.py</code> &mdash; Verify all 25 recorded session vectors (PASS: 25/25)",
    body_style
))

# 2. Vulnerability Analysis
story.append(Paragraph("2. Vulnerability Analysis: Logical Records vs. Byte Ranges", h1_style))
story.append(Paragraph(
    "The service maintains a serialized bundle of records. Inspecting the initial manifest at revision 0 (<code>GET /api/manifest</code>):",
    body_style
))

manifest_table_data = [
    ["Record", "Kind", "Bytes", "Inclusive Range"],
    ["m-sealed", "sealed", "64", "0–63"],
    ["p-public", "public", "48", "64–111"],
    ["z-owned", "owned", "64", "112–175 (Authorized)"],
    ["zz-scratch", "owned", "128", "176–303"],
    ["Total", "", "304", ""]
]
t1 = Table(manifest_table_data, colWidths=[100, 80, 80, 160])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaf1f7')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1b466b')),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fef3c7')),
]))
story.append(t1)
story.append(Spacer(1, 6))

story.append(Paragraph(
    "When requesting a ticket for <code>z-owned</code>, the server returned an authorization token specifying <code>range: bytes=112-175</code>. "
    "Decoding the base64url ticket revealed big-endian integers for start (112), end (175), bundle size (304), and a signature. "
    "Crucially, the ticket bound authorization to the <b>slice coordinates</b>, not the logical record.",
    body_style
))

# 3. Shifting the Layout
story.append(Paragraph("3. Shifting the Layout", h1_style))
story.append(Paragraph(
    "By deleting <code>p-public</code> and inserting two public records (<code>a-pub</code>: 48 bytes, <code>b-pub</code>: 64 bytes) followed by compaction, "
    "the total bundle size remained 304 bytes, but <code>m-sealed</code> shifted directly into bytes <b>112–175</b>:",
    body_style
))

modified_table_data = [
    ["Record", "Kind", "Bytes", "Inclusive Range"],
    ["a-pub", "public", "48", "0–47"],
    ["b-pub", "public", "64", "48–111"],
    ["m-sealed", "sealed", "64", "112–175 (Target)"],
    ["z-owned", "owned", "64", "176–239"],
    ["zz-scratch", "owned", "64", "240–303"],
    ["Total", "", "304", ""]
]
t2 = Table(modified_table_data, colWidths=[100, 80, 80, 160])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaf1f7')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1b466b')),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fee2e2')),
]))
story.append(t2)
story.append(Spacer(1, 8))

diagram_img = root / "images" / "layout_comparison.png"
if diagram_img.exists():
    story.append(RLImage(str(diagram_img), width=480, height=174))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Figure 2. Comparison between Revision 0 and modified layout. The ticket range 112–175 now overlays m-sealed.", caption_style))

# 4. Ticket Redemption
story.append(Paragraph("4. Ticket Redemption & Slice Retrieval", h1_style))
story.append(Paragraph(
    "Redeeming the original Revision 0 ticket against <code>/api/read</code> succeeded with HTTP 200, returning 64 bytes of ciphertext. "
    "The server verified that range 112–175 was within bounds for a 304-byte bundle and had a valid signature, unwittingly returning the secret sealed record.",
    body_style
))

# 5. Cryptographic Recovery
story.append(Paragraph("5. Cryptographic Plaintext Recovery via XOR Differences", h1_style))
story.append(Paragraph(
    "Because the server encrypted bundle slices under a stream cipher with keystream reuse:<br/>"
    "&bull; <i>C</i><sub>sealed</sub> = <i>P</i><sub>sealed</sub> &oplus; <i>K</i><br/>"
    "&bull; <i>C</i><sub>known</sub> = <i>P</i><sub>known</sub> &oplus; <i>K</i><br/>"
    "&bull; &Delta; = <i>C</i><sub>sealed</sub> &oplus; <i>C</i><sub>known</sub> = <i>P</i><sub>sealed</sub> &oplus; <i>P</i><sub>known</sub><br/>"
    "Each session provided an authentic difference vector &Delta; canceling keystream <i>K</i>.",
    body_style
))

# 6. 25-Session Intersection
story.append(Paragraph("6. 25-Session Candidate Set Intersection", h1_style))
story.append(Paragraph(
    "With the flag defined as <code>wctf{&lt;32 hex chars&gt;}</code>, each secret character <i>x</i> at offset <i>j</i> must satisfy "
    "<i>x</i> &in; {0-9, a-f} and (<i>x</i> &oplus; &Delta;<sub>i</sub>[<i>j</i>]) &in; {0-9, a-f} across all 25 sessions. "
    "Intersecting these constraints collapsed offsets 18..46 to exactly 1 candidate character per position:<br/>"
    "<b>2ad127e3d6d87a29e350f89b89c41</b> (29 characters).",
    body_style
))

# 7. Trailer Resolution
story.append(Paragraph("7. Trailer Resolution via Invariant Framing", h1_style))
story.append(Paragraph(
    "Offsets 47..50 exhibited invariant deltas across all sessions (<code>39 0e 4f 13</code>). "
    "Aligning with the known note record trailer <code>\\nowned</code>:<br/>"
    "&bull; Offset 47: 0x39 &oplus; '\\n' (0x0a) = <b>'3'</b><br/>"
    "&bull; Offset 48: 0x0e &oplus; 'o' (0x6f) = <b>'a'</b><br/>"
    "&bull; Offset 49: 0x4f &oplus; 'w' (0x77) = <b>'8'</b><br/>"
    "&bull; Offset 50: 0x13 &oplus; 'n' (0x6e) = <b>'}'</b><br/>"
    "Full flag: <b>wctf{2ad127e3d6d87a29e350f89b89c413a8}</b>",
    body_style
))

# 8. Key Takeaways
story.append(Paragraph("8. Key Takeaways", h1_style))
story.append(Paragraph(
    "&bull; <b>Positional vs. Semantic Authorization:</b> Authorizing byte intervals rather than immutable object identifiers creates severe authorization confusion when data structures are mutable.<br/>"
    "&bull; <b>Keystream Reuse Vulnerability:</b> Reusing keystreams across paired records allows attackers to cancel the keystream and completely reconstruct plaintexts under known character-set constraints.",
    body_style
))

doc.build(story)
print(f"Generated clean PDF: {pdf_path}")
