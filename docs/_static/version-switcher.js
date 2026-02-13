(async function () {
  // Only run on HTML pages
  if (!document || !document.querySelector) return;

  // Create UI
  const container = document.createElement("div");
  container.className = "version-switcher";
  container.style.margin = "0.75rem 0";
  container.style.display = "flex";
  container.style.gap = "0.5rem";
  container.style.alignItems = "center";

  const label = document.createElement("span");
  label.textContent = "Version:";
  label.style.fontSize = "0.9em";

  const select = document.createElement("select");
  select.setAttribute("aria-label", "Select documentation version");
  select.style.width = "100%";

  container.appendChild(label);
  container.appendChild(select);

  // Inject into RTD sidebar (works for sphinx_rtd_theme)
  const sidebar = document.querySelector(".wy-side-scroll .wy-menu") ||
                  document.querySelector(".wy-side-scroll");
  if (!sidebar) return;
  sidebar.prepend(container);

  // Determine base URL (root of GitHub Pages site)
  // Works for https://USER.github.io/REPO/... and custom domains.
  const origin = window.location.origin;
  const parts = window.location.pathname.split("/").filter(Boolean);

  // If hosted at https://user.github.io/repo/, repo is first path segment.
  // If hosted at custom domain, there may be no repo segment.
  // We'll assume "site root" is origin + (first segment if it matches repo-like behavior).
  // Robust approach: walk up until we find versions.json by trying candidate roots.
  async function fetchVersions() {
    const candidates = [];
    // candidate 1: origin + "/" + first segment (common gh-pages project site)
    if (parts.length >= 1) candidates.push(`${origin}/${parts[0]}/`);
    // candidate 2: origin + "/" (user/organization site or custom domain)
    candidates.push(`${origin}/`);

    for (const base of candidates) {
      try {
        const resp = await fetch(base + "versions.json", { cache: "no-store" });
        if (!resp.ok) continue;
        const data = await resp.json();
        return { base, data };
      } catch (e) {
        // try next
      }
    }
    return null;
  }

  const found = await fetchVersions();
  if (!found) {
    // Hide if versions.json not available
    container.remove();
    return;
  }

  const { base, data } = found;

  // Current version: first path segment after base.
  // Example: base=https://..../repo/ and pathname=/repo/v0.30.1/guide/page.html
  const relPath = window.location.href.replace(base, "");
  const currentVersion = relPath.split("/")[0] || "";

  // Populate dropdown
  data.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v.path;
    opt.textContent = v.label;
    if (v.path.replace(/\/+$/, "") === currentVersion) opt.selected = true;
    select.appendChild(opt);
  });

  // Navigate on change, preserving page path if possible
  select.addEventListener("change", () => {
    const targetVersionPath = select.value; // like "v0.30.1/"
    const rest = relPath.split("/").slice(1).join("/"); // drop current version
    const target = base + targetVersionPath + rest;

    // Prefer preserving the same page; if it 404s the browser will show it.
    // If you want a smarter fallback, see note below.
    window.location.href = target;
  });
})();

