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
            btn.textContent = 'Deleting...';
            
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
                    row.style.transition = 'opacity 0.3s';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                } else {
                    throw new Error('Failed to delete contact');
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.textContent = 'Delete';
                alert(error.message);
            });
        }
    }

    setupEditModal() {
        this.editModal = document.createElement('div');
        this.editModal.className = 'modal';
        this.editModal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <h2>Edit Contact</h2>
                <form id="editForm">
                    <input type="hidden" id="editId">
                    <div class="form-group">
                        <label for="editName">Name</label>
                        <input type="text" id="editName" required>
                        <div class="error" id="nameError"></div>
                    </div>
                    <div class="form-group">
                        <label for="editEmail">Email</label>
                        <input type="email" id="editEmail" required>
                        <div class="error" id="emailError"></div>
                    </div>
                    <div class="form-group">
                        <label for="editMessage">Message</label>
                        <textarea id="editMessage" required></textarea>
                        <div class="error" id="messageError"></div>
                    </div>
                    <button type="submit" class="btn btn-save">Save Changes</button>
                </form>
            </div>
        `;
        document.body.appendChild(this.editModal);

        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => this.showEditModal(e));
        });

        this.editModal.querySelector('.close').addEventListener('click', () => {
            this.editModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === this.editModal) {
                this.editModal.style.display = 'none';
            }
        });

        document.getElementById('editForm').addEventListener('submit', (e) => this.handleEditSubmit(e));
    }

    showEditModal(e) {
        const btn = e.currentTarget;
        document.getElementById('editId').value = btn.dataset.contactId;
        document.getElementById('editName').value = btn.dataset.contactName;
        document.getElementById('editEmail').value = btn.dataset.contactEmail;
        document.getElementById('editMessage').value = btn.dataset.contactMessage;
        
        document.querySelectorAll('.error').forEach(el => el.textContent = '');
        this.editModal.style.display = 'block';
    }

    handleEditSubmit(e) {
        e.preventDefault();
        
        const id = document.getElementById('editId').value;
        const name = document.getElementById('editName').value.trim();
        const email = document.getElementById('editEmail').value.trim();
        const message = document.getElementById('editMessage').value.trim();
        
        if (!this.validateForm(name, email, message)) return;
        
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
            alert(error.message);
        });
    }

    validateForm(name, email, message) {
        let isValid = true;
        
        if (name.length < 2) {
            document.getElementById('nameError').textContent = 'Name must be at least 2 characters';
            isValid = false;
        }
        
        if (!email.includes('@') || !email.includes('.')) {
            document.getElementById('emailError').textContent = 'Please enter a valid email';
            isValid = false;
        }
        
        if (message.length < 10) {
            document.getElementById('messageError').textContent = 'Message must be at least 10 characters';
            isValid = false;
        }
        
        return isValid;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AdminCRUD();
});