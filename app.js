const API_BASE = "http://localhost:5000";

async function api(path, options = {}) {
  const response = await fetch(API_BASE + path, {
    credentials: "include",
    headers: {"Content-Type": "application/json"},
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function setupRegister() {
  document.querySelector("#registerForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = new FormData(e.target);
    const message = document.querySelector("#message");
    try {
      const data = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(form))
      });
      message.textContent = `Account created. Referral code: ${data.referral_code}`;
      setTimeout(() => location.href = "login.html", 1200);
    } catch (err) { message.textContent = err.message; }
  });
}

function setupLogin() {
  document.querySelector("#loginForm").addEventListener("submit", async e => {
    e.preventDefault();
    const form = new FormData(e.target);
    const message = document.querySelector("#message");
    try {
      await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(form))
      });
      location.href = "dashboard.html";
    } catch (err) { message.textContent = err.message; }
  });
}

async function loadDashboard() {
  try {
    const data = await api("/api/dashboard");
    document.querySelector("#welcome").textContent = `Welcome, ${data.user.name}`;
    document.querySelector("#balance").textContent =
      `UGX ${data.balance_ugx.toLocaleString()}`;
    document.querySelector("#referral").textContent = data.user.referral_code;

    const tasks = document.querySelector("#tasks");
    tasks.innerHTML = data.tasks.map(task => `
      <article class="task">
        <h3>${escapeHtml(task.title)}</h3>
        <p>${escapeHtml(task.description)}</p>
        <strong>+UGX ${task.reward_ugx.toLocaleString()}</strong>
        <br><br>
        <button class="button" ${task.completed ? "disabled" : ""}
          onclick="completeTask(${task.id})">
          ${task.completed ? "Completed" : "Complete task"}
        </button>
      </article>
    `).join("");

    document.querySelector("#ledger").innerHTML =
      data.ledger.length
      ? data.ledger.map(x => `
        <div class="ledger-row">
          <span>${escapeHtml(x.type)}</span>
          <span class="${x.amount_ugx >= 0 ? "positive" : "negative"}">
            ${x.amount_ugx >= 0 ? "+" : ""}UGX ${Math.abs(x.amount_ugx).toLocaleString()}
          </span>
        </div>`).join("")
      : "<p>No transactions yet.</p>";
  } catch (err) {
    location.href = "login.html";
  }
}

async function completeTask(id) {
  try {
    await api(`/api/tasks/${id}/complete`, {method: "POST"});
    await loadDashboard();
  } catch (err) {
    alert(err.message);
  }
}

async function logout() {
  await api("/api/auth/logout", {method: "POST"});
  location.href = "index.html";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[ch]));
}
