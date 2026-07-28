let COMPANY_CONFIG = null;

async function loadCompanyConfig() {
  const response = await fetch("../data/company/company.json");

  if (!response.ok) {
    throw new Error("Could not load company configuration");
  }

  COMPANY_CONFIG = await response.json();

  applyBranding();

  return COMPANY_CONFIG;
}

function applyBranding() {
  const colors = COMPANY_CONFIG.branding?.colors;

  if (!colors) {
    return;
  }

  document.documentElement.style.setProperty("--primary-color", colors.primary);

  document.documentElement.style.setProperty(
    "--secondary-color",
    colors.secondary,
  );

  document.documentElement.style.setProperty("--accent-color", colors.accent);

  document.documentElement.style.setProperty(
    "--background-color",
    colors.background,
  );

  document.documentElement.style.setProperty("--text-color", colors.text);
}
