"""WhatsApp message generator — bilingual Tamil + English warning-shot messages.

Generates context-aware messages based on which patterns fired, with
the tenant's actual amounts and clause references.
"""

from .reasoner import LegalAnalysis
from .detector import Severity
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "output"


def generate_whatsapp(analyses: list[LegalAnalysis],
                      tenant_name: str = "[TENANT NAME]",
                      landlord_name: str = "[LANDLORD NAME]",
                      deposit_amount: str | None = None) -> str:
    """Generate a bilingual WhatsApp message based on fired patterns."""
    fired = [a for a in analyses if a.fired]
    red_flags = [a for a in fired if a.severity == Severity.RED]

    # Extract deposit amount if not provided
    if not deposit_amount:
        for a in analyses:
            dep = a.extracted.get("deposit_amount")
            if dep and isinstance(dep, int):
                deposit_amount = _fmt_inr(dep)
                break
    if not deposit_amount:
        deposit_amount = "[deposit amount]"

    # Pick the right message template based on the most serious issues
    pattern_ids = {a.pattern_id for a in fired}

    lines_en = []
    lines_ta = []

    # --- English section ---
    lines_en.append(f"Dear {landlord_name},")
    lines_en.append("")
    lines_en.append(f"This is regarding the security deposit of {deposit_amount} paid under the Lease Deed for the premises.")
    lines_en.append("")

    # Core demand
    lines_en.append("I am writing to formally request the refund of my security deposit in full, subject only to lawful and documented deductions.")
    lines_en.append("")

    # Pattern-specific lines
    if 1 in pattern_ids:
        ratio = None
        for a in analyses:
            if a.pattern_id == 1:
                ratio = a.extracted.get("deposit_ratio")
        if ratio:
            lines_en.append(f"The deposit of {deposit_amount} ({ratio} months' rent) is significantly above the 3-month statutory norm under Section 11(1) of the TN Tenancy Act 2017.")

    if 2 in pattern_ids:
        lines_en.append("Section 11(2) requires refund at the time of handover. Any deduction must be itemized and supported by proof.")

    if 4 in pattern_ids:
        lines_en.append("Any attempt to deduct lock-in penalty from the deposit without proof of actual loss will be disputed.")

    if 6 in pattern_ids:
        lines_en.append("Deductions for fixtures must be itemized with proof. Broad or undocumented deductions are not legally sustainable.")

    if 7 in pattern_ids:
        lines_en.append("The lease does not appear to be registered with the Rent Authority as required under Sections 4 and 4-A of the Act.")

    if 11 in pattern_ids:
        lines_en.append("Cutting off essential services (water, electricity, parking) is unlawful under Section 20. The Rent Authority can order immediate restoration.")

    lines_en.append("")
    lines_en.append("Please confirm the refund amount and timeline within 7 days. If not resolved, I will be compelled to send a formal legal notice and file a consumer complaint under the Consumer Protection Act, 2019.")
    lines_en.append("")
    lines_en.append(f"— {tenant_name}")

    # --- Tamil section ---
    lines_ta.append("")
    lines_ta.append("—————")
    lines_ta.append("")
    lines_ta.append(f"மதிப்பிற்குரிய {landlord_name} அவர்களுக்கு,")
    lines_ta.append("")
    lines_ta.append(f"குத்தகை ஒப்பந்தத்தின் கீழ் செலுத்திய {deposit_amount} காப்பு வைப்புத்தொகை குறித்து எழுதுகிறேன்.")
    lines_ta.append("")

    if 1 in pattern_ids:
        lines_ta.append("TN குத்தகை சட்டம் 2017 பிரிவு 11(1) படி, சட்டப்படியான நிலையான வைப்புத்தொகை 3 மாத வாடகை மட்டுமே.")

    if 2 in pattern_ids:
        lines_ta.append("பிரிவு 11(2) படி, காலி உடைமை ஒப்படைக்கும் நேரத்தில் வைப்புத்தொகை திருப்பித் தர வேண்டும். எந்த கழிப்பும் ஆவணச் சான்றுடன் இருக்க வேண்டும்.")

    if 4 in pattern_ids:
        lines_ta.append("லாக்-இன் அபராதத்தை உண்மையான இழப்புக்கான ஆதாரம் இல்லாமல் வைப்புத்தொகையிலிருந்து கழிப்பது சட்டப்படி நிலைக்காது.")

    if 6 in pattern_ids:
        lines_ta.append("பொருட்கள் மற்றும் சாதனங்களுக்கான கழிப்புகள் பட்டியலிடப்பட்டு ஆதாரத்துடன் இருக்க வேண்டும்.")

    if 7 in pattern_ids:
        lines_ta.append("சட்டத்தின் பிரிவு 4 மற்றும் 4-A படி வாடகை ஆணையத்தில் குத்தகை பதிவு கட்டாயம்.")

    if 11 in pattern_ids:
        lines_ta.append("தண்ணீர், மின்சாரம், பார்க்கிங் போன்ற அத்தியாவசிய சேவைகளை நிறுத்துவது பிரிவு 20 படி சட்டவிரோதம். வாடகை ஆணையம் உடனடி மறுசீரமைப்பு உத்தரவிடலாம்.")

    lines_ta.append("")
    lines_ta.append("7 நாட்களுக்குள் திருப்பித் தரும் தொகை மற்றும் காலக்கெடுவை உறுதிப்படுத்தவும். இல்லையெனில், சட்டப்படியான நடவடிக்கை எடுக்க நிர்பந்திக்கப்படுவேன்.")
    lines_ta.append("")
    lines_ta.append(f"— {tenant_name}")

    full_message = "\n".join(lines_en + lines_ta)

    # Save to file
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / "whatsapp_message.txt"
    out_path.write_text(full_message, encoding="utf-8")

    return full_message


def generate_whatsapp_text(analyses: list[LegalAnalysis],
                          tenant_name: str = "[TENANT NAME]",
                          landlord_name: str = "[LANDLORD NAME]",
                          deposit_amount: str | None = None) -> str:
    """Generate WhatsApp message and return as string (no file write)."""
    return generate_whatsapp(analyses, tenant_name, landlord_name, deposit_amount)


def _fmt_inr(amount: int) -> str:
    """Format amount in Indian numbering: ₹4,50,000."""
    s = str(amount)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    return f"₹{','.join(groups)},{last3}"
