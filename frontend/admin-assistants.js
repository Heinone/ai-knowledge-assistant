let assistantDocumentDragGuardsInitialized = false;

const ASSISTANT_MODE_PRESENTATION = {
  customer_support: {
    title: "Customer service assistant",
    defaultChatName: "Customer Service",
    documentDescription:
      "Upload customer-facing product, policy, service, and support information.",
  },

  internal_knowledge: {
    title: "Internal knowledge assistant",
    defaultChatName: "Internal Knowledge",
    documentDescription:
      "Upload internal policies, procedures, guides, and company information.",
  },
};

function getAssistantModePresentation(mode) {
  const presentation = ASSISTANT_MODE_PRESENTATION[mode];

  if (!presentation) {
    throw new Error(`Unsupported assistant mode: ${mode}.`);
  }

  return presentation;
}

function formatDocumentBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function initializeAssistantDocumentDragGuards() {
  if (assistantDocumentDragGuardsInitialized) {
    return;
  }

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
      event.preventDefault();
    },
    false,
  );

  assistantDocumentDragGuardsInitialized = true;
}

function createAssistantCard(mode) {
  const presentation = getAssistantModePresentation(mode);

  const modeConfig = COMPANY_CONFIG.modes?.[mode] || {};

  const assistant = modeConfig.assistant || {};

  const card = document.createElement("article");

  const contentId = `${mode}AssistantCardContent`;
  const fileInputId = `${mode}DocumentFileInput`;
  const assistantNameInputId = `${mode}AssistantNameInput`;
  const chatNameInputId = `${mode}ChatNameInput`;
  const toneInputId = `${mode}ToneInput`;
  const responseLengthInputId = `${mode}ResponseLengthInput`;
  const defaultLanguageInputId = `${mode}DefaultLanguageInput`;
  const supportedLanguagesInputId = `${mode}SupportedLanguagesInput`;
  const greetingEnabledInputId = `${mode}GreetingEnabledInput`;
  const greetingMessageInputId = `${mode}GreetingMessageInput`;
  const contactEmailInputId = `${mode}ContactEmailInput`;
  const contactPhoneInputId = `${mode}ContactPhoneInput`;
  const fallbackBaseMessageInputId = `${mode}FallbackBaseMessageInput`;
  const includeEmailInputId = `${mode}IncludeEmailInput`;
  const includePhoneInputId = `${mode}IncludePhoneInput`;
  const showCitationsInputId = `${mode}ShowCitationsInput`;
  const testQuestionInputId = `${mode}TestQuestionInput`;

  const contactLabel =
    mode === "internal_knowledge" ? "Helpdesk" : "Customer service";

  const citationFieldMarkup =
    mode === "internal_knowledge"
      ? `
        <div
          class="configured-form-field assistant-citation-field"
        >
          <label
            class="assistant-checkbox-control"
            for="${showCitationsInputId}"
          >
            <input
              id="${showCitationsInputId}"
              data-role="show-citations-input"
              type="checkbox"
            />

            <span>
              <strong>Show citations</strong>

              <small>
                Display document sources with internal answers.
              </small>
            </span>
          </label>
        </div>
      `
      : "";

  card.className = "card assistant-admin-card";
  card.dataset.assistantMode = mode;

  card.innerHTML = `
    <div class="assistant-card-header">
      <div class="assistant-card-heading">
        <h2>${presentation.title}</h2>

        <p data-role="card-summary">
          Loading documents...
        </p>
      </div>

      <button
        class="btn btn-secondary"
        type="button"
        data-role="toggle"
        aria-expanded="false"
        aria-controls="${contentId}"
      >
        Edit settings
      </button>
    </div>

    <div
      id="${contentId}"
      class="assistant-card-content"
      data-role="content"
      hidden
    >
<details class="assistant-section-disclosure">
  <summary class="assistant-section-summary">
    <span>
      <strong>Assistant settings</strong>

      <small>
        Configure this assistant's identity, chat name,
        communication style, and languages.
      </small>
    </span>
  </summary>

  <section class="assistant-section-panel assistant-settings-section">
    <form data-role="assistant-settings-form" novalidate>
      <div class="assistant-settings-grid">
        <div class="configured-form-field">
          <label for="${assistantNameInputId}">
            Assistant name
          </label>

          <input
            id="${assistantNameInputId}"
            data-role="assistant-name-input"
            type="text"
            required
          />
        </div>

        <div class="configured-form-field">
          <label for="${chatNameInputId}">
            Chat name
          </label>

          <input
            id="${chatNameInputId}"
            data-role="chat-name-input"
            type="text"
            required
          />
        </div>

        <div class="configured-form-field">
          <label for="${toneInputId}">
            Tone
          </label>

          <select
            id="${toneInputId}"
            data-role="tone-input"
            required
          >
            <option value="friendly">Friendly</option>
            <option value="professional">Professional</option>
            <option value="formal">Formal</option>
          </select>
        </div>

        <div class="configured-form-field">
          <label for="${responseLengthInputId}">
            Response length
          </label>

          <select
            id="${responseLengthInputId}"
            data-role="response-length-input"
            required
          >
            <option value="concise">Concise</option>
            <option value="balanced">Balanced</option>
            <option value="detailed">Detailed</option>
          </select>
        </div>

        <div class="configured-form-field">
          <label for="${defaultLanguageInputId}">
            Default language
          </label>

          <input
            id="${defaultLanguageInputId}"
            data-role="default-language-input"
            type="text"
            required
          />
        </div>

        <div class="configured-form-field">
          <label for="${supportedLanguagesInputId}">
            Supported languages
          </label>

          <input
            id="${supportedLanguagesInputId}"
            data-role="supported-languages-input"
            type="text"
            required
          />

          <small>
            Separate multiple languages with commas.
          </small>
        </div>
        <div class="configured-form-field assistant-citation-field">
  <label
    class="assistant-checkbox-control"
    for="${greetingEnabledInputId}"
  >
    <input
      id="${greetingEnabledInputId}"
      data-role="greeting-enabled-input"
      type="checkbox"
    />

    <span>
      <strong>Show greeting</strong>

      <small>
        Display a greeting when the chat opens.
      </small>
    </span>
  </label>
</div>

<div
  class="configured-form-field assistant-citation-field"
>
  <label for="${greetingMessageInputId}">
    Greeting message
  </label>

  <textarea
    id="${greetingMessageInputId}"
    data-role="greeting-message-input"
    rows="3"
    maxlength="500"
  ></textarea>
</div>
        ${citationFieldMarkup}
      </div>

      <div class="configured-settings-actions">
        <div data-role="assistant-settings-notice"></div>

        <button
          class="btn"
          data-role="save-assistant-settings"
          type="submit"
          disabled
        >
          Save assistant settings
        </button>
      </div>
    </form>
  </section>
</details>

<details class="assistant-section-disclosure">
  <summary class="assistant-section-summary">
    <span>
      <strong>Fallback and contacts</strong>

      <small>
        Configure what the assistant says when it cannot
        find a grounded answer.
      </small>
    </span>
  </summary>

  <section class="assistant-section-panel assistant-fallback-section">
    <form data-role="fallback-settings-form">
      <div class="assistant-settings-grid">
        <div class="configured-form-field">
          <label for="${contactEmailInputId}">
            ${contactLabel} email
          </label>

          <input
            id="${contactEmailInputId}"
            data-role="contact-email-input"
            type="email"
            inputmode="email"
            autocomplete="email"
            maxlength="254"
            placeholder="support@example.com"
          />

          <small>
            Enter a valid email address.
          </small>
        </div>

        <div class="configured-form-field">
          <label for="${contactPhoneInputId}">
            ${contactLabel} phone number
          </label>

          <input
            id="${contactPhoneInputId}"
            data-role="contact-phone-input"
            type="tel"
            inputmode="tel"
            autocomplete="tel"
            maxlength="25"
            pattern="[+]?[0-9][0-9 ().-]{6,24}"
            title="Enter a valid phone number, for example +358 40 123 4567."
            placeholder="+358 40 123 4567"
          />

          <small>
            Use digits and an optional international prefix.
          </small>
        </div>

        <div
          class="configured-form-field assistant-fallback-message-field"
        >
          <label for="${fallbackBaseMessageInputId}">
            Base fallback message
          </label>

          <textarea
            id="${fallbackBaseMessageInputId}"
            data-role="fallback-base-message-input"
            rows="4"
            required
          ></textarea>
        </div>
      </div>

      <div class="assistant-fallback-options">
        <label>
          <input
            id="${includeEmailInputId}"
            data-role="include-email-input"
            type="checkbox"
          />

          Include email in fallback
        </label>

        <label>
          <input
            id="${includePhoneInputId}"
            data-role="include-phone-input"
            type="checkbox"
          />

          Include phone in fallback
        </label>
      </div>

      <div class="assistant-fallback-preview">
        <span>Fallback preview</span>

        <p data-role="fallback-preview"></p>
      </div>

      <div class="configured-settings-actions">
        <div data-role="fallback-settings-notice"></div>

        <button
          class="btn"
          data-role="save-fallback-settings"
          type="submit"
          disabled
        >
          Save fallback settings
        </button>
      </div>
    </form>
  </section>
</details>

      <details class="assistant-section-disclosure">
  <summary class="assistant-section-summary">
    <span>
      <strong>Knowledge documents</strong>

      <small>
        ${presentation.documentDescription}
      </small>
    </span>
  </summary>

  <section class="assistant-section-panel assistant-knowledge-section">

        <div
          class="upload-zone"
          data-role="upload-zone"
        >
          <strong>Drag and drop files here</strong>

          <span>
            or choose files from your computer
          </span>

          <div
            class="button-row"
            style="justify-content: center"
          >
            <label
              class="btn btn-secondary"
              for="${fileInputId}"
            >
              Choose files
            </label>
          </div>

          <input
            id="${fileInputId}"
            class="file-input"
            data-role="file-input"
            type="file"
            multiple
            accept=".pdf,.txt,.md"
          />

          <div class="format-row">
            <span class="format-chip">PDF</span>
            <span class="format-chip">TXT</span>
            <span class="format-chip">MD</span>
          </div>
        </div>

        <div
          class="file-list"
          data-role="selected-files"
          hidden
        >
          <h3>Selected files</h3>

          <div data-role="selected-file-rows"></div>

          <div class="button-row">
            <button
              class="btn"
              type="button"
              data-role="process-button"
            >
              Process documents
            </button>

            <button
              class="btn btn-secondary"
              type="button"
              data-role="clear-button"
            >
              Clear selection
            </button>
          </div>
        </div>

        <div data-role="upload-notice"></div>

        <div
          class="file-list"
          data-role="indexed-documents"
        >
          <h3>Current documents</h3>

          <div data-role="indexed-file-rows">
            <p class="file-meta">
              Loading documents...
            </p>
          </div>
        </div>
      </section>
      </details>
      <details class="assistant-section-disclosure">
  <summary class="assistant-section-summary">
    <span>
      <strong>Test assistant</strong>

      <small>
        Ask a question using this assistant's
        knowledge documents and configuration.
      </small>
    </span>
  </summary>

  <section class="assistant-section-panel assistant-test-section">

        <form
          class="assistant-test-form"
          data-role="test-chat-form"
          novalidate
        >
          <div class="configured-form-field">
            <label for="${testQuestionInputId}">
              Test question
            </label>

            <textarea
              id="${testQuestionInputId}"
              data-role="test-question-input"
              rows="3"
              maxlength="8000"
              required
              placeholder="Ask a question..."
            ></textarea>
          </div>

          <div class="assistant-test-actions">
            <button
              class="btn"
              data-role="test-question-button"
              type="submit"
            >
              Ask assistant
            </button>
          </div>
        </form>

        <div data-role="test-chat-notice"></div>

        <div
          class="assistant-test-result"
          data-role="test-chat-result"
          hidden
        >
          <div class="assistant-test-answer">
            <span>Answer</span>

            <p data-role="test-answer"></p>
          </div>

          <div class="assistant-test-sources">
            <span>Retrieved sources</span>

            <small>
              These are visible here for admin verification,
              even when customer citations are hidden.
            </small>

            <div data-role="test-sources"></div>
          </div>
        </div>
        </section>
      </details>
    </div>
  `;
  return card;
}

async function initializeAssistantCard(card, mode) {
  const toggleButton = card.querySelector('[data-role="toggle"]');
  const content = card.querySelector('[data-role="content"]');
  const cardSummary = card.querySelector('[data-role="card-summary"]');

  const uploadZone = card.querySelector('[data-role="upload-zone"]');
  const fileInput = card.querySelector('[data-role="file-input"]');

  const selectedFilesContainer = card.querySelector(
    '[data-role="selected-files"]',
  );

  const selectedFileRows = card.querySelector(
    '[data-role="selected-file-rows"]',
  );

  const processButton = card.querySelector('[data-role="process-button"]');
  const clearButton = card.querySelector('[data-role="clear-button"]');
  const uploadNotice = card.querySelector('[data-role="upload-notice"]');

  const indexedFileRows = card.querySelector('[data-role="indexed-file-rows"]');

  const assistantSettingsForm = card.querySelector(
    '[data-role="assistant-settings-form"]',
  );

  const assistantNameInput = card.querySelector(
    '[data-role="assistant-name-input"]',
  );

  const chatNameInput = card.querySelector('[data-role="chat-name-input"]');

  const toneInput = card.querySelector('[data-role="tone-input"]');

  const responseLengthInput = card.querySelector(
    '[data-role="response-length-input"]',
  );

  const defaultLanguageInput = card.querySelector(
    '[data-role="default-language-input"]',
  );

  const supportedLanguagesInput = card.querySelector(
    '[data-role="supported-languages-input"]',
  );

  const greetingEnabledInput = card.querySelector(
  '[data-role="greeting-enabled-input"]',
  );

  const greetingMessageInput = card.querySelector(
    '[data-role="greeting-message-input"]',
  );

  const assistantSettingsNotice = card.querySelector(
    '[data-role="assistant-settings-notice"]',
  );

  const saveAssistantSettingsButton = card.querySelector(
    '[data-role="save-assistant-settings"]',
  );

  const showCitationsInput = card.querySelector(
    '[data-role="show-citations-input"]',
  );

  const fallbackSettingsForm = card.querySelector(
    '[data-role="fallback-settings-form"]',
  );

  const contactEmailInput = card.querySelector(
    '[data-role="contact-email-input"]',
  );

  const contactPhoneInput = card.querySelector(
    '[data-role="contact-phone-input"]',
  );

  const fallbackBaseMessageInput = card.querySelector(
    '[data-role="fallback-base-message-input"]',
  );

  const includeEmailInput = card.querySelector(
    '[data-role="include-email-input"]',
  );

  const includePhoneInput = card.querySelector(
    '[data-role="include-phone-input"]',
  );

  const fallbackPreview = card.querySelector('[data-role="fallback-preview"]');

  const fallbackSettingsNotice = card.querySelector(
    '[data-role="fallback-settings-notice"]',
  );

  const saveFallbackSettingsButton = card.querySelector(
    '[data-role="save-fallback-settings"]',
  );

  const testChatForm = card.querySelector('[data-role="test-chat-form"]');

  const testQuestionInput = card.querySelector(
    '[data-role="test-question-input"]',
  );

  const testQuestionButton = card.querySelector(
    '[data-role="test-question-button"]',
  );

  const testChatNotice = card.querySelector('[data-role="test-chat-notice"]');

  const testChatResult = card.querySelector('[data-role="test-chat-result"]');

  const testAnswer = card.querySelector('[data-role="test-answer"]');

  const testSources = card.querySelector('[data-role="test-sources"]');

  let currentModeConfig = COMPANY_CONFIG.modes?.[mode] || {};

  let selectedFiles = [];
  let dragCounter = 0;
  let documentsLoading = false;

  function getSupportedSelectValue(value, supportedValues, fallbackValue) {
    if (supportedValues.includes(value)) {
      return value;
    }

    return fallbackValue;
  }

  function populateAssistantSettingsForm() {
    const assistant = currentModeConfig.assistant || {};
    const conversation = currentModeConfig.conversation || {};
    const chat = currentModeConfig.chat || {};

    assistantNameInput.value = assistant.name || "";

    chatNameInput.value =
      currentModeConfig.display_name ||
      chat.chat_headline ||
      getAssistantModePresentation(mode).defaultChatName;

    const normalizedTone =
      conversation.tone === "friendly and helpful"
        ? "friendly"
        : conversation.tone;

    toneInput.value = getSupportedSelectValue(
      normalizedTone,
      ["friendly", "professional", "formal"],
      "professional",
    );

    responseLengthInput.value = getSupportedSelectValue(
      conversation.response_length,
      ["concise", "balanced", "detailed"],
      "balanced",
    );

    defaultLanguageInput.value = assistant.default_language || "English";

    supportedLanguagesInput.value =
      assistant.supported_languages?.join(", ") || "English";

    greetingEnabledInput.checked =
      conversation.greeting?.enabled !== false;

    greetingMessageInput.value =
      conversation.greeting?.message ||
      `Hello, I'm ${assistant.name || "your assistant"}. How can I help you today?`;

    greetingMessageInput.disabled = !greetingEnabledInput.checked;

    if (showCitationsInput) {
      showCitationsInput.checked = currentModeConfig.show_citations === true;
    }
  }

  function buildAssistantSettingsPayload() {
    const assistantName = assistantNameInput.value.trim();
    const chatName = chatNameInput.value.trim();

    const supportedLanguages = supportedLanguagesInput.value
      .split(",")
      .map((language) => language.trim())
      .filter(Boolean);

    const assistant = currentModeConfig.assistant || {};
    const conversation = currentModeConfig.conversation || {};
    const chat = currentModeConfig.chat || {};

    const defaultChatValues =
      mode === "customer_support"
        ? {
            description:
              "Ask questions about our products, services, support, and policies.",
            placeholder: "Type your question...",
            fallback:
              "Sorry, I couldn't find enough information to answer that confidently.",
          }
        : {
            description: "Ask questions about internal company information.",
            placeholder: "Ask a question...",
            fallback:
              "Sorry, I couldn't find enough information in the knowledge base to answer that confidently.",
          };

    return {
      display_name: chatName,

      assistant: {
        name: assistantName,
        title: assistant.title || "AI Assistant",
        default_language: defaultLanguageInput.value.trim(),
        supported_languages: supportedLanguages,
      },

      conversation: {
        tone: toneInput.value,
        response_length: responseLengthInput.value,

        greeting: {
          enabled: greetingEnabledInput.checked,

          message:
            greetingMessageInput.value.trim() ||
            `Hello, I'm ${assistantName}. How can I help you today?`,
        },
      },

      chat: {
        chat_headline: chatName,

        chat_description:
          chat.chat_description?.trim() || defaultChatValues.description,

        placeholder: chat.placeholder?.trim() || defaultChatValues.placeholder,

        loading_message:
          chat.loading_message?.trim() || "Searching the knowledge base...",

        fallback_message:
          chat.fallback_message?.trim() || defaultChatValues.fallback,
      },

      prompt_guide: currentModeConfig.prompt_guide || "",

      show_citations:
        mode === "internal_knowledge"
          ? showCitationsInput?.checked === true
          : false,
    };
  }

  function setAssistantSettingsNotice(type, message) {
    const notice = document.createElement("div");

    notice.className = `notice notice-${type}`;
    notice.textContent = message;

    assistantSettingsNotice.replaceChildren(notice);
  }

  populateAssistantSettingsForm();

  let assistantSettingsInitialSnapshot = JSON.stringify(
    buildAssistantSettingsPayload(),
  );

  function updateAssistantSettingsDirtyState() {
    const currentSnapshot = JSON.stringify(buildAssistantSettingsPayload());

    const isDirty = currentSnapshot !== assistantSettingsInitialSnapshot;

    saveAssistantSettingsButton.toggleAttribute("disabled", !isDirty);
  }

  const assistantSettingsFields = [
    assistantNameInput,
    chatNameInput,
    toneInput,
    responseLengthInput,
    defaultLanguageInput,
    supportedLanguagesInput,
    greetingEnabledInput,
    greetingMessageInput,
  ];

  if (showCitationsInput) {
    assistantSettingsFields.push(showCitationsInput);
  }

    greetingEnabledInput.addEventListener("change", () => {
    greetingMessageInput.disabled = !greetingEnabledInput.checked;
  });

  assistantSettingsFields.forEach((field) => {
    field.addEventListener("input", updateAssistantSettingsDirtyState);

    field.addEventListener("change", updateAssistantSettingsDirtyState);
  });

  assistantSettingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const requiredFields = Array.from(
      assistantSettingsForm.querySelectorAll("[required]"),
    );

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

    const payload = buildAssistantSettingsPayload();

    if (payload.assistant.supported_languages.length === 0) {
      supportedLanguagesInput.classList.add("field-invalid");

      supportedLanguagesInput.setAttribute("aria-invalid", "true");

      firstInvalidField ??= supportedLanguagesInput;
    }

    if (firstInvalidField) {
      setAssistantSettingsNotice(
        "error",
        "Please fill out all required assistant settings.",
      );

      firstInvalidField.focus();
      return;
    }

    saveAssistantSettingsButton.disabled = true;
    saveAssistantSettingsButton.textContent = "Saving...";

    assistantSettingsNotice.replaceChildren();

    try {
      const result = await updateAssistantModeSettings(mode, payload);

      currentModeConfig = result.assistant_config || currentModeConfig;

      COMPANY_CONFIG.modes[mode] = currentModeConfig;

      assistantSettingsInitialSnapshot = JSON.stringify(
        buildAssistantSettingsPayload(),
      );

      updateAssistantSettingsDirtyState();

      setAssistantSettingsNotice("success", "Assistant settings updated.");
    } catch (error) {
      console.error(error);

      setAssistantSettingsNotice("error", error.message);

      updateAssistantSettingsDirtyState();
    } finally {
      saveAssistantSettingsButton.textContent = "Save assistant settings";
    }
  });

  updateAssistantSettingsDirtyState();

  function getDefaultFallbackBaseMessage() {
    return mode === "internal_knowledge"
      ? "Sorry, I couldn't find enough information in the knowledge base to answer that confidently."
      : "Sorry, I couldn't find enough information to answer that confidently.";
  }

  function getFallbackContactName() {
    return mode === "internal_knowledge" ? "helpdesk" : "customer service";
  }

  function populateFallbackSettingsForm() {
    const legacyContacts = COMPANY_CONFIG[mode]?.support_contacts || {};

    const contacts = currentModeConfig.contacts || {};

    const fallback = currentModeConfig.fallback || {};

    contactEmailInput.value = contacts.email || legacyContacts.email || "";

    contactPhoneInput.value = contacts.phone || legacyContacts.phone || "";

    fallbackBaseMessageInput.value =
      fallback.base_message ||
      currentModeConfig.chat?.fallback_message ||
      getDefaultFallbackBaseMessage();

    includeEmailInput.checked = fallback.include_email === true;

    includePhoneInput.checked = fallback.include_phone === true;
  }

  function buildFallbackSettingsPayload() {
    return {
      contacts: {
        email: contactEmailInput.value.trim(),
        phone: contactPhoneInput.value.trim(),
      },

      fallback: {
        base_message: fallbackBaseMessageInput.value.trim(),

        include_email: includeEmailInput.checked,

        include_phone: includePhoneInput.checked,
      },
    };
  }

  function buildFallbackPreview(payload) {
    const baseMessage = payload.fallback.base_message;

    const email = payload.contacts.email;
    const phone = payload.contacts.phone;

    const includeEmail = payload.fallback.include_email;

    const includePhone = payload.fallback.include_phone;

    const contactName = getFallbackContactName();

    if (includeEmail && email && includePhone && phone) {
      return (
        `${baseMessage} You can email our ` +
        `${contactName} at ${email} or call ${phone}.`
      );
    }

    if (includeEmail && email) {
      return (
        `${baseMessage} You can email our ` + `${contactName} at ${email}.`
      );
    }

    if (includePhone && phone) {
      return `${baseMessage} You can call our ` + `${contactName} at ${phone}.`;
    }

    return baseMessage;
  }

  function setFallbackSettingsNotice(type, message) {
    const notice = document.createElement("div");

    notice.className = `notice notice-${type}`;
    notice.textContent = message;

    fallbackSettingsNotice.replaceChildren(notice);
  }

  function updateFallbackControls() {
    const hasEmail = contactEmailInput.value.trim().length > 0;

    const hasPhone = contactPhoneInput.value.trim().length > 0;

    if (!hasEmail) {
      includeEmailInput.checked = false;
    }

    if (!hasPhone) {
      includePhoneInput.checked = false;
    }

    includeEmailInput.disabled = !hasEmail;
    includePhoneInput.disabled = !hasPhone;
  }

  function updateFallbackPreview() {
    fallbackPreview.textContent = buildFallbackPreview(
      buildFallbackSettingsPayload(),
    );
  }

  populateFallbackSettingsForm();
  updateFallbackControls();
  updateFallbackPreview();

  let fallbackSettingsInitialSnapshot = JSON.stringify(
    buildFallbackSettingsPayload(),
  );

  function updateFallbackSettingsDirtyState() {
    updateFallbackControls();
    updateFallbackPreview();

    const currentSnapshot = JSON.stringify(buildFallbackSettingsPayload());

    saveFallbackSettingsButton.disabled =
      currentSnapshot === fallbackSettingsInitialSnapshot;
  }

  [
    contactEmailInput,
    contactPhoneInput,
    fallbackBaseMessageInput,
    includeEmailInput,
    includePhoneInput,
  ].forEach((field) => {
    field.addEventListener("input", updateFallbackSettingsDirtyState);

    field.addEventListener("change", updateFallbackSettingsDirtyState);
  });

  fallbackSettingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = buildFallbackSettingsPayload();

    if (!payload.fallback.base_message) {
      fallbackBaseMessageInput.classList.add("field-invalid");

      fallbackBaseMessageInput.setAttribute("aria-invalid", "true");

      setFallbackSettingsNotice("error", "Enter a fallback message.");

      fallbackBaseMessageInput.focus();
      return;
    }

    fallbackBaseMessageInput.classList.remove("field-invalid");

    fallbackBaseMessageInput.removeAttribute("aria-invalid");

    saveFallbackSettingsButton.disabled = true;
    saveFallbackSettingsButton.textContent = "Saving...";

    fallbackSettingsNotice.replaceChildren();

    try {
      const result = await updateAssistantModeFallbackSettings(mode, payload);

      currentModeConfig = result.assistant_config || currentModeConfig;

      COMPANY_CONFIG.modes[mode] = currentModeConfig;

      fallbackSettingsInitialSnapshot = JSON.stringify(
        buildFallbackSettingsPayload(),
      );

      updateFallbackSettingsDirtyState();

      setFallbackSettingsNotice("success", "Fallback settings updated.");
    } catch (error) {
      console.error(error);

      setFallbackSettingsNotice("error", error.message);

      updateFallbackSettingsDirtyState();
    } finally {
      saveFallbackSettingsButton.textContent = "Save fallback settings";
    }
  });

  function setTestChatNotice(type, message) {
    const notice = document.createElement("div");

    notice.className = `notice notice-${type}`;
    notice.textContent = message;

    testChatNotice.replaceChildren(notice);
  }

  function renderTestSources(sources) {
    testSources.replaceChildren();

    if (sources.length === 0) {
      const emptyState = document.createElement("p");

      emptyState.className = "file-meta";

      emptyState.textContent =
        "No source chunks were returned. This may be a configured refusal.";

      testSources.appendChild(emptyState);
      return;
    }

    sources.forEach((source, index) => {
      const sourceCard = document.createElement("article");

      sourceCard.className = "assistant-test-source";

      const heading = document.createElement("strong");

      heading.textContent = source.source || `Source ${index + 1}`;

      const metadata = document.createElement("div");

      metadata.className = "file-meta";

      metadata.textContent =
        typeof source.score === "number"
          ? `Similarity score: ${source.score.toFixed(3)}`
          : "Similarity score unavailable";

      const text = document.createElement("p");

      text.textContent = source.text || "No source text returned.";

      sourceCard.append(heading, metadata, text);

      testSources.appendChild(sourceCard);
    });
  }

  testQuestionInput.addEventListener("keydown", (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.isComposing
    ) {
      event.preventDefault();
      testChatForm.requestSubmit();
    }
  });

  testChatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = testQuestionInput.value.trim();

    if (!question) {
      testQuestionInput.classList.add("field-invalid");

      testQuestionInput.setAttribute("aria-invalid", "true");

      setTestChatNotice("error", "Enter a test question.");

      testQuestionInput.focus();
      return;
    }

    testQuestionInput.classList.remove("field-invalid");

    testQuestionInput.removeAttribute("aria-invalid");

    testQuestionInput.disabled = true;
    testQuestionButton.disabled = true;
    testQuestionButton.textContent = "Asking...";

    testChatNotice.replaceChildren();
    testChatResult.hidden = true;

    try {
      const result = await askQuestion(question, mode);

      if (result.mode !== mode) {
        throw new Error(
          `The response used '${result.mode}' instead of '${mode}'.`,
        );
      }

      testAnswer.textContent = result.answer || "No answer was returned.";

      renderTestSources(result.sources || []);

      testChatResult.hidden = false;
    } catch (error) {
      console.error(error);

      setTestChatNotice("error", error.message);
    } finally {
      testQuestionInput.disabled = false;
      testQuestionButton.disabled = false;
      testQuestionButton.textContent = "Ask assistant";
    }
  });

  function setExpanded(isExpanded) {
    content.hidden = !isExpanded;

    toggleButton.setAttribute("aria-expanded", String(isExpanded));

    toggleButton.textContent = isExpanded ? "Close settings" : "Edit settings";
  }

  function setNotice(type, message) {
    const notice = document.createElement("div");

    notice.className = `notice notice-${type}`;
    notice.textContent = message;

    uploadNotice.replaceChildren(notice);
  }

  function clearNotice() {
    uploadNotice.replaceChildren();
  }

  function clearSelectedFiles() {
    selectedFiles = [];
    fileInput.value = "";

    renderSelectedFiles();
  }

  function renderSelectedFiles() {
    selectedFileRows.replaceChildren();

    if (selectedFiles.length === 0) {
      selectedFilesContainer.hidden = true;
      return;
    }

    selectedFilesContainer.hidden = false;

    selectedFiles.forEach((file, index) => {
      const row = document.createElement("div");

      row.className = "file-row";

      const details = document.createElement("div");

      const filename = document.createElement("strong");

      filename.textContent = file.name;

      const metadata = document.createElement("div");

      metadata.className = "file-meta";
      metadata.textContent = formatDocumentBytes(file.size);

      details.append(filename, metadata);

      const removeButton = document.createElement("button");

      removeButton.className = "remove-btn";
      removeButton.type = "button";
      removeButton.textContent = "Remove";

      removeButton.addEventListener("click", () => {
        selectedFiles.splice(index, 1);

        renderSelectedFiles();
      });

      row.append(details, removeButton);

      selectedFileRows.appendChild(row);
    });
  }

  function updateCardSummary(documents) {
    const documentCount = documents.length;

    const documentLabel = documentCount === 1 ? "document" : "documents";

    const allIndexed =
      documentCount > 0 &&
      documents.every((documentRecord) => documentRecord.status === "indexed");

    if (documentCount === 0) {
      cardSummary.textContent = "0 documents · Upload required";

      card.classList.add("assistant-card-needs-attention");

      return true;
    }

    if (!allIndexed) {
      cardSummary.textContent = `${documentCount} ${documentLabel} · Needs attention`;

      card.classList.add("assistant-card-needs-attention");

      return true;
    }

    cardSummary.textContent = `${documentCount} ${documentLabel} · Chat ready`;

    card.classList.remove("assistant-card-needs-attention");

    return false;
  }

  function renderIndexedDocuments(documents) {
    indexedFileRows.replaceChildren();

    if (documents.length === 0) {
      const emptyState = document.createElement("p");

      emptyState.className = "file-meta";

      emptyState.textContent =
        "No documents have been indexed for this assistant.";

      indexedFileRows.appendChild(emptyState);
      return;
    }

    documents.forEach((documentRecord) => {
      const row = document.createElement("div");

      row.className = "file-row";

      const details = document.createElement("div");

      const filename = document.createElement("strong");

      filename.textContent = documentRecord.filename;

      const metadata = document.createElement("div");

      metadata.className = "file-meta";

      const status =
        documentRecord.status === "indexed" ? "Indexed" : documentRecord.status;

      metadata.textContent = `${formatDocumentBytes(
        documentRecord.size_bytes,
      )} · ${status}`;

      details.append(filename, metadata);

      const deleteButton = document.createElement("button");

      deleteButton.className = "remove-btn";
      deleteButton.type = "button";
      deleteButton.textContent = "Delete";

      deleteButton.addEventListener("click", async () => {
        const confirmed = window.confirm(
          `Delete "${documentRecord.filename}"?\n\n` +
            "The assistant index will be rebuilt without this document.",
        );

        if (!confirmed) {
          return;
        }

        deleteButton.disabled = true;
        deleteButton.textContent = "Deleting...";

        setNotice(
          "success",
          "Deleting document and rebuilding the knowledge base...",
        );

        try {
          await deleteDocument(documentRecord.document_id, mode);

          setNotice("success", `"${documentRecord.filename}" was deleted.`);

          await loadIndexedDocuments();
        } catch (error) {
          console.error(error);

          setNotice("error", error.message);

          deleteButton.disabled = false;
          deleteButton.textContent = "Delete";
        }
      });

      row.append(details, deleteButton);

      indexedFileRows.appendChild(row);
    });
  }

  async function loadIndexedDocuments() {
    if (documentsLoading) {
      return;
    }

    documentsLoading = true;

    indexedFileRows.replaceChildren();

    const loading = document.createElement("p");

    loading.className = "file-meta";
    loading.textContent = "Loading documents...";

    indexedFileRows.appendChild(loading);

    try {
      const result = await getDocuments(mode);

      const documents = result.documents || [];

      renderIndexedDocuments(documents);

      const needsAttention = updateCardSummary(documents);

      if (needsAttention) {
        setExpanded(true);
      }
    } catch (error) {
      console.error(error);

      cardSummary.textContent = "Could not load documents · Needs attention";

      card.classList.add("assistant-card-needs-attention");

      setNotice("error", error.message);

      setExpanded(true);
    } finally {
      documentsLoading = false;
    }
  }

  function addFiles(fileList) {
    const incomingFiles = Array.from(fileList);

    const acceptedFiles = incomingFiles.filter((file) => {
      const filename = file.name.toLowerCase();

      return (
        filename.endsWith(".pdf") ||
        filename.endsWith(".txt") ||
        filename.endsWith(".md")
      );
    });

    selectedFiles = [...selectedFiles, ...acceptedFiles];

    renderSelectedFiles();

    if (acceptedFiles.length !== incomingFiles.length) {
      setNotice(
        "error",
        "Some files were skipped. Only PDF, TXT, and MD files are supported.",
      );
    }
  }

  toggleButton.addEventListener("click", () => {
    setExpanded(content.hidden);
  });

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
    clearSelectedFiles();
    clearNotice();
  });

  processButton.addEventListener("click", async () => {
    if (selectedFiles.length === 0) {
      setNotice("error", "Choose at least one document first.");

      return;
    }

    processButton.disabled = true;
    processButton.textContent = "Processing documents...";

    setNotice("success", "Uploading and indexing documents...");

    try {
      const result = await uploadDocuments(selectedFiles, mode);

      setNotice(
        "success",
        `${result.files_processed} document(s) indexed successfully.`,
      );

      clearSelectedFiles();

      await loadIndexedDocuments();
    } catch (error) {
      console.error(error);

      setNotice("error", error.message);
    } finally {
      processButton.disabled = false;
      processButton.textContent = "Process documents";
    }
  });

  renderSelectedFiles();

  await loadIndexedDocuments();
}

async function initializeAssistantCards() {
  const container = document.getElementById("assistantCards");

  if (!container) {
    throw new Error("Assistant cards container is missing.");
  }

  const availableModes = CONFIG_STATUS?.available_modes || [];

  if (availableModes.length === 0) {
    throw new Error("No assistant modes are provisioned.");
  }

  initializeAssistantDocumentDragGuards();

  container.replaceChildren();

  const initializationTasks = availableModes.map((mode) => {
    const card = createAssistantCard(mode);

    container.appendChild(card);

    return initializeAssistantCard(card, mode);
  });

  await Promise.all(initializationTasks);
}
