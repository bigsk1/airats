const form = document.querySelector("#studio-form");
const fields = document.querySelector("#settings-fields");
const textMode = document.querySelector("#mode-text");
const imageFields = document.querySelector("#image-fields");
const textFields = document.querySelector("#text-fields");
const phrase = document.querySelector("#phrase");
const sample = document.querySelector("#sample");
const file = document.querySelector("#image");
const browseImage = document.querySelector("#browse-image");
const sourceFilename = document.querySelector("#source-filename");
const url = document.querySelector("#image-url");
const width = document.querySelector("#width");
const contrast = document.querySelector("#contrast");
const cropFrame = document.querySelector("#crop-frame");
const cropDetails = cropFrame.closest("details");
const cropImage = document.querySelector("#source-preview");
const cropBox = document.querySelector("#crop-box");
const cropPreviewStatus = document.querySelector("#crop-preview-status");
const cropEdges = Object.fromEntries(["top", "left", "right", "bottom"].map(edge => [
    edge, document.querySelector(`#crop-${edge}`),
]));
const status = document.querySelector("#status");
const art = document.querySelector("#art");
const canvas = document.querySelector("#canvas");
const previewColor = document.querySelector("#preview-color");
const previewFont = document.querySelector("#preview-font");
const dialog = document.querySelector("#screensaver-preview");
const previewArt = document.querySelector("#preview-art");
const previewCanvas = document.querySelector("#preview-canvas");
const screenStage = document.querySelector("#screen-stage");
const screenGrid = document.querySelector("#screen-grid");
const screenColumns = document.querySelector("#screen-columns");
const screenRows = document.querySelector("#screen-rows");
const screenStatus = document.querySelector("#screen-status");
const install = document.querySelector("#install");
const applyInstall = document.querySelector("#apply-screensaver");
const download = document.querySelector("#download");
const copy = document.querySelector("#copy");
const preview = document.querySelector("#preview");
const exportButtons = [download, copy, preview, install].filter(Boolean);
const maxBytes = 8 * 1024 * 1024;
const previewDelay = 160;
let dimensions = { columns: 0, rows: 0 };
let localImage;
let source;
let previewUrl;
let drag;
let selectedSource;
let previewVersion = 0;
let previewTimer;
let queuedPreview;
let rendering = false;
let renderedForm;
let screenRequest;
let screenTimer;

function announce(message, error = false) {
    if (status.textContent !== message) status.textContent = message;
    status.classList.toggle("error", error);
}

function clearArtwork() {
    renderedForm = undefined;
    dimensions = { columns: 0, rows: 0 };
    art.textContent = "";
    document.querySelector("#dimensions").textContent = "";
}

function fitArt() {
    if (!dimensions.columns || !canvas.clientWidth) return;
    const availableWidth = canvas.clientWidth - 32;
    const measuredWidth = art.getBoundingClientRect().width;
    const currentSize = Number.parseFloat(getComputedStyle(art).fontSize);
    const size = Math.min(18, currentSize * availableWidth / measuredWidth,
        480 / (1.04 * dimensions.rows));
    art.style.fontSize = `${Math.max(4, size)}px`;
}

function fitScreenFrame() {
    if (!dialog.open || !screenStage?.clientWidth || !screenGrid.checkValidity()) return;
    const ratio = Number(screenGrid.dataset.cellRatio);
    const rowHeight = Math.min(
        screenStage.clientWidth / (screenColumns.valueAsNumber * ratio),
        screenStage.clientHeight / screenRows.valueAsNumber,
    );
    const columnWidth = rowHeight * ratio;
    previewCanvas.style.width = `${columnWidth * screenColumns.valueAsNumber}px`;
    previewCanvas.style.height = `${rowHeight * screenRows.valueAsNumber}px`;
    previewArt.style.fontSize = `${rowHeight / 1.15}px`;
    previewArt.style.lineHeight = `${rowHeight}px`;
    const artColumns = previewArt.textContent.split("\n", 1)[0].length;
    if (artColumns && previewArt.offsetWidth) {
        previewArt.style.transform = `scaleX(${artColumns * columnWidth / previewArt.offsetWidth})`;
    }
}

new ResizeObserver(fitArt).observe(canvas);
if (screenStage) new ResizeObserver(fitScreenFrame).observe(screenStage);

function updatePreviewColor() {
    document.documentElement.style.setProperty("--art-color", previewColor.value);
}

if (previewColor) {
    previewColor.addEventListener("input", updatePreviewColor);
    previewColor.addEventListener("change", updatePreviewColor);
    updatePreviewColor();
}

function fitPreviews() {
    fitArt();
    fitScreenFrame();
}

function updatePreviewFont() {
    document.documentElement.dataset.artFont = previewFont.value;
    fitPreviews();
}

if (previewFont) {
    previewFont.addEventListener("change", updatePreviewFont);
    document.fonts.addEventListener("loadingdone", fitPreviews);
    updatePreviewFont();
}

function updateCrop() {
    const { top, left, right, bottom } = cropEdges;
    const fitsHorizontally = left.valueAsNumber + right.valueAsNumber < 100;
    const fitsVertically = top.valueAsNumber + bottom.valueAsNumber < 100;
    right.setCustomValidity(fitsHorizontally ? "" : "Left and right trims must add up to less than 100%.");
    bottom.setCustomValidity(fitsVertically ? "" : "Top and bottom trims must add up to less than 100%.");
    cropBox.hidden = Object.values(cropEdges).some(input => !input.validity.valid);
    for (const [edge, input] of Object.entries(cropEdges)) {
        cropBox.style.setProperty(`--crop-${edge}`, `${input.value}%`);
    }
}

function resetCrop() {
    for (const input of Object.values(cropEdges)) input.value = 0;
    updateCrop();
}

function clearSourcePreview() {
    cropFrame.hidden = true;
    cropPreviewStatus.hidden = true;
    cropImage.removeAttribute("src");
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = undefined;
}

cropImage.addEventListener("load", () => { cropFrame.hidden = !previewUrl; });
cropImage.addEventListener("error", () => { cropPreviewStatus.hidden = !previewUrl; });

function cropPoint(event) {
    const bounds = cropFrame.getBoundingClientRect();
    const percent = (offset, size) => Math.max(0, Math.min(100, Math.round(100 * offset / size)));
    return {
        x: percent(event.clientX - bounds.left, bounds.width),
        y: percent(event.clientY - bounds.top, bounds.height),
    };
}

cropFrame.addEventListener("pointerdown", event => {
    if (fields.disabled || !event.isPrimary || event.button !== 0) return;
    drag = cropPoint(event);
    cropFrame.setPointerCapture(event.pointerId);
});
cropFrame.addEventListener("pointermove", event => {
    if (!drag || !cropFrame.hasPointerCapture(event.pointerId)) return;
    const end = cropPoint(event);
    if (Math.abs(drag.x - end.x) < 2 || Math.abs(drag.y - end.y) < 2) return;
    cropEdges.left.value = Math.min(drag.x, end.x);
    cropEdges.right.value = 100 - Math.max(drag.x, end.x);
    cropEdges.top.value = Math.min(drag.y, end.y);
    cropEdges.bottom.value = 100 - Math.max(drag.y, end.y);
    updateCrop();
    requestPreview();
});
cropFrame.addEventListener("lostpointercapture", () => { drag = undefined; });

function setLocalImage(image) {
    localImage = image;
    if (sourceFilename) sourceFilename.textContent = image?.name ?? "No file selected";
}

browseImage?.addEventListener("click", () => file.click());
file.addEventListener("change", () => {
    const image = file.files[0];
    if (!image) return;
    // Reset the picker so choosing the same path still triggers a change.
    file.value = "";
    setLocalImage(image);
    url.value = "";
    requestPreview({ selectSource: true });
});
url.addEventListener("input", () => {
    if (url.value.trim()) setLocalImage(undefined);
});
width.addEventListener("input", () => {
    document.querySelector("#width-value").value = `${width.value} columns`;
});
contrast.addEventListener("input", () => {
    document.querySelector("#contrast-value").value = `${contrast.value}%`;
});
for (const [id, unit] of [["text-rows", " rows"], ["splatter", "%"]]) {
    const slider = document.getElementById(id);
    slider?.addEventListener("input", () => {
        document.getElementById(`${id}-value`).value = slider.value + unit;
    });
}
function showSourceFields() {
    if (!textMode) return;
    const writing = textMode.checked;
    imageFields.hidden = imageFields.disabled = writing;
    textFields.hidden = textFields.disabled = !writing;
    sample.hidden = writing;
}
for (const radio of form.querySelectorAll('input[name="mode"]')) {
    radio.addEventListener("change", () => {
        showSourceFields();
        requestPreview({ selectSource: true });
    });
}
form.addEventListener("input", event => {
    if (event.target.matches('select, input[type="checkbox"], input[type="file"], input[type="radio"]')) return;
    if (Object.values(cropEdges).includes(event.target)) updateCrop();
    requestPreview();
});
form.addEventListener("change", event => {
    if (event.target.matches('select, input[type="checkbox"]')) requestPreview();
});
cropDetails.addEventListener("invalid", () => { cropDetails.open = true; }, true);
document.querySelector("#reset-crop").addEventListener("click", () => {
    resetCrop();
    requestPreview();
});

async function readImageUrl(source, isSample) {
    const target = new URL(source, location.href);
    if (!["http:", "https:"].includes(target.protocol) || target.username || target.password) {
        throw new Error("Enter an HTTP or HTTPS image URL.");
    }
    let response;
    try {
        response = await fetch(target, {
            credentials: "omit", signal: AbortSignal.timeout(15000),
            redirect: "follow", referrerPolicy: "no-referrer",
        });
    } catch {
        throw new Error("Could not load that URL. If the host blocks downloads, use an image file.");
    }
    if (!response.ok || !response.body) {
        throw new Error(isSample ? "Could not load the sample image." : "Could not download that image.");
    }
    const reader = response.body.getReader();
    let size = 0;
    const chunks = [];
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            size += value.byteLength;
            if (size > maxBytes) throw new Error("Choose an image under 8 MiB.");
            chunks.push(value);
        }
    } finally {
        await reader.cancel().catch(() => {});
    }
    return new Blob(chunks);
}

async function checkResponse(response, fallback) {
    if (response.ok) return response;
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || fallback);
}

function requestPreview({ selectSource = false } = {}) {
    if (fields.disabled) return;
    clearTimeout(previewTimer);
    queuedPreview = undefined;
    const version = ++previewVersion;
    exportButtons.forEach(button => { button.disabled = true; });

    const key = textMode?.checked ? null : (localImage || url.value.trim() || form.dataset.sample);
    if (key === null && !phrase.value.trim()) {
        clearArtwork();
        announce("Enter a word or phrase.");
        return;
    }
    if (key !== null) {
        if (selectSource && key !== selectedSource) {
            selectedSource = key;
            resetCrop();
        }
        if (key !== selectedSource) {
            clearSourcePreview();
            announce("Click Generate ASCII to load the selected image.");
            return;
        }
        if (key !== source?.key) clearSourcePreview();
    }
    if (!form.checkValidity()) {
        if (selectSource) form.reportValidity();
        announce(key === null ? "Check the word or phrase." : "Check the crop values before updating the preview.", true);
        return;
    }

    announce(dimensions.columns || key === null ? "Updating preview…" : "Converting image…");
    function queuePreview() {
        const body = new FormData(form);
        if (key !== null) {
            for (const input of Object.values(cropEdges)) body.set(input.name, input.valueAsNumber);
        }
        queuedPreview = { key, version, body };
        renderPreview();
    }
    if (selectSource) queuePreview();
    else previewTimer = setTimeout(queuePreview, previewDelay);
}

async function renderPreview() {
    if (rendering || !queuedPreview) return;
    const { key, version, body } = queuedPreview;
    queuedPreview = undefined;
    rendering = true;
    try {
        if (key !== null && key !== source?.key) {
            const image = key instanceof File ? key : await readImageUrl(key, key === form.dataset.sample);
            if (key !== selectedSource) return;
            if (image.size > maxBytes) throw new Error("Choose an image under 8 MiB.");
            source = { key, image };
        }
        if (version !== previewVersion) return;
        if (key !== null) body.set("image", source.image, "image");
        const response = await fetch("/generate", {
            method: "POST", body, signal: AbortSignal.timeout(30000),
        });
        await checkResponse(response, "Could not convert the image.");
        const text = await response.text();
        // Keep a slower response from replacing the latest preview.
        if (version !== previewVersion) return;
        if (key !== null && !previewUrl) {
            previewUrl = URL.createObjectURL(source.image);
            cropImage.src = previewUrl;
        }
        const lines = text.split("\n");
        dimensions = { columns: lines[0].length, rows: lines.length };
        renderedForm = body;
        art.textContent = text;
        document.querySelector("#dimensions").textContent = `${dimensions.columns} × ${dimensions.rows}`;
        fitArt();
        announce("");
        exportButtons.forEach(button => { button.disabled = false; });
    } catch (error) {
        if (version !== previewVersion) return;
        clearArtwork();
        announce(error.message, true);
    } finally {
        rendering = false;
        if (queuedPreview) renderPreview();
    }
}

form.addEventListener("submit", event => {
    event.preventDefault();
    requestPreview({ selectSource: true });
});

sample.addEventListener("click", () => {
    setLocalImage(undefined);
    url.value = "";
    requestPreview({ selectSource: true });
});

download.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([art.textContent + "\n"], { type: "text/plain;charset=utf-8" }));
    link.download = "ascii-studio.txt";
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
});

copy.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(art.textContent);
        announce("Copied ASCII art.");
    } catch {
        announce("Clipboard access failed. Use Download .txt to save the artwork.", true);
    }
});

async function renderScreenPreview(controller) {
    const body = new FormData();
    for (const [name, value] of renderedForm) body.append(name, value);
    body.set("fit_columns", screenColumns.valueAsNumber);
    body.set("fit_rows", screenRows.valueAsNumber);
    try {
        const response = await fetch("/generate", {
            method: "POST", body,
            signal: AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]),
        });
        await checkResponse(response, "Could not fit the screensaver artwork.");
        const text = await response.text();
        if (controller.signal.aborted) return;
        const lines = text.split("\n");
        previewArt.textContent = text;
        fitScreenFrame();
        screenStatus.textContent = `${lines[0].length} × ${lines.length} characters on a ${screenColumns.valueAsNumber} × ${screenRows.valueAsNumber} grid.`;
        if (applyInstall) applyInstall.disabled = !text.trim();
    } catch (error) {
        if (!controller.signal.aborted) screenStatus.textContent = error.message;
    }
}

function refreshScreensaverPreview(debounce = false) {
    clearTimeout(screenTimer);
    screenRequest?.abort();
    if (applyInstall) applyInstall.disabled = true;
    previewArt.textContent = "";
    if (!screenGrid.checkValidity()) {
        screenStatus.textContent = "Enter valid terminal columns and rows.";
        return;
    }
    fitScreenFrame();
    screenStatus.textContent = "Fitting artwork…";
    const controller = new AbortController();
    screenRequest = controller;
    if (debounce) screenTimer = setTimeout(() => renderScreenPreview(controller), previewDelay);
    else renderScreenPreview(controller);
}

function openScreensaverPreview() {
    if (!screenGrid || !renderedForm) return;
    dialog.showModal();
    refreshScreensaverPreview();
}

preview.addEventListener("click", openScreensaverPreview);
install?.addEventListener("click", openScreensaverPreview);
screenGrid?.addEventListener("input", () => refreshScreensaverPreview(true));
dialog.addEventListener("close", () => {
    clearTimeout(screenTimer);
    screenRequest?.abort();
});

applyInstall?.addEventListener("click", async () => {
    if (!window.confirm("Replace your current Omarchy screensaver artwork? A backup will be saved beside it.")) return;
    applyInstall.disabled = true;
    exportButtons.forEach(button => { button.disabled = true; });
    fields.disabled = true;
    screenGrid.disabled = true;
    try {
        const response = await fetch("/screensaver", {
            method: "POST",
            headers: { "Content-Type": "text/plain;charset=utf-8", "X-ASCII-Studio-Token": applyInstall.dataset.token },
            body: previewArt.textContent,
        });
        const { backup } = await (await checkResponse(response, "Could not install the screensaver.")).json();
        dialog.close();
        announce(backup ? `Installed. Previous artwork backed up as ${backup}.` : "Installed for the next Omarchy screensaver launch.");
    } catch (error) {
        if (dialog.open) screenStatus.textContent = error.message;
        else announce(error.message, true);
    } finally {
        applyInstall.disabled = false;
        exportButtons.forEach(button => { button.disabled = false; });
        fields.disabled = false;
        screenGrid.disabled = false;
    }
});

showSourceFields();
requestPreview({ selectSource: true });
