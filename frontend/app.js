const state = {
  metadata: null,
  charts: {},
};

const palette = {
  teal: "#127c79",
  gold: "#c58a1e",
  rose: "#b94a64",
  blue: "#3766a6",
  ink: "#17202a",
  grid: "#dce4e8",
};

const formatLpa = (value) => `${Number(value || 0).toFixed(1)} LPA`;
const qs = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

function selectedValues(id) {
  return Array.from(qs(id).selectedOptions).map((option) => option.value);
}

function fillSelect(id, values, selected = values) {
  const select = qs(id);
  select.innerHTML = values
    .map((value) => `<option value="${value}" ${selected.includes(value) ? "selected" : ""}>${value}</option>`)
    .join("");
}

function buildDashboardUrl() {
  const params = new URLSearchParams();
  selectedValues("#year-filter").forEach((year) => params.append("years", year));
  selectedValues("#branch-filter").forEach((branch) => params.append("branches", branch));

  const cgpaMin = qs("#cgpa-min").value;
  const cgpaMax = qs("#cgpa-max").value;
  if (cgpaMin) params.set("cgpa_min", cgpaMin);
  if (cgpaMax) params.set("cgpa_max", cgpaMax);

  return `/api/dashboard?${params.toString()}`;
}

function destroyChart(id) {
  if (state.charts[id]) {
    state.charts[id].destroy();
  }
}

function renderChart(id, config) {
  destroyChart(id);
  state.charts[id] = new Chart(qs(`#${id}`), {
    ...config,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: palette.ink, padding: 10 },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#65717d" } },
        y: { grid: { color: palette.grid }, ticks: { color: "#65717d" }, beginAtZero: true },
      },
      ...config.options,
    },
  });
}

function renderKpis(kpis) {
  qs("#kpi-students").textContent = kpis.students;
  qs("#kpi-placed").textContent = kpis.placed;
  qs("#kpi-rate").textContent = `${kpis.placement_rate}%`;
  qs("#kpi-avg-package").textContent = formatLpa(kpis.avg_package);
  qs("#kpi-high-package").textContent = formatLpa(kpis.highest_package);
  qs("#kpi-cgpa").textContent = Number(kpis.avg_cgpa || 0).toFixed(1);
}

function renderTrend(rows) {
  renderChart("trend-chart", {
    type: "line",
    data: {
      labels: rows.map((row) => row.graduation_year),
      datasets: [
        {
          data: rows.map((row) => row.placement_rate),
          borderColor: palette.teal,
          backgroundColor: "rgba(18, 124, 121, 0.14)",
          fill: true,
          tension: 0.32,
          pointRadius: 4,
        },
      ],
    },
  });
}

function renderBranch(rows) {
  renderChart("branch-chart", {
    type: "bar",
    data: {
      labels: rows.map((row) => row.branch),
      datasets: [
        {
          data: rows.map((row) => row.placement_rate),
          backgroundColor: rows.map((_, index) => [palette.teal, palette.blue, palette.gold, palette.rose][index % 4]),
          borderRadius: 6,
        },
      ],
    },
  });
}

function renderCompanies(rows) {
  renderChart("company-chart", {
    type: "bar",
    data: {
      labels: rows.map((row) => row.company),
      datasets: [
        {
          data: rows.map((row) => row.hires),
          backgroundColor: palette.blue,
          borderRadius: 6,
        },
      ],
    },
    options: {
      indexAxis: "y",
    },
  });
}

function salaryBuckets(rows) {
  const buckets = ["0-4", "4-6", "6-8", "8-10", "10+"];
  const counts = Object.fromEntries(buckets.map((bucket) => [bucket, 0]));
  rows.forEach((row) => {
    const salary = Number(row.package_lpa);
    if (salary < 4) counts["0-4"] += 1;
    else if (salary < 6) counts["4-6"] += 1;
    else if (salary < 8) counts["6-8"] += 1;
    else if (salary < 10) counts["8-10"] += 1;
    else counts["10+"] += 1;
  });
  return { buckets, counts };
}

function renderSalary(rows) {
  const { buckets, counts } = salaryBuckets(rows);
  renderChart("salary-chart", {
    type: "doughnut",
    data: {
      labels: buckets,
      datasets: [
        {
          data: buckets.map((bucket) => counts[bucket]),
          backgroundColor: [palette.teal, palette.blue, palette.gold, palette.rose, "#6c757d"],
          borderColor: "#ffffff",
          borderWidth: 3,
        },
      ],
    },
    options: {
      cutout: "62%",
      scales: {},
      plugins: {
        legend: { display: true, position: "bottom", labels: { boxWidth: 12 } },
      },
    },
  });
}

function renderSkills(rows) {
  qs("#skills-list").innerHTML = rows.length
    ? rows
        .map(
          (row) => `
            <div class="skill-row">
              <strong>${row.skill}</strong>
              <span>${row.students} students | ${formatLpa(row.avg_package)}</span>
            </div>
          `,
        )
        .join("")
    : "<p>No skills available for this filter.</p>";
}

function renderOffers(rows) {
  qs("#top-offers").innerHTML = rows.length
    ? rows
        .map(
          (row) => `
            <div class="offer-row">
              <div>
                <strong>${row.name}</strong>
                <span>${row.company} | ${row.role} | ${row.branch}</span>
              </div>
              <span>${formatLpa(row.package_lpa)}</span>
            </div>
          `,
        )
        .join("")
    : "<p>No placed offers for this filter.</p>";
}

function renderStudents(rows) {
  qs("#student-table").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.name}</td>
          <td>${row.branch}</td>
          <td>${row.graduation_year}</td>
          <td>${Number(row.cgpa).toFixed(1)}</td>
          <td><span class="badge ${row.placed ? "placed" : "open"}">${row.placed ? "Placed" : "Not Placed"}</span></td>
          <td>${row.company || "-"}</td>
          <td>${row.role || "-"}</td>
          <td>${formatLpa(row.package_lpa)}</td>
        </tr>
      `,
    )
    .join("");
}

async function loadDashboard() {
  const data = await api(buildDashboardUrl());
  renderKpis(data.kpis);
  renderTrend(data.trend);
  renderBranch(data.branch_summary);
  renderCompanies(data.company_summary);
  renderSalary(data.salary_distribution);
  renderSkills(data.skill_summary);
  renderOffers(data.top_offers);
  renderStudents(data.students);
}

function resetFilters() {
  fillSelect("#year-filter", state.metadata.years.map(String), state.metadata.years.map(String));
  fillSelect("#branch-filter", state.metadata.branches, state.metadata.branches);
  qs("#cgpa-min").value = state.metadata.cgpa.min;
  qs("#cgpa-max").value = state.metadata.cgpa.max;
}

async function handlePrediction(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  [
    "graduation_year",
    "cgpa",
    "tenth_percent",
    "twelfth_percent",
    "internships",
    "projects",
    "certifications",
    "aptitude_score",
    "communication_score",
  ].forEach((key) => {
    payload[key] = Number(payload[key]);
  });

  const resultBox = qs("#prediction-result");
  resultBox.className = "prediction-result muted";
  resultBox.textContent = "Scoring...";

  try {
    const result = await api("/api/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    resultBox.className = `prediction-result ${result.prediction ? "" : "risk"}`;
    resultBox.textContent = `${result.probability}% - ${result.message}`;
  } catch (error) {
    resultBox.className = "prediction-result risk";
    resultBox.textContent = error.message;
  }
}

async function init() {
  state.metadata = await api("/api/metadata");
  resetFilters();
  fillSelect("#predict-gender", state.metadata.genders, [state.metadata.genders[0]]);
  fillSelect("#predict-branch", state.metadata.branches, [state.metadata.branches[0]]);

  qs("#apply-filters").addEventListener("click", loadDashboard);
  qs("#reset-filters").addEventListener("click", () => {
    resetFilters();
    loadDashboard();
  });
  qs("#prediction-form").addEventListener("submit", handlePrediction);

  await loadDashboard();
  lucide.createIcons();
}

init().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><section class="panel"><h3>Unable to load dashboard</h3><p>${error.message}</p></section></main>`;
});
