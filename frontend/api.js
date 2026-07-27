const API_BASE_URL = "http://127.0.0.1:8000";

async function uploadDocuments(files) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/documents/upload-batch`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Document upload failed.");
  }

  return data;
}

async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not generate an answer.");
  }

  return data;
}

function storeUploadSummary(summary) {
  localStorage.setItem("aka_upload_summary", JSON.stringify(summary));
}

function getUploadSummary() {
  const raw = localStorage.getItem("aka_upload_summary");

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function clearUploadSummary() {
  localStorage.removeItem("aka_upload_summary");
}
