# Glossary

## Overview

This glossary defines the terms used throughout the Printer Maintenance Manual. It is written for designated printer operators, IT support staff, and anyone who completes a service log entry.

Definitions describe general office printing equipment. Model-specific part names, replacement intervals, and error codes are documented in the manufacturer's service manual, which always takes precedence over this guide. Terms are grouped by topic so that related concepts appear together. Shortened forms are listed in the Abbreviations section.

---

## Hardware Components

### Imaging and Fusing

| Term | Definition |
|------|------------|
| **Drum unit** | Photosensitive cylinder that receives the latent image and transfers toner to paper. On many laser printers it is a separate, replaceable consumable. |
| **Fuser unit** | Heated roller assembly that melts toner into the paper fibers under pressure. It reaches high operating temperatures and must cool fully before any maintenance. |
| **Transfer belt** | Belt that carries the toner image from the imaging drums to the paper on color laser printers. |
| **Transfer roller** | Roller that applies the charge that pulls toner from the drum onto the paper. |
| **Corona wire / charge roller** | Component that applies a uniform electrostatic charge to the drum before exposure. A dirty or failing one causes streaks and uneven density. |
| **Laser scanner unit** | Optical assembly that writes the latent image onto the drum with a laser beam. Dust on its window produces faded or repeating defects. |
| **Developer roller** | Roller that delivers toner to the drum during development. |
| **Ozone filter** | Filter that captures ozone produced by high-voltage charging components. A strong, persistent odor can indicate a filter or corona wire problem. |
| **Waste toner container** | Reservoir that collects surplus toner removed from the drum during cleaning. Replace it before it fills. |

### Paper Path and Feeding

| Term | Definition |
|------|------------|
| **Pickup roller** | Roller that lifts the top sheet from the cassette and feeds it into the paper path. Worn or glazed rollers are the most common cause of misfeeds. |
| **Separation pad** | Friction pad that holds back all but the top sheet, preventing multiple sheets from feeding at once. |
| **Feed roller** | General term for the rollers that move paper along the path between the cassette and the output tray. |
| **Registration** | The alignment of the paper and of each color layer. Poor registration produces skewed sheets or color fringing. |
| **Duplex unit** | Mechanism that turns the sheet over for two-sided printing. |
| **Automatic document feeder (ADF)** | Tray that feeds originals across the scanner glass for copying or scanning, so that pages do not need to be placed one at a time. |
| **Output tray** | Bin that receives finished pages. An overfull tray can cause jams at the exit. |

---

## Consumables and Supplies

| Term | Definition |
|------|------------|
| **Consumable** | Any item that is used up during normal operation and replaced on a schedule, such as toner, ink, drums, and waste toner containers. |
| **OEM supplies** | Cartridges and parts made by the printer manufacturer. Compatible (third-party) supplies are new-built alternatives; remanufactured or refilled cartridges are neither. |
| **Toner yield** | Estimated page count for a cartridge, normally rated at 5% coverage of a standard page. Dense graphics reduce the actual yield. |
| **Maintenance kit** | Bundled set of wear items, typically a fuser, transfer roller, pickup rollers, and separation pads, replaced together at a set page interval. |
| **Meter reading** | Total page count reported by the printer. Record it daily to track usage and plan preventive maintenance. |
| **Shelf life** | Period an unopened consumable remains within specification when stored as directed. |

!!! note "Yield is an estimate"
    A cartridge rated for 2,000 pages prints far fewer pages when jobs contain full-page graphics or photos. Use the meter reading and observed print quality, not the rated yield alone, to plan replacements.

---

## Print Quality Terms

| Term | Definition |
|------|------------|
| **Ghosting** | Faint duplicate of an image appearing further down the page, usually caused by a drum or fuser that does not fully release toner. |
| **Banding** | Repeating light or dark bands across the page, often linked to the transfer belt or color calibration. |
| **Streak** | Continuous line running in the feed direction. Black streaks commonly point to the drum or cartridge; white streaks to a toner clog. |
| **Repeating defect** | Mark that recurs at a fixed interval. The interval matches the circumference of the faulty roller, which helps identify the component. |
| **Fading** | Overall light or uneven print density, commonly caused by low toner, damp paper, or toner save mode. |
| **Smudging** | Toner that rubs off after printing, indicating that the fuser did not bond the toner to the paper. |
| **Color calibration** | Control panel procedure that aligns color layers and corrects density. Run it before replacing hardware for color complaints. |

---

## Paper and Media Terms

| Term | Definition |
|------|------------|
| **Media** | Any material that passes through the printer, including plain paper, envelopes, labels, and transparencies. |
| **Basis weight** | Paper weight expressed in g/m² (gsm). Media outside the printer's supported range causes jams and poor fusing. |
| **Grain direction** | Direction in which most paper fibers align. It affects curl and how smoothly a sheet travels through the path. |
| **Double feed** | Two or more sheets entering the paper path together, caused by static, damp stock, a worn separation pad, or an overfilled cassette. |
| **Misfeed** | Failure to pick up a sheet, or a sheet that enters at an angle. |
| **Jam** | Sheet stopped inside the paper path. Always check for torn scraps after clearing one. |
| **Laser-safe media** | Media rated to withstand fuser temperatures. Inkjet-coated and photo media can melt inside a laser printer. |

---

## Network and Software Terms

| Term | Definition |
|------|------------|
| **Print driver** | Software that converts a document into the printer's page description language and sends it to the device. |
| **Print spooler** | Operating system service that queues print jobs. Restarting it clears jobs that remain stuck after cancellation. |
| **Print queue** | Ordered list of jobs waiting for a printer, visible from the operating system. |
| **Static IP address** | Fixed network address assigned to the printer. A changing DHCP address breaks driver connections and makes the printer appear offline. |
| **Configuration page** | Report printed from the control panel that lists the IP address, firmware version, installed options, and supply status. |
| **Firmware** | Software embedded in the printer. Update it on a planned schedule, not during business hours. |
| **Scan-to-email / scan-to-folder** | Functions that deliver scanned documents to a mailbox or network share without a connected computer. |
| **Page description language** | Format used to describe a page to the printer, such as PCL or PostScript. A mismatched driver can produce garbled output. |

---

## Maintenance and Service Terms

| Term | Definition |
|------|------------|
| **Preventive maintenance** | Scheduled work performed before a failure occurs, such as deep cleaning and maintenance kit replacement. |
| **Service log** | Record of checks, meter readings, replaced parts, and incidents for a single printer. See the template in [Home](index.md). |
| **Asset record** | Inventory entry that identifies a printer by model, serial number, location, and warranty or contract status. |
| **Escalation** | Handover from routine operator maintenance to IT support or a qualified technician. See [Troubleshooting Guide](troubleshooting.md). |
| **Service contract** | Agreement that defines response times, covered parts, and on-site support. Verify coverage before ordering parts. |
| **Qualified technician** | Person trained to service high-voltage or high-temperature assemblies. Fuser and internal lubrication work is restricted to this role. |

!!! warning "Terminology does not replace safety rules"
    Several entries above refer to high-voltage or high-temperature assemblies. Read [Safety Guidelines](safety.md) before opening any cover, and never service a printer that is powered on.

---

## Abbreviations

| Abbreviation | Full form |
|--------------|-----------|
| **ADF** | Automatic document feeder |
| **DHCP** | Dynamic Host Configuration Protocol |
| **DPI** | Dots per inch |
| **GSM** | Grams per square meter |
| **IP** | Internet Protocol |
| **LSU** | Laser scanner unit |
| **MFP** | Multifunction printer |
| **OEM** | Original equipment manufacturer |
| **PCL** | Printer Command Language |
| **PPM** | Pages per minute |
| **PPE** | Personal protective equipment |
| **RH** | Relative humidity |
| **SNMP** | Simple Network Management Protocol |
| **USB** | Universal Serial Bus |

---

## Related Pages

- [Getting Started](getting-started.md) — printer components and tools
- [Daily Checklist](daily-checklist.md) — scheduled checks and meter readings
- [Consumables Management](consumables.md) — replacement and inventory procedures
- [Troubleshooting Guide](troubleshooting.md) — symptom-to-solution reference
- [Safety Guidelines](safety.md) — hazards and protective equipment

---

*Return to [Home](index.md)*

---
