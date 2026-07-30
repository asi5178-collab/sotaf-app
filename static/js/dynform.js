// Renders repeatable "row card" groups (used for both table-style sections and
// free-form repeat groups) from a JSON config, and serializes them back into
// a hidden input as JSON right before the form submits.
(function () {
  function fieldInput(field, value) {
    const wrap = document.createElement("div");
    const label = document.createElement("label");
    label.textContent = field.label;
    wrap.appendChild(label);

    let input;
    if (field.kind === "textarea") {
      input = document.createElement("textarea");
      input.rows = 3;
    } else {
      input = document.createElement("input");
      input.type = "text";
    }
    input.name = field.id;
    input.value = value || "";
    wrap.appendChild(input);
    return wrap;
  }

  function buildRow(config, rowData) {
    const row = document.createElement("div");
    row.className = "dyn-row";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "dyn-row-remove";
    removeBtn.innerHTML = "&times;";
    removeBtn.title = "הסר";
    removeBtn.addEventListener("click", () => row.remove());
    row.appendChild(removeBtn);

    const fieldsWrap = document.createElement("div");
    fieldsWrap.className = "dyn-row-fields";
    config.fields.forEach((field) => {
      fieldsWrap.appendChild(fieldInput(field, rowData ? rowData[field.label] : ""));
    });
    row.appendChild(fieldsWrap);
    return row;
  }

  function initContainer(container) {
    const config = JSON.parse(container.dataset.dyn);
    const rowsEl = container.querySelector(".dyn-rows");
    const addBtn = container.querySelector(".dyn-add-btn");
    const initial = config.value && config.value.length ? config.value : config.seed;

    (initial || []).forEach((rowData) => rowsEl.appendChild(buildRow(config, rowData)));

    addBtn.addEventListener("click", () => {
      rowsEl.appendChild(buildRow(config, null));
    });

    container._dynConfig = config;
    container._dynRowsEl = rowsEl;
  }

  function collectValue(container) {
    const config = container._dynConfig;
    const rows = Array.from(container._dynRowsEl.querySelectorAll(".dyn-row"));
    return rows.map((row) => {
      const obj = {};
      config.fields.forEach((field) => {
        const el = row.querySelector(`[name="${CSS.escape(field.id)}"]`);
        obj[field.label] = el ? el.value : "";
      });
      return obj;
    });
  }

  function serializeForm(form) {
    form.querySelectorAll("[data-dyn]").forEach((container) => {
      const hidden = document.getElementById(container.dataset.hiddenInput);
      if (hidden) hidden.value = JSON.stringify(collectValue(container));
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-dyn]").forEach(initContainer);
    document.querySelectorAll("form[data-serialize-dyn]").forEach((form) => {
      form.addEventListener("submit", () => serializeForm(form));
    });
  });
})();
