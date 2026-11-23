from pathlib import Path
import mistune
from weasyprint import HTML
root=Path(__file__).resolve().parent
md=(root/'README.md').read_text(encoding='utf-8')
html_body=mistune.create_markdown(plugins=['table'])(md)
css='''
@page {size: A4; margin: 20mm 17mm 19mm 17mm; @bottom-right {content: "SHIFTED SLICE  /  " counter(page);color:#6d7988;font:8px "DejaVu Sans"}}
body{font-family:"DejaVu Sans",sans-serif;color:#162437;font-size:9.3pt;line-height:1.52}
h1{font-size:25pt;color:#183455;line-height:1.17;border-bottom:4px solid #2a608b;padding-bottom:11px;margin:0 0 13px}
h2{font-size:14pt;color:#194b71;margin:23px 0 9px;break-after:avoid}
h3{font-size:10.7pt;color:#1e557b;margin:13px 0 7px;break-after:avoid}
p{margin:6px 0 9px}
code{font-family:"DejaVu Sans Mono",monospace;font-size:8pt;color:#192e42;background:#edf2f7;overflow-wrap:anywhere}
pre{background:#192b3f;color:#e9f2f7;padding:12px 14px;border-radius:5px;font-size:8pt;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere;break-inside:avoid}
pre code{background:none;color:inherit;font-size:8pt}
table{border-collapse:collapse;table-layout:fixed;width:100%;font-size:8.2pt;margin:9px 0 14px}
th,td{padding:6px 7px;border-bottom:1px solid #e0e6ec;overflow-wrap:anywhere;vertical-align:top}th{background:#eaf1f7;text-align:left;color:#1b466b}
tr{break-inside:avoid}tr:nth-child(even) td{background:#fafbfd}
img{display:block;max-width:100%;max-height:195px;object-fit:contain;object-position:left center;margin:12px 0 4px}
em{color:#52677c}
a{color:#1c5279}strong{font-weight:700}
'''
HTML(string=f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{html_body}</body></html>',base_url=str(root)+'/').write_pdf(str(root/'Shifted_Slice_Writeup.pdf'))
print(root/'Shifted_Slice_Writeup.pdf')
