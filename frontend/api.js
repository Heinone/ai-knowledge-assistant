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

async function validateCompanySetup(setupPayload) {
  const response = await fetch(
    `${CONFIG_API_BASE_URL}/config/company/setup/validate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(setupPayload),
    },
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    console.error("Company setup validation failed:", errorBody);

    throw new Error("Could not validate company setup.");
  }

  return response.json();
}

async function validateCompanySetupWithAssets(
  setupPayload,
  { logo = null, favicon = null, assistantAvatar = null } = {},
) {
  const formData = new FormData();

  formData.append("setup_json", JSON.stringify(setupPayload));

  if (logo) {
    formData.append("logo", logo);
  }

  if (favicon) {
    formData.append("favicon", favicon);
  }

  if (assistantAvatar) {
    formData.append("assistant_avatar", assistantAvatar);
  }

  const response = await fetch(
    `${CONFIG_API_BASE_URL}/config/company/setup/validate-multipart`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    console.error("Multipart company setup validation failed:", errorBody);

    throw new Error("Could not validate company setup and assets.");
  }

  return response.json();
}

async function createCompanySetupWithAssets(
  setupPayload,
  { logo = null, favicon = null, assistantAvatar = null } = {},
) {
  const formData = new FormData();

  formData.append("setup_json", JSON.stringify(setupPayload));

  if (logo) {
    formData.append("logo", logo);
  }

  if (favicon) {
    formData.append("favicon", favicon);
  }

  if (assistantAvatar) {
    formData.append("assistant_avatar", assistantAvatar);
  }

  const response = await fetch(`${CONFIG_API_BASE_URL}/config/company/setup`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    console.error("Company setup creation failed:", errorBody);

    const errorMessage =
      typeof errorBody?.detail === "string"
        ? errorBody.detail
        : "Could not create the company setup.";

    throw new Error(errorMessage);
  }

  return response.json();
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
