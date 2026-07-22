from fpdf import FPDF
import os

def create_pdf(filename, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    for line in text.split('\n'):
        pdf.cell(w=0, h=10, txt=line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(filename)
    print(f"Created {filename}")

def generate_all():
    # 1. Incident Report
    incident_text = """INCIDENT REPORT - September 02, 2023
Title: Q3 pressure trip incident
Equipment Tag: C-101 (Main Air Compressor)

Reporter: Alan Walker
Severity: High

Description:
At 14:00 hours, C-101 experienced a sudden surge in discharge pressure, triggering the automated safety shutdown sequence (pressure trip).
The incident resulted in a 4-hour production halt.

Root Cause Analysis:
Initial findings suggest a failure in the primary pressure relief valve due to unexpected particulate buildup.

Follow-up Actions:
Immediate replacement of the relief valve and a full annual inspection of C-101 are required before restarting continuous operations.
"""
    create_pdf("incident_q3_trip.pdf", incident_text)

    # 2. SOP Document
    sop_text = """STANDARD OPERATING PROCEDURE - Version 2.4
Title: C-101 Startup and Shutdown Procedure
Equipment Tag: C-101 (Main Air Compressor)

Author: Tech Ops Team

1. Startup:
- Ensure all intake valves are clear.
- Verify oil levels in the main lubrication reservoir.
- Initiate the slow-roll sequence for 5 minutes before engaging the main drive.

2. Shutdown (Normal):
- Gradually reduce load over 15 minutes.
- Engage the cooling loop for 30 minutes post-shutdown.

3. Emergency Trip Response:
- If a pressure trip occurs, DO NOT attempt immediate restart.
- Follow the Lockout/Tagout (LOTO) procedure per OSHA standard 1910.147.
- A supervisor must inspect the unit before the trip can be reset.
"""
    create_pdf("sop_c101.pdf", sop_text)

    # 3. Follow-up Inspection
    inspection_text = """INSPECTION FINDING - September 05, 2023
Title: Post-trip internal inspection
Equipment Tag: C-101 (Main Air Compressor)

Inspector: Jane Smith

Findings:
Following the Q3 pressure trip incident, an internal boroscope inspection was performed on the compressor housing.
No catastrophic damage was found to the rotor blades. However, the primary seal showed signs of thermal stress.

Recommendations:
Replace the primary seal during the next scheduled maintenance window.
Update the SOP to include more frequent monitoring of the intake filters.
"""
    create_pdf("inspection_q3.pdf", inspection_text)

if __name__ == "__main__":
    generate_all()
