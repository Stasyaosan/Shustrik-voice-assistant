const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

const chatDiv = document.getElementById("chat");
const emptyState = document.getElementById("emptyState");
const statusBadge = document.getElementById("statusBadge");
const statusSpinner = document.getElementById("statusSpinner");
const statusText = document.getElementById("statusText");
const container_link = document.getElementById("container_link");

socket.onopen = function () {
  statusBadge.className =
    "badge bg-success-subtle text-success ms-auto d-flex align-items-center gap-1";
  statusSpinner.classList.remove("spinner-grow");
  statusText.innerText = "В сети";
};
socket.onmessage = function (event) {
  const data = JSON.parse(event.data);

  if (data.length === 1) {
    if (data[0].mode === "message") {
      if (emptyState) emptyState.remove();
      const bubble = document.createElement("div");
      bubble.className =
        "bubble " + (data[0].class === "left" ? "bubble-left" : "bubble-right");
      bubble.innerText = data[0].text;
      chatDiv.appendChild(bubble);
      chatDiv.scrollTop = chatDiv.scrollHeight;
    } else {
      renderLinks([data[0]]);
    }
    return;
  }

  renderLinks(data);
};

function renderLinks(items) {
  container_link.innerHTML = "";

  const groups = new Map();
  items.forEach((item, index) => {
    if (item.mode !== "link") return;
    if (!groups.has(item.name)) groups.set(item.name, []);
    groups.get(item.name).push({ link: item.link, index });
  });

  for (const [name, links] of groups) {
    const details = document.createElement("details");
    details.classList.add("accordion-item");
    details.setAttribute("open", "");

    const linksHtml = links
      .map(({ link, index }) => {
        const urls = String(link)
          .split(",")
          .map((u) => u.trim())
          .filter((u) => u.length > 0);

        const rows = urls
          .map(
            (url) => `
        <div class="d-flex justify-content-between align-items-center gap-4 mb-2">
          <div><a href="${url}" target="_blank">${url}</a></div>
          <button class="btn btn-outline-danger btn-sm" onclick="removeUrl(${index}, '${url.replace(/'/g, "\\'")}')">Удалить ссылку</button>
        </div>
      `,
          )
          .join("");

        const deleteGroupBtn = `
        <div class="d-flex justify-content-end mt-2 pt-2 border-top">
          <button class="btn btn-danger btn-sm" onclick="removeLin(${index})">Удалить всё</button>
        </div>
      `;

        return rows + deleteGroupBtn;
      })
      .join("");

    details.innerHTML = `
      <summary class="accordion-header">
        ${name}
        <svg class="accordion-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
          <path d="m2 5 6 6 6-6"/>
        </svg>
      </summary>
      <div class="accordion-body">
        ${linksHtml}
      </div>
    `;

    container_link.appendChild(details);
  }

  container_link.scrollTop = container_link.scrollHeight;
}

socket.onclose = function (e) {
  console.log("WebSocket соединение закрыто.", e.reason);
  statusBadge.classList.add("offline");
  statusText.innerText = "Оффлайн";
};

socket.onerror = function (err) {
  console.error("Ошибка WebSocket: ", err);
};

document.getElementById("add_link_btn").addEventListener("click", function () {
  const formData = new FormData();
  formData.append("name", document.getElementById("form_name").value);
  formData.append("link", document.getElementById("form_link").value);

  fetch("/api/add_link", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        return response.text();
      }
      throw new Error("Ошибка сети или сервера");
    })
    .then((data) => {
      console.log("Успешно отправлено:", data);
      document.getElementById("form_name").value = "";
      document.getElementById("form_link").value = "";
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
});

function removeLin(index) {
  const formData = new FormData();
  formData.append("index", index);

  fetch("/api/remove_link", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        const btn = document.querySelector(
          `button[onclick="removeLin(${index})"]`,
        );
        if (btn) {
          const details = btn.closest("details");
          if (details) details.remove();
        }
        reindexRemoveButtons();
      }
    })
    .then((data) => {
      console.log("Успешно отправлено:", data);
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
}

function removeUrl(index, url) {
  const formData = new FormData();
  formData.append("index", index);
  formData.append("url", url);

  fetch("/api/remove_url", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        const buttons = container_link.querySelectorAll(
          `button[onclick^="removeUrl(${index},"]`,
        );
        buttons.forEach((btn) => {
          const match = btn
            .getAttribute("onclick")
            .match(/removeUrl\(\d+,\s*'((?:\\'|[^'])*)'\)/);
          if (match) {
            const btnUrl = match[1].replace(/\\'/g, "'");
            if (btnUrl === url) {
              const row = btn.closest(".d-flex");
              if (row) row.remove();
            }
          }
        });

        // Если у группы не осталось ни одной ссылки — перерисовать через WS
        reindexRemoveButtons();
      }
    })
    .then((data) => {
      console.log("Успешно отправлено:", data);
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
}

function reindexRemoveButtons() {
  const allButtons = container_link.querySelectorAll(
    ".accordion-body button.btn-danger",
  );
  allButtons.forEach((btn, i) => {
    btn.setAttribute("onclick", `removeLin(${i})`);
  });
}
