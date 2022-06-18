import yaml
import os
import re
from os import listdir
from operator import itemgetter

# + [Mandatory guardrails](mandatory-guardrails.md)
# + [Strongly recommended guardrails](strongly-recommended-guardrails.md)
# + [Elective guardrails](elective-guardrails.md)

def processcontrol(source, guidance):

    BLOCK_LIST = ["# Guardrail update"]

    guardrail = {}
    guardrail["Guidance"] = guidance
    guardrail['FullDocumentation'] = source
    guardrail["Name"] = (source.splitlines()[0].strip()).split("<a")[0].strip()
    print(guardrail["Name"])

    if guardrail["Name"] in BLOCK_LIST:
        print(" - Is Blocked")
        return guardrail

    if guardrail["Name"].find("Previously") > 0:
        splitname = guardrail["Name"].split("\\[Previously: ")
        guardrail["Name"] = splitname[0].strip()
        guardrail["PreviousName"] = splitname[1].replace("\\]", "").strip()

    firstlineless = '\n'.join(source.splitlines()[1:]).strip()
    guardrail["Description"] = firstlineless.split("The artifact for this guardrail")[0].strip()

    m1 = re.search('SourceIdentifier:(.+?)\n', source)
    if m1:
        guardrail["Type"] = "ConfigRule"
        guardrail["Sid"] = m1.group(1).strip()

    m = re.search('Sid\": \"(.+?)\"', source)
    if m is not None:
        guardrail["Type"] = "ServiceControlPolicy"
        guardrail["Sid"] = m.group(1).strip()

    return guardrail



filemap = [
    ("doc_source/mandatory-guardrails.md", "Mandatory"),
    ("doc_source/strongly-recommended-guardrails.md", "Recommended"),
    ("doc_source/elective-guardrails.md", "Elective"),
    ("doc_source/data-residency-guardrails.md", "DataResidency"),
]
all_guardrails = []

for path, guidance in filemap:
    print(path)
    print(guidance)
    with open(path, 'r') as infile:
        contents = infile.read()
        controls = contents.split("## ")[1:]

        for source in controls:

            guardrail = processcontrol(source, guidance)

            if "Sid" not in guardrail:
                print(" - Has NO Sid")
                continue

            all_guardrails.append(guardrail)

all_guardrails = sorted(all_guardrails, key=itemgetter('Sid'))

with open('control-tower-controls.yml', 'w') as outfile:
    yaml.dump(all_guardrails, outfile, default_flow_style=False)