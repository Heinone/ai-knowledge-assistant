let COMPANY_CONFIG = null;
let ANSWERLY_BRANDING = null;
let CONFIG_STATUS = null;

const CONFIG_API_BASE_URL = "http://127.0.0.1:8000";

async function loadCompanyConfig() {
  const statusResponse = await fetch(`${CONFIG_API_BASE_URL}/config/status`);

  if (!statusResponse.ok) {
    throw new Error("Could not load configuration status");
  }

  CONFIG_STATUS = await statusResponse.json();

  if (CONFIG_STATUS.has_active_company) {
    const companyResponse = await fetch(
      `${CONFIG_API_BASE_URL}/config/company.json`,
    );

    if (!companyResponse.ok) {
      throw new Error("Could not load company configuration");
    }

    COMPANY_CONFIG = await companyResponse.json();
    ANSWERLY_BRANDING = null;
  } else {
    const brandingResponse = await fetch(
      `${CONFIG_API_BASE_URL}/config/answerly/branding.json`,
    );

    if (!brandingResponse.ok) {
      throw new Error("Could not load Answer.ly branding");
    }

    ANSWERLY_BRANDING = await brandingResponse.json();
    COMPANY_CONFIG = null;
  }

  applyBranding();

  return COMPANY_CONFIG;
}

function applyFavicon() {
  const favicon = document.getElementById("favicon");

  if (!favicon) {
    return;
  }

  const hasCompanyFavicon =
    CONFIG_STATUS?.has_active_company === true &&
    COMPANY_CONFIG?.branding?.assets?.favicon;

  if (!hasCompanyFavicon) {
    favicon.href = "./assets/answerly_favicon.png?v=1";
    return;
  }

  favicon.href = `${getBrandAssetUrl("favicon")}?version=${Date.now()}`;
}

function applyBranding() {
  const colors = CONFIG_STATUS?.has_active_company
    ? COMPANY_CONFIG?.branding?.colors
    : ANSWERLY_BRANDING?.colors;

  if (colors) {
    setBrandColor("--primary", colors.primary);
    setBrandColor("--primary-dark", colors.primary_dark || colors.primary);
    setBrandColor("--secondary", colors.secondary);
    setBrandColor("--accent", colors.accent);
    setBrandColor("--bg", colors.background || colors.secondary);
    setBrandColor("--text", colors.text);
    setBrandColor("--success", colors.success);
  }

  applyFavicon();
}

function setBrandColor(variableName, value) {
  if (!value) {
    return;
  }

  document.documentElement.style.setProperty(variableName, value);
}

function getBrandAssetUrl(assetName) {
  return `${CONFIG_API_BASE_URL}/config/assets/${encodeURIComponent(
    assetName,
  )}`;
}

function applyBrandLogo(imageElement, fallbackElement) {
  if (!COMPANY_CONFIG) {
    return;
  }

  const companyName = COMPANY_CONFIG.company_name || "Company";

  fallbackElement.textContent = companyName.charAt(0).toUpperCase();

  const logoPath = COMPANY_CONFIG.branding?.assets?.logo;

  if (!logoPath) {
    imageElement.hidden = true;
    fallbackElement.hidden = false;
    return;
  }

  const logoContainer = imageElement.closest(".logo");

  imageElement.onload = () => {
    imageElement.hidden = false;
    fallbackElement.hidden = true;
    logoContainer?.classList.add("has-image");
  };

  imageElement.onerror = () => {
    imageElement.hidden = true;
    fallbackElement.hidden = false;
    logoContainer?.classList.remove("has-image");
  };

  imageElement.src = `${getBrandAssetUrl("logo")}?version=${Date.now()}`;
}
