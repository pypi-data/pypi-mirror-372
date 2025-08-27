(function () {
    function setupLogStreamHandler(taskId, logElementId = "log-output", taskElementId = "log-task-id", cardElementId = "log-card") {
        const logElement = document.getElementById(logElementId);
        const taskLabel = document.getElementById(taskElementId);
        const card = document.getElementById(cardElementId);

        if (!logElement) {
            console.warn("[LogStream] One or more DOM elements missing.");
            return;
        }

        if (taskLabel) {
            taskLabel.textContent = taskId;
        }
        if (card) {
            card.style.display = "block";

        }

        if (typeof safeRegisterHandler === 'function') {
            safeRegisterHandler("logs", function (msg) {
                if (msg.meta?.task_id !== taskId) return;

                const level = msg.meta?.level || "INFO";
                const content = msg.content || "";

                logElement.innerHTML += `<div><span class="badge bg-${level.toLowerCase()}">${level}</span> ${content}</div>`;
                logElement.scrollTop = logElement.scrollHeight;

                const log = document.getElementById("log-output");

                if (msg.meta?.event === "__TASK_DONE__") {
                    log.innerHTML += "<br><strong>[END OF TASK]</strong><br>";
                    return;
                }
            });
        } else {
            console.warn("[LogStream] safeRegisterHandler is not defined. Log streaming will not work.");
        }
    }

    window.setupLogStreamHandler = setupLogStreamHandler;
})();
