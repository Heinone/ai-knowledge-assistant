const API_BASE_URL = "http://127.0.0.1:8000";

async function uploadDocuments(files, mode) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  formData.append("mode", mode);

  const response = await fetch(`${API_BASE_URL}/documents/upload-batch`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Document upload failed.",
    );
  }

  return data;
}

async function getDocuments(mode) {
  const query = new URLSearchParams({
    mode,
  });

  const response = await fetch(`${API_BASE_URL}/documents?${query.toString()}`);

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Could not load documents.",
    );
  }

  return data;
}

async function deleteDocument(documentId, mode) {
  const query = new URLSearchParams({
    mode,
  });

  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(
      documentId,
    )}?${query.toString()}`,
    {
      method: "DELETE",
    },
  );

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Could not delete the document.",
    );
  }

  return data;
}

async function askQuestion(question, mode = null) {
  const payload = {
    question,
  };

  if (mode) {
    payload.mode = mode;
  }

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    let errorMessage = "Could not generate an answer.";

    if (typeof data?.detail === "string") {
      errorMessage = data.detail;
    } else if (Array.isArray(data?.detail)) {
      errorMessage = data.detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(" ");
    }

    throw new Error(errorMessage);
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

async function updateCompanySettings(settingsPayload) {
  const response = await fetch(
    `${CONFIG_API_BASE_URL}/config/company/settings`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settingsPayload),
    },
  );

  const responseBody = await response.json().catch(() => null);

  if (!response.ok) {
    console.error("Company settings update failed:", responseBody);

    const errorMessage =
      typeof responseBody?.detail === "string"
        ? responseBody.detail
        : "Could not update company settings.";

    throw new Error(errorMessage);
  }

  return responseBody;
}

async function updateAssistantModeSettings(mode, settingsPayload) {
  const response = await fetch(
    `${CONFIG_API_BASE_URL}/config/company/assistants/${encodeURIComponent(
      mode,
    )}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settingsPayload),
    },
  );

  const responseBody = await response.json().catch(() => null);

  if (!response.ok) {
    console.error("Assistant settings update failed:", responseBody);

    let errorMessage = "Could not update assistant settings.";

    if (typeof responseBody?.detail === "string") {
      errorMessage = responseBody.detail;
    } else if (Array.isArray(responseBody?.detail)) {
      errorMessage = responseBody.detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(" ");
    }

    throw new Error(errorMessage);
  }

  return responseBody;
}

async function updateAssistantModeFallbackSettings(mode, payload) {
  const response = await fetch(
    `${CONFIG_API_BASE_URL}/config/company/assistants/${encodeURIComponent(
      mode,
    )}/fallback`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  const responseBody = await response.json().catch(() => null);

  if (!response.ok) {
    console.error("Fallback settings update failed:", responseBody);

    let errorMessage = "Could not update fallback settings.";

    if (typeof responseBody?.detail === "string") {
      errorMessage = responseBody.detail;
    } else if (Array.isArray(responseBody?.detail)) {
      errorMessage = responseBody.detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(" ");
    }

    throw new Error(errorMessage);
  }

  return responseBody;
}

async function updateCompanyBranding(
  brandingPayload,
  { logo = null, favicon = null, assistantAvatar = null } = {},
) {
  const formData = new FormData();

  formData.append("branding_json", JSON.stringify(brandingPayload));

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
    `${CONFIG_API_BASE_URL}/config/company/branding`,
    {
      method: "PUT",
      body: formData,
    },
  );

  const responseBody = await response.json().catch(() => null);

  if (!response.ok) {
    console.error("Company branding update failed:", responseBody);

    let errorMessage = "Could not update company branding.";

    if (typeof responseBody?.detail === "string") {
      errorMessage = responseBody.detail;
    } else if (Array.isArray(responseBody?.detail)) {
      errorMessage = responseBody.detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(" ");
    }

    throw new Error(errorMessage);
  }

  return responseBody;
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
