// transcription_detail.js

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
