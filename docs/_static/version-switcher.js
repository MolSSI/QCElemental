(async function () {
  if (!document || !document.querySelector) return;

  // --- UI ---
  const container = document.createElement("div");
  container.className = "version-switcher";
  container.style.padding = "0.5rem 1rem";
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

  // Place under RTD search box (left sidebar)
  const search = document.querySelector(".wy-side-nav-search");
  if (search && search.parentNode) {
    search.insertAdjacentElement("afterend", container);
  } else {
    const sidebarScroll = document.querySelector(".wy-side-scroll");
    if (!sidebarScroll) return;
    sidebarScroll.prepend(container);
  }

  // Disabled until we populate
  select.disabled = true;
  const loadingOpt = document.createElement("option");
  loadingOpt.textContent = "Loading…";
  select.appendChild(loadingOpt);

  // --- Find versions.json ---
  async function tryFetch(url) {
    try {
      const resp = await fetch(url, { cache: "no-store" });
      if (!resp.ok) return null;
      const data = await resp.json();
      return data;
    } catch {
      return null;
    }
  }

  // Candidate URLs, from most local to more global
  const origin = window.location.origin;
  const pathname = window.location.pathname; // e.g. /QCElemental/dev/index.html

  const parts = pathname.split("/").filter(Boolean); // ["QCElemental","dev","index.html"]
  const projectRoot = parts.length ? `/${parts[0]}/` : "/"; // "/QCElemental/" or "/"

  const candidates = [
    // relative (useful for local build if versions.json copied to root)
    "versions.json",
    "../versions.json",
    "../../versions.json",

    // absolute roots
    origin + projectRoot + "versions.json",
    origin + "/versions.json",
  ];

  let data = null;
  let usedBase = null;

  for (const url of candidates) {
    data = await tryFetch(url);
    if (data) {
      // derive base URL from the successful URL (strip trailing "versions.json")
      usedBase = url.replace(/versions\.json.*$/, "");
      // ensure base is absolute
      if (!usedBase.startsWith("http")) usedBase = origin + (usedBase.startsWith("/") ? usedBase : "/" + usedBase);
      if (!usedBase.endsWith("/")) usedBase += "/";
      break;
    }
  }

  if (!data || !usedBase) {
    console.warn("[version-switcher] Could not load versions.json. Tried:", candidates);
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.textContent = "No versions.json";
    select.appendChild(opt);
    return; // keep it visible so you notice the problem
  }

  // --- Populate ---
  select.innerHTML = "";
  data.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v.path;          // e.g. "dev/" or "v0.30.1/"
    opt.textContent = v.label;   // e.g. "dev"
    select.appendChild(opt);
  });

  // Determine current version folder (if any)
  // If hosted at /QCElemental/dev/... then currentVersion is "dev"
  const rel = pathname.startsWith(projectRoot)
    ? pathname.slice(projectRoot.length)
    : pathname.replace(/^\//, "");
  const currentVersion = rel.split("/")[0] || "";

  // Select matching option if present
  for (const opt of select.options) {
    if (opt.value.replace(/\/+$/, "") === currentVersion) {
      opt.selected = true;
      break;
    }
  }

  select.disabled = false;

  // Navigate on change; preserve rest-of-path after version folder if possible
  select.addEventListener("change", () => {
    const targetVersionPath = select.value; // "dev/" etc.
    const rest = rel.split("/").slice(1).join("/"); // drop currentVersion
    const target = usedBase + targetVersionPath + rest;
    window.location.href = target;
  });
})();

