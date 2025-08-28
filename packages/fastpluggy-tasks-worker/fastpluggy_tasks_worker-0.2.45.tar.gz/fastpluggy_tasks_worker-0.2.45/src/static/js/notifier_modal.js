let availableNotifiers = [];
let editIndex = null;
let notifierMetaCache = null;

/**
 * Fetch and cache notifier metadata (available + default rules).
 */
async function fetchNotifierMeta() {
    if (notifierMetaCache) return notifierMetaCache;

    const url = window.NOTIFIER_MODAL_CONFIG?.url_list_available_notifiers;
    if (!url) throw new Error("Missing notifier config URL");

    const res = await fetch(url);
    const data = await res.json();
    notifierMetaCache = data;
    return data;
}

/**
 * Load available notifiers and default rules into the form initially.
 */
async function loadAvailableNotifiersAndDefaults() {
    try {
        const response = await fetchNotifierMeta();
        availableNotifiers = response.available_notifiers || [];

        const defaultRules = response.default_rules || [];
        const notifyInput = document.getElementById("notify-on-data");

        // Only prefill if no existing config
        if (notifyInput && (!notifyInput.value || notifyInput.value === "[]")) {
            notifyInput.value = JSON.stringify(defaultRules);
            renderNotifierPreview();
        }
    } catch (err) {
        console.error("Failed to load notifiers:", err);
    }
}

/**
 * Open modal to add or edit a notifier.
 * @param {boolean} isEdit - True if editing, false if adding
 */
async function openAddNotifierModal(isEdit = false) {
    const response = await fetchNotifierMeta();
    availableNotifiers = response.available_notifiers || [];

    const select = document.getElementById("notifier-select");
    select.innerHTML = "";

    // Rebuild select to clear previous listeners
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    availableNotifiers.forEach(n => {
        const option = document.createElement("option");
        option.value = n.name;
        option.textContent = n.name;
        newSelect.appendChild(option);
    });

    newSelect.addEventListener("change", updateEventCheckboxes);

    // Button label
    const submitButton = document.getElementById("notifier-submit-button");
    submitButton.textContent = isEdit ? "Save" : "Add";

    // Disable select during edit
    newSelect.disabled = isEdit;

    updateEventCheckboxes();

    new bootstrap.Modal(document.getElementById("modal-add-notifier")).show();

    return Promise.resolve();
}

/**
 * Update the checkboxes for notifier events based on the selected notifier.
 */
function updateEventCheckboxes() {
    const selected = document.getElementById("notifier-select").value;
    const notifier = availableNotifiers.find(n => n.name === selected);
    const container = document.getElementById("event-checkboxes");

    container.innerHTML = "";
    (notifier?.events || []).forEach(event => {
        const id = `event-${event}`;
        container.innerHTML += `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="${event}" id="${id}" checked>
                <label class="form-check-label" for="${id}">${event}</label>
            </div>`;
    });
}

/**
 * Submit button handler to add or update notifier config.
 */
function addNotifierConfig(e) {
    e.preventDefault();

    const name = document.getElementById("notifier-select").value;
    const events = Array.from(document.querySelectorAll("#event-checkboxes input:checked"))
                        .map(cb => cb.value);

    if (!events.length) {
        alert("You must select at least one event.");
        return;
    }

    const notifyInput = document.getElementById("notify-on-data");
    const current = JSON.parse(notifyInput.value);

    if (editIndex !== null) {
        current[editIndex] = { name, events };
    } else {
        if (current.find(n => n.name === name)) {
            alert("Notifier already added.");
            return;
        }
        current.push({ name, events });
    }

    notifyInput.value = JSON.stringify(current);
    renderNotifierPreview();

    bootstrap.Modal.getInstance(document.getElementById("modal-add-notifier")).hide();

    resetNotifierModalState();
}

/**
 * Populate modal fields with existing notifier for editing.
 */
function editNotifier(index) {
    const notifyInput = document.getElementById("notify-on-data");
    const current = JSON.parse(notifyInput.value);
    const entry = current[index];
    if (!entry) return;

    editIndex = index;

    openAddNotifierModal(true).then(() => {
        const select = document.getElementById("notifier-select");
        select.value = entry.name;

        updateEventCheckboxes();

        // Pre-check stored events
        const checkboxes = document.querySelectorAll("#event-checkboxes input[type=checkbox]");
        checkboxes.forEach(cb => {
            cb.checked = entry.events.includes(cb.value);
        });
    });
}

/**
 * Renders the list of configured notifiers with Edit/Remove buttons.
 */
function renderNotifierPreview() {
    const list = document.getElementById("configured-notifiers");
    const notifyInput = document.getElementById("notify-on-data");
    const current = JSON.parse(notifyInput.value);

    list.innerHTML = "";
    current.forEach((entry, i) => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `
            <div>
              <strong>${entry.name}</strong> → ${entry.events.join(", ")}
            </div>
            <div class="btn-group btn-group-sm">
              <button type="button" class="btn btn-outline-secondary" onclick="editNotifier(${i})">Edit</button>
              <button type="button" class="btn btn-outline-danger" onclick="removeNotifier(${i})">Remove</button>
            </div>
        `;
        list.appendChild(li);
    });
}

/**
 * Remove a notifier from the configured list.
 */
function removeNotifier(index) {
    const notifyInput = document.getElementById("notify-on-data");
    const current = JSON.parse(notifyInput.value);
    current.splice(index, 1);
    notifyInput.value = JSON.stringify(current);
    renderNotifierPreview();
}

/**
 * Reset modal UI state (after closing).
 */
function resetNotifierModalState() {
    editIndex = null;

    const select = document.getElementById("notifier-select");
    if (select) select.disabled = false;

    const submitButton = document.getElementById("notifier-submit-button");
    if (submitButton) submitButton.textContent = "Add";
}

function selectAllEvents() {
  const checkboxes = document.querySelectorAll("#event-checkboxes input[type='checkbox']");
  checkboxes.forEach(cb => {
    cb.checked = true;
  });
}

function deselectAllEvents() {
  const checkboxes = document.querySelectorAll("#event-checkboxes input[type='checkbox']");
  checkboxes.forEach(cb => {
    cb.checked = false;
  });
}

