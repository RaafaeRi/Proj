
let currentView = "results";
let internships = [];

const $ = (id) => document.getElementById(id);

const basePath = document.currentScript
    .getAttribute("src")
    .replace(/\/static\/app\.js(?:\?.*)?$/, "");

function showMessage(message) {
    $("message").textContent = message;
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}

async function loadInternships() {
    const username = $("user").value.trim();

    if (!username) {
        showMessage("Please enter a username.");
        return;
    }

    showMessage("Loading internships...");

    const parameters = new URLSearchParams({
        username: username,
        keyword: $("keyword").value,
        company: $("company").value,
        location: $("location").value,
        view: currentView
    });

    try {
        internships = await apiRequest(
            `${basePath}/api/internships?${parameters}`
        );

        displayInternships();

    } catch (error) {
        showMessage(error.message);
    }
}

function displayInternships() {
    const container = $("jobs");

    container.replaceChildren();

    const headings = {
        results: "Search Results",
        saved: "Saved Internships",
        hidden: "Not Interested"
    };

    $("heading").textContent = headings[currentView];
    $("bulk").hidden = currentView !== "results";
    $("all").checked = false;

    showMessage(`${internships.length} internships found`);

    for (const internship of internships) {
        const column = document.createElement("div");
        column.className = "col-md-6";

        const card = document.createElement("div");
        card.className = "card h-100 shadow-sm";

        const body = document.createElement("div");
        body.className = "card-body";

        if (currentView === "results") {
            const checkbox = document.createElement("input");

            checkbox.type = "checkbox";
            checkbox.className = "form-check-input internship-checkbox mb-3";
            checkbox.value = internship.id;

            body.appendChild(checkbox);
        }

        const title = document.createElement("h5");
        title.className = "card-title";
        title.textContent = internship.title;

        const company = document.createElement("p");
        company.className = "fw-semibold mb-1";
        company.textContent = internship.company;

        const location = document.createElement("p");
        location.className = "text-muted";
        location.textContent = internship.location || "Location unavailable";

        const link = document.createElement("a");
        link.href = internship.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.className = "btn btn-sm btn-outline-primary";
        link.textContent = "View Posting";

        body.append(title, company, location, link);

        if (currentView !== "results") {
            const undoButton = document.createElement("button");

            undoButton.className = "btn btn-sm btn-outline-secondary ms-2";
            undoButton.textContent = "Undo";
            undoButton.onclick = () => updatePreferences([internship.id], "none");

            body.appendChild(undoButton);
        }

        card.appendChild(body);
        column.appendChild(card);
        container.appendChild(column);
    }
}

function getSelectedInternships() {
    return Array.from(
        document.querySelectorAll(".internship-checkbox:checked")
    ).map((checkbox) => Number(checkbox.value));
}

async function updatePreferences(ids, status) {
    if (ids.length === 0) {
        showMessage("Select at least one internship.");
        return;
    }

    const username = $("user").value.trim();

    if (!username) {
        showMessage("Please enter a username.");
        return;
    }

    try {
        await apiRequest(`${basePath}/api/preferences`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                internship_ids: ids,
                status: status
            })
        });

        await loadInternships();

    } catch (error) {
        showMessage(error.message);
    }
}

$("search").onclick = loadInternships;

$("save").onclick = () => {
    updatePreferences(getSelectedInternships(), "saved");
};

$("hide").onclick = () => {
    updatePreferences(getSelectedInternships(), "hidden");
};

$("all").onchange = (event) => {
    document.querySelectorAll(".internship-checkbox").forEach((checkbox) => {
        checkbox.checked = event.target.checked;
    });
};

$("refresh").onclick = async () => {
    const company = $("company").value.trim().toLowerCase();

    if (!company) {
        showMessage("Enter a company to fetch internships.");
        return;
    }

    const button = $("refresh");

    button.disabled = true;
    showMessage(`Fetching internships from ${company}...`);

    try {
        const result = await apiRequest(
            `${basePath}/api/refresh?company=${encodeURIComponent(company)}`,
            { method: "POST" }
        );

        await loadInternships();

        showMessage(`Fetched ${result.found} matching postings from ${company}.`);

    } catch (error) {
        showMessage(error.message);

    } finally {
        button.disabled = false;
    }
};

document.querySelectorAll("[data-view]").forEach((button) => {
    button.onclick = () => {
        currentView = button.dataset.view;

        document.querySelectorAll("[data-view]").forEach((tab) => {
            const active = tab === button;

            tab.classList.toggle("active", active);
            tab.classList.toggle("btn-dark", active);
            tab.classList.toggle("btn-outline-dark", !active);
        });

        loadInternships();
    };
});
