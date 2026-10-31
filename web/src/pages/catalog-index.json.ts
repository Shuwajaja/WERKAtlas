import type { APIRoute } from "astro";
import { catalogEntries, taxonomy } from "../utils/dataLoader";
import githubVerified from "../../../data/verified-github.json";

// Public static data, not a server endpoint querying GitHub on every search.
// Browser requests must never execute repository code.
export const GET: APIRoute = () => {
  const verified = githubVerified.entries as Record<string, {
    stars:number; forks:number|null; license:string|null; archived:boolean|null;
    pushed_at:string|null; verified_at:string;
  }>;
  const groups=Object.entries(taxonomy.categories).map(([id,group])=>({
    id, name:group.name,
    subcategories:Object.entries(group.subcategories).map(([subId,sub])=>({id:subId,name:sub.name}))
  }));
  const entries=catalogEntries.map(item=>{
    const git=verified[item.id.toLowerCase()]||null;
    return {
      id:item.id, name:item.name, description:item.description,
      repository_url:item.repository_url, project_type:item.project_type,
      category:item.primary_category, group:item.primary_category.split(".")[0],
      topics:item.topics.slice(0,14), capabilities:item.capabilities.slice(0,10),
      protocols:item.protocols.slice(0,10), language:item.primary_language,
      score:item.score, stars:git?.stars ?? item.stars,
      forks:git?.forks ?? item.forks,
      verified:!!git, verified_at:git?.verified_at ?? null,
      checked_at:item.checked_at,
      maintenance_status:item.maintenance_status || "unclear",
      license:git?.license ?? null,
      archived:git?.archived ?? item.archived,
      pushed_at:git?.pushed_at ?? null,
      fit_note:"Text- und Katalogtreffer sind keine technische Funktionsbestätigung.",
      detail_slug:item.repository.replace("/", "-"),
    };
  });
  return new Response(JSON.stringify({
    schema_version:1,generated_at:githubVerified.generated_at,
    catalog_count:entries.length,groups,entries
  }),{headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"public, max-age=3600"}});
};
