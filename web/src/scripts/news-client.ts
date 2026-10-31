type NewsItem={title:string;url:string;summary:string;published_at:string;source_id:string;source_name:string;source_kind:string;category:string;verification:string};
type Source={id:string;name:string;status:string;error_type?:string};
type NewsData={generated_at:string;count:number;articles:NewsItem[];sources:Source[];successful_sources:number;failed_sources:number};
const get=(id:string)=>document.getElementById(id)!;
const ui={
 search:get("news-search") as HTMLInputElement,
 days:get("news-days") as HTMLSelectElement,
 kind:get("news-kind") as HTMLSelectElement,
 topics:get("news-topics"),
 count:get("news-count"),items:get("news-items"),
 more:get("news-more") as HTMLButtonElement,
 loading:get("news-loading"),empty:get("news-empty")
};
let articles:NewsItem[]=[];
let topic="all",shown=16,filtered:NewsItem[]=[];
let fetchedAt=Date.now();
const pageSize=16;
const element=(tag:string,cls?:string,value?:string)=>{
 const el=document.createElement(tag);if(cls)el.className=cls;if(value!==undefined)el.textContent=value;return el;
};
function readable(date:string){
 return new Intl.DateTimeFormat("de-DE",{day:"2-digit",month:"short",year:"numeric",timeZone:"UTC"}).format(new Date(date));
}
function makeNewsCard(item:NewsItem){
 const article=element("article","radar-article");
 article.dataset.testid="news-article";
 const top=element("div","radar-article-top");
 const kind=item.source_kind;
 const badge=element("span","radar-kind "+kind,
   kind==="official"?"Hersteller":kind==="release"?"GitHub Release":
   kind==="research"?"Forschung":kind==="press"?"Presse":"Unabhängig");
 const date=element("span","radar-article-date",readable(item.published_at));
 top.append(badge,date);
 const title=element("h3");
 const link=element("a",undefined,item.title);
 link.href=item.url;link.target="_blank";link.rel="noopener noreferrer";
 title.append(link);
 const summary=element("p",undefined,item.summary||"Originalquelle öffnen, um die vollständige Veröffentlichung zu lesen.");
 const foot=element("div","radar-article-bottom");
 foot.append(element("span",undefined,item.source_name+" · "+item.category));
 const go=element("a",undefined,"Originalquelle ↗");
 go.href=item.url;go.target="_blank";go.rel="noopener noreferrer";
 foot.append(go);
 article.append(top,title,summary,foot);
 return article;
}
function apply(){
 const query=ui.search.value.toLocaleLowerCase("de").trim().split(/\s+/).filter(Boolean);
 const days=ui.days.value,kind=ui.kind.value;
 const threshold=days==="all"?null:fetchedAt-Number(days)*86400000;
 filtered=articles.filter(article=>
  (topic==="all"||article.category===topic) &&
  (kind==="all"||article.source_kind===kind) &&
  (threshold===null||Date.parse(article.published_at)>=threshold) &&
  query.every(term=>(article.title+" "+article.summary+" "+article.source_name+" "+article.category).toLocaleLowerCase("de").includes(term))
 );
 shown=pageSize;
 draw();
}
function draw(){
 const fragment=document.createDocumentFragment();
 filtered.slice(0,shown).forEach(item=>fragment.append(makeNewsCard(item)));
 ui.items.replaceChildren(fragment);
 ui.count.textContent=filtered.length+" Meldungen · "+(topic==="all"?"Alle Themen":topic);
 ui.empty.hidden=filtered.length!==0;
 ui.more.hidden=filtered.length<=shown;
 ui.more.textContent="Weitere "+Math.min(pageSize,filtered.length-shown)+" Meldungen laden ↓";
}
ui.topics.addEventListener("click",event=>{
 const button=(event.target as HTMLElement).closest<HTMLButtonElement>("button[data-topic]");
 if(!button)return;topic=button.dataset.topic||"all";
 ui.topics.querySelectorAll("button").forEach(el=>el.classList.toggle("active",el===button));
 apply();
});
ui.search.addEventListener("input",apply);
ui.days.addEventListener("change",apply);
ui.kind.addEventListener("change",apply);
ui.more.addEventListener("click",()=>{shown+=pageSize;draw()});
fetch("/WERKAtlas/news/latest.json",{cache:"no-cache"})
 .then(async response=>{if(!response.ok)throw Error("HTTP "+response.status);return await response.json() as NewsData})
 .then(data=>{
  articles=Array.isArray(data.articles)?data.articles:[];
  fetchedAt=Date.parse(data.generated_at)||Date.now();
  const age=Date.now()-fetchedAt;
  const updated=get("news-updated");
  updated.textContent=new Date(fetchedAt).toLocaleString("de-DE",{timeZone:"UTC"})+" UTC"+(age>48*3600000?" · VERALTET":"");
  ui.loading.hidden=true;
  apply();
 })
 .catch(()=>{ui.loading.textContent="Der News-Datensatz konnte nicht geladen werden. Lokalen Feed-Update prüfen.";ui.count.textContent="News-Daten nicht verfügbar"});
