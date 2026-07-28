let COMPANY_CONFIG = null;

async function loadCompanyConfig() {
  const response = await fetch("http://localhost:8000/config/company.json");

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

  document.documentElement.style.setProperty(
    "--primary",
    colors.primary,
  );

  document.documentElement.style.setProperty(
    "--secondary",
    colors.secondary,
  );

  document.documentElement.style.setProperty(
    "--accent",
    colors.accent,
  );

  document.documentElement.style.setProperty(
    "--bg",
    colors.background,
  );

  document.documentElement.style.setProperty(
    "--text",
    colors.text,
  );
}
