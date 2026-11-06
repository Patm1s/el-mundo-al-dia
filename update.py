"""Daily RSS aggregation and optional AI editorial summarization. Python 3.11+."""
import os, json, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from email.utils import parsedate_to_datetime

ROOT=Path(__file__).parent; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
TOPICS=[('Geopolítica','geopolitics world diplomacy conflict'),('Europa y Austria','Austria Europe politics economy'),('Estados Unidos','United States politics'),('Perú','Peru noticias actualidad'),('Economía','world economy financial markets'),('Inteligencia artificial','artificial intelligence technology'),('Criptomonedas','bitcoin cryptocurrency regulation')]
AGENTS={'User-Agent':'ElMundoAlDia/1.0 (personal news reader)'}
def fetch(url):
    req=urllib.request.Request(url,headers=AGENTS)
    with urllib.request.urlopen(req,timeout=20) as r:return r.read()
def collect():
    cutoff=datetime.now(timezone.utc)-timedelta(hours=30); out=[]
    for cat,q in TOPICS:
        query=urllib.parse.quote(q+' when:1d')
        feed='https://news.google.com/rss/search?q='+query+'&hl=es-419&gl=US&ceid=US:es-419'
        try:
            root=ET.fromstring(fetch(feed))
            for item in root.findall('.//item')[:12]:
                title=item.findtext('title','').strip(); link=item.findtext('link','').strip(); pub=item.findtext('pubDate','')
                try: dt=parsedate_to_datetime(pub).astimezone(timezone.utc)
                except: continue
                if dt<cutoff or not title or not link:continue
                source=item.find('source'); name=source.text if source is not None else 'Google News'
                out.append({'category':cat,'title':title,'url':link,'source':name,'published':dt.isoformat()})
        except Exception as exc:print('Feed failed',cat,exc)
    return out

def summarize(items):
    key=os.environ.get('OPENAI_API_KEY','').strip()
    if not key:raise RuntimeError('OPENAI_API_KEY no configurada. No se publica una edición automática sin resumen y revisión editorial.')
    from openai import OpenAI
    client=OpenAI(api_key=key)
    prompt='''Eres editor de un periódico familiar en español peruano. Recibirás SOLO TITULARES, FUENTES, FECHAS Y ENLACES de agregación RSS, NO textos completos. Selecciona 7 a 10 noticias diferentes de las últimas 24 horas (si no hay suficientes confiables, elige menos). Prioriza geopolítica, Europa/Austria, EE.UU., Perú, economía, IA y cripto. No inventes cifras, víctimas, declaraciones ni hechos que no se puedan deducir del titular. Nunca presentes como confirmado algo que solo dice un titular; indica expresamente "Información basada en titulares; consultar la fuente original" en verification. Evita afirmaciones sensacionalistas y duplicados. No inventes URLs: usa literalmente las URL entregadas. Incluye Perú si hay información pertinente. Devuelve exclusivamente JSON con {"headline":"...","intro":"...","stories":[{"category":"...","title":"...","summary":"...","impact":"...","verification":"...","source":"...","url":"..."}]}. Cada summary 1-2 frases prudentes, impact 1 frase condicional. Ordena las tres más importantes primero. No atribuyas corroboración independiente. NO llames noticias verificadas a los titulares. La redacción es una selección de titulares, no un reportaje comprobado.'''
    response=client.chat.completions.create(model=os.environ.get('OPENAI_MODEL','gpt-4.1-mini'),temperature=0.1,response_format={'type':'json_object'},messages=[{'role':'system','content':prompt},{'role':'user','content':json.dumps(items,ensure_ascii=False)}])
    return json.loads(response.choices[0].message.content)

def main():
    items=collect(); print('Collected',len(items),'headlines')
    if len(items)<10:raise RuntimeError('Insuficientes titulares recientes; se conserva la edición anterior.')
    edition=summarize(items)
    allowed={x['url']:x for x in items}; cleaned=[]
    for n in edition.get('stories',[]):
        if n.get('url') not in allowed:continue
        original=allowed[n['url']];n['source']=original['source'];n['category']=original['category'];n['verification']='Información basada en titulares; consultar la fuente original. '+n.get('verification','')
        cleaned.append(n)
    if len(cleaned)<5:raise RuntimeError('Selección insuficiente; se conserva la edición anterior.')
    now=datetime.now(ZoneInfo('Europe/Vienna')); day=now.date().isoformat()
    edition.update(date=day,date_label=now.strftime('%d/%m/%Y · %H:%M (Austria)'),stories=cleaned[:10],demo=False)
    (DATA/(day+'.json')).write_text(json.dumps(edition,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest=DATA/'manifest.json'; old=json.loads(manifest.read_text()) if manifest.exists() else {'editions':[]}
    editions=[{'date':day,'file':day+'.json'}]+[x for x in old['editions'] if x['date']!=day]
    manifest.write_text(json.dumps({'editions':editions[:90]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Published edition',day)
if __name__=='__main__':main()
