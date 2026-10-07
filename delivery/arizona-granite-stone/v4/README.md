# Arizona Granite & Stone LLC — website, version 4 "The Build"

Built by GreenAI Solutions for Carlos Marrufo, Waddell AZ. Static HTML/CSS/JS, no build step, no dependencies.
Preview: https://greenaidigital.com/delivery/arizona-granite-stone/v4/

Earlier versions: v1 `GreenAiSolution/arizona-granite-stone`, v2 `-v2`, v3 `-v3` ("The Cut").

## The idea

The page opens on one of the shop's own kitchens drawn as a white-line template, and the visitor scrolls it into
existence: cabinets, then the perimeter stone wiping in, then the island slab dropping into place, then the finished
photo. Every layer is cut from the same real photo (`assets/img/kitchen-2000.webp`); the line drawing
(`kitchen-template-*.webp`) is an edge trace of that photo. Nothing is generated or stock.

## Sections

| # | Section | What happens |
|---|---------|--------------|
| 01 | The build | Pinned for ~6 screens. Five captions, a progress rail, a slow camera push-in |
| 02 | Slogan | "Quality is our best discount!" marquee, scroll-linked |
| 03 | Facts | Family-owned · ROC 332009 · own shop · free quotes |
| 04 | What we build | Six things they build; the picture follows the row in view (desktop) |
| 05 | Stone | Granite / quartz / marble cards that stack and settle |
| 06 | Process | Five steps, call to install |
| 07 | The work | Twelve of their installs. Pinned sideways reel on desktop, swipe strip on phones; lightbox |
| 08 | Instagram | @arizonagraniteandstonellc profile + the nine real posts embedded (Meta's embed.js, loaded only when near) |
| 09 | Quote | Big phone number, hours, shop, email, Instagram, and the quote form |

## Switches

- `<meta name="robots" content="noindex">` is PREVIEW ONLY. Delete at go-live.
- Quote form posts to FormSubmit (`CONFIG.formEndpoint` in `main.js`; plain POST fallback in the form's `action`).
  The first submission sends a one-time activation email to arizonagraniteandstone@gmail.com; nothing delivers until it is clicked.
- Reduced motion or JS off: no pinning, the finished kitchen shows still, everything is readable.
- Region shapes for the build (cabinets, counters, island) are the `<polygon>`s in the SVG `<defs>` in `index.html`,
  in the photo's own 1179×766 pixel space.
