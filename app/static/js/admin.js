class AdminCRUD {
    constructor() {
        this.initDeleteHandlers();
        this.setupEditModal();
    }

    initDeleteHandlers() {
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleDelete(e));
        });
    }

    handleDelete(e) {
        const btn = e.currentTarget;
        const id = btn.dataset.contactId;
        const row = btn.closest('tr');
        
        if (confirm('Are you sure you want to delete this contact?')) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
            
            fetch('/admin/api/contacts/' + id, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    row.classList.add('table-danger');
                    setTimeout(() => row.remove(), 300);
                } else {
                    throw new Error('Failed to delete contact');
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-trash"></i> Delete';
                alert(error.message);
            });
        }
    }

    setupEditModal() {
        // Create Bootstrap modal template
        this.editModal = new bootstrap.Modal(document.getElementById('editModal'), {
            keyboard: false
        });

        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => this.showEditModal(e));
        });

        document.getElementById('editForm').addEventListener('submit', (e) => this.handleEditSubmit(e));
    }

    showEditModal(e) {
        const btn = e.currentTarget;
        document.getElementById('editId').value = btn.dataset.contactId;
        document.getElementById('editName').value = btn.dataset.contactName;
        document.getElementById('editEmail').value = btn.dataset.contactEmail;
        document.getElementById('editMessage').value = btn.dataset.contactMessage;
        
        // Clear previous errors
        document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        this.editModal.show();
    }

    handleEditSubmit(e) {
        e.preventDefault();
        
        const id = document.getElementById('editId').value;
        const name = document.getElementById('editName').value.trim();
        const email = document.getElementById('editEmail').value.trim();
        const message = document.getElementById('editMessage').value.trim();
        
        if (!this.validateForm(name, email, message)) return;
        
        const saveBtn = document.getElementById('saveBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        fetch('/admin/api/contacts/' + id, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ name, email, message })
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to update contact');
                });
            }
        })
        .catch(error => {
            saveBtn.disabled = false;
            saveBtn.innerHTML = 'Save Changes';
            alert(error.message);
        });
    }

    validateForm(name, email, message) {
        let isValid = true;
        
        if (name.length < 2) {
            document.getElementById('nameError').textContent = 'Name must be at least 2 characters';
            document.getElementById('editName').classList.add('is-invalid');
            isValid = false;
        }
        
        if (!email.includes('@') || !email.includes('.')) {
            document.getElementById('emailError').textContent = 'Please enter a valid email';
            document.getElementById('editEmail').classList.add('is-invalid');
            isValid = false;
        }
        
        if (message.length < 10) {
            document.getElementById('messageError').textContent = 'Message must be at least 10 characters';
            document.getElementById('editMessage').classList.add('is-invalid');
            isValid = false;
        }
        
        return isValid;
    }
}

// Add modal template to the page
const modalTemplate = `
<div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="editModalLabel">Edit Contact</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="editForm">
                    <input type="hidden" id="editId">
                    <div class="mb-3">
                        <label for="editName" class="form-label">Name</label>
                        <input type="text" class="form-control" id="editName" required>
                        <div class="invalid-feedback" id="nameError"></div>
                    </div>
                    <div class="mb-3">
                        <label for="editEmail" class="form-label">Email</label>
                        <input type="email" class="form-control" id="editEmail" required>
                        <div class="invalid-feedback" id="emailError"></div>
                    </div>
                    <div class="mb-3">
                        <label for="editMessage" class="form-label">Message</label>
                        <textarea class="form-control" id="editMessage" rows="3" required></textarea>
                        <div class="invalid-feedback" id="messageError"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="submit" form="editForm" class="btn btn-primary" id="saveBtn">Save Changes</button>
            </div>
        </div>
    </div>
</div>`;

document.body.insertAdjacentHTML('beforeend', modalTemplate);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load Bootstrap JS if not already loaded
    if (typeof bootstrap === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js';
        script.onload = () => new AdminCRUD();
        document.head.appendChild(script);
    } else {
        new AdminCRUD();
    }
});