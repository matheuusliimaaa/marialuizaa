"""Painel local: usa somente Python e Tkinter, sem pacotes extras."""
from pathlib import Path
import json, shutil, uuid, webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from build import ROOT, EDADES, build
DATA=ROOT/'ensaios.json'
def read_data():return json.loads(DATA.read_text(encoding='utf-8'))
def write_data(data):
 temp=DATA.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(DATA)
def valid_image(path):
 p=Path(path);ext=p.suffix.lower()
 if ext not in ['.jpg','.jpeg','.png','.webp'] or not p.is_file():raise ValueError('Selecione uma imagem JPG, PNG ou WEBP existente.')
 b=p.read_bytes()[:16]
 if not (b.startswith(b'\x89PNG\r\n\x1a\n') or b.startswith(b'\xff\xd8\xff') or (b.startswith(b'RIFF') and b[8:12]==b'WEBP')):raise ValueError('O arquivo selecionado não é uma imagem válida.')
 return p

def save_session(nome,descricao,idades,capa,original,current=None):
 if not nome.strip() or not descricao.strip() or not idades:raise ValueError('Preencha nome, descrição e selecione pelo menos uma idade.')
 if not set(idades)<=set(s for s,_ in EDADES):raise ValueError('Idade inválida.')
 c=valid_image(capa);o=valid_image(original);data=read_data();ident=current or uuid.uuid4().hex
 # Cada gravação usa uma pasta nova: arquivos existentes nunca são sobrescritos.
 folder=ROOT/'img'/'ensaios'/uuid.uuid4().hex;folder.mkdir(parents=True)
 shutil.copy2(c,folder/('capa'+c.suffix.lower()));shutil.copy2(o,folder/('original'+o.suffix.lower()))
 item={'id':ident,'nome':nome.strip(),'descricao':descricao.strip(),'idades':idades,'capa':(folder/('capa'+c.suffix.lower())).relative_to(ROOT).as_posix(),'original':(folder/('original'+o.suffix.lower())).relative_to(ROOT).as_posix()}
 updated=[item if e['id']==ident else e for e in data]
 if not current:updated.append(item)
 write_data(updated)
 try:build()
 except Exception:
  write_data(data);build();raise
 return ident

def main():
 root=tk.Tk();root.title('Pequeños Retratos — Cadastro de ensaios');root.geometry('900x690');root.minsize(800,640)
 style=ttk.Style();style.theme_use('clam');style.configure('TButton',padding=8);style.configure('TLabel',padding=3)
 frame=ttk.Frame(root,padding=20);frame.pack(fill='both',expand=True)
 ttk.Label(frame,text='Cadastro de ensaios',font=('Segoe UI',20,'bold')).pack(anchor='w')
 ttk.Label(frame,text='Salve aqui. Depois faça Commit e Push no GitHub Desktop para publicar.').pack(anchor='w')
 columns=ttk.Frame(frame);columns.pack(fill='both',expand=True,pady=15)
 left=ttk.Frame(columns);left.pack(side='left',fill='y',padx=(0,20))
 listing=tk.Listbox(left,width=27,height=20,exportselection=False);listing.pack(fill='both',expand=True)
 right=ttk.Frame(columns);right.pack(side='left',fill='both',expand=True)
 selected={'id':None};names=tk.StringVar();cover=tk.StringVar();full=tk.StringVar();checks={s:tk.BooleanVar() for s,_ in EDADES}
 ttk.Label(right,text='Nome do ensaio (como aparece no site)').pack(anchor='w');ttk.Entry(right,textvariable=names).pack(fill='x')
 ttk.Label(right,text='Descrição (em espanhol, para seu público)').pack(anchor='w',pady=(10,0));description=tk.Text(right,height=5,wrap='word',font=('Segoe UI',10));description.pack(fill='x')
 ttk.Label(right,text='Mostrar nas idades:').pack(anchor='w',pady=(10,0))
 for s,t in EDADES:ttk.Checkbutton(right,text=t,variable=checks[s]).pack(anchor='w')
 def choose(variable):
  f=filedialog.askopenfilename(title='Selecione a imagem',filetypes=[('Imagens','*.png *.jpg *.jpeg *.webp')])
  if f:variable.set(f)
 for label,var in [('Capa menor (mesma proporção do mosaico)',cover),('Mosaico original com as 4 poses',full)]:
  ttk.Label(right,text=label).pack(anchor='w',pady=(10,0));row=ttk.Frame(right);row.pack(fill='x');ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True);ttk.Button(row,text='Escolher…',command=lambda v=var:choose(v)).pack(side='right')
 def refresh():
  listing.delete(0,'end')
  for e in read_data():listing.insert('end',e['nome'])
 def new():
  selected['id']=None;names.set('');cover.set('');full.set('');description.delete('1.0','end');listing.selection_clear(0,'end')
  for v in checks.values():v.set(False)
 def load(_=None):
  if not listing.curselection():return
  e=read_data()[listing.curselection()[0]];selected['id']=e['id'];names.set(e['nome']);cover.set(str(ROOT/e['capa']));full.set(str(ROOT/e['original']));description.delete('1.0','end');description.insert('1.0',e['descricao'])
  for s,v in checks.items():v.set(s in e['idades'])
 def save():
  try:
   selected['id']=save_session(names.get(),description.get('1.0','end'),[s for s,v in checks.items() if v.get()],cover.get(),full.get(),selected['id']);refresh();messagebox.showinfo('Ensaio salvo','Ensaio adicionado ao site local.\nConfira em “Abrir site”.\nPara publicar: Commit e Push no GitHub Desktop.')
  except Exception as e:messagebox.showerror('Não foi possível salvar',str(e))
 def remove():
  if not selected['id']:return
  if not messagebox.askyesno('Remover ensaio','Remover este ensaio do site? As imagens serão mantidas na pasta.'):return
  old=read_data()
  try:write_data([e for e in old if e['id']!=selected['id']]);build();refresh();new()
  except Exception as e:write_data(old);messagebox.showerror('Erro',str(e))
 listing.bind('<<ListboxSelect>>',load)
 ttk.Button(left,text='Novo ensaio',command=new).pack(fill='x',pady=8);ttk.Button(left,text='Remover selecionado',command=remove).pack(fill='x')
 buttons=ttk.Frame(right);buttons.pack(fill='x',pady=20);ttk.Button(buttons,text='Salvar ensaio e atualizar site',command=save).pack(side='left');ttk.Button(buttons,text='Abrir site',command=lambda:webbrowser.open((ROOT/'index.html').as_uri())).pack(side='right')
 refresh();root.mainloop()
if __name__=='__main__':main()
