"""Released-report PDF export, generated from the immutable approved snapshot."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
from reportlab.lib.pagesizes import A4
from .store import ROOT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for _name,_file in [("KLESans","DejaVuSans.ttf"),("KLEBold","DejaVuSans-Bold.ttf"),("KLESerif","DejaVuSerif.ttf")]:
    pdfmetrics.registerFont(TTFont(_name,str(ROOT/"data/fonts"/_file)))

def render_pdf(release):
    r=release['report'];buf=BytesIO();styles=getSampleStyleSheet();styles['Heading2'].fontName='KLEBold'
    styles.add(ParagraphStyle(name='BodySmall',fontName='KLESans',fontSize=9,leading=13,spaceAfter=7))
    styles.add(ParagraphStyle(name='TitleKLE',fontName='KLESerif',fontSize=27,leading=31,textColor=colors.HexColor('#272a30'),spaceAfter=12))
    styles.add(ParagraphStyle(name='SectionKLE',fontName='KLEBold',fontSize=11,leading=16,spaceBefore=14,spaceAfter=8,textColor=colors.HexColor('#a82330')))
    def p(t,style='BodySmall'):
        text=str(t).replace('→',' / ').replace('×','x').replace('—','-').replace('–','-')
        return Paragraph(escape(text),styles[style])
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=42,title=f"Faculty appraisal - {r['faculty_name']}",author='KLE Technological University')
    story=[]
    logo=ROOT/'web/assets/kle-logo.jpg'
    if logo.is_file():
        story.extend([Image(str(logo),width=300,height=51),Spacer(1,20)])
    story.extend([p('Faculty Appraisal Report','TitleKLE'),p(f"{r['cycle']} | Version {release['version']} | Released {release['created'][:10]}"),p(r['faculty_name'],'Heading2'),p(r['department']),p(f"API score: {r['score']['total']:.2f} | Final rating: {r['final_rating']}"),p(r['summary'].replace('Pending named human review.','Human review completed; see approval trail.'))])
    story.append(p('Calculation and policy references','SectionKLE'))
    data=[[p('Component'),p('Method and source'),p('Points')]]
    for c in r['score']['components']:data.append([p(c['kind'].replace('_',' ').title()),p(c['formula']+'\nPolicy: '+c['policy_citation']),p(f"{c['points']:.2f}")])
    t=Table(data,colWidths=[112,322,77],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f0ede9')),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#ddd9d4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([t,Spacer(1,8),p(r['score']['rounding'])])
    story.append(p('Human approval trail','SectionKLE'))
    for a in r['approvals']:story.append(p(f"{a['reviewer']} ({a['role']}) | {a['action']} | {a['at'][:19]} UTC. {a['note']}"))
    story.append(p('Evidence register','SectionKLE'))
    for i,ev in enumerate(r['evidence'],1):
        story.append(KeepTogether([p(f"{i}. {ev['title']}"),p(f"{ev['source_name']} | {ev['locator']} | Verified by {ev['review']['reviewer']}"),p('SHA-256: '+ev['sha256']),Spacer(1,5)]))
    story.append(p('Validation and declarations','SectionKLE'))
    for chk in r['checks']:story.append(p(f"{'PASS' if chk['passed'] else 'FAIL'} - {chk['name']}"))
    for category,note in r.get('completeness',{}).items():story.append(p(f'{category}: {note}'))
    for item in r.get('excluded',[]):story.append(p(f"Excluded: {item['id']} - {item['reason']}"))
    story.extend([p('Release integrity','SectionKLE'),p('Report SHA-256: '+release['hash']),p('Release ID: '+release['id']),p('A restored historical version retains its original approvals. The active version is identified in the application.')])
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#b52835'));canvas.line(42,33,553,33);canvas.setFont('KLESans',8);canvas.setFillColor(colors.HexColor('#777777'));canvas.drawString(42,21,'KLE Technological University | Confidential faculty appraisal');canvas.drawRightString(553,21,f'Page {doc.page}');canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer);return buf.getvalue()
