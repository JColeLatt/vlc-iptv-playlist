const state = {
  channels: [],
  category: "All",
  search: "",
  favorites: new Set(JSON.parse(localStorage.getItem("movieVaultFavorites") || "[]")),
};

const categoryOrder = ["All", "Local", "News", "Sports", "Kids", "Movies", "Entertainment", "Favorites"];
const grid = document.querySelector("#channels");
const template = document.querySelector("#channel-template");
const search = document.querySelector("#search");

function currentPrograms(channel, now = new Date()) {
  const nowMs = now.getTime();
  const currentIndex = channel.programs.findIndex(p => new Date(p.start).getTime() <= nowMs && nowMs < new Date(p.stop).getTime());
  const current = currentIndex >= 0 ? channel.programs[currentIndex] : null;
  const next = currentIndex >= 0 ? channel.programs[currentIndex + 1] : channel.programs.find(p => new Date(p.start).getTime() > nowMs);
  return { current, next };
}

function timeLabel(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function progress(current) {
  if (!current) return 0;
  const start = new Date(current.start).getTime();
  const stop = new Date(current.stop).getTime();
  return Math.max(0, Math.min(100, ((Date.now() - start) / (stop - start)) * 100));
}

function saveFavorites() {
  localStorage.setItem("movieVaultFavorites", JSON.stringify([...state.favorites]));
}

function buildCategories() {
  const nav = document.querySelector("#categories");
  nav.replaceChildren(...categoryOrder.map(category => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.textContent = category;
    button.dataset.category = category;
    button.setAttribute("aria-pressed", String(category === state.category));
    button.addEventListener("click", () => {
      state.category = category;
      buildCategories();
      render();
    });
    return button;
  }));
}

function matches(channel) {
  const categoryMatch = state.category === "All"
    || (state.category === "Favorites" ? state.favorites.has(channel.id) : channel.category === state.category);
  const needle = state.search.trim().toLowerCase();
  if (!categoryMatch || !needle) return categoryMatch;
  const { current, next } = currentPrograms(channel);
  return [channel.name, channel.id, channel.category, current?.title, next?.title]
    .filter(Boolean).some(value => value.toLowerCase().includes(needle));
}

function channelCard(channel) {
  const fragment = template.content.cloneNode(true);
  const card = fragment.querySelector(".channel-card");
  const { current, next } = currentPrograms(channel);
  fragment.querySelector(".channel-number").textContent = `CH ${String(channel.number).padStart(3, "0")}`;
  fragment.querySelector(".channel-category").textContent = channel.category;
  fragment.querySelector(".channel-name").textContent = channel.name;
  fragment.querySelector(".channel-id").textContent = channel.id;

  const logo = fragment.querySelector(".channel-logo");
  const logoFrame = fragment.querySelector(".logo-frame");
  logo.src = channel.logo;
  logo.alt = `${channel.name} logo`;
  logo.addEventListener("error", () => logoFrame.classList.add("missing"), { once: true });
  if (!channel.logo) logoFrame.classList.add("missing");

  fragment.querySelector(".now-title").textContent = current?.title || "Program data unavailable";
  fragment.querySelector(".now-time").textContent = current ? `${timeLabel(current.start)} – ${timeLabel(current.stop)}` : "Live channel";
  fragment.querySelector(".progress-track span").style.width = `${progress(current)}%`;
  fragment.querySelector(".next-title").textContent = next?.title || "Not listed";
  fragment.querySelector(".next-time").textContent = timeLabel(next?.start);

  const favorite = fragment.querySelector(".favorite-button");
  const isFavorite = state.favorites.has(channel.id);
  favorite.setAttribute("aria-pressed", String(isFavorite));
  favorite.setAttribute("aria-label", `${isFavorite ? "Remove" : "Add"} ${channel.name} ${isFavorite ? "from" : "to"} favorites`);
  favorite.firstChild.textContent = isFavorite ? "★ " : "☆ ";
  favorite.addEventListener("click", () => {
    state.favorites.has(channel.id) ? state.favorites.delete(channel.id) : state.favorites.add(channel.id);
    saveFavorites();
    buildCategories();
    render();
  });

  const watch = fragment.querySelector(".watch-button");
  watch.href = channel.stream;
  watch.setAttribute("aria-label", `Watch ${channel.name}`);
  card.dataset.channelId = channel.id;
  return fragment;
}

function render() {
  const channels = state.channels.filter(matches);
  grid.replaceChildren(...channels.map(channelCard));
  grid.setAttribute("aria-busy", "false");
  document.querySelector("#empty-state").hidden = channels.length !== 0;
  document.querySelector("#result-count").textContent = `${channels.length} channel${channels.length === 1 ? "" : "s"}`;
  document.querySelector("#section-kicker").textContent = state.category === "All" ? "All channels" : state.category;
  document.querySelector("#section-title").textContent = state.search ? `Results for “${state.search}”` : "Live lineup";
}

function updateClock() {
  document.querySelector("#clock").textContent = new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date());
}

search.addEventListener("input", event => { state.search = event.target.value; render(); });

fetch("data/channels.json")
  .then(response => { if (!response.ok) throw new Error(`Guide data HTTP ${response.status}`); return response.json(); })
  .then(data => {
    state.channels = data.channels;
    document.querySelector("#guide-summary").textContent = `${data.channelCount} channels · ${data.epgChannelCount} with program listings`;
    document.querySelector("#data-status").textContent = `Guide updated ${new Date(data.generatedAt).toLocaleString()}`;
    buildCategories();
    render();
  })
  .catch(error => {
    grid.setAttribute("aria-busy", "false");
    document.querySelector("#guide-summary").textContent = "The guide data could not be loaded.";
    document.querySelector("#data-status").textContent = error.message;
  });

updateClock();
setInterval(updateClock, 30_000);
setInterval(render, 60_000);
