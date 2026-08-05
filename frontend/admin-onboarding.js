const ONBOARDING_ASSISTANT_FIELDS = {
  customer_support: {
    sectionId: "customerSupportSetupSection",
    assistantNameId: "customerSupportAssistantNameInput",
    chatNameId: "customerSupportChatNameInput",
    contactEmailId: "customerSupportEmailInput",
    contactPhoneId: "customerSupportPhoneInput",
  },

  internal_knowledge: {
    sectionId: "internalKnowledgeSetupSection",
    assistantNameId: "internalKnowledgeAssistantNameInput",
    chatNameId: "internalKnowledgeChatNameInput",
    contactEmailId: "internalKnowledgeEmailInput",
    contactPhoneId: "internalKnowledgePhoneInput",
  },
};

function setOnboardingNotice(type, message) {
  const container = document.getElementById("companyFormNotice");

  const notice = document.createElement("div");

  notice.className = `notice notice-${type}`;
  notice.textContent = message;

  container.replaceChildren(notice);
}

function configureOnboardingAssistantSections(availableModes) {
  Object.entries(ONBOARDING_ASSISTANT_FIELDS).forEach(([mode, fields]) => {
    const isAvailable = availableModes.includes(mode);

    const section = document.getElementById(fields.sectionId);

    section.hidden = !isAvailable;

    const assistantNameInput = document.getElementById(fields.assistantNameId);

    const chatNameInput = document.getElementById(fields.chatNameId);

    const contactEmailInput = document.getElementById(fields.contactEmailId);

    const contactPhoneInput = document.getElementById(fields.contactPhoneId);

    [
      assistantNameInput,
      chatNameInput,
      contactEmailInput,
      contactPhoneInput,
    ].forEach((input) => {
      input.disabled = !isAvailable;
    });

    assistantNameInput.required = isAvailable;
    chatNameInput.required = isAvailable;
  });
}

function buildInitialCompanySetupPayload(availableModes) {
  const payload = {
    company_name: document.getElementById("companyNameInput").value.trim(),

    industry: document.getElementById("industryInput").value.trim(),
  };

  availableModes.forEach((mode) => {
    const fields = ONBOARDING_ASSISTANT_FIELDS[mode];

    payload[mode] = {
      assistant_name: document
        .getElementById(fields.assistantNameId)
        .value.trim(),

      chat_name: document.getElementById(fields.chatNameId).value.trim(),

      contact_email: document
        .getElementById(fields.contactEmailId)
        .value.trim(),

      contact_phone: document
        .getElementById(fields.contactPhoneId)
        .value.trim(),
    };
  });

  return payload;
}

function initializeCompanyOnboarding() {
  const form = document.getElementById("companySetupForm");

  const submitButton = document.getElementById("finishSetupButton");

  const notice = document.getElementById("companyFormNotice");

  const availableModes = CONFIG_STATUS?.available_modes || [];

  if (!form || !submitButton || !notice) {
    throw new Error("Company onboarding form elements are missing.");
  }

  if (availableModes.length === 0) {
    throw new Error("No assistant modes are provisioned.");
  }

  const unsupportedMode = availableModes.find(
    (mode) => !ONBOARDING_ASSISTANT_FIELDS[mode],
  );

  if (unsupportedMode) {
    throw new Error(`Unsupported provisioned mode: ${unsupportedMode}.`);
  }

  configureOnboardingAssistantSections(availableModes);

  const formFields = Array.from(form.querySelectorAll("input:not([disabled])"));

  formFields.forEach((field) => {
    const clearInvalidState = () => {
      if (field.checkValidity()) {
        field.classList.remove("field-invalid");

        field.removeAttribute("aria-invalid");
      }
    };

    field.addEventListener("input", clearInvalidState);

    field.addEventListener("change", clearInvalidState);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const activeFields = Array.from(
      form.querySelectorAll("input:not([disabled])"),
    );

    let firstInvalidField = null;

    activeFields.forEach((field) => {
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
      setOnboardingNotice("error", "Please check the highlighted fields.");

      firstInvalidField.focus();
      return;
    }

    const payload = buildInitialCompanySetupPayload(availableModes);

    submitButton.disabled = true;
    submitButton.textContent = "Saving setup...";

    notice.replaceChildren();

    try {
      await createCompanySetupWithAssets(payload);

      setOnboardingNotice(
        "success",
        "Setup complete. Opening the admin page...",
      );

      setTimeout(() => {
        window.location.reload();
      }, 600);
    } catch (error) {
      console.error(error);

      setOnboardingNotice("error", error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Finish setup";
    }
  });

  requestAnimationFrame(() => {
    document.getElementById("companyNameInput")?.focus();
  });
}
