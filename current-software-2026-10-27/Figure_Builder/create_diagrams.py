from pathlib import Path
import os
import subprocess
os.environ.setdefault('MPLCONFIGDIR', '/tmp/zypath-thesis-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, Circle, FancyArrowPatch, Polygon

R=Path(__file__).parent/'diagrams';R.mkdir(exist_ok=True)
NAVY='#243d57';BLUE='#e8f0f7';GREY='#f4f6f8'

def dot(name,body):
    src='''digraph G { graph [rankdir=TB,bgcolor=white,pad="0.15",nodesep="0.23",ranksep="0.38",dpi=230];
node [shape=box,style="rounded,filled",fillcolor="#edf3f8",color="#536b82",fontname="DejaVu Sans",fontsize=11,margin="0.1,0.08"];
edge [color="#536b82",fontname="DejaVu Sans",fontsize=9];
'''+body+'\n}'
    path=R/(name+'.dot');path.write_text(src)
    for fmt in ['png','svg']:subprocess.run(['dot','-T'+fmt,str(path),'-o',str(R/(name+'.'+fmt))],check=True)

dot('architecture',r'''
user [label="Educational / research user"];
mw [label="MainWindow\nnew Run: current Preferences snapshot\nRe-run: recorded parameter snapshot\nworker lifecycle · display · artifact saving"];
ui [label="Input / history / settings / result panels\nnumbered crops · linked coordinates\nclear view / selection · task-specific model choices"];
engine [label="InferenceEngine (QThread)\nCPU PyTorch · compatible model validation\nclassification OR independent segmentation pathway"];
database [label="DatabaseManager\nSQLite records + saved analysis / artifact paths"];
export [label="PdfExportWorker → ExportManager\nStandard / Original resolution\nprogress / cancel · atomic destination replacement"];
prefs [label="QSettings\ncurrent settings and startup model defaults"];
files [label="Local sources, model resources and saved outputs\nsource images / weights · PNG / maps / JSON / PDF"];
{rank=same;ui;prefs;}
{rank=same;database;export;}
ui -> engine [style=invis];engine -> database [style=invis];
user -> mw;mw -> ui [dir=both,label="signals / state"];
mw -> engine [label="start / cancel"];engine -> mw [style=dashed,label="result / progress / error",constraint=false];
mw -> database;mw -> export;mw -> prefs [dir=both];
database -> files [style=dashed,label="references artifacts"];
engine -> files [label="reads"];export -> files [label="writes completed PDF"];
''')

dot('class_diagram',r'''
node [shape=record,style=filled,fillcolor="#f7f9fb",fontsize=11];
mw [label="{MainWindow|_start_inference()\l_classification_preferences()\l}"];
ip [label="{InferencePanel|set_classification_parameters()\l}"];
hp [label="{HistoryPanel|select_record()\lselected_record_ids()\l}"];
engine [label="{InferenceEngine|run_pipeline()\lcancel()\l}"];
pdf [label="{PdfExportWorker|run()\lcancel()\l}"];
db [label="{DatabaseManager|insert_record()\lget_record_by_id()\l}"];
loader [label="{ModelLoader|load_with_info()\lvalidate()\l}"];
prep [label="{Preprocessor|transform()\l}"];
parse [label="{OutputParser|extract_logits()\l}"];
export [label="{ExportManager|export_pdf()\lexport_png()\l}"];
compare [label="{ImageComparison|set_images()\l}"];
zoom [label="{ZoomableImageView|set_tile_grid()\lfit_to_view()\l}"];
qt [label="{QThread}",fillcolor="#e4eaf0"];
{rank=same;ip;hp;}
{rank=same;engine;pdf;db;}
{rank=same;loader;prep;parse;}
mw -> ip [dir=both,arrowtail=diamond,arrowhead=none];mw -> hp [dir=both,arrowtail=diamond,arrowhead=none];
mw -> engine [style=dashed,label="starts / observes"];
mw -> pdf [style=dashed,label="snapshots / starts"];mw -> db [style=dashed];
engine -> loader [style=dashed];engine -> prep [style=dashed];engine -> parse [style=dashed];
pdf -> export [style=dashed,label="delegates"];
mw -> compare [style=dashed,label="via spatial result pages"];
compare -> zoom [dir=both,arrowtail=diamond,arrowhead=none,label="two views"];
pdf -> qt [arrowhead=empty,label="inherits"];
engine -> qt [arrowhead=empty,label="via owned-worker base"];
legend [shape=plaintext,label="Solid diamond: ownership    Dashed arrow: dependency\nHollow triangle: inheritance    Selected classes only",fontsize=10];
zoom -> legend [style=invis];qt -> legend [style=invis];
''')

dot('activity',r'''
start [shape=circle,label="",width=.15,fillcolor="#243d57"];
action [shape=diamond,label="Requested action?"];
fresh [label="Ordinary Run\nsnapshot current Preferences"];
rerun [label="Recorded Re-run\nsnapshot saved model / image / mode / parameters"];
valid [shape=diamond,label="Inputs and model compatible?"];
path [shape=diamond,label="Task / classification mode?"];
single [label="Single image\nwhole source → selected classifier"];
tiles [label="Tiled classification\nreal source crops → classifier\nactual areas → class coverage"];
seg [label="Segmentation\nindependent preprocessing / labels\nprocessing regions → restored mask"];
cancel [shape=diamond,label="Cancel at safe checkpoint?"];
stop [label="Acknowledge cancellation\nkeep previous completed record"];
save [label="Render completed result\nsave completed artifacts"];
ok [shape=diamond,label="Artifacts saved?"];
db [label="Insert completed record with actual parameters"];
error [label="Report actionable error\nno new completed record"];
end [shape=doublecircle,label="",width=.15,fillcolor="#243d57"];
start -> action;action -> fresh [label="[Run]"];action -> rerun [label="[Re-run]"];
fresh -> valid;rerun -> valid;valid -> error [label="[no]"];valid -> path [label="[yes]"];
path -> single [label="[Single image]"];path -> tiles [label="[Tiled analysis]"];path -> seg [label="[Segmentation]"];
single -> cancel;tiles -> cancel;seg -> cancel;
note [shape=note,label="Cancellation is checked before/after\nkey work and between processing regions;\na running forward operation is not killed.",fillcolor="#fff8e6",fontsize=10];
note -> cancel [style=dotted,arrowhead=none,constraint=false];
cancel -> stop [label="[yes]"];cancel -> save [label="[no]"];
save -> ok;ok -> error [label="[no]"];ok -> db [label="[yes]"];
db -> end;stop -> end;error -> end;
''')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.facecolor':'white'})
def save(fig,name):
    fig.savefig(R/(name+'.png'),dpi=240,bbox_inches='tight',pad_inches=.12)
    fig.savefig(R/(name+'.svg'),bbox_inches='tight',pad_inches=.12)
    plt.close(fig)

# Use-case diagram: actor associations are solid, include/extend dashed with
# the arrow directed at the included/base use case.
fig,ax=plt.subplots(figsize=(7.0,8.2));ax.set_xlim(0,10);ax.set_ylim(0,11.5);ax.axis('off')
ax.add_patch(Rectangle((2,.25),7.7,10.9,fill=False,edgecolor=NAVY,lw=1.4))
ax.text(5.85,10.9,'ZY-Path local application',ha='center',weight='bold',color=NAVY)
ax.add_patch(Circle((.75,6.1),.22,fill=False,edgecolor=NAVY));ax.plot([.75,.75],[5.88,5.05],color=NAVY)
ax.plot([.3,1.2],[5.65,5.65],color=NAVY);ax.plot([.75,.35],[5.05,4.55],color=NAVY);ax.plot([.75,1.15],[5.05,4.55],color=NAVY)
ax.text(.75,4.15,'Research /\neducation user',ha='center',va='top',fontsize=10)
nodes={
'select':(4.1,10.1,'Select model'), 'validate':(7.9,10.1,'Validate model'),
'image':(4.1,9.0,'Select image'), 'classify':(4.1,7.9,'Run classification'), 'tiled':(7.9,7.9,'Tiled analysis'),
'seg':(4.1,6.8,'Run segmentation'), 'inspect':(4.1,5.7,'Inspect results'), 'compare':(7.9,5.7,'Compare / link views'),
'restore':(4.1,4.6,'Restore saved result'), 'rerun':(7.9,4.6,'Re-run recorded\nanalysis'),
'search':(4.1,3.5,'Search / filter history'), 'export':(7.9,3.5,'Export result'),
'cancel':(4.1,2.4,'Cancel active work'), 'defaults':(7.9,2.4,'Configure defaults'),
'clear':(4.1,1.3,'Clear view / selection'), 'delete':(7.9,1.3,'Delete selected records')}
for key,(x,y,label) in nodes.items():
    ax.add_patch(Ellipse((x,y),3.0,.75,facecolor=BLUE,edgecolor=NAVY,lw=1))
    ax.text(x,y,label,ha='center',va='center',fontsize=9.5)
for key in ['select','image','classify','seg','inspect','restore','rerun','search','export','cancel','defaults','clear','delete']:
    x,y,_=nodes[key];ax.plot([1.2,x-1.5],[5.6,y],color='#7e91a4',lw=.55,zorder=0)
for start,end,label in [('select','validate','«include»'),('tiled','classify','«extend»'),('compare','inspect','«extend»')]:
    x,y,_=nodes[start];xx,yy,_=nodes[end];sign=1 if xx>x else -1
    ax.annotate('',(xx-sign*1.5,yy),(x+sign*1.5,y),arrowprops=dict(arrowstyle='->',linestyle='--',color=NAVY,lw=1))
    ax.text((x+xx)/2,y+.23,label,ha='center',fontsize=8)
save(fig,'use_case')

# Sequence diagram with actual guarded alternative fragments.
fig,ax=plt.subplots(figsize=(6.8,8.2));ax.set_xlim(-.1,10.1);ax.set_ylim(0,12);ax.axis('off')
xs=[.8,2.9,5.0,7.1,9.2];names=['MainWindow','InferenceEngine\n(QThread)','Model pipeline','Artifact files','DatabaseManager']
for x,name in zip(xs,names):
    ax.add_patch(Rectangle((x-.83,11),1.66,.65,facecolor=BLUE,edgecolor=NAVY))
    ax.text(x,11.325,name,ha='center',va='center',fontsize=8)
    ax.plot([x,x],[.35,11],ls='--',lw=.7,color='#a5b4c2')
def msg(a,b,y,text,dashed=False):
    ax.annotate('',(xs[b],y),(xs[a],y),arrowprops=dict(arrowstyle='->',lw=1,color=NAVY,linestyle='--' if dashed else '-'))
    ax.text((xs[a]+xs[b])/2,y+.13,text,ha='center',va='bottom',fontsize=8)
msg(0,1,10.2,'start(parameter snapshot)\nPreferences OR recorded analysis')
msg(1,2,9.6,'validate / preprocess / forward')
msg(2,1,8.9,'parsed output or error',True)
ax.add_patch(Rectangle((.05,.35),9.9,8.0,fill=False,edgecolor=NAVY,lw=1))
ax.text(.15,8.15,'alt  [cancelled or pipeline error]',fontsize=8,weight='bold')
msg(1,0,7.6,'cancelled / error signal',True)
ax.text(5.1,7.45,'No completed history inserted',ha='center',fontsize=8)
ax.plot([.05,9.95],[7.0,7.0],ls='--',lw=.7,color=NAVY)
ax.text(.15,6.8,'[completed]',fontsize=8,weight='bold')
msg(1,0,6.2,'result_ready signal',True)
msg(0,3,5.0,'render / save completed artifacts')
ax.add_patch(Rectangle((.15,.45),9.7,4.1,fill=False,edgecolor=NAVY,lw=1))
ax.text(.15,4.35,'alt  [artifact save failed]',fontsize=8,weight='bold')
msg(3,0,3.8,'saving failure',True)
ax.text(5.2,3.45,'Show error; no completed database record',ha='center',fontsize=8)
ax.plot([.05,9.95],[3.0,3.0],ls='--',lw=.7,color=NAVY)
ax.text(.15,2.8,'[artifact save succeeded]',fontsize=8,weight='bold')
msg(3,0,2.3,'saved paths',True)
msg(0,4,1.65,'insert actual metadata / artifact paths')
msg(4,0,.95,'record ID → refresh history',True)
save(fig,'sequence')

# Fixed portrait class layout keeps method names readable at thesis page width.
fig,ax=plt.subplots(figsize=(6.8,5.9));ax.set_xlim(-.4,7.15);ax.set_ylim(.1,9.35);ax.axis('off')
classes={
'mw':(2.35,8.3,'MainWindow','_start_inference()'),
'ip':(.05,6.95,'InferencePanel','classification_mode()'),
'hp':(2.35,6.95,'HistoryPanel','selected_record_ids()'),
'db':(4.65,6.95,'DatabaseManager','insert_record()'),
'engine':(.05,5.55,'InferenceEngine','run_pipeline()\ncancel()'),
'pdf':(2.35,5.55,'PdfExportWorker','run()\ncancel()'),
'compare':(4.65,5.55,'ImageComparison','set_images()'),
'loader':(.05,4.15,'ModelLoader','load_with_info()\nvalidate()'),
'export':(2.35,4.15,'ExportManager','export_pdf()\nexport_png()'),
'zoom':(4.65,4.15,'ZoomableImageView','set_tile_grid()\nfit_to_view()'),
'prep':(.05,2.75,'Preprocessor','transform()'),
'parse':(2.35,2.75,'OutputParser','extract_logits()'),
'qt':(4.65,2.75,'QThread','Qt worker base')}
w,h=2.1,.8
for key,(x,y,name,methods) in classes.items():
    ax.add_patch(Rectangle((x,y),w,h,facecolor=GREY,edgecolor=NAVY,lw=1))
    ax.plot([x,x+w],[y+.43,y+.43],color=NAVY,lw=.7)
    ax.text(x+w/2,y+.62,name,ha='center',va='center',fontsize=8.6,weight='bold')
    ax.text(x+w/2,y+.22,methods,ha='center',va='center',fontsize=7.6)
def edge(points,kind='dependency'):
    for a,b in zip(points[:-2],points[1:-1]):ax.plot([a[0],b[0]],[a[1],b[1]],color='#71859a',ls='--' if kind=='dependency' else '-',lw=.8)
    a,b=points[-2:]
    arrow=FancyArrowPatch(a,b,arrowstyle='-|>' if kind=='inheritance' else '->',mutation_scale=12,
                          lw=.9,linestyle='--' if kind=='dependency' else '-',edgecolor=NAVY,
                          facecolor='white' if kind=='inheritance' else NAVY)
    ax.add_patch(arrow)
edge([(3.4,8.3),(1.1,7.75)])
edge([(3.4,8.3),(3.4,7.75)])
edge([(3.4,8.3),(5.7,7.75)])
edge([(2.35,8.7),(-.2,8.7),(-.2,5.95),(.05,5.95)])
edge([(4.45,8.7),(4.55,8.7),(4.55,5.95),(4.45,5.95)])
edge([(4.45,8.7),(7.0,8.7),(7.0,5.95),(6.75,5.95)])
edge([(1.1,5.55),(1.1,4.95)])
edge([(.05,5.95),(-.2,5.95),(-.2,3.15),(.05,3.15)])
edge([(2.15,5.95),(2.25,5.95),(2.25,3.15),(2.35,3.15)])
edge([(3.4,5.55),(3.4,4.95)])
edge([(5.7,5.55),(5.7,4.95)])
edge([(4.45,5.95),(4.55,5.95),(4.55,3.15),(4.65,3.15)],'inheritance')
edge([(1.1,5.55),(1.1,5.2),(6.95,5.2),(6.95,3.15),(6.75,3.15)],'inheritance')
ax.text(3.4,1.95,'Dashed arrow: dependency / coordination\nHollow triangle: inheritance (InferenceEngine via its owned-worker base)',
        ha='center',va='center',fontsize=8.3,color=NAVY)
ax.text(3.4,1.2,'Spatial pages use ImageComparison; selected classes are shown.\nThe diagram does not enumerate every widget or method.',ha='center',fontsize=8.2)
save(fig,'class_diagram')

fig,ax=plt.subplots(figsize=(6.8,7.4));ax.set_xlim(-.1,7);ax.set_ylim(.2,9.4);ax.axis('off')
def box(x,y,w,h,text,fontsize=9):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=BLUE,edgecolor=NAVY,lw=.9))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fontsize)
def arr(a,b,text='',dashed=False):
    ax.annotate('',b,a,arrowprops=dict(arrowstyle='->',lw=.8,color=NAVY,linestyle='--' if dashed else '-'))
    if text:ax.text((a[0]+b[0])/2+.04,(a[1]+b[1])/2,text,fontsize=8,color=NAVY)
box(2.0,8.7,2.7,.5,'Educational / research user')
box(.35,7.2,6.0,1.05,'MainWindow: orchestration\nRun → current Preferences snapshot\nRe-run → saved-record snapshot\nworker lifecycle · completed result · artifact saving',9)
arr((3.35,8.7),(3.35,8.25))
box(.35,5.7,3.35,.95,'Input / history / result panels\nnumbered crops · aligned views\nclear view / selection',8.8)
box(4.0,5.7,2.35,.95,'QSettings\ncurrent Preferences\nper-task startup defaults',8.7)
arr((2.0,7.2),(2.0,6.65));arr((5.2,7.2),(5.2,6.65))
box(.7,4.15,5.3,1.05,'InferenceEngine + model pipeline (core/)\nCPU PyTorch · validation · preprocessing\nclassification crops OR separate segmentation path',9)
arr((6.35,7.7),(6.65,7.7));arr((6.65,7.7),(6.65,4.65));arr((6.65,4.65),(6.0,4.65),'start')
arr((.7,4.65),(.1,4.65),dashed=True);arr((.1,4.65),(.1,7.7),dashed=True);arr((.1,7.7),(.35,7.7),dashed=True)
ax.text(.14,6.65,'result / progress / error',rotation=90,fontsize=7.6,va='center')
box(.35,2.6,2.8,.95,'DatabaseManager (data/)\nSQLite record / analysis JSON\nreferences saved artifacts',8.7)
box(3.55,2.6,2.8,.95,'PdfExportWorker → ExportManager\nquality / progress / cancellation\natomic completed PDF write',8.1)
arr((.1,7.7),(-.02,7.7));arr((-.02,7.7),(-.02,3.1));arr((-.02,3.1),(.35,3.1))
arr((6.65,4.65),(6.65,3.1));arr((6.65,3.1),(6.35,3.1))
box(.7,.8,5.3,1.0,'Local model / source / output files\nweights + configuration · original images\nPNG / maps / JSON / PDF',9)
arr((1.75,2.6),(1.75,1.8),'paths');arr((4.9,2.6),(4.9,1.8),'PDF')
save(fig,'architecture')

fig,ax=plt.subplots(figsize=(6.8,8.4));ax.set_xlim(-.3,7.5);ax.set_ylim(-.8,11.3);ax.axis('off')
def diamond(x,y,w,h,text):
    ax.add_patch(Polygon([(x,y+h/2),(x+w/2,y+h),(x+w,y+h/2),(x+w/2,y)],closed=True,facecolor='#fff6e5',edgecolor=NAVY,lw=.9))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=8.6)
ax.add_patch(Circle((3.45,11),.08,color=NAVY))
diamond(2.0,9.9,2.9,.7,'Requested action?');arr((3.45,10.92),(3.45,10.6))
box(.1,8.7,3.0,.75,'Ordinary Run\nsnapshot current Preferences',8.8)
box(3.8,8.7,3.0,.75,'Recorded Re-run\nsnapshot saved parameters',8.8)
arr((2.0,10.25),(1.6,9.45),'[Run]');arr((4.9,10.25),(5.3,9.45),'[Re-run]')
diamond(1.5,7.3,3.9,.8,'Compatible model / inputs?')
arr((1.6,8.7),(3.45,8.1));arr((5.3,8.7),(3.45,8.1))
diamond(2.0,6.05,2.9,.65,'Task / mode?');arr((3.45,7.3),(3.45,6.7),'[yes]')
box(-.1,4.5,2.25,1.0,'Single image\nwhole source\n→ one class vector',8.6)
box(2.4,4.5,2.25,1.0,'Tiled classification\nreal crops / areas\n→ class map',8.6)
box(4.9,4.5,2.25,1.0,'Segmentation\nindependent geometry\n→ restored mask',8.4)
arr((2.0,6.38),(1.0,5.5),'[Single]');arr((3.45,6.05),(3.5,5.5),'[Tiled]');arr((4.9,6.38),(6.0,5.5),'[Segmentation]')
diamond(1.5,3.1,3.9,.7,'Cancel at safe checkpoint?')
arr((1.0,4.5),(3.45,3.8));arr((3.5,4.5),(3.45,3.8));arr((6.0,4.5),(3.45,3.8))
box(.1,1.8,2.3,.75,'Acknowledge cancel\nkeep previous record',8.3)
box(3.0,1.8,3.6,.75,'Render / save completed artifacts\ninsert record only after success',8.6)
arr((1.5,3.45),(1.25,2.55),'[yes]');arr((4.1,3.1),(4.8,2.55),'[no]')
box(4.9,.35,2.3,.6,'Report error\nno new completed record',8.3)
arr((5.4,7.7),(7.35,7.7),'[no]');arr((7.35,7.7),(7.35,.65));arr((7.35,.65),(7.2,.65))
arr((6.6,2.15),(7.35,2.15),'[save fails]')
ax.add_patch(Circle((3.45,-.3),.1,fill=False,edgecolor=NAVY));ax.add_patch(Circle((3.45,-.3),.05,color=NAVY))
arr((4.8,1.8),(3.45,-.2),'[saved]')
arr((1.25,1.8),(1.25,.1));arr((1.25,.1),(3.35,-.3))
arr((6.05,.35),(6.05,.1));arr((6.05,.1),(3.55,-.3))
ax.text(3.6,-.65,'Safe checks occur before/after key work and between processing regions.',ha='center',fontsize=7.8)
save(fig,'activity')

from PIL import Image
for p in R.glob('*.png'):print(p.name,Image.open(p).size)
