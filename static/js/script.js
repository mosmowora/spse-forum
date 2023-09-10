// Menu

const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle("show");
  });
}

// Upload Image
const photoInput = document.querySelector("#avatar");
const photoPreview = document.querySelector("#preview-avatar");
if (photoInput)
  photoInput.onchange = () => {
    const [file] = photoInput.files;
    if (file) {
      photoPreview.src = URL.createObjectURL(file);
    }
  };

const formClear = document.querySelector('[for="avatar-clear_id"]');
if (formClear != null) {
  formClear.innerHTML = "Vymazať";
  const formClearCheckbox = document.querySelector('input[name="avatar-clear"]');
  function disable() {
    $('input[name="avatar"]').attr('disabled', true);
  }
  function enable() {
    $('input[name="avatar"]').attr('disabled', false);
  }

  formClearCheckbox.addEventListener('click', () => {
    if (formClearCheckbox.checked) {
      disable();
    } else {
      enable();
    }
  });
}

function prevent(e) {
  return !(e.which == 13 || e.keyCode == 13);
}