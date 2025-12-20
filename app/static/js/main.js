document.addEventListener('DOMContentLoaded', () => {
    // ---- Navbar Burger Logic ----
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    if ($navbarBurgers.length > 0) {
        $navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = el.dataset.target;
                const $target = document.getElementById(target);
                el.classList.toggle('is-active');
                $target.classList.toggle('is-active');
            });
        });
    }

    // ---- Drag & Drop Logic for Index Page ----
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#file-upload');
    const fileNameDisplay = document.querySelector('#file-name');
    const form = document.querySelector('form');

    if (uploadArea && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadArea.classList.add('drag-over');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('drag-over');
        }

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            updateFileName(files);

            // Optional: Auto submit on drop
            // form.submit();
        }

        fileInput.addEventListener('change', function () {
            updateFileName(this.files);
        });

        function updateFileName(files) {
            if (files && files.length > 0) {
                fileNameDisplay.textContent = files[0].name;
                fileNameDisplay.classList.add('has-text-primary', 'has-text-weight-bold');
                // Trigger fade in effect for feedback
                fileNameDisplay.style.opacity = '0';
                setTimeout(() => fileNameDisplay.style.opacity = '1', 50);
            }
        }
    }

    // ---- Notification Dismissal ----
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;
        $delete.addEventListener('click', () => {
            $notification.remove(); // cleaner standard DOM method
        });
    });

    // Dynamic Fields Logic
    const addBtn = document.getElementById('add-field-btn');
    const container = document.getElementById('custom-fields-container');

    // List of supported tags for logical suggestions, but now we support arbitrary inputs
    // This array isn't strictly needed for the dropdown generation anymore, effectively replaced by html datalist
    const supportedTags = [
        'Make', 'Model', 'Software', 'DateTime',
        'HostComputer', 'UserComment', 'LensMake',
        'LensModel', 'BodySerialNumber', 'CameraOwnerName'
    ];

    if (addBtn && container) {
        addBtn.addEventListener('click', () => {
            const fieldDiv = document.createElement('div');
            // Using Bulma field with addons
            fieldDiv.className = 'field has-addons mb-2';

            fieldDiv.innerHTML = `
                <div class="control">
                    <input class="input tag-key" type="text" list="tag-suggestions" placeholder="Tag Name (e.g. Model)">
                </div>
                <div class="control is-expanded">
                    <input class="input tag-value" type="text" placeholder="Value">
                </div>
                <div class="control">
                    <button class="button is-danger is-outlined delete-row" type="button">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            container.appendChild(fieldDiv);

            // Add event listeners for this row
            const keyInput = fieldDiv.querySelector('.tag-key');
            const valueInput = fieldDiv.querySelector('.tag-value');
            const deleteBtn = fieldDiv.querySelector('.delete-row');

            // Logic: The backend needs name="TagName" value="Value".
            // We set the name attribute of the valueInput to be the value of keyInput.

            const updateName = () => {
                if (keyInput.value) {
                    valueInput.name = keyInput.value;
                }
            };

            keyInput.addEventListener('input', updateName);
            keyInput.addEventListener('change', updateName);

            deleteBtn.addEventListener('click', () => {
                container.removeChild(fieldDiv);
            });
        });
    }
});
