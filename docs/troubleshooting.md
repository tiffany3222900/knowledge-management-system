# Troubleshooting Guide

## Overview

This section provides symptom-to-solution reference for the most common printer problems. Problems are organized by category. Always start with the simplest solution (power cycle) and work toward more complex fixes.

---

## Quick Fix: Power Cycle

Before any advanced troubleshooting, perform a power cycle. This resolves approximately 40% of transient errors.

1. Press the power button to turn off the printer.
2. **Unplug** the power cable from the wall outlet (not just the printer).
3. Wait **60 seconds** — this allows capacitors to discharge and memory to clear.
4. While waiting, check that all covers are closed and no paper is jammed.
5. Plug the power cable back in.
6. Power on and wait for the printer to reach "Ready" state.
7. Print a test page.

!!! note "Network printers"
    If the printer is network-connected, also restart the network switch or router port if connectivity issues persist.

---

## Print Quality Problems

### Faded or Light Prints

| Possible Cause | Solution |
|----------------|----------|
| Toner cartridge low or empty | Replace toner cartridge |
| Toner is unevenly distributed | Remove cartridge, shake gently 5 times side to side, reinstall |
| Economode / toner save mode is on | Disable toner save mode in printer settings |
| Drum unit near end of life | Replace drum unit |
| Paper is damp or too thick | Replace with fresh, dry paper within spec |
| Transfer roller dirty or worn | Clean transfer roller; replace if needed |
| Laser scanner window dirty | Clean the scanner window (accessible via front cover on some models) |

### Vertical Streaks or Lines

| Pattern | Cause | Solution |
|---------|-------|----------|
| Black vertical line | Damaged drum or toner cartridge | Replace toner; if persists, replace drum |
| White vertical line | Toner clog or dirty developer roller | Replace toner cartridge |
| Repeating spots at regular intervals | Drum damage or fuser roller damage | Measure interval; replace drum or fuser |
| Streaks only on scans/copies | Dirty scanner glass or ADF glass strip | Clean scanner glass (see [Cleaning](cleaning.md)) |
| Streaks in same position on all prints | Dirty corona wire or primary charge roller | Clean per manufacturer instructions; replace drum |

### Smudges or Toner Rubs Off

| Cause | Solution |
|-------|----------|
| Fuser temperature too low | Check paper type setting (thick paper requires higher fuser temp) |
| Fuser unit worn or failing | Replace fuser (maintenance kit) |
| Paper is too thick or has wrong texture | Use paper within printer's weight specification |
| Toner is non-OEM / incompatible | Use genuine OEM toner |
| Print speed too high for media | Reduce print speed in driver settings for heavy media |

### Ghosting / Repeated Images

A faint duplicate of the image appears further down the page.

- **Cause**: Worn drum or fuser roller; the image is not fully transferred or fused.
- **Fix**: Replace the drum unit first. If ghosting persists, replace the fuser.

### Color Issues (Color Printers)

| Symptom | Cause | Solution |
|---------|-------|----------|
| One color missing | Empty cartridge or clogged nozzle | Replace cartridge; run head cleaning (inkjet) |
| Colors are wrong / shifted | Color registration misaligned | Run automatic color calibration from the menu |
| Color banding | Dirty LED print head or faulty cartridge | Clean; replace affected cartridge |
| All colors faded | Transfer belt nearing end of life | Replace transfer belt (maintenance kit) |
| Background haze | Incorrect toner density setting | Reset to factory defaults; replace drum |

---

## Paper Feed Problems

### Printer Says "No Paper" But Paper Is Loaded

1. Remove the cassette and inspect the pickup roller.
2. Clean the roller with isopropyl alcohol.
3. Check that the paper size sensor flag is not stuck.
4. Verify the paper is below the maximum fill line and above the minimum.
5. Ensure the cassette is fully inserted (push firmly until it clicks).
6. If the problem persists, the pickup roller may need replacement.

### Multiple Sheets Feed at Once

1. Remove the paper and fan it thoroughly to reduce static.
2. Check that the paper is not damp (replace with fresh stock).
3. Clean the separation pad with isopropyl alcohol.
4. If the separation pad is worn smooth, replace it.
5. Do not mix paper types or weights in the same cassette.

### Paper Skews / Prints Crooked

1. Check that the paper guides in the cassette are snug against the stack.
2. Ensure the paper is loaded squarely (not at an angle).
3. Clean the feed rollers — uneven roller wear causes skew.
4. Check for a torn paper scrap in the paper path causing asymmetric drag.
5. Verify the paper cassette is not warped or damaged.

---

## Error Codes

### Common Error Codes (Generic)

| Code | Meaning | Action |
|------|---------|--------|
| **E1** / **13.xx** | Paper jam | Clear jam per [Paper Handling](paper-handling.md) |
| **E2** / **10.xx** | Paper size mismatch | Verify cassette paper size matches driver setting |
| **E3** / **50.xx** | Fuser error | Power cycle; if persists, replace fuser |
| **E4** / **51.xx** | Laser scanner error | Power cycle; if persists, service required |
| **E5** / **52.xx** | Motor error | Check for obstructions; service required |
| **E6** / **53.xx** | Memory error | Power cycle; reseat memory if upgradeable |
| **E7** / **54.xx** | Color registration error | Run auto calibration; service if persists |
| **79.xx** | Firmware error | Power cycle; update firmware; remove faulty print jobs |
| **50.4** | Fuser power supply error | Check power outlet; try different circuit |

!!! note "Model-specific codes"
    Error codes vary by manufacturer (HP, Canon, Brother, Epson, Xerox, etc.). Always refer to the printer's service manual for exact code definitions. The codes above are generic patterns.

### 79 Service Error (HP Common)

This is a firmware crash, often caused by a corrupted print job.

1. Power off the printer and unplug for 60 seconds.
2. While off, clear all print jobs from the computer's print queue.
3. Plug in and power on.
4. If the error returns without sending a job, update the firmware.
5. If the error appears only when printing a specific file, the file is corrupted — re-save or re-export it.

---

## Network and Connectivity Problems

### Printer Offline / Not Found on Network

1. Print a configuration page from the printer's control panel to verify its IP address.
2. From a computer on the same network, ping the printer's IP address.
    - If ping fails: check network cable, switch port, and printer network settings.
    - If ping succeeds: the issue is with the printer driver/port on the computer.
3. Verify the printer has a static IP address (DHCP addresses can change and break the connection).
4. Restart the print spooler service on Windows:
    ```
    net stop spooler
    net start spooler
    ```
5. Remove and re-add the printer on the affected computer.
6. Update the printer driver to the latest version.

### Slow Printing Over Network

- Check network cable (replace Cat5e with Cat6 if possible)
- Reduce print resolution or use "Fast" print mode for drafts
- Disable "Keep printed documents" in the printer driver
- Update firmware and network card drivers
- For large documents, use a direct USB connection as a workaround

### Scan-to-Email Fails

1. Verify the printer has a valid DNS server configured.
2. Check SMTP server settings (address, port, authentication, encryption).
3. Test with a known-working email address.
4. If using Office 365 / Gmail, ensure "less secure app" access or app passwords are configured.
5. Check firewall settings — the printer must be able to reach the SMTP port.

---

## Hardware and Mechanical Problems

### Unusual Noises

| Noise | Likely Cause | Action |
|-------|-------------|--------|
| Grinding / clicking | Gear train issue, torn paper in gears | Inspect for paper scraps; service if persists |
| Squealing | Dry or worn rollers | Clean/lubricate per service manual; replace rollers |
| High-pitched whine | Fuser bearing or motor failing | Replace fuser or motor |
| Loud thumping | Imbalanced drum or toner cartridge | Reseat or replace cartridge |
| Buzzing / humming | Power supply or transformer | Normal if faint; service if loud or new |

### Printer Does Not Power On

1. Verify the power cable is firmly connected at both ends.
2. Try a different power outlet (test the outlet with another device).
3. Try a different power cable.
4. Check the power switch is in the "On" position.
5. If the printer has a power supply module, it may need replacement.
6. If there was a recent power surge, the fuse or power supply may be damaged — service required.

### Control Panel Display Issues

- **Blank display**: Check power; adjust display contrast/brightness; the display module may be faulty.
- **Display shows garbled characters**: Firmware corruption — update firmware; if unable, service required.
- **Touchscreen unresponsive**: Clean the screen; recalibrate touch if available; the touch panel may need replacement.
- **Buttons not responding**: Sticky or worn buttons — clean around buttons; control panel may need replacement.

---

## Software and Driver Problems

### Print Jobs Stuck in Queue

1. Open the print queue on the computer.
2. Cancel all documents.
3. Restart the print spooler service (Windows) or cups service (Linux/macOS).
4. Power cycle the printer.
5. Resend the print job.

### Wrong Paper Size or Orientation

- Check the paper size setting in the application's print dialog.
- Verify the printer driver's default paper size matches the loaded paper.
- Ensure the printer's control panel reports the correct paper size for each tray.
- For mixed-size documents, use "Select by Paper Source" or auto-select.

### Printer Prints Garbled Characters

- The wrong printer driver is installed — download and install the correct driver for the model.
- The print job is corrupted — cancel and resend.
- The interface cable is faulty — replace USB or network cable.
- Firmware is outdated — update to the latest version.

---

## When to Escalate

Contact IT support or an authorized service provider when:

- [ ] Error codes persist after power cycle and basic troubleshooting
- [ ] Print quality does not improve after toner, drum, and cleaning
- [ ] Recurring jams (2+ per day) after roller cleaning
- [ ] Any hardware error (fuser, laser scanner, motor, power supply)
- [ ] Physical damage to the printer or accessories
- [ ] The printer is under warranty — do not open sealed components (voids warranty)
- [ ] Firmware update fails or bricks the device
- [ ] Network issues that cannot be resolved with basic checks

---

## Troubleshooting Decision Flow

```
Start
  │
  ├─ Power cycle resolves it? ──Yes──→ Done (log transient error)
  │
  └─ No
      │
      ├─ Error code on display? ──Yes──→ Look up code → Follow fix
      │
      └─ No code
          │
          ├─ Paper jam? ──Yes──→ Clear jam → Test
          │
          ├─ Print quality issue? ──Yes──→ Check toner → Drum → Clean → Fuser
          │
          ├─ Connectivity issue? ──Yes──→ Check IP → Ping → Driver → Spooler
          │
          └─ Other ──→ Consult service manual → Escalate
```

---

*Next: [Safety](safety.md)*
