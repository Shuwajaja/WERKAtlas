# Instagram GitHub research reconciliation

Checked: 2026-10-28 (GitHub API, no paid model or vendor API).

`WERKAtlas_v2_Ausfuehrungsplan.md` was not in the repository and not on Google Drive.
The 110 verified repository identities come from the Instagram GitHub Research files
(MASTER-KATALOG, decision report, and a fresh public GitHub read of each repository).
Drive originals were not modified.

## Result

- Verified repository identities: 110
- Already in the catalog: 32
- Added: 48
- Excluded from the catalog, with a reason: 30
- License values filled where the catalog had none: 30
- Archived flags corrected from GitHub: 3
- Catalog entries before / after: 1468 / 1516

Existing descriptions, star counts, timestamps, and scores were left as stored.
A later scoring run would move maintenance scores because it uses the current date.
New entries were scored once with `scripts/score.py` on 2026-10-28.

Protected fields of every pre-existing entry are hashed in
`baseline-protected-sha256.json`. Mutable fields are license, archived,
maintenance_status, limitations, and discovered_from.

## Excluded

- `Anil-matcha/Open-Generative-AI` — Image and video generation product, not an agent-engineering project.
- `AppFlowy-IO/AppFlowy` — Collaborative workspace product. AI features do not make it an agent-engineering project.
- `CapSoftware/Cap` — Screen-recording application, not an agent-engineering project.
- `FlashML-org/FreeVideo` — Local video-model runner. Hardware and model licenses were not part of this catalog pass.
- `OpenWhispr/openwhispr` — Dictation application, not an agent-engineering project.
- `augusto-scarvalho/claude-pxl` — GitHub description was empty on 2026-10-28, so no function was inferred.
- `bilawalsidhu/gods-eye-view` — Satellite-imagery viewer, not an agent-engineering project.
- `calcom/cal.diy` — Scheduling product, not an agent, MCP, or model tool.
- `chatwoot/chatwoot` — Customer-support desk, not an agent-engineering project.
- `coollabsio/coolify` — General hosting platform, not an agent-engineering project.
- `debpalash/VoiceStudio` — Local voice-cloning application, not an agent-engineering project.
- `deepbeepmeep/WanGP` — Local video generator. Hardware and model licenses were not part of this catalog pass.
- `docusealco/docuseal` — Document-signing application, not an agent-engineering project.
- `every-app/open-seo` — Search-marketing suite. The repository description does not describe an agent system.
- `freeCodeCamp/devdocs` — API documentation browser, not an agent-engineering project.
- `google-research/google-research` — Undifferentiated research monorepo, not one agent system.
- `harry0703/MoneyPrinterTurbo` — Short-video generator, not an agent-engineering project.
- `hasanharman/isomiddleearth` — Isometric world builder, not an agent-engineering project.
- `hcengineering/platform` — General project-management suite, not an agent-engineering project.
- `hoppscotch/hoppscotch` — API client, not an agent-engineering project.
- `hypit-ai/hypit` — Video-cloning product. Agent wording in the tagline is not a cataloged agent framework.
- `jasonkneen/tiny-world-builder` — GitHub description repeats the repository name and states no agent function.
- `metabase/metabase` — Business-intelligence application, not an agent-engineering project.
- `nhost/nhost` — General backend platform, not an agent-engineering project.
- `obsidianmd/obsidian-releases` — Plugin and release list. The desktop application source is not this repository.
- `opf/openproject` — Project-management suite, not an agent-engineering project.
- `practical-tutorials/project-based-learning` — General programming tutorials, not an agent-engineering project.
- `supabase/supabase` — General database platform, not an agent-engineering project.
- `tmux/tmux` — Terminal multiplexer, not an agent-engineering project.
- `triggerdotdev/jsonhero-web` — JSON viewer, not an agent-engineering project.

## Added

- `microsoft/markitdown`
- `paperclipai/paperclip`
- `yamadashy/repomix`
- `ace-agent/ace`
- `luoyuctl/agenttrace`
- `microsoft/AI-Engineering-Coach`
- `unclecode/crawl4ai`
- `blader/humanizer`
- `pbakaus/impeccable`
- `Leonxlnx/taste-skill`
- `lingzhi227/agent-research-skills`
- `agenthatch/agenthatch`
- `anthropics/claude-cookbooks`
- `punkpeye/awesome-mcp-servers`
- `filipecalegario/awesome-vibe-coding`
- `spinabot/brigade`
- `jo-inc/camofox-browser`
- `JuliusBrussee/caveman`
- `AgriciDaniel/claude-ads`
- `feiskyer/claude-code-settings`
- `eyaltoledano/claude-task-master`
- `HKUDS/CLI-Anything`
- `JustVugg/colibri`
- `coleam00/context-engineering-intro`
- `langgenius/dify`
- `firecrawl/firecrawl`
- `tashfeenahmed/freellmapi`
- `gamedev-skills/awesome-gamedev-agent-skills`
- `ahmedkhaleel2004/gitdiagram`
- `garrytan/gstack`
- `alchaincyf/huashu-design`
- `hyperfx-ai/marketing-skills`
- `heygen-com/hyperframes`
- `anthropics/knowledge-work-plugins`
- `magnitudedev/magnitude`
- `yetone/magpie`
- `getmaxun/maxun`
- `code-yeongyu/oh-my-openagent`
- `cheaper-inference/OmniRoute`
- `openai/openai-cookbook`
- `openai/evals`
- `calesthio/OpenMontage`
- `remotion-dev/skills`
- `RyanCodrai/turbovec`
- `nextlevelbuilder/ui-ux-pro-max-skill`
- `KhazP/vibe-coding-prompt-template`
- `Imbad0202/academic-research-skills`
- `lfnovo/open-notebook`
