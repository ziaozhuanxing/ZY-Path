"""Reproducible muted-colour thesis diagrams with explicit orthogonal routing.
Run with Python, PyMuPDF and Inkscape. Outputs SVG masters, print-resolution PNGs and
geometry checks. No inference, measurements or screenshots are generated.
"""
from pathlib import Path
from html import escape
import json,math,subprocess
import xml.etree.ElementTree as ET
import fitz
R=Path(__file__).parent/'diagrams';R.mkdir(exist_ok=True)
FONT=fitz.Font('helv');BOLD=fitz.Font('hebo')
# Colour is applied after drawing. This pass never changes coordinates, paths,
# text, type sizes, line widths, object order or image dimensions.
PALETTE = {
 'ui':('#E6EFF8','#567B9D'),
 'core':('#E8F4F0','#538C7D'),
 'records':('#F0ECF7','#84739F'),
 'decision':('#FFF3DC','#B48A40'),
 'error':('#FBEDE8','#B37766'),
 'neutral':('#F2F5F7','#899BA9'),
 'coordinator':('#DCE9F5','#416A91'),
}
ROLE_MAP = {
 'architecture':dict(user='neutral',coordinator='coordinator',ui='ui',engine='core',services='records',settings='ui',pipeline='core',outputs='records',sources='neutral'),
 'use_case':dict(model='ui',image='ui',classification='core',segmentation='core',inspect='ui',search='records',restore='records',rerun='records',export='records',defaults='ui',cancel='decision',clear='ui',delete='error',validate='decision',tiled='core',compare='ui'),
 'sequence':dict(window='coordinator',engine='core',files='records',database='records',pipeline='core'),
 'class_diagram':dict(main='coordinator',input='ui',history='records',database='records',engine='core',pdf='records',compare='ui',loader='core',exporter='records',zoom='ui',preprocess='core',parser='core',ownedworker='neutral',qthread='neutral'),
 'activity':dict(action='decision',run='ui',rerun='records',valid='decision',mode='decision',single='core',tiled='core',segmentation='core',state='decision',cancel='decision',save='ui',saved='decision',error='error',insert='records'),
}
def colour_svg(src,name,nodes):
 ET.register_namespace('', 'http://www.w3.org/2000/svg')
 root=ET.fromstring(src)
 for node in root:
  tag=node.tag.rsplit('}',1)[-1]
  if node.get('stroke')=='black':node.set('stroke','#526D84')
  if node.get('fill')=='black':node.set('fill','#20374C' if tag=='text' else '#526D84')
  box=None
  if tag=='rect' and node.get('x') is not None:
   x,y,w,h=[float(node.get(v)) for v in ['x','y','width','height']];box=[x,y,x+w,y+h]
  elif tag=='ellipse':
   x,y,rx,ry=[float(node.get(v)) for v in ['cx','cy','rx','ry']];box=[x-rx,y-ry,x+rx,y+ry]
  elif tag=='polygon':
   xy=[tuple(map(float,p.split(','))) for p in node.get('points').split()];box=[min(p[0] for p in xy),min(p[1] for p in xy),max(p[0] for p in xy),max(p[1] for p in xy)]
  if box is not None:
   for key,bounds in nodes.items():
    if all(abs(x-y)<.001 for x,y in zip(box,bounds)):
     fill,stroke=PALETTE[ROLE_MAP[name].get(key,'neutral')];node.set('fill',fill);node.set('stroke',stroke);break
 return ET.tostring(root,encoding='unicode')

class Drawing:
 def __init__(self,name,w,h):
  self.name=name;self.w=w;self.h=h;self.parts=[];self.nodes={};self.routes=[];self.texts=[]
 def rect(self,x,y,w,h,**kw):
  fill=kw.get('fill','white')
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="black" stroke-width="2"/>')
 def text(self,x,y,s,size=23,bold=False,anchor='middle',mask=False):
  width=(BOLD if bold else FONT).text_length(s,fontsize=size)
  left=x-width/2 if anchor=='middle' else x
  bounds=[left,y-size,left+width,y+size*.24]
  assert left>=-1 and bounds[2]<=self.w+1,(self.name,s,bounds)
  self.texts.append({'text':s,'bounds':bounds,'masked':mask})
  if mask:self.parts.append(f'<rect x="{bounds[0]-3}" y="{bounds[1]-2}" width="{width+6}" height="{size*1.24+4}" fill="white" stroke="none"/>')
  self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="black">{escape(s)}</text>')
  return bounds
 def label(self,x,y,s,size=22):return self.text(x,y,s,size,mask=True)
 def node(self,key,x,y,w,h,lines,shape='box',size=23):
  self.nodes[key]=[x,y,x+w,y+h]
  if shape=='diamond':
   points=[(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]
   self.parts.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in points)+'" fill="white" stroke="black" stroke-width="2"/>')
  elif shape=='ellipse':self.parts.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="white" stroke="black" stroke-width="2"/>')
  else:self.rect(x,y,w,h)
  if isinstance(lines,str):lines=lines.split('\n')
  gap=size*1.28;first=y+h/2-(len(lines)-1)*gap/2+size*.32
  for i,line in enumerate(lines):
   b=self.text(x+w/2,first+i*gap,line,size)
   assert b[0]>=x+8 and b[2]<=x+w-8 and b[1]>=y+2 and b[3]<=y+h-2,(self.name,key,line,b)
 def route(self,points,style='solid',arrow=True,name='',audit=True):
  assert len(points)>=2
  for (x,y),(xx,yy) in zip(points,points[1:]):
   if audit:assert x==xx or y==yy,(self.name,name,points)
  dashed=' stroke-dasharray="9 6"' if style=='dashed' else ''
  self.parts.append('<polyline points="'+' '.join(f'{a},{b}' for a,b in points)+'" fill="none" stroke="black" stroke-width="2"'+dashed+'/>')
  if arrow:
   a,b=points[-2:];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);assert length>0
   ux,uy=dx/length,dy/length;z=13 if style!='inheritance' else 19;half=5 if style!='inheritance' else 9
   triangle=[b,(b[0]-ux*z-uy*half,b[1]-uy*z+ux*half),(b[0]-ux*z+uy*half,b[1]-uy*z-ux*half)]
   self.parts.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in triangle)+'" fill="'+('white' if style=='inheritance' else 'black')+'" stroke="black" stroke-width="1.5"/>')
  self.routes.append({'name':name,'points':points,'audit':audit})
 def circle(self,x,y,r=7,final=False):
  if final:self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r+5}" fill="white" stroke="black" stroke-width="2"/>')
  self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="black"/>')
 def actor(self,x,y):
  self.parts.append(f'<circle cx="{x}" cy="{y-33}" r="14" fill="white" stroke="black" stroke-width="2"/>')
  for points in [[(x,y-19),(x,y+22)],[(x-23,y),(x+23,y)],[(x,y+22),(x-23,y+47)],[(x,y+22),(x+23,y+47)]]:self.route(points,arrow=False,audit=False)
  self.text(x,y+75,'User',21)
 def save(self):
  issues=[]
  for route in self.routes:
   if not route['audit']:continue
   for a,b in zip(route['points'],route['points'][1:]):
    for key,(x,y,xx,yy) in self.nodes.items():
     # Shrink the bounding rectangle slightly: touching a node port is allowed.
     if a[0]==b[0]:hit=x+.5<a[0]<xx-.5 and max(min(a[1],b[1]),y+.5)<min(max(a[1],b[1]),yy-.5)
     else:hit=y+.5<a[1]<yy-.5 and max(min(a[0],b[0]),x+.5)<min(max(a[0],b[0]),xx-.5)
     # Diamond corners are unoccupied; routes terminate at side/top/bottom ports.
     if hit:issues.append((route['name'],key,a,b))
  assert not issues,(self.name,issues)
  label_issues=[]
  for route in self.routes:
   if not route['audit']:continue
   for a,b in zip(route['points'],route['points'][1:]):
    for text in self.texts:
     if text['masked']:continue
     x,y,xx,yy=text['bounds']
     if a[0]==b[0]:hit=x<a[0]<xx and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),yy)
     else:hit=y<a[1]<yy and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),xx)
     if hit:label_issues.append((route['name'],text['text']))
  assert not label_issues,(self.name,label_issues)
  src=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>'+''.join(self.parts)+'</svg>'
  src=colour_svg(src,self.name,self.nodes)
  (R/(self.name+'.svg')).write_text(src)
  subprocess.run(['inkscape',str(R/(self.name+'.svg')),'--export-type=png','--export-filename='+str(R/(self.name+'.png')),'--export-width='+str(self.w*2)],check=True,capture_output=True)
  audit={'canvas':[self.w,self.h],'node_count':len(self.nodes),'routes_checked':sum(r['audit'] for r in self.routes),'route_node_intersections':issues,'text_fits_nodes':True,'unmasked_route_text_intersections':label_issues,'text_boxes':self.texts,'nodes':self.nodes,'routes':self.routes}
  (R/(self.name+'_geometry.json')).write_text(json.dumps(audit,indent=2));return audit

checks={}
# Figure 3.1: three parallel responsibilities; no return path shares a rail.
a=Drawing('architecture',1100,1100)
a.node('user',350,20,400,70,'Research / education user')
a.node('coordinator',50,160,1000,130,['MainWindow: application coordinator','Run: current Preferences snapshot','Re-run: recorded analysis snapshot'],size=25)
a.route([(550,90),(550,160)],name='user action')
a.node('ui',40,390,300,160,['Interface panels','Input / history / settings','Linked spatial inspection','Clear view / selection'])
a.node('engine',400,390,300,160,['InferenceEngine','Owned worker thread','Model / input validation','CPU PyTorch inference'])
a.node('services',760,390,300,160,['Record / export services','DatabaseManager','ExportManager','PdfExportWorker'])
for x in [190,550,910]:a.route([(x,290),(x,390)],name='coordinator responsibility')
a.text(210,350,'signals / display',22,anchor='start');a.text(570,350,'start / cancel',22,anchor='start');a.text(930,350,'save / export',22,anchor='start')
a.node('settings',40,670,300,150,['QSettings','Current Preferences','Per-task model defaults'])
a.node('pipeline',400,670,300,150,['Task-specific pipeline','Classification crops OR','segmentation windows','Independent labels'])
a.node('outputs',760,670,300,150,['Saved records / files','SQLite + analysis JSON','PNG / maps / PDF'])
a.route([(190,550),(190,670)],name='preferences through UI');a.text(210,620,'configure',22,anchor='start')
a.route([(550,550),(550,670)],name='model execution');a.text(570,620,'execute',22,anchor='start')
a.route([(910,550),(910,670)],name='completed persistence');a.text(930,620,'completed outputs',20,anchor='start')
a.node('sources',400,920,300,85,['Local source image','Trusted model resources'])
a.route([(550,920),(550,820)],name='read source resources');a.label(675,880,'read inputs')
a.text(550,1080,'Logical responsibilities; arrows identify actions or data flow.',22)
checks[a.name]=a.save()

# Figure 3.3: repeat the same actor by workflow band, preventing a 13-line fan.
a=Drawing('use_case',1100,1400)
a.rect(220,20,870,1350)
a.text(655,50,'ZY-Path local application',25,True)
for y in [270,620,960]:a.route([(220,y),(1090,y)],style='dashed',arrow=False,audit=False)
for cy in [155,445,800,1150]:a.actor(80,cy)
left=[('model',105,'Select model',155),('image',205,'Select image',155),('classification',345,'Run classification',445),('segmentation',445,'Run segmentation',445),('inspect',545,'Inspect results',445),('search',700,'Search / filter history',800),('restore',800,'Restore saved result',800),('rerun',900,'Recorded Re-run',800),('export',1010,'Export result',1150),('defaults',1090,'Configure model defaults',1150),('cancel',1170,'Cancel active work',1150),('clear',1250,'Clear view / selection',1150),('delete',1330,'Delete selected records',1150)]
for key,y,label,actor_y in left:
 a.node(key,280,y-29,360,58,label,shape='ellipse',size=22)
 a.route([(105,actor_y),(155,actor_y),(155,y),(280,y)],arrow=False,name='actor association '+key)
a.node('validate',760,76,300,58,'Validate model',shape='ellipse',size=22)
a.node('tiled',760,316,300,58,'Tiled analysis',shape='ellipse',size=22)
a.node('compare',760,516,300,58,'Compare / link views',shape='ellipse',size=22)
a.route([(640,105),(760,105)],style='dashed',name='include validation');a.label(700,89,'<<include>>',18)
a.route([(760,345),(640,345)],style='dashed',name='extend classification');a.label(700,329,'<<extend>>',18)
a.route([(760,545),(640,545)],style='dashed',name='extend inspection');a.label(700,529,'<<extend>>',18)
a.text(550,1390,'The same user actor is repeated by workflow band for clarity.',21)
checks[a.name]=a.save()

# Figure 3.4: four lifelines; pipeline work is local to InferenceEngine.
a=Drawing('sequence',1100,1190);xs=[130,410,690,970]
for x,key,label in zip(xs,['window','engine','files','database'],['MainWindow','InferenceEngine','Artifact files','DatabaseManager']):
 a.node(key,x-110,20,220,70,label,size=22)
 a.route([(x,90),(x,1170)],style='dashed',arrow=False,audit=False)
def message(i,j,y,label):
 a.route([(xs[i],y),(xs[j],y)],style='dashed' if j<i else 'solid',name=label,audit=True)
 a.label((xs[i]+xs[j])/2,y-13,label,22)
message(0,1,180,'start(snapshot)')
a.node('pipeline',290,225,240,105,['Validate model','Preprocess / forward','Parse model output'],size=22)
a.rect(20,370,1060,790,fill='none');a.text(30,399,'alt [cancelled / pipeline error]',22,True,anchor='start',mask=True)
message(1,0,470,'cancelled / error')
a.text(700,500,'No new completed record',22,mask=True)
a.route([(20,540),(1080,540)],style='dashed',arrow=False,audit=False)
a.text(30,575,'[completed]',22,True,anchor='start',mask=True)
message(1,0,630,'result_ready')
message(0,2,700,'render / save completed artifacts')
a.rect(40,745,1020,385,fill='none');a.text(50,776,'alt [artifact save failed]',22,True,anchor='start',mask=True)
message(2,0,835,'saving error: no database insert')
a.route([(40,875),(1060,875)],style='dashed',arrow=False,audit=False)
a.text(50,910,'[artifact save succeeded]',22,True,anchor='start',mask=True)
message(2,0,970,'saved artifact paths')
message(0,3,1035,'insert actual analysis metadata + paths')
message(3,0,1100,'record ID; refresh history')
checks[a.name]=a.save()

# Figure 3.5: dedicated outer lanes and a shared UML generalisation tree.
a=Drawing('class_diagram',1100,1170)
def cls(k,x,y,title,method):
 a.node(k,x,y,280,100,[],size=22)
 a.text(x+140,y+33,title,22,True)
 a.text(x+140,y+79,method,21)
 a.route([(x,y+48),(x+280,y+48)],arrow=False,audit=False)
a.node('main',50,20,1000,110,['MainWindow','_start_inference()'],size=26)
for key,x,title,method in [('input',100,'InferencePanel','classification_mode()'),('history',410,'HistoryPanel','selected_record_ids()'),('database',800,'DatabaseManager','insert_record()')]:
 cls(key,x,220,title,method);a.route([(x+140,130),(x+140,220)],style='dashed',name='coordinates '+title)
cls('engine',100,400,'InferenceEngine','run_pipeline(); cancel()')
cls('pdf',410,400,'PdfExportWorker','run(); cancel()')
cls('compare',800,400,'ImageComparison','set_images()')
a.route([(50,80),(20,80),(20,435),(100,435)],style='dashed',name='starts inference')
a.route([(740,130),(740,435),(690,435)],style='dashed',name='starts export')
a.route([(1050,80),(1090,80),(1090,435),(1080,435)],style='dashed',name='via spatial pages')
cls('loader',100,620,'ModelLoader','load_with_info(); validate()')
cls('exporter',410,620,'ExportManager','export_pdf(); export_png()')
cls('zoom',800,620,'ZoomableImageView','set_tile_grid(); fit_to_view()')
a.route([(240,500),(240,620)],style='dashed',name='loads and validates')
a.route([(550,500),(550,620)],style='dashed',name='delegates PDF')
a.route([(940,500),(940,620)],style='dashed',name='paired views')
cls('preprocess',100,800,'Preprocessor','transform()')
cls('parser',100,980,'OutputParser','extract_logits()')
a.route([(100,480),(60,480),(60,875),(100,875)],style='dashed',name='preprocessing dependency')
a.route([(60,875),(60,1055),(100,1055)],style='dashed',name='output parsing dependency')
cls('ownedworker',410,900,'_OwnedWorkerThread','worker lifetime')
cls('qthread',800,980,'QThread','Qt thread base')
a.route([(380,435),(390,435),(390,975),(410,975)],style='inheritance',name='engine inherits owned worker')
a.route([(690,480),(740,480),(740,975)],arrow=False,name='PDF direct Qt generalisation')
a.route([(690,975),(740,975)],arrow=False,name='owned worker direct Qt generalisation')
a.route([(740,975),(740,1055),(800,1055)],style='inheritance',name='common Qt inheritance')
a.text(550,1120,'Dashed arrow: dependency / coordination. Hollow triangle: inheritance.',21)
a.text(550,1150,'Selected classes and methods; MainWindow uses spatial comparison via result pages.',21)
checks[a.name]=a.save()

# Figure 3.6: separate error rail, branch/merge bars and persistence decisions.
a=Drawing('activity',1100,1380)
a.circle(550,20)
a.node('action',390,65,320,80,'Run or Re-run?',shape='diamond',size=23)
a.route([(550,27),(550,65)],name='begin')
a.node('run',80,220,340,90,['Ordinary Run','Snapshot current Preferences'])
a.node('rerun',680,220,340,90,['Recorded Re-run','Snapshot saved parameters'])
a.route([(390,105),(250,105),(250,220)],name='ordinary run');a.label(305,90,'Run')
a.route([(710,105),(850,105),(850,220)],name='recorded rerun');a.label(795,90,'Re-run')
a.route([(250,310),(250,345),(850,345),(850,310)],arrow=False,name='merge snapshots')
a.node('valid',370,385,360,80,'Inputs / model valid?',shape='diamond')
a.route([(550,345),(550,385)],name='validate')
a.node('mode',390,510,320,80,'Task / mode?',shape='diamond')
a.route([(550,465),(550,510)],name='valid inputs');a.label(590,498,'Yes')
a.node('single',20,650,320,110,['Single image','Whole source','One class vector'])
a.node('tiled',390,650,320,110,['Tiled classification','Real source crops','Class map + tile coverage'])
a.node('segmentation',760,650,320,110,['Segmentation','Independent geometry','Restored pixel mask'])
a.route([(390,550),(180,550),(180,650)],name='single classification');a.label(265,535,'Single image')
a.route([(550,590),(550,650)],name='tiled classification');a.label(650,628,'Tiled analysis')
a.route([(710,550),(920,550),(920,650)],name='segmentation');a.label(825,535,'Segmentation')
a.route([(180,760),(180,795),(920,795),(920,760)],arrow=False,name='merge task output')
a.node('state',370,835,360,80,'Execution outcome?',shape='diamond')
a.route([(550,795),(550,835)],name='completion state')
a.node('cancel',20,970,320,85,['Acknowledge cancellation','Keep previous record'])
a.node('save',390,970,320,85,['Render / save','Completed artifacts'])
a.route([(370,875),(180,875),(180,970)],name='cancel acknowledged');a.label(265,860,'Cancelled')
a.route([(550,915),(550,970)],name='completed');a.label(655,952,'Completed')
a.node('saved',410,1100,280,80,'Artifacts saved?',shape='diamond')
a.route([(550,1055),(550,1100)],name='check persistence')
a.node('error',760,1100,320,85,['Report actionable error','No new completed record'])
a.route([(730,875),(920,875),(920,1100)],name='pipeline error');a.label(820,860,'Error')
a.route([(730,425),(1090,425),(1090,1142),(1080,1142)],name='invalid input');a.label(805,411,'No')
a.route([(690,1140),(760,1140)],name='save failure');a.label(725,1125,'No')
a.node('insert',390,1230,320,75,['Insert record','Actual parameters + paths'])
a.route([(550,1180),(550,1230)],name='commit completed record');a.label(590,1210,'Yes')
a.circle(550,1350,final=True)
a.route([(550,1305),(550,1338)],name='completed end')
a.route([(180,1055),(180,1350),(538,1350)],name='cancelled end')
a.route([(920,1185),(920,1350),(562,1350)],name='error end')
checks[a.name]=a.save()
(R/'Geometry_Checks.json').write_text(json.dumps(checks,indent=2))
(R/'Colour_Palette.json').write_text(json.dumps({'palette':PALETTE,'roles':ROLE_MAP,'scope':'Diagram presentation only; these colours are not classification or segmentation class palettes.'},indent=2))
print('Generated and checked',len(checks),'coloured SVG/PNG diagrams; geometry unchanged.')
