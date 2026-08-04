const ASSISTANT_MODE_FIELDS = [
  {
    mode: "customer_support",
    enabledInputId: "customerSupportEnabledInput",
    defaultInputId: "customerSupportDefaultInput",
  },
  {
    mode: "internal_knowledge",
    enabledInputId: "internalKnowledgeEnabledInput",
    defaultInputId: "internalKnowledgeDefaultInput",
  },
];

function getConfiguredDefaultAssistantMode() {
  const configuredDefault = COMPANY_CONFIG?.default_mode;

  if (
    configuredDefault &&
    COMPANY_CONFIG?.modes?.[configuredDefault]?.enabled === true
  ) {
    return configuredDefault;
  }

  const defaultFlagMode = ASSISTANT_MODE_FIELDS.find(
    ({ mode }) => COMPANY_CONFIG?.modes?.[mode]?.default === true,
  );

  if (defaultFlagMode) {
    return defaultFlagMode.mode;
  }

  const firstEnabledMode = ASSISTANT_MODE_FIELDS.find(
    ({ mode }) => COMPANY_CONFIG?.modes?.[mode]?.enabled === true,
  );

  return firstEnabledMode?.mode || null;
}

function buildAssistantModesPayload() {
  const enabledModes = ASSISTANT_MODE_FIELDS.filter(
    ({ enabledInputId }) => document.getElementById(enabledInputId).checked,
  ).map(({ mode }) => mode);

  const checkedDefault = ASSISTANT_MODE_FIELDS.find(
    ({ defaultInputId }) => document.getElementById(defaultInputId).checked,
  );

  return {
    enabledModes,
    defaultMode: checkedDefault?.mode || null,
  };
}

function populateAssistantModesForm() {
  const defaultMode = getConfiguredDefaultAssistantMode();

  ASSISTANT_MODE_FIELDS.forEach(({ mode, enabledInputId, defaultInputId }) => {
    const enabledInput = document.getElementById(enabledInputId);

    const defaultInput = document.getElementById(defaultInputId);

    const isEnabled = COMPANY_CONFIG?.modes?.[mode]?.enabled === true;

    enabledInput.checked = isEnabled;
    defaultInput.checked = isEnabled && mode === defaultMode;

    defaultInput.disabled = !isEnabled;
  });
}

function setAssistantModesNotice(type, message) {
  const container = document.getElementById("assistantModesNotice");

  const notice = document.createElement("div");

  notice.className = `notice notice-${type}`;
  notice.textContent = message;

  container.replaceChildren(notice);
}

function initializeAssistantModesPanel() {
  const form = document.getElementById("assistantModesForm");

  const saveButton = document.getElementById("saveAssistantModesButton");

  const notice = document.getElementById("assistantModesNotice");

  if (!form || !saveButton || !notice) {
    throw new Error("Assistant mode form elements are missing.");
  }

  populateAssistantModesForm();

  let initialSnapshot = JSON.stringify(buildAssistantModesPayload());

  function synchronizeDefaultSelection(changedMode = null) {
    ASSISTANT_MODE_FIELDS.forEach(({ enabledInputId, defaultInputId }) => {
      const enabledInput = document.getElementById(enabledInputId);

      const defaultInput = document.getElementById(defaultInputId);

      defaultInput.disabled = !enabledInput.checked;

      if (!enabledInput.checked) {
        defaultInput.checked = false;
      }
    });

    const current = buildAssistantModesPayload();

    if (
      current.defaultMode &&
      current.enabledModes.includes(current.defaultMode)
    ) {
      return;
    }

    const preferredField = ASSISTANT_MODE_FIELDS.find(
      ({ mode, enabledInputId }) =>
        mode === changedMode && document.getElementById(enabledInputId).checked,
    );

    const fallbackField =
      preferredField ||
      ASSISTANT_MODE_FIELDS.find(
        ({ enabledInputId }) => document.getElementById(enabledInputId).checked,
      );

    if (fallbackField) {
      document.getElementById(fallbackField.defaultInputId).checked = true;
    }
  }

  function updateDirtyState() {
    const currentSnapshot = JSON.stringify(buildAssistantModesPayload());

    saveButton.disabled = currentSnapshot === initialSnapshot;
  }

  ASSISTANT_MODE_FIELDS.forEach(({ mode, enabledInputId, defaultInputId }) => {
    const enabledInput = document.getElementById(enabledInputId);

    const defaultInput = document.getElementById(defaultInputId);

    enabledInput.addEventListener("change", () => {
      synchronizeDefaultSelection(mode);
      notice.replaceChildren();
      updateDirtyState();
    });

    defaultInput.addEventListener("change", () => {
      notice.replaceChildren();
      updateDirtyState();
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = buildAssistantModesPayload();

    if (payload.enabledModes.length === 0) {
      setAssistantModesNotice("error", "Enable at least one assistant mode.");

      return;
    }

    if (
      !payload.defaultMode ||
      !payload.enabledModes.includes(payload.defaultMode)
    ) {
      setAssistantModesNotice(
        "error",
        "Choose an enabled assistant as the default.",
      );

      return;
    }

    saveButton.disabled = true;
    saveButton.textContent = "Saving...";
    notice.replaceChildren();

    try {
      const result = await updateAssistantModes(
        payload.enabledModes,
        payload.defaultMode,
      );

      COMPANY_CONFIG.modes = result.modes;
      COMPANY_CONFIG.default_mode = result.default_mode;

      populateAssistantModesForm();

      initialSnapshot = JSON.stringify(buildAssistantModesPayload());

      setAssistantModesNotice("success", "Assistant mode settings updated.");

      setTimeout(() => {
        window.location.reload();
      }, 600);
    } catch (error) {
      console.error(error);

      setAssistantModesNotice("error", error.message);

      updateDirtyState();
    } finally {
      saveButton.textContent = "Save mode settings";
    }
  });

  synchronizeDefaultSelection();
  updateDirtyState();
}
