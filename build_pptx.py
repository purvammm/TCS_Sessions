#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline HTML -> PPTX converter for parasites-haematology-theory.html.
Pure standard library (no python-pptx / lxml). Builds OOXML by hand.
"""
import os, re, math, zipfile
from html.parser import HTMLParser

SRC = "parasites-haematology-theory.html"
OUT = "parasites-haematology-theory.pptx"

# ---------- palette ----------
ACCENT="0A84FF"; PURPLE="5E5CE6"; INK="1D1D1F"; MUTED="6E6E73"; BORDER="D2D2D7"
CARDBG="FAFAFC"; TITLEBG="E8E8EA"; WHITE="FFFFFF"
GREEN="28C840"; GREEN_TX="1A9E34"; RED="FF5F57"; YELLOW="FEBC2E"; AMBER_TX="B8860B"
KEY_BG="EAF2FE"; WARN_BG="FEF6E6"; DANGER_BG="FFEEEC"; NOTE_BG="F7F7F9"
GOOD_CELL="E7F8EA"; BAD_CELL="FDEBEA"; HL_CELL="E4F0FE"; HL_HEAD="D6E9FF"
RBC="F7D9D4"; RBC_ED="FBE9E6"; CYTO="7FB0E8"; CHROM="B3005A"; PIG="5A3A1A"

# ---------- geometry ----------
SW, SH = 1280, 720            # px grid
EMU = 9525                    # emu per px (96 dpi)
MX = 64
CW = SW - 2*MX
BLOCK_TOP = 128
BLOCK_BOTTOM = 684
FOOT_Y = 688

def px(v): return int(round(v*EMU))
def pt(v): return int(round(v*100))
def esc(s):
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

# =========================================================
#  Minimal HTML DOM
# =========================================================
VOID={'br','img','meta','hr','input','link','col','area','base','source','wbr'}
SKIP={'svg','style','script'}

class Node:
    __slots__=("tag","attrs","classes","children","parent")
    def __init__(self,tag,attrs=None):
        self.tag=tag; self.attrs=attrs or {}
        self.classes=(self.attrs.get("class","") or "").split()
        self.children=[]; self.parent=None
    def add(self,c):
        if isinstance(c,Node): c.parent=self
        self.children.append(c)
    def has(self,cls): return cls in self.classes
    def child_elems(self):
        return [c for c in self.children if isinstance(c,Node)]
    def find_all(self,tag=None,cls=None):
        out=[]
        for c in self.child_elems():
            if (tag is None or c.tag==tag) and (cls is None or c.has(cls)):
                out.append(c)
            out.extend(c.find_all(tag,cls))
        return out
    def first(self,tag=None,cls=None):
        r=self.find_all(tag,cls); return r[0] if r else None

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root=Node("root"); self.stack=[self.root]
        self.skip=0; self.skiptag=None; self.skipdepth=0
    def handle_starttag(self,tag,attrs):
        if self.skip:
            if tag not in VOID: self.skipdepth+=1
            return
        d={}
        for k,v in attrs: d[k]=v if v is not None else ""
        n=Node(tag,d)
        self.stack[-1].add(n)
        if tag in SKIP:
            self.skip=1; self.skiptag=tag; self.skipdepth=0
            # keep node in tree (for svg aria-label) but ignore children
            return
        if tag not in VOID:
            self.stack.append(n)
    def handle_startendtag(self,tag,attrs):
        if self.skip: return
        d={}
        for k,v in attrs: d[k]=v if v is not None else ""
        self.stack[-1].add(Node(tag,d))
    def handle_endtag(self,tag):
        if self.skip:
            if tag==self.skiptag and self.skipdepth==0:
                self.skip=0; self.skiptag=None
            elif tag not in VOID:
                self.skipdepth=max(0,self.skipdepth-1)
            return
        if tag in VOID: return
        # pop until matching
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:
                del self.stack[i:]; break
    def handle_data(self,data):
        if self.skip: return
        if data:
            self.stack[-1].add(data)

# =========================================================
#  Inline run extraction (bold / italic / mono)
# =========================================================
def _runs(node, style, out, skip_lbl):
    for c in node.children:
        if isinstance(c,str):
            out.append((c, dict(style)))
        else:
            if c.tag in SKIP: continue
            if skip_lbl and c.has("lbl"): continue
            st=dict(style)
            if c.tag in ("strong","b"): st["b"]=True
            elif c.tag in ("em","i"): st["i"]=True
            elif c.tag=="code": st["mono"]=True
            _runs(c, st, out, skip_lbl)

def inline_runs(node, skip_lbl=False):
    raw=[]; _runs(node, {"b":False,"i":False,"mono":False}, raw, skip_lbl)
    # collapse whitespace, keep single spaces, merge same-style
    runs=[]
    for t,st in raw:
        t=t.replace("\xa0"," ")
        t=re.sub(r"\s+"," ",t)
        if t=="": continue
        if runs and runs[-1][1]==st:
            runs[-1]=(runs[-1][0]+t, st)
        else:
            runs.append((t,st))
    # trim leading/trailing spaces overall
    if runs:
        t0,s0=runs[0]; runs[0]=(t0.lstrip(),s0)
        tn,sn=runs[-1]; runs[-1]=(tn.rstrip(),sn)
        runs=[(t,s) for t,s in runs if t!=""]
    return runs

def plain(node):
    return "".join(t for t,_ in inline_runs(node)).strip()

# =========================================================
#  Slide model extraction
# =========================================================
def extract_slides(dom):
    slides=[]
    for sec in dom.root.find_all("section","slide"):
        cover=sec.first("div","cover")
        if cover is not None:
            slides.append({"type":"cover","node":cover})
            continue
        blocks=[]
        for ch in sec.child_elems():
            b=classify(ch)
            if b: blocks.append(b)
        slides.append({"type":"content","blocks":blocks})
    return slides

def classify(el):
    tag=el.tag
    if tag=="p":
        if el.has("eyebrow"): return {"k":"eyebrow","runs":inline_runs(el)}
        if el.has("src-note"): return {"k":"para","runs":inline_runs(el),"muted":True,"sz":10.5,"italic":True}
        return {"k":"para","runs":inline_runs(el),"lead":el.has("lead")}
    if tag in ("h1","h2","h3"):
        return {"k":"title","text":plain(el)}
    if tag=="ul":
        if el.has("agenda"):
            items=[]
            for li in el.find_all("li"):
                # remove the .num span text
                r=inline_runs(li, skip_lbl=False)
                # drop a leading pure-number run
                if r and re.fullmatch(r"\d+", r[0][0].strip()):
                    r=r[1:]
                    if r: r[0]=(r[0][0].lstrip(),r[0][1])
                items.append(r)
            return {"k":"list","items":items,"style":"num"}
        if el.has("checklist"):
            items=[inline_runs(li) for li in el.find_all("li")]
            return {"k":"list","items":items,"style":"check"}
        items=[inline_runs(li) for li in el.find_all("li")]
        return {"k":"list","items":items,"style":"dot"}
    if tag=="ol":
        items=[inline_runs(li) for li in el.find_all("li")]
        return {"k":"list","items":items,"style":"num"}
    if tag=="table":
        return extract_table(el)
    if tag=="div":
        if el.has("cards"):
            cols=4 if el.has("c4") else 3 if el.has("c3") else 2
            cards=[]
            for c in el.find_all("div","card"):
                h=c.first("h3"); p=c.first("p")
                cards.append({"title":plain(h) if h else "",
                              "runs":inline_runs(p) if p is not None else []})
            return {"k":"cards","cols":cols,"cards":cards}
        if el.has("steps3"):
            cards=[]
            for c in el.find_all("div","step-chip"):
                h=c.first("h3"); p=c.first("p")
                cards.append({"title":plain(h) if h else "",
                              "runs":inline_runs(p) if p is not None else []})
            return {"k":"cards","cols":3,"cards":cards}
        if el.has("twocol") or el.has("panels"):
            cols=[]
            boxsel="colbox" if el.has("twocol") else "panel"
            for cb in el.find_all("div",boxsel):
                h=cb.first("h3")
                ul=cb.first("ul")
                items=[inline_runs(li) for li in ul.find_all("li")] if ul else []
                paras=[inline_runs(p) for p in cb.child_elems() if p.tag=="p"]
                accent=ACCENT
                if cb.has("a"): accent=AMBER_TX
                if cb.has("b"): accent=GREEN_TX
                cols.append({"title":plain(h) if h else "","items":items,"paras":paras,"accent":accent})
            return {"k":"twocol","cols":cols}
        for kind,bg,stripe,lblcol in (
            ("keybox",KEY_BG,ACCENT,ACCENT),("warnbox",WARN_BG,YELLOW,AMBER_TX),
            ("dangerbox",DANGER_BG,RED,RED),("note",NOTE_BG,BORDER,INK)):
            if el.has(kind):
                lbl=el.first(None,"lbl")
                return {"k":"callout","bg":bg,"stripe":stripe,"lblcol":lblcol,
                        "label":plain(lbl) if lbl is not None else "",
                        "runs":inline_runs(el,skip_lbl=True)}
        if el.has("figure"):
            svg=el.first("svg")
            cap=el.first(None,"figcap")
            label=svg.attrs.get("aria-label","") if svg is not None else ""
            return {"k":"figure","label":label,"caption":plain(cap) if cap is not None else ""}
        if el.has("flow"):
            nodes=[]
            for fb in el.find_all("div","flow-box"):
                # main text excluding .sm
                main=[]; sm=[]
                for c in fb.children:
                    if isinstance(c,str):
                        main.append(c)
                    elif c.has("sm"):
                        sm.append(plain(c))
                    else:
                        main.append(plain(c))
                mtext=re.sub(r"\s+"," ","".join(main)).strip()
                nodes.append({"main":mtext,"sm":" ".join(sm).strip()})
            return {"k":"flow","nodes":nodes}
        if el.has("src-note"):
            return {"k":"para","runs":inline_runs(el),"muted":True,"sz":10.5,"italic":True}
    return None

def extract_table(el):
    heads=[]
    thead=el.first("thead")
    if thead:
        for th in thead.find_all("th"):
            heads.append({"runs":inline_runs(th),"hl":th.has("hl")})
    rows=[]
    tbody=el.first("tbody") or el
    for tr in tbody.find_all("tr"):
        if tr.parent and tr.parent.tag=="thead": continue
        cells=[]
        for td in tr.child_elems():
            if td.tag not in ("td","th"): continue
            cls=None
            if td.has("good"): cls="good"
            elif td.has("bad"): cls="bad"
            elif td.has("hl"): cls="hl"
            cells.append({"runs":inline_runs(td),"cls":cls})
        if cells: rows.append(cells)
    return {"k":"table","heads":heads,"rows":rows}

# =========================================================
#  OOXML shape helpers
# =========================================================
class Shapes:
    def __init__(self):
        self.xml=[]; self.sid=1
    def _id(self):
        self.sid+=1; return self.sid
    def rect(self,x,y,w,h,fill=None,line=None,lw=1.0,round_=False,rad=None,grad=None):
        gid=self._id()
        geom= 'roundRect' if round_ else 'rect'
        adj=''
        if round_:
            r=rad if rad is not None else 9000
            adj=f'<a:gd name="adj" fmla="val {r}"/>'
        if grad:
            fillx=(f'<a:gradFill><a:gsLst>'
                   f'<a:gs pos="0"><a:srgbClr val="{grad[0]}"/></a:gs>'
                   f'<a:gs pos="100000"><a:srgbClr val="{grad[1]}"/></a:gs>'
                   f'</a:gsLst><a:lin ang="2700000" scaled="1"/></a:gradFill>')
        elif fill:
            fillx=f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
        else:
            fillx='<a:noFill/>'
        if line:
            linex=(f'<a:ln w="{px(lw)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>')
        else:
            linex='<a:ln><a:noFill/></a:ln>'
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{gid}" name="r{gid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst>{adj}</a:avLst></a:prstGeom>{fillx}{linex}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>')
    def oval(self,x,y,w,h,fill=None,line=None,lw=1.0):
        gid=self._id()
        fillx=(f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>') if fill else '<a:noFill/>'
        linex=(f'<a:ln w="{px(lw)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>') if line else '<a:ln><a:noFill/></a:ln>'
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{gid}" name="o{gid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>{fillx}{linex}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>')
    def line(self,x1,y1,x2,y2,color=ACCENT,lw=2.0):
        gid=self._id()
        x=min(x1,x2); y=min(y1,y2); w=abs(x2-x1); h=abs(y2-y1)
        flipV=' flipV="1"' if (y2<y1) else ''
        flipH=' flipH="1"' if (x2<x1) else ''
        self.xml.append(
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{gid}" name="l{gid}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flipV}{flipH}><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(max(w,1))}" cy="{px(max(h,1))}"/></a:xfrm>'
            f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{px(lw)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln></p:spPr></p:cxnSp>')
    def text(self,x,y,w,h,paras,anchor="t",wrap=True,inset=6,autofit=False):
        gid=self._id()
        body=txbody(paras,anchor=anchor,wrap=wrap,inset=inset,autofit=autofit)
        self.xml.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{gid}" name="t{gid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>{body}</p:sp>')

def run_xml(text,sz,color,b=False,i=False,mono=False):
    at=f' sz="{pt(sz)}"'
    if b: at+=' b="1"'
    if i: at+=' i="1"'
    latin='<a:latin typeface="Consolas"/>' if mono else '<a:latin typeface="+mn-lt"/>'
    return (f'<a:r><a:rPr lang="en-US"{at}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'{latin}</a:rPr><a:t>{esc(text)}</a:t></a:r>')

def para_xml(runs,sz=14,color=INK,align="l",bullet=None,level=0,space_before=0,line_pct=100):
    algn=f' algn="{align}"' if align!="l" else ''
    if bullet in ("dot","check","num"):
        marL=228600*(level+1); indent=-228600
        if bullet=="dot":
            bu='<a:buFont typeface="Arial"/><a:buChar char="\u2022"/>'
        elif bullet=="check":
            bu='<a:buFont typeface="Arial"/><a:buChar char="\u2713"/>'
        else:
            bu='<a:buFont typeface="+mn-lt"/><a:buAutoNum type="arabicPeriod"/>'
        marx=f' marL="{marL}" indent="{indent}"'
    else:
        bu='<a:buNone/>'; marx=f' marL="{level*228600}" indent="0"'
    spc=f'<a:spcBef><a:spcPts val="{pt(space_before)}"/></a:spcBef>' if space_before else ''
    lns=f'<a:lnSpc><a:spcPct val="{line_pct*1000}"/></a:lnSpc>'
    rx=""
    if not runs:
        rx=f'<a:endParaRPr sz="{pt(sz)}"/>'
    else:
        for t,st in runs:
            if isinstance(st,dict):
                rx+=run_xml(t,sz,st.get("color",color),st.get("b",False),st.get("i",False),st.get("mono",False))
            else:
                rx+=run_xml(t,sz,color)
    return f'<a:p><a:pPr{marx}{algn}>{lns}{spc}{bu}</a:pPr>{rx}</a:p>'

def txbody(paras,anchor="t",wrap=True,inset=6,autofit=False):
    ins=px(inset/1.0)  # inset given in px-ish; convert
    ins=int(round(inset*EMU))
    wr='square' if wrap else 'none'
    af='<a:normAutofit/>' if autofit else '<a:noAutofit/>'
    bodypr=(f'<a:bodyPr wrap="{wr}" lIns="{ins}" tIns="{ins}" rIns="{ins}" bIns="{ins}" anchor="{anchor}">{af}</a:bodyPr>')
    return f'<p:txBody>{bodypr}<a:lstStyle/>{"".join(paras)}</p:txBody>'

# ---- table graphicFrame ----
def table_xml(sid_start,x,y,w,heads,rows,fsz,col_w,row_h):
    gid=sid_start
    grid="".join(f'<a:gridCol w="{px(cw)}"/>' for cw in col_w)
    trs=[]
    # header
    if heads:
        tcs=[]
        for j,hc in enumerate(heads):
            fill=HL_HEAD if hc["hl"] else TITLEBG
            paras=[para_xml(hc["runs"] or [("",{})],sz=fsz,color=INK,align="l")]
            tcs.append(tc_xml(paras,fill))
        trs.append(f'<a:tr h="{px(row_h[0])}">{"".join(tcs)}</a:tr>')
    # body
    off=1 if heads else 0
    for i,row in enumerate(rows):
        tcs=[]
        for cell in row:
            fill=WHITE
            if cell["cls"]=="good": fill=GOOD_CELL
            elif cell["cls"]=="bad": fill=BAD_CELL
            elif cell["cls"]=="hl": fill=HL_CELL
            paras=[para_xml(cell["runs"] or [("",{})],sz=fsz,color=INK,align="l")]
            tcs.append(tc_xml(paras,fill))
        trs.append(f'<a:tr h="{px(row_h[i+off])}">{"".join(tcs)}</a:tr>')
    tbl=(f'<a:tbl><a:tblPr firstRow="1" bandRow="0"/>'
         f'<a:tblGrid>{grid}</a:tblGrid>{"".join(trs)}</a:tbl>')
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{gid}" name="tbl{gid}"/>'
            f'<p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(sum(row_h))}"/></p:xfrm>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
            f'{tbl}</a:graphicData></a:graphic></p:graphicFrame>')

def tc_xml(paras,fill):
    b='<a:lnL w="6350"><a:solidFill><a:srgbClr val="'+BORDER+'"/></a:solidFill></a:lnL>'
    b+='<a:lnR w="6350"><a:solidFill><a:srgbClr val="'+BORDER+'"/></a:solidFill></a:lnR>'
    b+='<a:lnT w="6350"><a:solidFill><a:srgbClr val="'+BORDER+'"/></a:solidFill></a:lnT>'
    b+='<a:lnB w="6350"><a:solidFill><a:srgbClr val="'+BORDER+'"/></a:solidFill></a:lnB>'
    tcpr=(f'<a:tcPr marL="45720" marR="45720" marT="27432" marB="27432" anchor="t">'
          f'{b}<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></a:tcPr>')
    return f'<a:tc>{txbody(paras,inset=0)}{tcpr}</a:tc>'

# =========================================================
#  Height estimation
# =========================================================
def lh(sz): return sz*1.5
def cpl(width,sz): return max(4,int(width/(sz*0.56)))
def nlines(text,width,sz): return max(1, math.ceil(max(1,len(text))/cpl(width,sz)))
def runs_text(runs): return "".join(t for t,_ in runs)

def block_height(b,sf):
    k=b["k"]
    if k=="eyebrow": return lh(12*sf)+2
    if k=="title": return lh(28*sf)+8
    if k=="para":
        sz=b.get("sz",15 if b.get("lead") else 14)*sf
        return nlines(runs_text(b["runs"]),CW,sz)*lh(sz)+6
    if k=="list":
        sz=13.5*sf; h=0
        for it in b["items"]:
            h+=nlines(runs_text(it),CW-30,sz)*lh(sz)+4
        return h+4
    if k=="cards":
        cols=b["cols"]; rows=math.ceil(len(b["cards"])/cols)
        cw=(CW-14*(cols-1))/cols
        rowh=0
        for r in range(rows):
            mh=0
            for c in b["cards"][r*cols:(r+1)*cols]:
                th=lh(13*sf)
                bh=nlines(runs_text(c["runs"]),cw-24,11.5*sf)*lh(11.5*sf)
                mh=max(mh,th+bh+22)
            rowh+=mh+12
        return rowh
    if k=="twocol":
        cw=(CW-18)/2; mh=0
        for c in b["cols"]:
            hh=lh(14*sf)+6
            for it in c["items"]:
                hh+=nlines(runs_text(it),cw-34,12.5*sf)*lh(12.5*sf)+3
            for p in c["paras"]:
                hh+=nlines(runs_text(p),cw-24,12.5*sf)*lh(12.5*sf)+3
            mh=max(mh,hh)
        return mh+24
    if k=="callout":
        sz=12*sf; w=CW-40
        h=(lh(11*sf)+2) if b["label"] else 0
        h+=nlines(runs_text(b["runs"]),w,sz)*lh(sz)
        return h+24
    if k=="flow":
        h=0
        for i,n in enumerate(b["nodes"]):
            nh=lh(13*sf)+ (lh(10.5*sf) if n["sm"] else 0)+18
            h+=nh
            if i<len(b["nodes"])-1: h+=22
        return h
    if k=="figure":
        return 250*sf+ nlines(b["caption"],CW,10.5)*lh(10.5)+10
    if k=="table":
        return table_dims(b,sf)[3]
    return 20

def table_dims(b,sf):
    heads=b["heads"]; rows=b["rows"]
    ncol=len(heads) if heads else (len(rows[0]) if rows else 1)
    fsz=11*sf
    # column weights: first col wider
    weights=[1.5]+[1.0]*(ncol-1) if ncol>1 else [1.0]
    tot=sum(weights)
    col_w=[CW*wt/tot for wt in weights]
    row_h=[]
    if heads:
        mh=0
        for j,hc in enumerate(heads):
            mh=max(mh,nlines(runs_text(hc["runs"]),col_w[j]-16,fsz))
        row_h.append(max(28*sf,mh*lh(fsz)+14))
    for row in rows:
        mh=1
        for j,cell in enumerate(row):
            cwj=col_w[j] if j<len(col_w) else col_w[-1]
            mh=max(mh,nlines(runs_text(cell["runs"]),cwj-16,fsz))
        row_h.append(max(26*sf,mh*lh(fsz)+12))
    return fsz,col_w,row_h,sum(row_h)

# =========================================================
#  Render blocks
# =========================================================
def render_content(blocks):
    S=Shapes()
    # split off eyebrow/title
    eyebrow=None; title=None; rest=[]
    for b in blocks:
        if b["k"]=="eyebrow" and eyebrow is None: eyebrow=b
        elif b["k"]=="title" and title is None: title=b
        else: rest.append(b)
    # header
    if eyebrow:
        S.text(MX,42,CW,22,[para_xml(eyebrow["runs"],sz=12,color=ACCENT,line_pct=100)],inset=0)
    if title:
        S.text(MX,62,CW,46,[para_xml([(title["text"],{"b":True})],sz=27,color=INK)],inset=0)
    S.rect(MX,116,58,4,fill=ACCENT)
    # fit
    avail=BLOCK_BOTTOM-BLOCK_TOP
    sf=1.0
    total=sum(block_height(b,1.0)+14 for b in rest)
    if total>avail:
        sf=max(0.6, avail/total)
    y=BLOCK_TOP
    for b in rest:
        h=block_height(b,sf)
        draw_block(S,b,y,h,sf)
        y+=h+14*sf
    footer(S,None)
    return S

def draw_block(S,b,y,h,sf):
    k=b["k"]
    if k=="para":
        sz=b.get("sz",15 if b.get("lead") else 14)*sf
        col=MUTED if b.get("muted") else INK
        it=b.get("italic",False)
        runs=b["runs"]
        if it: runs=[(t,{**(s if isinstance(s,dict) else {}),"i":True}) for t,s in runs]
        S.text(MX,y,CW,h,[para_xml(runs,sz=sz,color=col)],inset=0)
    elif k=="list":
        paras=[]
        style=b["style"]
        for it in b["items"]:
            paras.append(para_xml(it,sz=13.5*sf,color=INK,bullet=style,space_before=3))
        S.text(MX,y,CW,h,paras,inset=0)
    elif k=="cards":
        draw_cards(S,b,y,sf)
    elif k=="twocol":
        draw_twocol(S,b,y,h,sf)
    elif k=="callout":
        draw_callout(S,b,y,h,sf)
    elif k=="flow":
        draw_flow(S,b,y,sf)
    elif k=="table":
        draw_table(S,b,y,sf)
    elif k=="figure":
        draw_figure(S,b,y,h,sf)

def draw_cards(S,b,y,sf):
    cols=b["cols"]; gap=14
    cw=(CW-gap*(cols-1))/cols
    rows=math.ceil(len(b["cards"])/cols)
    yy=y
    for r in range(rows):
        rowcards=b["cards"][r*cols:(r+1)*cols]
        # row height
        mh=0
        for c in rowcards:
            th=lh(13*sf); bh=nlines(runs_text(c["runs"]),cw-24,11.5*sf)*lh(11.5*sf)
            mh=max(mh,th+bh+22)
        for i,c in enumerate(rowcards):
            xx=MX+i*(cw+gap)
            S.rect(xx,yy,cw,mh,fill=CARDBG,line=BORDER,lw=1,round_=True,rad=7000)
            paras=[para_xml([(c["title"],{"b":True})],sz=13*sf,color=INK,space_before=0)]
            if c["runs"]:
                paras.append(para_xml(c["runs"],sz=11.5*sf,color=INK,space_before=4))
            S.text(xx+10,yy+8,cw-20,mh-16,paras,inset=0)
        yy+=mh+12

def draw_twocol(S,b,y,h,sf):
    cols=b["cols"]; gap=18; n=len(cols)
    cw=(CW-gap*(n-1))/n
    for i,c in enumerate(cols):
        xx=MX+i*(cw+gap)
        S.rect(xx,y,cw,h,fill=CARDBG,line=BORDER,lw=1,round_=True,rad=6000)
        paras=[para_xml([(c["title"],{"b":True,"color":c["accent"]})],sz=14*sf,color=c["accent"],align="ctr",space_before=0)]
        for it in c["items"]:
            paras.append(para_xml(it,sz=12.5*sf,color=INK,bullet="dot",space_before=3))
        for p in c["paras"]:
            paras.append(para_xml(p,sz=12.5*sf,color=INK,space_before=3))
        S.text(xx+12,y+10,cw-24,h-20,paras,inset=0)

def draw_callout(S,b,y,h,sf):
    S.rect(MX,y,CW,h,fill=b["bg"],round_=True,rad=5000)
    S.rect(MX,y,5,h,fill=b["stripe"])
    paras=[]
    if b["label"]:
        paras.append(para_xml([(b["label"].upper(),{"b":True,"color":b["lblcol"]})],sz=11*sf,color=b["lblcol"]))
    paras.append(para_xml(b["runs"],sz=12*sf,color=INK,space_before=2))
    S.text(MX+16,y+8,CW-28,h-14,paras,inset=0)

def draw_flow(S,b,y,sf):
    yy=y
    n=len(b["nodes"])
    bw=min(560, CW*0.62)
    xx=MX+(CW-bw)/2
    for i,node in enumerate(b["nodes"]):
        nh=lh(13*sf)+(lh(10.5*sf) if node["sm"] else 0)+18
        S.rect(xx,yy,bw,nh,fill="F3F8FF",line=ACCENT,lw=1.5,round_=True,rad=9000)
        paras=[para_xml([(node["main"],{"b":True})],sz=13*sf,color=INK,align="ctr")]
        if node["sm"]:
            paras.append(para_xml([(node["sm"],{})],sz=10.5*sf,color=MUTED,align="ctr",space_before=1))
        S.text(xx+8,yy+6,bw-16,nh-10,paras,anchor="ctr",inset=0)
        yy+=nh
        if i<n-1:
            S.text(MX,yy,CW,20,[para_xml([("\u2193",{"b":True})],sz=15*sf,color=ACCENT,align="ctr")],inset=0)
            yy+=22

def draw_table(S,b,y,sf):
    fsz,col_w,row_h,tot=table_dims(b,sf)
    S.xml.append(table_xml(S._id(),MX,y,CW,b["heads"],b["rows"],fsz,col_w,row_h))

# ---------- footer ----------
def footer(S,pageinfo):
    S.rect(0,FOOT_Y,SW,SH-FOOT_Y,fill=TITLEBG)
    S.text(MX-24,FOOT_Y+4,700,24,
           [para_xml([("Parasites in Haematology \u2014 Pathology Teaching",{"b":True})],sz=9.5,color=INK)],anchor="ctr",inset=0)
    S.text(SW-560,FOOT_Y+4,560-40,24,
           [para_xml([("Haematology \u00b7 Blood & Marrow Parasites",{})],sz=9.5,color=MUTED,align="r")],anchor="ctr",inset=0)

# ---------- cover ----------
def render_cover(node):
    S=Shapes()
    S.rect(0,0,SW,SH,grad=(ACCENT,PURPLE))
    badge=node.first(None,"badge")
    h1=node.first("h1")
    sub=node.first(None,"sub")
    meta=node.first(None,"meta")
    y=210
    if badge is not None:
        bt=plain(badge)
        bw=min(560, 40+len(bt)*8)
        S.rect(MX,y,bw,34,fill=None,line="FFFFFF",lw=1.2,round_=True,rad=20000)
        S.text(MX,y,bw,34,[para_xml([(bt,{"b":True})],sz=12,color=WHITE,align="ctr")],anchor="ctr",inset=0)
        y+=52
    if h1 is not None:
        ht=plain(h1)
        S.text(MX,y,CW,120,[para_xml([(ht,{"b":True})],sz=52,color=WHITE)],inset=0)
        y+=120
    if sub is not None:
        st=plain(sub)
        hh=nlines(st,CW,19)*lh(19)+6
        S.text(MX,y,CW,hh,[para_xml([(st,{})],sz=19,color="EAF1FF")],inset=0)
        y+=hh+18
    if meta is not None:
        S.text(MX,y,CW,40,[para_xml([(plain(meta),{})],sz=14,color="DCE6FF")],inset=0)
    return S

# =========================================================
#  Package assembly
# =========================================================
def slide_xml(shapes):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        + "".join(shapes.xml) +
        '</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping '
        'bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
        'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" '
        'hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sld>')

CONTENT_TYPES_HEAD=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
    '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
    '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
    '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
    '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>')

RELS_ROOT=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
    '</Relationships>')

PRESPROPS=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>')

def theme_xml():
    accents=[ACCENT,PURPLE,GREEN,YELLOW,RED,"5AC8FA"]
    acc="".join(f'<a:accent{i+1}><a:srgbClr val="{c}"/></a:accent{i+1}>' for i,c in enumerate(accents))
    fill=('<a:fillStyleLst>'
          '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
          '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
          '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
          '</a:fillStyleLst>')
    ln=('<a:lnStyleLst>'
        '<a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
        '<a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
        '<a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
        '</a:lnStyleLst>')
    eff=('<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>'
         '<a:effectStyle><a:effectLst/></a:effectStyle>'
         '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>')
    bg=('<a:bgFillStyleLst>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '</a:bgFillStyleLst>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Kiro">'
        '<a:themeElements><a:clrScheme name="Kiro">'
        '<a:dk1><a:srgbClr val="1D1D1F"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
        '<a:dk2><a:srgbClr val="6E6E73"/></a:dk2><a:lt2><a:srgbClr val="ECECEE"/></a:lt2>'
        +acc+
        '<a:hlink><a:srgbClr val="0A84FF"/></a:hlink><a:folHlink><a:srgbClr val="5E5CE6"/></a:folHlink>'
        '</a:clrScheme>'
        '<a:fontScheme name="Kiro"><a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
        '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>'
        '<a:fmtScheme name="Kiro">'+fill+ln+eff+bg+'</a:fmtScheme></a:themeElements>'
        '<a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')

SLIDE_MASTER=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
    '<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
    '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '</p:spTree></p:cSld>'
    '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
    'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
    '<p:txStyles>'
    '<p:titleStyle><a:lvl1pPr><a:defRPr sz="2800"><a:solidFill><a:srgbClr val="1D1D1F"/></a:solidFill>'
    '<a:latin typeface="+mn-lt"/></a:defRPr></a:lvl1pPr></p:titleStyle>'
    '<p:bodyStyle><a:lvl1pPr><a:defRPr sz="1400"><a:solidFill><a:srgbClr val="1D1D1F"/></a:solidFill>'
    '<a:latin typeface="+mn-lt"/></a:defRPr></a:lvl1pPr>'
    '<a:lvl2pPr><a:defRPr sz="1300"/></a:lvl2pPr></p:bodyStyle>'
    '<p:otherStyle><a:lvl1pPr><a:defRPr sz="1400"><a:latin typeface="+mn-lt"/></a:defRPr></a:lvl1pPr></p:otherStyle>'
    '</p:txStyles></p:sldMaster>')

SLIDE_MASTER_RELS=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
    '</Relationships>')

SLIDE_LAYOUT=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">'
    '<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '</p:spTree></p:cSld>'
    '<p:clrMapOvr><a:overrideClrMapping bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" '
    'accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" '
    'hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sldLayout>')

SLIDE_LAYOUT_RELS=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
    '</Relationships>')

def slide_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '</Relationships>')

def presentation_xml(n):
    sldids="".join(f'<p:sldId id="{256+i}" r:id="rId{2+i}"/>' for i in range(n))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{sldids}</p:sldIdLst>'
        '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>'
        '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>')

def presentation_rels(n):
    rels=['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(n):
        rels.append(f'<Relationship Id="rId{2+i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>')
    rels.append(f'<Relationship Id="rId{2+n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>')
    rels.append(f'<Relationship Id="rId{3+n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        +"".join(rels)+'</Relationships>')

# =========================================================
#  Figures (simplified schematics)
# =========================================================
def draw_figure(S,b,y,h,sf):
    label=b["label"].lower()
    fh=250*sf
    S.rect(MX,y,CW,fh,fill=CARDBG,line=BORDER,lw=1,round_=True,rad=4000)
    cx=MX+CW/2; cy=y+fh/2
    if "life cycle" in label:
        fig_lifecycle(S,y,fh,sf)
    elif "asexual stages" in label or "stages" in label and "cell" not in label:
        fig_stages(S,y,fh,sf)
    elif "stippling" in label:
        fig_stippling(S,y,fh,sf)
    elif "maltese" in label or "tetrad" in label:
        fig_maltese(S,y,fh,sf)
    elif "microfilaria" in label:
        fig_microfilaria(S,b,y,fh,sf)
    elif "trypomastigote" in label:
        fig_tryp(S,y,fh,sf)
    elif "leishman" in label or "donovan" in label:
        fig_ld(S,y,fh,sf)
    else:
        S.text(MX,y+fh/2-20,CW,40,[para_xml([("Schematic diagram",{"b":True})],sz=14,color=MUTED,align="ctr")],anchor="ctr",inset=0)
    # caption
    if b["caption"]:
        ch=nlines(b["caption"],CW,10.5)*lh(10.5)+6
        S.text(MX,y+fh+4,CW,ch,[para_xml([(b["caption"],{"i":True})],sz=10.5,color=MUTED,align="ctr")],inset=0)

def lbl(S,x,y,w,text,sz,color,align="ctr",bold=False):
    S.text(x,y,w,sz*1.6,[para_xml([(text,{"b":bold})],sz=sz,color=color,align=align)],anchor="ctr",inset=0)

def fig_lifecycle(S,y,fh,sf):
    labels=[("Mosquito bite","injects sporozoites",PURPLE),
            ("Liver stage","schizonts; hypnozoites relapse (vivax/ovale)",ACCENT),
            ("Blood stage","ring\u2192troph\u2192schizont\u2192rupture (fever)",GREEN_TX),
            ("Gametocytes","sexual forms taken up by mosquito",ACCENT),
            ("Mosquito midgut","sporogony \u2192 sporozoites",PURPLE)]
    n=len(labels); gap=10
    bw=(CW-40-gap*(n-1))/n
    yy=y+40; bh=fh-120
    for i,(m,s,col) in enumerate(labels):
        xx=MX+20+i*(bw+gap)
        S.rect(xx,yy,bw,bh,fill="F3F8FF",line=col,lw=1.5,round_=True,rad=8000)
        paras=[para_xml([(m,{"b":True})],sz=11.5*sf,color=INK,align="ctr"),
               para_xml([(s,{})],sz=9.5*sf,color=MUTED,align="ctr",space_before=3)]
        S.text(xx+6,yy+8,bw-12,bh-16,paras,anchor="ctr",inset=0)
        if i<n-1:
            S.text(xx+bw,yy,gap+4,bh,[para_xml([("\u2192",{"b":True})],sz=13*sf,color=ACCENT,align="ctr")],anchor="ctr",inset=0)
    S.text(MX,y+fh-64,CW,26,[para_xml([("Cycle repeats every 24 / 48 / 72 h \u2192 periodic fever; only blood stages appear on the film",{"b":True})],sz=10.5*sf,color=ACCENT,align="ctr")],anchor="ctr",inset=0)

def rbc(S,cx,cy,r,fill=RBC):
    S.oval(cx-r,cy-r,2*r,2*r,fill=fill,line="D98B80",lw=1.2)

def fig_stages(S,y,fh,sf):
    names=[("Ring","thin ring + red dot"),("Trophozoite","amoeboid + pigment"),
           ("Schizont","merozoites + pigment"),("Gametocyte","banana (falciparum)")]
    n=4; slot=CW/n; r=34*sf; cy=y+90*sf
    for i,(nm,ds) in enumerate(names):
        cx=MX+slot*(i+0.5)
        rbc(S,cx,cy,r)
        if i==0:
            S.oval(cx-14,cy-14,28,28,fill=None,line=CYTO,lw=4); S.oval(cx+4,cy-12,8,8,fill=CHROM)
        elif i==1:
            S.oval(cx-16,cy-12,30,26,fill=CYTO,line="4a6fa5",lw=1); S.oval(cx-2,cy-6,8,8,fill=CHROM); S.oval(cx+6,cy+4,5,5,fill=PIG)
        elif i==2:
            import math as _m
            for k in range(8):
                a=k*_m.pi/4; S.oval(cx+14*_m.cos(a)-4,cy+14*_m.sin(a)-4,8,8,fill=CHROM)
            S.oval(cx-4,cy-4,8,8,fill=PIG)
        else:
            S.oval(cx-10,cy-20,20,40,fill="8aa9d6",line="4a6fa5",lw=1); S.oval(cx-4,cy-4,9,9,fill=CHROM)
        lbl(S,cx-slot/2,cy+r+8,slot,nm,12*sf,INK,bold=True)
        lbl(S,cx-slot/2,cy+r+26,slot,ds,9.5*sf,MUTED)

def fig_stippling(S,y,fh,sf):
    import random
    data=[("Schüffner's dots","vivax / ovale",RBC_ED,46*sf,"E0708A",True),
          ("Maurer's clefts","falciparum",RBC,38*sf,"A11E46",False),
          ("Ziemann's dots","malariae",RBC,34*sf,"C98A9C",False)]
    slot=CW/3; cy=y+95*sf
    random.seed(7)
    for i,(nm,sp,fill,r,dot,many) in enumerate(data):
        cx=MX+slot*(i+0.5)
        rbc(S,cx,cy,r,fill=fill)
        S.oval(cx-13,cy-13,26,26,fill=None,line=CYTO,lw=4); S.oval(cx+4,cy-11,7,7,fill=CHROM)
        cnt=9 if many else 3
        for k in range(cnt):
            a=random.random()*6.283; rr=random.random()*(r-10)
            dx=cx+rr*math.cos(a); dy=cy+rr*math.sin(a)
            sz=2.6 if many else (3.4 if i==1 else 2)
            S.oval(dx-sz,dy-sz,2*sz,2*sz,fill=dot)
        lbl(S,cx-slot/2,cy+r+8,slot,nm,12*sf,INK,bold=True)
        lbl(S,cx-slot/2,cy+r+26,slot,sp,10*sf,MUTED)

def fig_maltese(S,y,fh,sf):
    cx=MX+CW*0.30; cy=y+fh/2-10; r=54*sf
    rbc(S,cx,cy,r)
    off=20*sf
    for dx,dy in [(0,-off),(0,off),(-off,0),(off,0)]:
        S.oval(cx+dx-8,cy+dy-11,16,22,fill="8fb6e6",line="3f6fae",lw=1.2)
        S.oval(cx+dx-2,cy+dy-2,5,5,fill=CHROM)
    lbl(S,cx-90,cy+r+10,180,'"Maltese cross" tetrad',12*sf,INK,bold=True)
    lbl(S,cx-90,cy+r+28,180,"pathognomonic of Babesia",10*sf,MUTED)
    # ring cell
    cx2=MX+CW*0.68
    rbc(S,cx2,cy,r)
    S.oval(cx2-16,cy-10,22,22,fill=None,line="8fb6e6",lw=4); S.oval(cx2-8,cy-4,6,6,fill=CHROM)
    S.oval(cx2+8,cy+8,16,16,fill=None,line="8fb6e6",lw=3)
    S.oval(cx2+38,cy-30,13,13,fill=None,line="8fb6e6",lw=3)  # extracellular
    lbl(S,cx2-100,cy+r+10,200,"Rings + extracellular forms",12*sf,INK,bold=True)
    lbl(S,cx2-100,cy+r+28,200,"small, pleomorphic, NO pigment",10*sf,MUTED)

def fig_microfilaria(S,b,y,fh,sf):
    cap=b["caption"].lower()+ b["label"].lower()
    cy=y+fh*0.42
    # sheath (light thick) as rounded rect band
    S.rect(MX+40,cy-16,CW-80,30,fill="EDE0F2",line=None,round_=True,rad=50000)
    # body: series of small circles forming gentle wave
    nseg=26
    for i in range(nseg):
        t=i/(nseg-1)
        xx=MX+50+t*(CW-100)
        yy=cy + math.sin(t*3.14159*2)*14
        S.oval(xx-3,yy-3,6,6,fill="5E5CE6")
    # nuclei dots
    tail_to_tip = ("loa" in cap) or ("perstans" in cap)
    two_terminal = ("brugia" in cap)
    nn=16
    for i in range(nn):
        t=i/(nn-1)
        if not tail_to_tip and not two_terminal and t>0.86: continue
        xx=MX+55+t*(CW-110)
        yy=cy + math.sin(t*3.14159*2)*14
        S.oval(xx-2.6,yy-2.6,5.2,5.2,fill=CHROM)
    if two_terminal:
        xt=MX+55+(CW-110); yt=cy+math.sin(3.14159*2)*14
        S.oval(xt-16-3,yt-3,6,6,fill=CHROM); S.oval(xt-3,yt-3,6,6,fill=CHROM)
    lbl(S,MX+40,cy+26,CW-80,"sheath present" if ("mansonella" not in cap and "ozzardi" not in cap and "perstans" not in cap) else "unsheathed",11*sf,ACCENT,bold=True)
    tip_note="nuclei extend to tail tip" if tail_to_tip else ("two separate terminal nuclei" if two_terminal else "nuclei stop short of tail tip")
    lbl(S,MX+40,cy+44,CW-80,tip_note,10.5*sf,MUTED)

def fig_tryp(S,y,fh,sf):
    cx=MX+CW/2; cy=y+fh*0.42
    # body ellipse
    S.oval(cx-160,cy-26,320,52,fill="BCD3F0",line="3f6fae",lw=1.6)
    # nucleus
    S.oval(cx-14,cy-12,28,24,fill=CYTO,line="3f6fae",lw=1)
    # kinetoplast posterior
    S.oval(cx-158,cy-6,14,14,fill=CHROM)
    # flagellum
    S.line(cx+160,cy,cx+240,cy-22,color=ACCENT,lw=2.5)
    lbl(S,cx-260,cy+40,180,"kinetoplast (posterior)",10.5*sf,ACCENT,align="l",bold=True)
    lbl(S,cx-30,cy-56,120,"nucleus",10.5*sf,ACCENT,bold=True)
    lbl(S,cx+150,cy-52,150,"free flagellum",10.5*sf,ACCENT,align="l",bold=True)
    lbl(S,cx-120,cy+58,240,"undulating membrane along body",10*sf,MUTED)

def fig_ld(S,y,fh,sf):
    cx=MX+CW*0.32; cy=y+fh/2
    S.oval(cx-120,cy-70,240,140,fill="EAF1FB",line="8aa9d6",lw=2)
    S.oval(cx-70,cy-56,50,38,fill="9DB8E0",line="5e7cb0",lw=1)  # macrophage nucleus
    import random; random.seed(3)
    for _ in range(7):
        dx=random.uniform(-70,70); dy=random.uniform(-30,50)
        S.oval(cx+dx-11,cy+dy-8,22,16,fill="CFE0F5",line="4a6fa5",lw=1)
        S.oval(cx+dx-6,cy+dy-3,6,6,fill="7A1440")
        S.rect(cx+dx+2,cy+dy-2,6,3,fill=CHROM)
    lbl(S,cx-120,cy+76,240,"Macrophage packed with LD bodies",11.5*sf,INK,bold=True)
    # enlarged
    ex=MX+CW*0.74
    S.oval(ex-46,cy-32,92,66,fill="CFE0F5",line="4a6fa5",lw=1.4)
    S.oval(ex-22,cy-12,24,24,fill="7A1440")
    S.rect(ex+6,cy-8,22,9,fill=CHROM)
    lbl(S,ex-70,cy+40,140,"amastigote (enlarged)",10.5*sf,MUTED)
    lbl(S,ex-70,cy-52,60,"nucleus",9.5*sf,ACCENT,bold=True)
    lbl(S,ex+2,cy-52,90,"kinetoplast",9.5*sf,ACCENT,bold=True)

# =========================================================
#  Main
# =========================================================
def main():
    html=open(SRC,encoding="utf-8").read()
    dom=DOM(); dom.feed(html)
    slides=extract_slides(dom)
    print("slides parsed:",len(slides))
    slide_parts=[]
    for i,sl in enumerate(slides):
        if sl["type"]=="cover":
            S=render_cover(sl["node"])
        else:
            S=render_content(sl["blocks"])
        slide_parts.append(slide_xml(S))
    n=len(slide_parts)
    with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED) as z:
        ct=CONTENT_TYPES_HEAD
        for i in range(n):
            ct+=f'<Override PartName="/ppt/slides/slide{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        ct+='</Types>'
        z.writestr("[Content_Types].xml",ct)
        z.writestr("_rels/.rels",RELS_ROOT)
        z.writestr("ppt/presentation.xml",presentation_xml(n))
        z.writestr("ppt/_rels/presentation.xml.rels",presentation_rels(n))
        z.writestr("ppt/presProps.xml",PRESPROPS)
        z.writestr("ppt/theme/theme1.xml",theme_xml())
        z.writestr("ppt/slideMasters/slideMaster1.xml",SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels",SLIDE_MASTER_RELS)
        z.writestr("ppt/slideLayouts/slideLayout1.xml",SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels",SLIDE_LAYOUT_RELS)
        for i,part in enumerate(slide_parts):
            z.writestr(f"ppt/slides/slide{i+1}.xml",part)
            z.writestr(f"ppt/slides/_rels/slide{i+1}.xml.rels",slide_rels())
    print("wrote",OUT,os.path.getsize(OUT),"bytes")

if __name__=="__main__":
    main()
