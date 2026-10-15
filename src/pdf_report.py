"""CrossPay PDF Financial Report Generator."""
import io
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# CrossPay brand colors
BLUE = colors.HexColor('#0A2463')
GOLD = colors.HexColor('#E8B84B')
LIGHT_BLUE = colors.HexColor('#EEF2FF')
GREEN = colors.HexColor('#00C853')
RED = colors.HexColor('#E53935')
GRAY = colors.HexColor('#546E7A')
LIGHT_GRAY = colors.HexColor('#F8FAFF')


def _styles():
    styles = getSampleStyleSheet()
    custom = {
        "Title": ParagraphStyle("CPTitle", fontSize=24, textColor=colors.white,
                                fontName="Helvetica-Bold", alignment=TA_LEFT, leading=28),
        "Subtitle": ParagraphStyle("CPSub", fontSize=11, textColor=colors.HexColor('#BBDEFB'),
                                   fontName="Helvetica", alignment=TA_LEFT, leading=14),
        "SectionHeader": ParagraphStyle("CPSection", fontSize=13, textColor=BLUE,
                                        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
                                        borderPad=4),
        "Body": ParagraphStyle("CPBody", fontSize=9.5, textColor=colors.HexColor('#0D1B2A'),
                               fontName="Helvetica", leading=14, spaceAfter=4),
        "Small": ParagraphStyle("CPSmall", fontSize=8, textColor=GRAY,
                                fontName="Helvetica", leading=11),
        "Highlight": ParagraphStyle("CPHighlight", fontSize=10, textColor=BLUE,
                                    fontName="Helvetica-Bold", leading=14),
        "Chinese": ParagraphStyle("CPChinese", fontSize=9, textColor=GRAY,
                                  fontName="Helvetica", leading=12, spaceAfter=2),
    }
    return custom


def generate_pdf_report(student_data: dict, health_data: dict, alerts: list,
                        spending: dict, credit_history: list) -> bytes:
    """Generate a professional 3-page PDF financial report.
    Returns bytes of the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title="CrossPay Financial Report",
        author="CrossPay AI"
    )
    S = _styles()
    story = []
    W = A4[0] - 40*mm  # usable width
    
    # ── COVER HEADER ──────────────────────────────────────────────────────────
    # Blue header block
    header_table = Table([['']], colWidths=[W], rowHeights=[45*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLUE),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, -45*mm))  # overlap text over table
    
    name = student_data.get("name", "Student")
    home_currency = student_data.get("home_currency", "")
    home_country = student_data.get("home_country", "")
    today = datetime.now().strftime("%B %d, %Y")
    
    # Title area (drawn over the blue box)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(f"<font color='white' size='22'><b>CrossPay</b></font>"
                           f"<font color='#E8B84B' size='14'> Financial Report</font>", S["Body"]))
    story.append(Paragraph(f"<font color='white'>{name}</font>"
                           f"<font color='#BBDEFB'>  ·  {home_country} → China  ·  {home_currency}/CNY</font>", S["Body"]))
    story.append(Paragraph(f"<font color='#90CAF9'>Generated: {today}  ·  Powered by Gemini 3.8 Flash  ·  WeBank International</font>", S["Small"]))
    story.append(Spacer(1, 12*mm))
    
    # ── SECTION 1: FINANCIAL HEALTH OVERVIEW ──────────────────────────────────
    story.append(Paragraph("📊 Financial Health Overview  财务健康概览", S["SectionHeader"]))
    story.append(HRFlowable(width=W, thickness=2, color=BLUE, spaceAfter=8))
    
    score = health_data.get("score", 0)
    band = health_data.get("band", "Unknown")
    band_zh = health_data.get("band_zh", "")
    components = health_data.get("components", {})
    
    # Health score summary table
    score_color = GREEN if score >= 76 else GOLD if score >= 61 else RED
    summary_data = [
        [Paragraph('<b>CrossPay Health Score™</b>', S["Highlight"]),
         Paragraph(f'<font size="28" color="{score_color.hexval() if hasattr(score_color,"hexval") else "#0A2463"}"><b>{score}</b></font> / 100', S["Body"]),
         Paragraph(f'<b>{band}</b> · {band_zh}', S["Highlight"])],
    ]
    score_table = Table(summary_data, colWidths=[W*0.35, W*0.25, W*0.40])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BLUE]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E3E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 6))
    
    # Component breakdown
    weights = health_data.get("weights", {})
    comp_data = [[Paragraph('<b>Component</b>', S["Small"]),
                  Paragraph('<b>Score</b>', S["Small"]),
                  Paragraph('<b>Weight</b>', S["Small"]),
                  Paragraph('<b>Contribution</b>', S["Small"])]]
    comp_labels = {
        "credit": "Credit Score · 信用分数",
        "spending_discipline": "Spending Discipline · 支出纪律",
        "savings_rate": "Savings Rate · 储蓄率",
        "tuition_readiness": "Tuition Readiness · 学费准备",
    }
    for key, label in comp_labels.items():
        comp_score = components.get(key, 0)
        weight = weights.get(key, 0)
        contribution = round(comp_score * weight)
        bar = '█' * (comp_score // 10) + '░' * (10 - comp_score // 10)
        comp_data.append([
            Paragraph(label, S["Small"]),
            Paragraph(f'{comp_score}/100  {bar}', S["Small"]),
            Paragraph(f'{weight*100:.0f}%', S["Small"]),
            Paragraph(f'+{contribution}', S["Small"]),
        ])
    
    comp_table = Table(comp_data, colWidths=[W*0.38, W*0.30, W*0.12, W*0.20])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E3E8F0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 10))
    
    # ── SECTION 2: ACCOUNT SNAPSHOT ───────────────────────────────────────────
    story.append(Paragraph("💰 Account Snapshot  账户概览", S["SectionHeader"]))
    story.append(HRFlowable(width=W, thickness=2, color=BLUE, spaceAfter=8))
    
    balance_cny = student_data.get("balance_cny", 0)
    tuition = student_data.get("tuition_amount_cny", 0)
    due_date = student_data.get("tuition_due_date", "N/A")
    credit = student_data.get("credit_score", 0)
    account = student_data.get("bank_account", "****")
    
    snap_data = [
        ["CNY Balance", f"¥ {balance_cny:,.2f}",  "Credit Score", str(credit)],
        ["Tuition Due", f"¥ {tuition:,.0f}",       "Due Date", due_date],
        ["Bank Account", account,                   "Home Currency", home_currency],
    ]
    snap_table = Table(snap_data, colWidths=[W*0.20, W*0.30, W*0.20, W*0.30])
    snap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
        ('BACKGROUND', (2,0), (2,-1), LIGHT_BLUE),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E3E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (1,0), (1,-1), BLUE),
        ('TEXTCOLOR', (3,0), (3,-1), BLUE),
    ]))
    story.append(snap_table)
    story.append(Spacer(1, 10))
    
    # ── SECTION 3: SPENDING ANALYSIS ──────────────────────────────────────────
    story.append(Paragraph("📈 Spending Analysis  支出分析", S["SectionHeader"]))
    story.append(HRFlowable(width=W, thickness=2, color=BLUE, spaceAfter=8))
    
    categories = spending.get("categories", {})
    total_spend = spending.get("total_cny", 0)
    budget_pct = spending.get("vs_budget_pct", 0)
    
    if categories:
        spend_data = [[Paragraph('<b>Category</b>', S["Small"]),
                       Paragraph('<b>Amount (CNY)</b>', S["Small"]),
                       Paragraph('<b>% of Total</b>', S["Small"]),
                       Paragraph('<b>Trend</b>', S["Small"])]]
        cat_names = {"food": "Food 餐饮", "transport": "Transport 交通", "books": "Books 书籍",
                     "utilities": "Utilities 水电", "entertainment": "Entertainment 娱乐"}
        for cat, amt in sorted(categories.items(), key=lambda x: -x[1]):
            pct = (amt / total_spend * 100) if total_spend > 0 else 0
            bar = '▓' * int(pct / 10)
            spend_data.append([
                Paragraph(cat_names.get(cat, cat.title()), S["Small"]),
                Paragraph(f'¥ {amt:,.2f}', S["Small"]),
                Paragraph(f'{pct:.1f}% {bar}', S["Small"]),
                Paragraph('↔ Stable', S["Small"]),
            ])
        spend_data.append([
            Paragraph('<b>TOTAL</b>', S["Small"]),
            Paragraph(f'<b>¥ {total_spend:,.2f}</b>', S["Small"]),
            Paragraph(f'<b>{budget_pct}% of budget</b>', S["Small"]),
            Paragraph('', S["Small"]),
        ])
        spend_table = Table(spend_data, colWidths=[W*0.30, W*0.23, W*0.27, W*0.20])
        spend_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BLUE),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_GRAY]),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#E3E8F0')),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(spend_table)
    else:
        story.append(Paragraph("No spending data available for current month.", S["Body"]))
    story.append(Spacer(1, 10))
    
    # ── SECTION 4: ALERTS & RECOMMENDATIONS ──────────────────────────────────
    story.append(Paragraph("⚡ Smart Alerts & Recommendations  智能提醒与建议", S["SectionHeader"]))
    story.append(HRFlowable(width=W, thickness=2, color=GOLD, spaceAfter=8))
    
    if alerts:
        for alert in alerts[:5]:
            sev = alert.get("severity", "info")
            bg = colors.HexColor('#FFEBEE') if sev == "critical" else \
                 colors.HexColor('#FFF8E1') if sev == "warning" else \
                 colors.HexColor('#E3F2FD')
            border = RED if sev == "critical" else GOLD if sev == "warning" else colors.HexColor('#1976D2')
            msg = f"{alert.get('icon','')} {alert.get('message','')}"
            zh = alert.get('message_zh', '')
            alert_table = Table(
                [[Paragraph(msg, S["Body"]), Paragraph(zh, S["Chinese"])]],
                colWidths=[W*0.55, W*0.45]
            )
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg),
                ('LINEBEFORE', (0,0), (0,-1), 3, border),
                ('TOPPADDING', (0,0), (-1,-1), 7),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('ROUNDEDCORNERS', [4]),
            ]))
            story.append(alert_table)
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("✅ All clear! No urgent alerts at this time.", S["Body"]))
    
    story.append(Spacer(1, 10))
    
    # ── COMPLIANCE FOOTER ─────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, thickness=1, color=colors.HexColor('#E3E8F0'), spaceAfter=6))
    story.append(Paragraph(
        "🏛️ <b>Regulatory Notice:</b> All cross-border transfers are subject to PBOC (People's Bank of China) "
        "and SAFE (State Administration of Foreign Exchange) regulations. Transfers exceeding $10,000 USD "
        "are subject to AML reporting requirements per FATF guidelines.",
        S["Small"]
    ))
    story.append(Paragraph(
        "监管提示：所有跨境转账均受中国人民银行及国家外汇管理局监管。超过10,000美元的转账须依据金融行动特别工作组准则进行反洗钱申报。",
        S["Small"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"CrossPay © 2026 · WeBank International AI Finance Challenge · Generated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        ParagraphStyle("Footer", fontSize=7, textColor=GRAY, alignment=TA_CENTER)
    ))
    
    doc.build(story)
    return buffer.getvalue()
