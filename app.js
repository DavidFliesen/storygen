async function loadStories(filter = "all") {
  const response = await fetch("stories.json");
  const stories = await response.json();

  const container = document.getElementById("storiesContainer");
  container.innerHTML = "";

  let filtered = stories;

  if (filter === "used") {
    filtered = stories.filter(s => s.status === "used");
  }

  if (filter === "unused") {
    filtered = stories.filter(s => s.status !== "used");
  }

  filtered.forEach(story => {
    const card = document.createElement("div");
    card.className = "story-card";

    card.innerHTML = `
      <h2>${story.title}</h2>
      <p><strong>Status:</strong> ${story.status}</p>
      <p><strong>Themes:</strong> ${story.themes.join(", ")}</p>
    `;

    story.panels.forEach(panel => {
      const panelDiv = document.createElement("div");
      panelDiv.className = "panel";

      panelDiv.innerHTML = `
        <h3>Panel ${panel.panel}</h3>
        <p>${panel.scene}</p>
      `;

      card.appendChild(panelDiv);
    });

    container.appendChild(card);
  });
}

document.getElementById("loadStories").addEventListener("click", () => {
  loadStories();
});

document.getElementById("showUnused").addEventListener("click", () => {
  loadStories("unused");
});

document.getElementById("showUsed").addEventListener("click", () => {
  loadStories("used");
});

loadStories();
