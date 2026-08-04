let files = [];

const CONFIGURED_BRAND_ASSET_FIELDS = {
  logo: {
    inputId: "configuredLogoInput",
    previewId: "brandingLogoPreview",
    hoverPreviewId: "brandingLogoHoverPreview",
    fallbackId: "brandingLogoFallback",
    hoverFallbackId: "brandingLogoHoverFallback",
    statusId: "brandingLogoStatus",
    removeButtonId: "removeConfiguredLogoFileButton",
  },

  favicon: {
    inputId: "configuredFaviconInput",
    previewId: "brandingFaviconPreview",
    hoverPreviewId: "brandingFaviconHoverPreview",
    fallbackId: "brandingFaviconFallback",
    hoverFallbackId: "brandingFaviconHoverFallback",
    statusId: "brandingFaviconStatus",
    removeButtonId: "removeConfiguredFaviconFileButton",
  },

  assistant_avatar: {
    inputId: "configuredAvatarInput",
    previewId: "brandingAvatarPreview",
    hoverPreviewId: "brandingAvatarHoverPreview",
    fallbackId: "brandingAvatarFallback",
    hoverFallbackId: "brandingAvatarHoverFallback",
    statusId: "brandingAvatarStatus",
    removeButtonId: "removeConfiguredAvatarFileButton",
  },
};

const configuredBrandAssetObjectUrls = {};

async function startAdmin() {
  try {
    await initializeAdmin();

    if (CONFIG_STATUS?.has_active_company === true) {
      initializeUpload();
      initializeAssistantModesPanel();
      initializeCompanySettingsToggle();
      initializeBrandingOverviewToggle();
      populateCompanySettingsForm();
      initializeCompanySettingsForm();
      populateBrandingForm();
      initializeConfiguredBrandingForm();
    } else {
      initializeCompanySetupForm();
      initializeBrandingFields();
      initializeFinishSetupButton();
    }
  } catch (error) {
    console.error("Admin initialization failed:", error);

    document.body.insertAdjacentHTML(
      "afterbegin",
      `
              <div class="notice notice-error">
                Could not load company configuration.
              </div>
            `,
    );
  }
}

async function initializeAdmin() {
  await loadCompanyConfig();

  const hasActiveCompany = CONFIG_STATUS?.has_active_company === true;

  const answerlyHeader = document.getElementById("answerlyHeader");
  const companyTopbar = document.getElementById("companyTopbar");

  const answerlySetupContent = document.getElementById("answerlySetupContent");

  const configuredAdminContent = document.getElementById(
    "configuredAdminContent",
  );

  document.body.classList.toggle("answerly-onboarding", !hasActiveCompany);

  document.body.classList.toggle("company-configured", hasActiveCompany);

  answerlyHeader.hidden = hasActiveCompany;
  companyTopbar.hidden = !hasActiveCompany;

  answerlySetupContent.hidden = hasActiveCompany;
  configuredAdminContent.hidden = !hasActiveCompany;

  if (!hasActiveCompany) {
    document.title = "Answer.ly — Company Setup";
    return;
  }

  const enabledModeKeys = Object.keys(COMPANY_CONFIG.modes).filter(
    (mode) => COMPANY_CONFIG.modes[mode].enabled,
  );

  const enabledModeLabels = enabledModeKeys
    .map((mode) =>
      mode
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" "),
    )
    .join(", ");

  const defaultMode =
    COMPANY_CONFIG.default_mode ||
    enabledModeKeys.find((mode) => COMPANY_CONFIG.modes[mode].default) ||
    enabledModeKeys[0];

  document.title = `${COMPANY_CONFIG.company_name} — Assistant Setup`;

  document.getElementById("welcomeHeadline").textContent =
    `${COMPANY_CONFIG.company_name} Assistant Setup`;

  document.getElementById("welcomeDescription").textContent =
    "Upload company documents and manage how the AI assistant behaves.";

  document.getElementById("companyName").textContent =
    COMPANY_CONFIG.company_name;

  const defaultModeConfig = COMPANY_CONFIG.modes?.[defaultMode] || {};

  const defaultAssistant =
    defaultModeConfig.assistant || COMPANY_CONFIG.assistant || {};

  document.getElementById("assistantName").textContent =
    defaultAssistant.name || "Not configured";

  document.getElementById("assistantMode").textContent =
    enabledModeLabels || "Not configured";

  const showCitations =
    typeof defaultModeConfig.show_citations === "boolean"
      ? defaultModeConfig.show_citations
      : COMPANY_CONFIG.visibility?.[defaultMode]?.show_citations === true;

  document.getElementById("citationMode").textContent = showCitations
    ? "Visible"
    : "Hidden";

  applyBrandLogo(
    document.getElementById("brandLogo"),
    document.getElementById("logoInitial"),
  );
}

function initializeCompanySetupForm() {
  const form = document.getElementById("companySetupForm");

  const extendedSection = document.getElementById("extendedCompanySection");

  const requiredFields = Array.from(form.querySelectorAll("[required]"));

  requiredFields.forEach((field) => {
    const clearInvalidState = () => {
      if (field.checkValidity()) {
        field.classList.remove("field-invalid");
        field.removeAttribute("aria-invalid");
      }
    };

    field.addEventListener("input", clearInvalidState);
    field.addEventListener("change", clearInvalidState);
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    let firstInvalidField = null;

    requiredFields.forEach((field) => {
      const isValid = field.checkValidity();

      field.classList.toggle("field-invalid", !isValid);

      if (!isValid) {
        field.setAttribute("aria-invalid", "true");
        firstInvalidField ??= field;
      } else {
        field.removeAttribute("aria-invalid");
      }
    });

    if (firstInvalidField) {
      window.alert("Please fill out all the fields");
      firstInvalidField.focus();
      return;
    }

    extendedSection.hidden = false;

    extendedSection.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });

  requestAnimationFrame(() => {
    document.getElementById("companyNameInput")?.focus();
  });
}

function initializeBrandingFields() {
  const colorFields = [
    ["primaryColorPicker", "primaryColorText"],
    ["secondaryColorPicker", "secondaryColorText"],
    ["accentColorPicker", "accentColorText"],
    ["backgroundColorPicker", "backgroundColorText"],
    ["textColorPicker", "textColorText"],
  ];

  const hexPattern = /^#[0-9A-Fa-f]{6}$/;

  colorFields.forEach(([pickerId, textId]) => {
    const picker = document.getElementById(pickerId);
    const text = document.getElementById(textId);

    picker.addEventListener("input", () => {
      text.value = picker.value.toUpperCase();
      text.classList.remove("field-invalid");
    });

    text.addEventListener("input", () => {
      const value = text.value.trim();

      if (hexPattern.test(value)) {
        picker.value = value;
        text.value = value.toUpperCase();
        text.classList.remove("field-invalid");
      }
    });

    text.addEventListener("blur", () => {
      const value = text.value.trim();

      if (!hexPattern.test(value)) {
        text.classList.add("field-invalid");
        return;
      }

      text.value = value.toUpperCase();
      picker.value = value;
      text.classList.remove("field-invalid");
    });
  });
}

function initializeFinishSetupButton() {
  const button = document.getElementById("finishSetupButton");
  const notice = document.getElementById("finishSetupNotice");

  button.addEventListener("click", async () => {
    const supportedLanguages = document
      .getElementById("supportedLanguagesInput")
      .value.split(",")
      .map((language) => language.trim())
      .filter(Boolean);

    const setupPayload = {
      company_name: document.getElementById("companyNameInput").value.trim(),
      industry: document.getElementById("industryInput").value.trim(),

      assistant: {
        name: document.getElementById("assistantNameInput").value.trim(),
        title: document.getElementById("assistantTitleInput").value.trim(),
        mode: document.getElementById("assistantModeInput").value,
        default_language: document
          .getElementById("defaultLanguageInput")
          .value.trim(),
        supported_languages: supportedLanguages,
      },

      conversation: {
        tone: document.getElementById("toneInput").value,
        response_length: document.getElementById("responseLengthInput").value,
      },

      company_details: {
        description: document
          .getElementById("companyDescriptionInput")
          .value.trim(),
      },

      branding: {
        colors: {
          primary: document.getElementById("primaryColorText").value.trim(),
          secondary: document.getElementById("secondaryColorText").value.trim(),
          accent: document.getElementById("accentColorText").value.trim(),
          background: document
            .getElementById("backgroundColorText")
            .value.trim(),
          text: document.getElementById("textColorText").value.trim(),
        },
      },
    };

    button.disabled = true;
    button.textContent = "Saving setup...";
    notice.innerHTML = "";

    try {
      const result = await createCompanySetupWithAssets(setupPayload, {
        logo: document.getElementById("companyLogoInput").files[0] || null,
        favicon:
          document.getElementById("companyFaviconInput").files[0] || null,
        assistantAvatar:
          document.getElementById("assistantAvatarInput").files[0] || null,
      });

      console.log("Created company setup:", result);

      notice.innerHTML = `
              <div class="notice notice-success">
                Setup complete. Opening document upload...
              </div>`;

      setTimeout(() => {
        window.location.reload();
      }, 600);
    } catch (error) {
      console.error(error);

      notice.innerHTML = `
        <div class="notice notice-error">
          ${error.message}
        </div>
      `;
    } finally {
      button.disabled = false;
      button.textContent = "Finish setup";
    }
  });
}

function populateCompanySettingsForm() {
  const defaultMode =
    COMPANY_CONFIG.default_mode ||
    Object.keys(COMPANY_CONFIG.modes).find(
      (mode) => COMPANY_CONFIG.modes[mode].default,
    );

  document.getElementById("configuredCompanyNameInput").value =
    COMPANY_CONFIG.company_name || "";

  document.getElementById("configuredIndustryInput").value =
    COMPANY_CONFIG.industry || "";

  document.getElementById("configuredDescriptionInput").value =
    COMPANY_CONFIG.description || "";

  document.getElementById("configuredAssistantNameInput").value =
    COMPANY_CONFIG.assistant.name || "";

  document.getElementById("configuredAssistantTitleInput").value =
    COMPANY_CONFIG.assistant.title || "";

  document.getElementById("configuredAssistantModeInput").value =
    defaultMode || "customer_support";

  document.getElementById("configuredToneInput").value =
    COMPANY_CONFIG.conversation?.tone || "professional";

  document.getElementById("configuredResponseLengthInput").value =
    COMPANY_CONFIG.conversation?.response_length || "concise";

  document.getElementById("configuredDefaultLanguageInput").value =
    COMPANY_CONFIG.assistant.default_language || "English";

  document.getElementById("configuredSupportedLanguagesInput").value =
    COMPANY_CONFIG.assistant.supported_languages?.join(", ") || "English";
}

function buildCompanySettingsPayload() {
  const supportedLanguages = document
    .getElementById("configuredSupportedLanguagesInput")
    .value.split(",")
    .map((language) => language.trim())
    .filter(Boolean);

  return {
    company_name: document
      .getElementById("configuredCompanyNameInput")
      .value.trim(),

    industry: document.getElementById("configuredIndustryInput").value.trim(),

    assistant: {
      name: document
        .getElementById("configuredAssistantNameInput")
        .value.trim(),

      title: document
        .getElementById("configuredAssistantTitleInput")
        .value.trim(),

      mode: document.getElementById("configuredAssistantModeInput").value,

      default_language: document
        .getElementById("configuredDefaultLanguageInput")
        .value.trim(),

      supported_languages: supportedLanguages,
    },

    conversation: {
      tone: document.getElementById("configuredToneInput").value,

      response_length: document.getElementById("configuredResponseLengthInput")
        .value,
    },

    company_details: {
      description: document
        .getElementById("configuredDescriptionInput")
        .value.trim(),
    },
  };
}

function setConfiguredSettingsNotice(type, message) {
  const container = document.getElementById("configuredSettingsNotice");

  const notice = document.createElement("div");

  notice.className = `notice notice-${type}`;
  notice.textContent = message;

  container.replaceChildren(notice);
}

function initializeCompanySettingsForm() {
  const form = document.getElementById("configuredCompanySettingsForm");

  const saveButton = document.getElementById("saveCompanySettingsButton");

  const notice = document.getElementById("configuredSettingsNotice");

  if (!form || !saveButton || !notice) {
    throw new Error("Configured company settings form elements are missing.");
  }

  let initialSnapshot = JSON.stringify(buildCompanySettingsPayload());

  function updateDirtyState() {
    const currentSnapshot = JSON.stringify(buildCompanySettingsPayload());

    saveButton.disabled = currentSnapshot === initialSnapshot;
  }

  form.addEventListener("input", updateDirtyState);
  form.addEventListener("change", updateDirtyState);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const requiredFields = Array.from(form.querySelectorAll("[required]"));

    let firstInvalidField = null;

    requiredFields.forEach((field) => {
      const isValid = field.checkValidity() && field.value.trim().length > 0;

      field.classList.toggle("field-invalid", !isValid);

      if (!isValid) {
        field.setAttribute("aria-invalid", "true");
        firstInvalidField ??= field;
      } else {
        field.removeAttribute("aria-invalid");
      }
    });

    const payload = buildCompanySettingsPayload();

    if (payload.assistant.supported_languages.length === 0) {
      const supportedLanguagesInput = document.getElementById(
        "configuredSupportedLanguagesInput",
      );

      supportedLanguagesInput.classList.add("field-invalid");

      supportedLanguagesInput.setAttribute("aria-invalid", "true");

      firstInvalidField ??= supportedLanguagesInput;
    }

    if (firstInvalidField) {
      setConfiguredSettingsNotice(
        "error",
        "Please fill out all required fields.",
      );

      firstInvalidField.focus();
      return;
    }

    saveButton.disabled = true;
    saveButton.textContent = "Saving...";
    notice.replaceChildren();

    try {
      const result = await updateCompanySettings(payload);

      COMPANY_CONFIG = result.company_config;

      initialSnapshot = JSON.stringify(payload);

      setConfiguredSettingsNotice("success", "Company settings updated.");

      setTimeout(() => {
        window.location.reload();
      }, 600);
    } catch (error) {
      console.error(error);

      setConfiguredSettingsNotice("error", error.message);

      updateDirtyState();
    } finally {
      saveButton.textContent = "Save changes";
    }
  });

  updateDirtyState();
}

function initializeCompanySettingsToggle() {
  const button = document.getElementById("editCompanySettingsButton");

  const content = document.getElementById("companySettingsContent");

  button.addEventListener("click", () => {
    const isOpening = content.hidden;

    content.hidden = !isOpening;
    button.setAttribute("aria-expanded", String(isOpening));
    button.textContent = isOpening ? "Close settings" : "Edit settings";

    if (isOpening) {
      content.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  });
}

function populateBrandingForm() {
  Object.keys(CONFIGURED_BRAND_ASSET_FIELDS).forEach(
    restoreConfiguredBrandAsset,
  );

  const colors = COMPANY_CONFIG.branding?.colors || {};

  const colorValues = {
    Primary: colors.primary,
    Secondary: colors.secondary,
    Accent: colors.accent,
    Background: colors.background,
    Text: colors.text,
  };

  Object.entries(colorValues).forEach(([colorName, value]) => {
    setConfiguredBrandColorValue(colorName, value);
  });
}

function getConfiguredBrandAssetState(assetName) {
  const assets = COMPANY_CONFIG.branding?.assets || {};

  const companyInitial = (COMPANY_CONFIG.company_name || "C")
    .charAt(0)
    .toUpperCase();

  if (assetName === "assistant_avatar") {
    if (assets.assistant_avatar) {
      return {
        sourceAssetName: "assistant_avatar",
        status: "Currently configured",
        fallbackText: companyInitial,
      };
    }

    if (assets.logo) {
      return {
        sourceAssetName: "logo",
        status: "Using company logo fallback",
        fallbackText: companyInitial,
      };
    }

    return {
      sourceAssetName: null,
      status: "Using company initial fallback",
      fallbackText: companyInitial,
    };
  }

  if (assets[assetName]) {
    return {
      sourceAssetName: assetName,
      status: "Currently configured",
      fallbackText: "Not configured",
    };
  }

  return {
    sourceAssetName: null,
    status: "Not configured",
    fallbackText: "Not configured",
  };
}

function setBrandingAssetPreview({
  assetName,
  sourceUrl,
  status,
  fallbackText,
}) {
  const field = CONFIGURED_BRAND_ASSET_FIELDS[assetName];

  const preview = document.getElementById(field.previewId);

  const hoverPreview = document.getElementById(field.hoverPreviewId);

  const fallback = document.getElementById(field.fallbackId);

  const hoverFallback = document.getElementById(field.hoverFallbackId);

  const statusElement = document.getElementById(field.statusId);

  fallback.textContent = fallbackText;
  hoverFallback.textContent = fallbackText;
  statusElement.textContent = status;

  const showFallbacks = () => {
    preview.hidden = true;
    hoverPreview.hidden = true;
    fallback.hidden = false;
    hoverFallback.hidden = false;
  };

  showFallbacks();

  if (!sourceUrl) {
    return;
  }

  preview.onload = () => {
    preview.hidden = false;
    fallback.hidden = true;
  };

  hoverPreview.onload = () => {
    hoverPreview.hidden = false;
    hoverFallback.hidden = true;
  };

  preview.onerror = () => {
    showFallbacks();

    statusElement.textContent = "Preview could not be loaded";
  };

  hoverPreview.onerror = () => {
    hoverPreview.hidden = true;
    hoverFallback.hidden = false;
  };

  preview.src = sourceUrl;
  hoverPreview.src = sourceUrl;
}

function restoreConfiguredBrandAsset(assetName) {
  const field = CONFIGURED_BRAND_ASSET_FIELDS[assetName];

  const state = getConfiguredBrandAssetState(assetName);

  const removeButton = document.getElementById(field.removeButtonId);

  removeButton.hidden = true;

  const sourceUrl = state.sourceAssetName
    ? `${getBrandAssetUrl(state.sourceAssetName)}?version=${Date.now()}`
    : null;

  setBrandingAssetPreview({
    assetName,
    sourceUrl,
    status: state.status,
    fallbackText: state.fallbackText,
  });
}

function showSelectedBrandAsset(assetName, file) {
  const field = CONFIGURED_BRAND_ASSET_FIELDS[assetName];

  const previousObjectUrl = configuredBrandAssetObjectUrls[assetName];

  if (previousObjectUrl) {
    URL.revokeObjectURL(previousObjectUrl);
  }

  const objectUrl = URL.createObjectURL(file);

  configuredBrandAssetObjectUrls[assetName] = objectUrl;

  document.getElementById(field.removeButtonId).hidden = false;

  setBrandingAssetPreview({
    assetName,
    sourceUrl: objectUrl,
    status: `${file.name} selected`,
    fallbackText: "Preview unavailable",
  });
}

function clearConfiguredBrandAssetSelection(assetName) {
  const field = CONFIGURED_BRAND_ASSET_FIELDS[assetName];

  const input = document.getElementById(field.inputId);

  input.value = "";

  const objectUrl = configuredBrandAssetObjectUrls[assetName];

  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);

    delete configuredBrandAssetObjectUrls[assetName];
  }

  restoreConfiguredBrandAsset(assetName);
}

function setConfiguredBrandColorValue(colorName, value) {
  const normalizedValue = value?.toUpperCase() || "#000000";

  const picker = document.getElementById(`configuredBrand${colorName}Picker`);

  const text = document.getElementById(`configuredBrand${colorName}Text`);

  picker.value = normalizedValue;
  text.value = normalizedValue;

  text.classList.remove("field-invalid");
  text.removeAttribute("aria-invalid");
}

function buildBrandingPayload() {
  return {
    colors: {
      primary: document
        .getElementById("configuredBrandPrimaryText")
        .value.trim()
        .toUpperCase(),

      secondary: document
        .getElementById("configuredBrandSecondaryText")
        .value.trim()
        .toUpperCase(),

      accent: document
        .getElementById("configuredBrandAccentText")
        .value.trim()
        .toUpperCase(),

      background: document
        .getElementById("configuredBrandBackgroundText")
        .value.trim()
        .toUpperCase(),

      text: document
        .getElementById("configuredBrandTextText")
        .value.trim()
        .toUpperCase(),
    },
  };
}

function setConfiguredBrandingNotice(type, message) {
  const container = document.getElementById("configuredBrandingNotice");

  const notice = document.createElement("div");

  notice.className = `notice notice-${type}`;
  notice.textContent = message;

  container.replaceChildren(notice);
}

function initializeConfiguredBrandingForm() {
  const form = document.getElementById("configuredBrandingForm");

  const saveButton = document.getElementById("saveBrandingButton");

  const cancelButton = document.getElementById("cancelBrandingChangesButton");

  const notice = document.getElementById("configuredBrandingNotice");

  const colorFields = [
    ["Primary", "configuredBrandPrimaryPicker", "configuredBrandPrimaryText"],
    [
      "Secondary",
      "configuredBrandSecondaryPicker",
      "configuredBrandSecondaryText",
    ],
    ["Accent", "configuredBrandAccentPicker", "configuredBrandAccentText"],
    [
      "Background",
      "configuredBrandBackgroundPicker",
      "configuredBrandBackgroundText",
    ],
    ["Text", "configuredBrandTextPicker", "configuredBrandTextText"],
  ];

  const hexPattern = /^#[0-9A-Fa-f]{6}$/;

  const initialPayload = JSON.parse(JSON.stringify(buildBrandingPayload()));

  let initialSnapshot = JSON.stringify(initialPayload);

  function hasSelectedFiles() {
    return Object.values(CONFIGURED_BRAND_ASSET_FIELDS).some((field) => {
      const input = document.getElementById(field.inputId);

      return input.files.length > 0;
    });
  }

  function updateDirtyState() {
    const currentSnapshot = JSON.stringify(buildBrandingPayload());

    const isDirty = currentSnapshot !== initialSnapshot || hasSelectedFiles();

    saveButton.disabled = !isDirty;
    cancelButton.disabled = !isDirty;
  }

  colorFields.forEach(([, pickerId, textId]) => {
    const picker = document.getElementById(pickerId);

    const text = document.getElementById(textId);

    picker.addEventListener("input", () => {
      text.value = picker.value.toUpperCase();

      text.classList.remove("field-invalid");

      text.removeAttribute("aria-invalid");

      updateDirtyState();
    });

    text.addEventListener("input", () => {
      const value = text.value.trim();

      if (hexPattern.test(value)) {
        picker.value = value;

        text.classList.remove("field-invalid");

        text.removeAttribute("aria-invalid");
      }

      updateDirtyState();
    });

    text.addEventListener("blur", () => {
      const value = text.value.trim();

      if (!hexPattern.test(value)) {
        text.classList.add("field-invalid");

        text.setAttribute("aria-invalid", "true");

        return;
      }

      text.value = value.toUpperCase();
      picker.value = value;

      text.classList.remove("field-invalid");

      text.removeAttribute("aria-invalid");

      updateDirtyState();
    });
  });

  Object.entries(CONFIGURED_BRAND_ASSET_FIELDS).forEach(
    ([assetName, field]) => {
      const input = document.getElementById(field.inputId);

      const removeButton = document.getElementById(field.removeButtonId);

      input.addEventListener("change", () => {
        const selectedFile = input.files[0];

        if (selectedFile) {
          showSelectedBrandAsset(assetName, selectedFile);
        } else {
          clearConfiguredBrandAssetSelection(assetName);
        }

        notice.replaceChildren();
        updateDirtyState();
      });

      removeButton.addEventListener("click", () => {
        clearConfiguredBrandAssetSelection(assetName);

        notice.replaceChildren();
        updateDirtyState();
      });
    },
  );

  cancelButton.addEventListener("click", () => {
    Object.keys(CONFIGURED_BRAND_ASSET_FIELDS).forEach(
      clearConfiguredBrandAssetSelection,
    );

    Object.entries(initialPayload.colors).forEach(([colorName, value]) => {
      const formattedName =
        colorName.charAt(0).toUpperCase() + colorName.slice(1);

      setConfiguredBrandColorValue(formattedName, value);
    });

    notice.replaceChildren();
    updateDirtyState();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    let firstInvalidField = null;

    colorFields.forEach(([, , textId]) => {
      const text = document.getElementById(textId);

      const isValid = hexPattern.test(text.value.trim());

      text.classList.toggle("field-invalid", !isValid);

      if (!isValid) {
        text.setAttribute("aria-invalid", "true");

        firstInvalidField ??= text;
      } else {
        text.removeAttribute("aria-invalid");
      }
    });

    if (firstInvalidField) {
      setConfiguredBrandingNotice(
        "error",
        "Enter valid six-digit hexadecimal colours.",
      );

      firstInvalidField.focus();
      return;
    }

    const payload = buildBrandingPayload();

    saveButton.disabled = true;
    cancelButton.disabled = true;
    saveButton.textContent = "Saving...";

    notice.replaceChildren();

    try {
      const result = await updateCompanyBranding(payload, {
        logo: document.getElementById("configuredLogoInput").files[0] || null,

        favicon:
          document.getElementById("configuredFaviconInput").files[0] || null,

        assistantAvatar:
          document.getElementById("configuredAvatarInput").files[0] || null,
      });

      COMPANY_CONFIG = result.company_config;

      initialSnapshot = JSON.stringify(payload);

      setConfiguredBrandingNotice("success", "Branding updated.");

      setTimeout(() => {
        window.location.reload();
      }, 600);
    } catch (error) {
      console.error(error);

      setConfiguredBrandingNotice("error", error.message);

      updateDirtyState();
    } finally {
      saveButton.textContent = "Save branding";
    }
  });

  updateDirtyState();
}

function initializeBrandingOverviewToggle() {
  const button = document.getElementById("editBrandingButton");
  const content = document.getElementById("brandingOverviewContent");

  button.addEventListener("click", () => {
    const isOpening = content.hidden;

    content.hidden = !isOpening;
    button.setAttribute("aria-expanded", String(isOpening));
    button.textContent = isOpening ? "Close branding" : "Edit branding";

    if (isOpening) {
      content.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  });
}

function initializeUpload() {
  const uploadZone = document.getElementById("uploadZone");
  const fileInput = document.getElementById("fileInput");
  const selectedFiles = document.getElementById("selectedFiles");
  const selectedFileRows = document.getElementById("selectedFileRows");
  const processButton = document.getElementById("processButton");
  const clearButton = document.getElementById("clearButton");
  const uploadNotice = document.getElementById("uploadNotice");
  const indexedDocuments = document.getElementById("indexedDocuments");
  const indexedFileRows = document.getElementById("indexedFileRows");

  let dragCounter = 0;

  document.body.addEventListener(
    "dragover",
    (event) => {
      event.preventDefault();
    },
    false,
  );

  document.body.addEventListener(
    "drop",
    (event) => {
      if (!uploadZone.contains(event.target)) {
        event.preventDefault();
      }
    },
    false,
  );

  uploadZone.addEventListener("dragenter", (event) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter += 1;
    uploadZone.classList.add("drag-over");
  });

  uploadZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    event.stopPropagation();

    uploadZone.classList.add("drag-over");
  });

  uploadZone.addEventListener("dragleave", (event) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter -= 1;

    if (dragCounter <= 0) {
      dragCounter = 0;
      uploadZone.classList.remove("drag-over");
    }
  });

  uploadZone.addEventListener("drop", (event) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter = 0;
    uploadZone.classList.remove("drag-over");

    console.log("Upload drop:", event.dataTransfer.files);

    addFiles(event.dataTransfer.files);

    setNotice(
      "success",
      `${event.dataTransfer.files.length} file(s) selected.`,
    );
  });

  fileInput.addEventListener("change", (event) => {
    addFiles(event.target.files);
  });

  clearButton.addEventListener("click", () => {
    files = [];
    fileInput.value = "";
    uploadNotice.innerHTML = "";

    renderSelectedFiles();
  });

  processButton.addEventListener("click", async () => {
    if (files.length === 0) {
      setNotice("error", "Choose at least one document first.");
      return;
    }

    processButton.disabled = true;
    processButton.textContent = "Processing documents...";

    setNotice("success", "Uploading and indexing documents...");

    try {
      const result = await uploadDocuments(files);

      storeUploadSummary(result);

      setNotice(
        "success",
        `${result.files_processed} documents indexed successfully. You can now open the chat.`,
      );

      renderIndexedFiles(result.results);
    } catch (error) {
      setNotice("error", error.message);
    } finally {
      processButton.disabled = false;
      processButton.textContent = "Process documents";
    }
  });

  function renderSelectedFiles() {
    selectedFileRows.innerHTML = "";

    if (files.length === 0) {
      selectedFiles.hidden = true;
      return;
    }

    selectedFiles.hidden = false;

    files.forEach((file, index) => {
      const row = document.createElement("div");

      row.className = "file-row";

      row.innerHTML = `
              <div>
                <strong>${file.name}</strong>
                <div class="file-meta">${formatBytes(file.size)}</div>
              </div>

              <button
                class="remove-btn"
                type="button"
                data-index="${index}"
              >
                Remove
              </button>
            `;

      selectedFileRows.appendChild(row);
    });

    document.querySelectorAll(".remove-btn").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number(button.dataset.index);

        files.splice(index, 1);
        renderSelectedFiles();
      });
    });
  }

  function setNotice(type, message) {
    uploadNotice.innerHTML = `
            <div class="notice notice-${type}">
              ${message}
            </div>
          `;
  }

  function renderIndexedFiles(results) {
    indexedFileRows.innerHTML = "";

    results.forEach((result) => {
      const row = document.createElement("div");

      row.className = "file-row";

      row.innerHTML = `
              <div>
                <strong>${result.filename}</strong>

                <div class="file-meta">
                  ${result.documents_loaded} document loaded
                </div>
              </div>

              <span class="badge badge-success">
                Indexed
              </span>
            `;

      indexedFileRows.appendChild(row);
    });

    indexedDocuments.hidden = false;
  }

  function formatBytes(bytes) {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function addFiles(fileList) {
    const accepted = Array.from(fileList).filter((file) => {
      const name = file.name.toLowerCase();

      return (
        name.endsWith(".pdf") || name.endsWith(".txt") || name.endsWith(".md")
      );
    });

    files = [...files, ...accepted];

    renderSelectedFiles();

    if (accepted.length !== fileList.length) {
      setNotice(
        "error",
        "Some files were skipped. Only PDF, TXT, and MD files are supported.",
      );
    }
  }
}

startAdmin();
