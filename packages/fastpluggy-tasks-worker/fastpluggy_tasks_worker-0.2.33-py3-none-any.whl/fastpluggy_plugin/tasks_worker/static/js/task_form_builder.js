/**
 * Render dynamic form fields based on task parameter metadata.
 * Supports text, number, boolean, textarea, date, and other HTML5 types.
 */
function renderTaskForm(containerId, fields) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';

  if (!fields || typeof fields !== 'object' || Object.keys(fields).length === 0) {
    container.innerHTML = '<p class="text-muted">No parameters required.</p>';
    return;
  }

  Object.entries(fields).forEach(([name, meta]) => {
    const formGroup = document.createElement('div');
    formGroup.className = 'mb-3';

    // Label
    const label = document.createElement('label');
    label.className = 'form-label';
    label.setAttribute('for', `field-${name}`);
    label.textContent = meta.label || `${name} (${meta.type})`;
    if (meta.required) {
      label.classList.add('required');
    }

    let input;
    const fieldType = mapFieldType(meta.type);

    // Input Type Handling
    if (fieldType === 'textarea') {
      input = document.createElement('textarea');
      input.className = 'form-control';
      if (meta.default !== undefined && meta.default !== null) {
        input.value = meta.default;
      }
    } else if (fieldType === 'checkbox') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.className = 'form-check-input';
      if (meta.default) {
        input.checked = true;
      }
    } else {
      input = document.createElement('input');
      input.type = fieldType;
      input.className = 'form-control';
      if (meta.default !== undefined && meta.default !== null) {
        input.value = meta.default;
      }
    }

    // Common attributes
    input.id = `field-${name}`;
    input.name = name;
    input.setAttribute('data-type', meta.type);
    if (meta.required) {
      input.required = true;
    }
    if (meta.readonly) {
      input.readOnly = true;
    }
    if (meta.disabled) {
      input.disabled = true;
    }

    formGroup.appendChild(label);
    formGroup.appendChild(input);
    container.appendChild(formGroup);
  });
}

/**
 * Collect values from the rendered form.
 * Returns a dictionary of {name: value}.
 */
function collectFormValues(containerId) {
  const container = document.getElementById(containerId);
  const inputs = container.querySelectorAll('input, select, textarea');
  const values = {};

  inputs.forEach(input => {
    if (!input.name) return;

    if (input.type === 'checkbox') {
      values[input.name] = input.checked;
    } else {
      values[input.name] = input.value;
    }
  });

  return values;
}

/**
 * Map generic type names to HTML5 input types.
 */
function mapFieldType(type) {
  switch (type) {
    case 'integer':
    case 'int':
    case 'number':
      return 'number';
    case 'boolean':
      return 'checkbox';
    case 'textarea':
      return 'textarea';
    case 'date':
      return 'date';
    case 'datetime':
    case 'datetime-local':
      return 'datetime-local';
    case 'email':
      return 'email';
    case 'text':
    case 'string':
    default:
      return 'text';
  }
}
