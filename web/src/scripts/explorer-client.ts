type Repo = {
 id:string;name:string;description:string;repository_url:string;project_type:string;
 category:string;group:string;topics:string[];capabilities:string[];protocols:string[];
 language:string|null;score:number;stars:number;forks:number;verified:boolean;
 verified_at:string|null;license:string|null;archived:boolean;pushed_at:string|null;
 detail_slug:string;checked_at:string;maintenance_status:string;
};
type Catalog = {catalog_count:number;groups:{id:string;name:string}[];entries:Repo[];generated_at:string};
type Sort = "relevance"|"stars"|"name"|"active";
const byId=(id:string)=>document.getElementById(id)!;
const elements={
 search:byId("catalog-search") as HTMLInputElement,
 sort:byId("catalog-sort") as HTMLSelectElement,
 license:byId("catalog-license") as HTMLSelectElement,
 verified:byId("catalog-verified") as HTMLSelectElement,
 maintenance:byId("catalog-maintenance") as HTMLSelectElement,
 freshness:byId("catalog-freshness") as HTMLSelectElement,
 chips:byId("catalog-categories"),
 count:byId("catalog-count"),
 context:byId("catalog-context"),
 results:byId("catalog-projects"),
 loading:byId("catalog-loading"),
 empty:byId("catalog-empty"),
 more:byId("catalog-more") as HTMLButtonElement,
 reset:byId("catalog-reset") as HTMLButtonElement,
 grid:byId("view-grid") as HTMLButtonElement,
 list:byId("view-list") as HTMLButtonElement,
};
let projects:Repo[]=[];
let group="all";
let view:"grid"|"list"="grid";
let visible=18;
let filtered:Repo[]=[];
const PAGE=18;
const fragment=(tag:string,cls?:string,text?:string)=>{
 const node=document.createElement(tag);
 if(cls)node.className=cls;
 if(text!==undefined)node.textContent=text;
 return node;
};
const short=(n:number)=>new Intl.NumberFormat("de-DE",{notation:"compact",maximumFractionDigits:1}).format(n);
const searchText=(item:Repo)=>[
 item.id,item.name,item.description,item.project_type,item.language,
 ...item.topics,...item.capabilities,...item.protocols
].join(" ").toLocaleLowerCase("de");
function makeCard(item:Repo) {
 const card=fragment("article","atlas-card");
 card.dataset.testid="catalog-card";
 const top=fragment("div","atlas-card-top"),head=fragment("div","atlas-card-head");
 const symbol=fragment("div","atlas-card-symbol",(item.name.trim()[0]||"#").toUpperCase());
 const meta=fragment("div");meta.style.minWidth="0";
 const link=fragment("a","atlas-card-name",item.name);
 link.href="/WERKAtlas/project/"+encodeURIComponent(item.detail_slug)+"/";
 link.title=item.id;
 const subtitle=fragment("div","atlas-card-repo",item.id);
 meta.append(link,subtitle);head.append(symbol,meta);
 const pill=fragment("span","atlas-card-status"+(item.verified?"":" unknown"),item.verified?"GitHub geprüft":"Ungeklärt");
 top.append(head,pill);
 const description=fragment("p","atlas-card-desc",item.description||"Keine Beschreibung im Katalog vorhanden.");
 const tags=fragment("div","atlas-card-tags");
 [item.project_type,item.language,...item.topics].filter(Boolean).slice(0,4).forEach(tag=>
  tags.append(fragment("span",undefined,String(tag)))
 );
 const bottom=fragment("div","atlas-card-bottom");
 bottom.append(fragment("span",undefined,"★ "+short(item.stars)),
               fragment("span",undefined,"⑂ "+short(item.forks??0)),
               fragment("span",undefined,item.license||"Lizenz offen"));
 const score=fragment("span","atlas-card-score");
 score.append(fragment("span",undefined,"Katalog-Score"),fragment("strong",undefined,item.score.toFixed(1)));
 bottom.append(score);
 const info=fragment("p","atlas-card-verify",item.verified
  ?"GitHub-Abgleich: "+(item.verified_at||"").slice(0,10)+" · Score historisch"
  :"GitHub-Metadaten nicht bestätigt · Score historisch");
 card.append(top,description,tags,bottom,info);
 return card;
}
function runFilter() {
 const terms=elements.search.value.toLocaleLowerCase("de").trim().split(/\s+/).filter(Boolean);
 const license=elements.license.value,verified=elements.verified.value;
 const maintenance=elements.maintenance.value,freshness=elements.freshness.value;
 const NINETY_DAYS=90*86400000;
 filtered=projects.filter(item=>
  (group==="all"||item.group===group) &&
  (license==="all"||(license==="known" ? !!item.license : !item.license)) &&
  (verified==="all"||(verified==="verified" ? item.verified:!item.verified)) &&
  (maintenance==="all"||item.maintenance_status===maintenance|| (maintenance==="archived"&&item.archived)) &&
  (freshness==="all"|| (()=>{
    const age=Date.now()-Date.parse(item.checked_at||"");
    const state=!Number.isFinite(age) || age<0 ? "unknown" : age<=NINETY_DAYS ? "fresh" : "stale";
    return state===freshness;
  })()) &&
  terms.every(term=>searchText(item).includes(term))
 );
 const sort=elements.sort.value as Sort;
 filtered.sort((a,b)=>{
  if(sort==="stars")return b.stars-a.stars||a.id.localeCompare(b.id);
  if(sort==="name")return a.name.localeCompare(b.name,"de");
  if(sort==="active")return (b.pushed_at||"").localeCompare(a.pushed_at||"")||b.score-a.score;
  return (terms.length
   ? terms.reduce((val,t)=>val+(a.name.toLowerCase().includes(t)?3:0),0)-
     terms.reduce((val,t)=>val+(b.name.toLowerCase().includes(t)?3:0),0)
   : 0)*-1 || b.score-a.score || b.stars-a.stars;
 });
 visible=PAGE;
 render();
}
function render() {
 elements.results.replaceChildren();
 const items=filtered.slice(0,visible);
 const holder=document.createDocumentFragment();
 items.forEach(item=>holder.append(makeCard(item)));
 elements.results.append(holder);
 elements.count.textContent=new Intl.NumberFormat("de-DE").format(filtered.length)+" Projekte gefunden";
 elements.context.textContent=group==="all"?"Alle Themenbereiche":(
  elements.chips.querySelector<HTMLButtonElement>('[data-group="'+group+'"]')?.textContent || "Themenbereich");
 elements.empty.hidden=filtered.length!==0;
 elements.more.hidden=filtered.length<=visible;
 elements.more.textContent="Weitere Projekte laden ("+Math.min(PAGE,filtered.length-visible)+" von "+
   new Intl.NumberFormat("de-DE").format(filtered.length-visible)+") ↓";
 elements.results.classList.toggle("list",view==="list");
 elements.grid.setAttribute("aria-pressed",String(view==="grid"));
 elements.list.setAttribute("aria-pressed",String(view==="list"));
}
elements.chips.addEventListener("click",event=>{
 const button=(event.target as HTMLElement).closest<HTMLButtonElement>("button[data-group]");
 if(!button)return;
 group=button.dataset.group||"all";
 elements.chips.querySelectorAll("button").forEach(x=>x.classList.toggle("active",x===button));
 runFilter();
});
elements.search.addEventListener("input",runFilter);
elements.license.addEventListener("change",runFilter);
elements.sort.addEventListener("change",runFilter);
elements.verified.addEventListener("change",runFilter);
elements.maintenance.addEventListener("change",runFilter);
elements.freshness.addEventListener("change",runFilter);
elements.reset.addEventListener("click",()=>{
 elements.search.value="";
 elements.sort.value="relevance";
 elements.license.value="all";
 elements.verified.value="all";
 elements.maintenance.value="all";
 elements.freshness.value="all";
 group="all";
 elements.chips.querySelectorAll<HTMLButtonElement>("button").forEach(x=>x.classList.toggle("active",x.dataset.group==="all"));
 runFilter();
});
elements.more.addEventListener("click",()=>{visible+=PAGE;render()});
elements.grid.addEventListener("click",()=>{view="grid";render()});
elements.list.addEventListener("click",()=>{view="list";render()});

fetch("/WERKAtlas/catalog-index.json")
 .then(async response=>{if(!response.ok)throw Error("HTTP "+response.status);return await response.json() as Catalog})
 .then(data=>{
  projects=data.entries;
  elements.loading.hidden=true;
  runFilter();
 })
 .catch(()=>{
  elements.loading.textContent="Der Suchindex konnte nicht geladen werden. Lokalen Server/Build prüfen.";
  elements.count.textContent="Katalog nicht verfügbar";
 });
