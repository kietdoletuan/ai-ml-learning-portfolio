# Vietnamese Manufacturing NER - Annotation Guidelines v1

- Source: hlauto.vn, suadiencongnghiep.vn, 251 rows, `sentences_raw.csv`
- Goal: With this dataset, our goal is train a model to read and label mainenance logs and figure out 
what broke, how, and where. This requires a consistent labeling defining what each label actually encompasses. That is the reason for this 
annotation guideline


## Entity Types

### MACHINE
The primary physical equipment unit acting as the main subject of the sentence. Brand + model when present, generic term when not.
- "máy phay CNC" (row 138)
- "máy tiện CNC" (row 145)
- "băng tải cao su" 

**Hierarchy Rule:** 
Sub-systems like "biến tần" (VFD/inverters) or "PLC" change labels depending on context:
- **If isolated:** If the sentence is only about the VFD (e.g., "Sửa chữa biến tần Mitsubishi E700"), tag "biến tần Mitsubishi E700" as the MACHINE.
- **If attached:** If the sentence mentions the larger system it drives (e.g., "Biến tần báo lỗi khi băng tải chạy"), tag "băng tải" as the MACHINE. The "biến tần" becomes a COMPONENT.

### COMPONENT
A physical part inside or attached to a MACHINE. Not the primary machine itself.
- "IGBT" (row 92)
- "tụ điện" / "tụ DC bus" (row 94, row 238)
- "cảm biến nhiệt NTC" (row 190)
- "biến tần Mitsubishi E700" (ONLY when a larger MACHINE like a crane or conveyor is present in the sentence).

Boundary rule: Include the qualifying noun if it specifies which component ("tụ DC bus" not just "tụ" when the sentence specifies DC bus).

### DEFECT_TYPE
A descriptive phrase for what physically failed or degraded. Not a code.
Verb or noun phrases both qualify.
- "vòng bi motor bị mòn" (row 12)
- "tụ điện phồng" / "tụ tantalum ... bị phồng" (row 205)
- "board bị ăn mòn nặng" (row 207)
- "IGBT bị ngắn mạch" (row 169)
Boundary rule: span the full descriptive phrase, not just the affected component.
DEFECT_TYPE starts at the failure verb/adjective, COMPONENT is tagged separately when present.

### ERROR_CODE
Any alphanumeric fault code the machine itself displays. Distinct from DEFECT_TYPE
because these are short, non-descriptive tokens, not phrases.
- "OC", "OC1", "OC2", "OC3", "OCA" (rows 9, 11, 13, 44)
- "OV", "OV3" (rows 16, 67)
- "UV", "UV1" (rows 50, 242)
- "OH", "OH1" (rows 18, 227, 228)
- "F0001", "F0002", "F0003", "F3001", "F3801" (rows 111-124)
- "ERR12", "Er02", "Trip 16" (rows 24, 25, 215)
- "SPO", "E-16", "UnF" (rows 218, 220, 208)
Boundary rule: tag the code only, not the Vietnamese gloss next to it. In
"lỗi OC (Overcurrent)" (row 43), OC is ERROR_CODE, "Overcurrent" is the English
gloss and stays untagged.

### LOCATION
Named place: factory, workshop, city, industrial zone.
- "xưởng dệt vải ở Nam Định" (row 2)
- "nhà máy xi măng Hoàng Thạch" (row 188)
- "Bắc Ninh, Hưng Yên, Thái Nguyên" (row 236)
Boundary rule: tag the place name itself. Whether to include "xưởng" / "nhà máy"
as part of the span or treat it as a separate generic noun is a judgment call,
recommended: include it, since "xưởng dệt Nam Định" as one span is more useful
for downstream retrieval than splitting generic + proper noun.

## Notes

The hardest recurring case in this file: a code and a defect description appear
in the same sentence describing the same event. Example row 43:
"Lỗi OC (Overcurrent) là lỗi phổ biến nhất..." — OC is ERROR_CODE. If a later
clause described what physically happened ("IGBT cháy do quá dòng"), that clause
is DEFECT_TYPE even though it's the same underlying fault as OC. Codes and
descriptive phrases can co-occur and both get tagged, they are not mutually exclusive.

There are also names that are jargons, requiring additional research to annotate.

Sentences can also contain multiple instances of a label. The standard procedure would be to list them with a "; " seperating the instances. 

## Annotation Process

1. Read the full sentence before tagging anything. Some sentences (rows 34-38)
   are commentary about defect frequency, not incident descriptions, they
   may have zero MACHINE/LOCATION entities and only DEFECT_TYPE or ERROR_CODE.
2. Tag in a consistent left-to-right pass: MACHINE first if present, then
   COMPONENT, then DEFECT_TYPE, then ERROR_CODE, then LOCATION.
3. If uncertain whether something is DEFECT_TYPE or ERROR_CODE, apply this test:
   does it appear on the machine's display as a code, or is it a technician's
   description of physical failure? Display code → ERROR_CODE. Description → DEFECT_TYPE.
4. Skip rows that contain no target entities rather than force a tag (some rows,
   e.g. row 92's IGBT metaphor sentence, may be borderline, use judgment, log
   ambiguous rows in a separate notes column for review).


