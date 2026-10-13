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
const scheduleDialog = document.querySelector("#schedule-dialog");

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

function dateTimeLabel(value) {
  if (!value) return "Not listed";
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short", hour: "numeric", minute: "2-digit"
  }).format(new Date(value));
}

function programTime(program) {
  return program ? `${dateTimeLabel(program.start)} – ${timeLabel(program.stop)}` : "Not listed";
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

  const schedule = fragment.querySelector(".schedule-button");
  schedule.setAttribute("aria-label", `View ${channel.name} schedule`);
  schedule.addEventListener("click", () => openSchedule(channel));

  const watch = fragment.querySelector(".watch-button");
  watch.href = channel.stream;
  watch.setAttribute("aria-label", `Watch ${channel.name}`);
  card.dataset.channelId = channel.id;
  return fragment;
}

function openSchedule(channel) {
  const now = new Date();
  const end = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  const { current, next } = currentPrograms(channel, now);
  const upcoming = channel.programs.filter(program =>
    new Date(program.stop) > now && new Date(program.start) < end
  );

  document.querySelector("#schedule-number").textContent = `CH ${String(channel.number).padStart(3, "0")} · ${channel.category}`;
  document.querySelector("#schedule-title").textContent = channel.name;
  document.querySelector("#detail-now-title").textContent = current?.title || "Program data unavailable";
  document.querySelector("#detail-now-time").textContent = programTime(current);
  document.querySelector("#detail-next-title").textContent = next?.title || "Not listed";
  document.querySelector("#detail-next-time").textContent = programTime(next);
  document.querySelector("#schedule-count").textContent = `${upcoming.length} listing${upcoming.length === 1 ? "" : "s"}`;

  const logo = document.querySelector("#schedule-logo");
  const logoFrame = logo.closest(".logo-frame");
  logoFrame.classList.remove("missing");
  logo.src = channel.logo;
  logo.alt = `${channel.name} logo`;
  logo.onerror = () => logoFrame.classList.add("missing");
  if (!channel.logo) logoFrame.classList.add("missing");

  const list = document.querySelector("#schedule-list");
  list.replaceChildren(...upcoming.map(program => {
    const item = document.createElement("li");
    if (program === current) item.classList.add("is-now");
    const time = document.createElement("time");
    time.dateTime = program.start;
    time.textContent = dateTimeLabel(program.start);
    const content = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = program.title;
    const description = document.createElement("p");
    description.textContent = program.subtitle || program.description || "";
    content.append(title, description);
    item.append(time, content);
    return item;
  }));
  document.querySelector("#schedule-empty").hidden = upcoming.length !== 0;
  const watch = document.querySelector("#schedule-watch");
  watch.href = channel.stream;
  watch.setAttribute("aria-label", `Watch ${channel.name}`);
  scheduleDialog.showModal();
}

function updateHealth(data) {
  const refreshed = new Date(data.generatedAt);
  const ageHours = (Date.now() - refreshed.getTime()) / 3_600_000;
  document.querySelector("#health-refresh").textContent = refreshed.toLocaleString();
  document.querySelector("#health-coverage").textContent = `${data.epgChannelCount} of ${data.channelCount} channels`;
  document.querySelector("#stale-warning").hidden = ageHours <= 18;
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
    updateHealth(data);
    buildCategories();
    render();
  })
  .catch(error => {
    grid.setAttribute("aria-busy", "false");
    document.querySelector("#guide-summary").textContent = "The guide data could not be loaded.";
    document.querySelector("#data-status").textContent = error.message;
  });

document.querySelector("#schedule-close").addEventListener("click", () => scheduleDialog.close());
scheduleDialog.addEventListener("click", event => {
  if (event.target === scheduleDialog) scheduleDialog.close();
});

updateClock();
setInterval(updateClock, 30_000);
setInterval(render, 60_000);
