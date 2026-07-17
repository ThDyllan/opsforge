(() => {
  "use strict";

  const body = document.body;
  const toast = document.querySelector("[data-toast]");

  const renderIcons = () => {
    if (window.lucide) {
      window.lucide.createIcons({ attrs: { "stroke-width": 1.8 } });
    }
  };

  const messageFromError = (payload, fallback) => {
    if (!payload) return fallback;
    if (typeof payload.detail === "string") return payload.detail;
    if (payload.detail && typeof payload.detail.message === "string") {
      return payload.detail.message;
    }
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item) => item.msg || "Valeur invalide").join(" · ");
    }
    return fallback;
  };

  const showToast = (message, type = "success") => {
    if (!toast) return;
    toast.hidden = false;
    toast.classList.toggle("is-error", type === "error");
    const messageNode = toast.querySelector("[data-toast-message]");
    const iconNode = toast.querySelector("[data-toast-icon]");
    if (messageNode) messageNode.textContent = message;
    if (iconNode) {
      iconNode.innerHTML = type === "error"
        ? '<i data-lucide="circle-alert" aria-hidden="true"></i>'
        : '<i data-lucide="circle-check" aria-hidden="true"></i>';
    }
    renderIcons();
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
      toast.hidden = true;
    }, 5000);
  };

  const storeToast = (message) => {
    window.sessionStorage.setItem("opsforge-toast", message);
  };

  const apiRequest = async (url, method, bodyData) => {
    const options = {
      method,
      headers: {
        Accept: "application/json",
        "X-OpsForge-Actor": "Dyllan",
      },
    };
    if (bodyData !== undefined) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(bodyData);
    }
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : null;
    if (!response.ok) {
      throw new Error(messageFromError(payload, `Erreur HTTP ${response.status}`));
    }
    return payload;
  };

  const serializeForm = (form) => {
    const payload = {};
    const arrayFields = new Set();

    form.querySelectorAll("[data-array][name]").forEach((element) => {
      arrayFields.add(element.name);
      if (!Object.hasOwn(payload, element.name)) payload[element.name] = [];
    });

    for (const [name, rawValue] of new FormData(form).entries()) {
      const element = form.querySelector(`[name="${CSS.escape(name)}"]`);
      let value = rawValue;
      if (element?.hasAttribute("data-number")) {
        if (rawValue === "") continue;
        value = Number(rawValue);
      }
      if (arrayFields.has(name)) {
        payload[name].push(value);
      } else if (rawValue === "" && element?.hasAttribute("data-empty-null")) {
        payload[name] = null;
      } else if (rawValue !== "") {
        payload[name] = value;
      }
    }

    form.querySelectorAll("[data-boolean][name]").forEach((element) => {
      payload[element.name] = element.checked;
    });
    return payload;
  };

  document.querySelectorAll("[data-api-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const submit = form.querySelector('[type="submit"]');
      const originalText = submit?.innerHTML;
      if (submit) {
        submit.disabled = true;
        submit.innerHTML = '<i data-lucide="loader-circle" aria-hidden="true"></i><span>Traitement...</span>';
        renderIcons();
      }
      try {
        const result = await apiRequest(
          form.dataset.url,
          form.dataset.method || "POST",
          serializeForm(form),
        );
        const success = form.dataset.success || "Action terminée";
        const template = form.dataset.redirectTemplate;
        const redirect = template && result
          ? template.replace("{id}", result.id)
          : form.dataset.redirect;
        if (redirect) {
          storeToast(success);
          window.location.assign(redirect);
        } else {
          storeToast(success);
          window.location.reload();
        }
      } catch (error) {
        showToast(error.message || "Une erreur est survenue.", "error");
        if (submit) {
          submit.disabled = false;
          submit.innerHTML = originalText;
          renderIcons();
        }
      }
    });
  });

  document.querySelectorAll("[data-api-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (button.dataset.confirm && !window.confirm(button.dataset.confirm)) return;
      button.disabled = true;
      try {
        const bodyData = button.dataset.body ? JSON.parse(button.dataset.body) : undefined;
        await apiRequest(button.dataset.url, button.dataset.method || "POST", bodyData);
        storeToast(button.dataset.success || "Action terminée");
        window.location.reload();
      } catch (error) {
        showToast(error.message || "Une erreur est survenue.", "error");
        button.disabled = false;
      }
    });
  });

  document.querySelectorAll("[data-row-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.rowExpand);
      if (!target) return;
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      target.hidden = expanded;
    });
  });

  document.querySelectorAll("[data-href]").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest("a, button, input, select, textarea")) return;
      window.location.assign(row.dataset.href);
    });
  });

  const normalizeSlug = (value, separator) => value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, separator)
    .replace(new RegExp(`^\\${separator}+|\\${separator}+$`, "g"), "");

  const bindGeneratedField = (sourceSelector, targetSelector, separator) => {
    const source = document.querySelector(sourceSelector);
    const target = document.querySelector(targetSelector);
    if (!source || !target || target.value) return;
    let manuallyEdited = false;
    target.addEventListener("input", () => {
      manuallyEdited = target.value.length > 0;
    });
    source.addEventListener("input", () => {
      if (!manuallyEdited) target.value = normalizeSlug(source.value, separator);
    });
  };

  bindGeneratedField("[data-slug-source]", "[data-slug-target]", "-");
  bindGeneratedField("[data-key-source]", "[data-key-target]", "_");

  const updateStepNumbers = () => {
    document.querySelectorAll("[data-steps-editor] .step-input").forEach((row, index) => {
      const number = row.querySelector(":scope > span");
      if (number) number.textContent = String(index + 1);
    });
  };

  const stepsEditor = document.querySelector("[data-steps-editor]");
  const addStepButton = document.querySelector("[data-add-step]");
  if (stepsEditor && addStepButton) {
    addStepButton.addEventListener("click", () => {
      const row = document.createElement("div");
      row.className = "step-input";
      row.innerHTML = '<span></span><input name="steps" data-array placeholder="Décrire la vérification" required><button class="icon-button" type="button" data-remove-step aria-label="Supprimer l\'étape" title="Supprimer"><i data-lucide="trash-2" aria-hidden="true"></i></button>';
      stepsEditor.append(row);
      updateStepNumbers();
      renderIcons();
      row.querySelector("input")?.focus();
    });
    stepsEditor.addEventListener("click", (event) => {
      const remove = event.target.closest("[data-remove-step]");
      if (!remove) return;
      const rows = stepsEditor.querySelectorAll(".step-input");
      if (rows.length === 1) {
        rows[0].querySelector("input").value = "";
      } else {
        remove.closest(".step-input")?.remove();
        updateStepNumbers();
      }
    });
  }

  const modeSelect = document.querySelector("[data-runbook-mode]");
  const automationField = document.querySelector("[data-automation-field]");
  const updateAutomationField = () => {
    if (!modeSelect || !automationField) return;
    const automated = modeSelect.value === "automated";
    automationField.hidden = !automated;
    const select = automationField.querySelector("select");
    if (select) {
      select.required = automated;
      if (!automated) select.value = "";
    }
  };
  modeSelect?.addEventListener("change", updateAutomationField);
  updateAutomationField();

  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  const compactSidebarQuery = window.matchMedia("(max-width: 1050px)");
  const updateSidebarToggle = () => {
    if (!sidebarToggle) return;
    const expanded = compactSidebarQuery.matches
      ? body.classList.contains("sidebar-open")
      : !body.classList.contains("sidebar-compact");
    sidebarToggle.setAttribute("aria-expanded", String(expanded));
  };

  sidebarToggle?.addEventListener("click", () => {
    if (compactSidebarQuery.matches) {
      body.classList.toggle("sidebar-open");
    } else {
      body.classList.toggle("sidebar-compact");
      body.classList.remove("sidebar-open");
    }
    updateSidebarToggle();
  });
  document.querySelector("[data-sidebar-close]")?.addEventListener("click", () => {
    body.classList.remove("sidebar-open");
    updateSidebarToggle();
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      body.classList.remove("sidebar-open");
      updateSidebarToggle();
    }
  });
  compactSidebarQuery.addEventListener("change", () => {
    body.classList.remove("sidebar-open");
    if (compactSidebarQuery.matches) body.classList.remove("sidebar-compact");
    updateSidebarToggle();
  });
  updateSidebarToggle();

  document.querySelector("[data-toast-close]")?.addEventListener("click", () => {
    if (toast) toast.hidden = true;
  });

  const storedToast = window.sessionStorage.getItem("opsforge-toast");
  if (storedToast) {
    window.sessionStorage.removeItem("opsforge-toast");
    showToast(storedToast);
  }

  renderIcons();
})();
