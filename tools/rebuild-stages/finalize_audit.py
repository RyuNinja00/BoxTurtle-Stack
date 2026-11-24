from pathlib import Path
import re

path = Path('audited/BoxTurtle-V1-Dual-Tier.step')
body = path.read_bytes()
# Find the assembly representations corresponding to the option product definitions.
pattern = re.compile(
    rb'#\d+ = SHAPE_DEFINITION_REPRESENTATION\(#\d+,(#\d+)\);\n'
    rb'#\d+ = PRODUCT_DEFINITION_SHAPE\([^;]+;\n'
    rb'#\d+ = PRODUCT_DEFINITION\([^;]+;\n'
    rb'#\d+ = PRODUCT_DEFINITION_FORMATION\([^;]+;\n'
    rb"#\d+ = PRODUCT\(\s*'(0[1-7]) - ", re.M
)
matches=sorted((int(option),rep) for rep,option in pattern.findall(body))
assert [option for option,rep in matches]==list(range(1,8)), matches
last=max(int(n) for n in re.findall(rb'^#(\d+) =',body[-200000:],re.M))
visibility=b''.join(b'#%d = INVISIBILITY((%s));\n'%(last+n,rep) for n,rep in matches)
assert body.endswith(b'ENDSEC;\nEND-ISO-10303-21;\n')
body=body[:-len(b'ENDSEC;\nEND-ISO-10303-21;\n')]+visibility+b'ENDSEC;\nEND-ISO-10303-21;\n'
original=Path('revised/BoxTurtle-V1-Dual-Tier.step').read_bytes()
existing_credit=original[original.index(b'/*\n'):original.index(b'\n*/')+3]
existing_credit=existing_credit.replace(b'Modified 2026-11-23.',b'Modified 2026-11-23 to add and audit seven optional fit-up assemblies.')
path.write_bytes(body.replace(b'HEADER;',b'HEADER;\n'+existing_credit,1))
print('Default invisible STEP representations:',matches)
