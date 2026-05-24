const ingestTextArea = document.getElementById("ingest-text");
const fileInput = document.getElementById("file-input");
const ingestButton = document.getElementById("ingest-button");
const ingestStatus = document.getElementById("ingest-status");
const questionInput = document.getElementById("question-input");
const queryButton = document.getElementById("query-button");
const queryStatus = document.getElementById("query-status");
const serviceStatus = document.getElementById("service-status");
const answerCard = document.getElementById("answer-card");
const answerContent = document.getElementById("answer-content");
const copyAnswer = document.getElementById("copy-answer");
const clearAnswer = document.getElementById("clear-answer");


function setStatus(element, message, type) {
  element.textContent = message;
  element.className = `status ${type}`;
}

async function postForm(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || response.statusText || "Request failed");
  }

  return response.json();
}

ingestButton.addEventListener("click", async () => {
  const text = ingestTextArea.value.trim();
  const file = fileInput.files[0];
  const formData = new FormData();

  if (file) {
    formData.append("file", file);
  } else if (text) {
    formData.append("text", text);
  } else {
    setStatus(ingestStatus, "Please paste text or upload a file.", "error");
    return;
  }

  ingestButton.disabled = true;
  setStatus(ingestStatus, "Ingesting document...", "loading");

  try {
    const result = await postForm("/api/ingest", formData);
    setStatus(ingestStatus, "Document ingested successfully.", "success");
    const preview = file ? file.name : text.slice(0, 250) + (text.length > 250 ? "..." : "");
    // clear inputs for a tidy UX
    ingestTextArea.value = "";
    fileInput.value = "";
    setTimeout(() => setStatus(ingestStatus, `Ingested ${result.detail.ingested_chunks} chunk(s).`, "success"), 400);
  } catch (error) {
    setStatus(ingestStatus, error.message, "error");
  } finally {
    ingestButton.disabled = false;
  }
});

queryButton.addEventListener("click", async () => {
  const question = questionInput.value.trim();
  if (!question) {
    setStatus(queryStatus, "Please enter a question.", "error");
    return;
  }

  queryButton.disabled = true;
  setStatus(queryStatus, "Querying knowledge base...", "loading");

  try {
    const formData = new FormData();
    formData.append("question", question);
    const result = await postForm("/api/query", formData);
    setStatus(queryStatus, "Answer received.", "success");
    // show result in single-answer view
    answerContent.textContent = result.answer || "(no answer returned)";
    answerCard.classList.remove("hidden");
    // clear input for tidy UX
    questionInput.value = "";
  } catch (error) {
    setStatus(queryStatus, error.message, "error");
  } finally {
    queryButton.disabled = false;
  }
});

copyAnswer.addEventListener("click", () => {
  const text = answerContent.textContent || "";
  if (!text) return;
  navigator.clipboard?.writeText(text).then(() => {
    setStatus(queryStatus, "Answer copied to clipboard.", "success");
  });
});

clearAnswer.addEventListener("click", () => {
  answerContent.textContent = "";
  answerCard.classList.add("hidden");
});

window.addEventListener("load", () => {
  setStatus(serviceStatus, "Ready — upload a file or paste text, then ask a question.", "");
});
