let transcriptionId   = null;              
let intervalId        = null;              
const renderedTasks   = {};                
let activeTasks = null;

function showAlert(message) {
    const alert = document.createElement('div');
    alert.classList.add("custom-alert");
    alert.innerText = message;

    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 1000);
}

function copyToClipboard() {
    const wrapper  = document.getElementById("transcription-text");
    const textElement = wrapper.querySelector("p");
    if (textElement) {
        navigator.clipboard.writeText(textElement.innerText)
            .then(() => showAlert("✅ Transcription copied!"));
    }
}

function copySummaryToClipboard() {
    const wrapper  = document.getElementById("summary-text");
    const textElement = wrapper.querySelector("p");
    if (textElement) {
        navigator.clipboard.writeText(textElement.innerText)
            .then(() => showAlert("✅ Summary copied!"));
    }
}

function downloadAsTxt() {
    const wrapper  = document.getElementById("transcription-text");
    const textElement = wrapper.querySelector("p");
    if (textElement) {
        const blob = new Blob([textElement.innerText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "transcription.txt";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

function downloadSummaryAsTxt() {
    const wrapper  = document.getElementById("summary-text");
    const textElement = wrapper.querySelector("p");
    if (textElement) {
        const blob = new Blob([textElement.innerText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "summary.txt";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}
/* -------------------- FETCHING DATA -------------------- */
function fetchActiveTasks() {
    if (!transcriptionId) {
        console.error("No transcriptionId – stopping polling");
        stopPolling();
        return;
    }

    fetch(`/api/transcriptions/${transcriptionId}/active-tasks/`)
        .then(r => r.json())
        .then(updateDOM)
        .catch(err => {
            console.error("Fetch error:", err);
        });
}

/* -------------------- DOM UPDATE -------------------- */
function updateDOM(data) {
    const box = document.getElementById("active-tasks-box");
    if (!box) return;

    const taskIds = Object.keys(data);

    /* 1. NO ACTIVE TASKS → hide box and reload */
    if (taskIds.length === 0) {
        box.hidden = true;
        stopPolling();
        location.reload();
        return;
    }
    box.hidden = false;

    /* 2. ITERATE THROUGH EACH TASK FROM ENDPOINT */
    taskIds.forEach(taskId => {
        const taskData   = data[taskId];
        const boxId      = `task-${taskId}`;
        let   taskBox    = document.getElementById(boxId);

        /* 2a. If task-box does not exist yet → create it */
        if (!taskBox) {
            taskBox = document.createElement("div");
            taskBox.id = boxId;
            taskBox.classList.add("task-box");

            /* pretty status:  in_progress → In Progress */
            const prettyStatus = taskData.status
                .replace(/_/g, " ")
                .replace(/\b\w/g, c => c.toUpperCase());

            taskBox.innerHTML = `
                <p>
                    <strong class="task-type">${taskData.type}</strong>
                    &mdash;
                    <span class="task-status badge">${prettyStatus}</span>
                </p>
                <ul class="log-list"></ul>
            `;
            box.appendChild(taskBox);
            renderedTasks[taskId] = new Set();
        }


        /* ─── 2b. Add only new logs ─── */
        const logUl = taskBox.querySelector(".log-list");
        taskData.logs.forEach(log => {
            if (!renderedTasks[taskId].has(log.id)) {
                const li = document.createElement("li");
                li.textContent = log.message;           // or `${log.status}: ${log.message}`
                logUl.appendChild(li);
                renderedTasks[taskId].add(log.id);      // remember that log is already rendered
            }
        });
    });
}

/* -------------------- START / STOP POLLING -------------------- */
function startPolling() {
    fetchActiveTasks();                    // first time immediately
    intervalId = setInterval(fetchActiveTasks, 3000);
}
function stopPolling() {
    if (intervalId) clearInterval(intervalId);
}

/* -------------------- INIT AFTER DOM LOAD -------------------- */
document.addEventListener("DOMContentLoaded", () => {
    const tData         = document.getElementById("transcription-id");
    transcriptionId     = tData?.dataset.transcriptionId;
    const hasActiveTask = tData?.dataset.activeTasks === "1";

    if (hasActiveTask) startPolling();
});