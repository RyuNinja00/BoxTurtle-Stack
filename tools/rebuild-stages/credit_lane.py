from pathlib import Path
import sys
step = Path(sys.argv[1])
body = step.read_bytes()
assert body.startswith(b'ISO-10303-21;')
assert body.rstrip().endswith(b'END-ISO-10303-21;')
credit = (
    b'Dual-tier concept assembly adapted from ArmoredTurtle BoxTurtle Enclosure V1.0 CAD.\n'
    b'https://github.com/ArmoredTurtle/BoxTurtle-Enclosure/tree/c2940c63be7a276a4c5c59f111fb72c9bd807601\n'
    b'Four-lane buffers and rear skirts adapted from N3MI-DG Lane-Buffer.\n'
    b'https://github.com/N3MI-DG/Lane-Buffer/tree/0a6b0cdb551db7cce285cbef08f7ae515c3962ac\n'
    b'Both upstream projects are licensed under the GNU GPL v3. Modified 2026-11-23.\n\n'
    + Path('bte/LICENSE').read_bytes()
)
assert b'*/' not in credit
step.write_bytes(body.replace(b'HEADER;',b'HEADER;\n/*\n'+credit+b'\n*/',1))
