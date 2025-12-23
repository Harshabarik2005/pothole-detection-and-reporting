const API_URL = "http://localhost:8000";

class API {
    static get token() {
        return localStorage.getItem('token');
    }

    static async request(endpoint, options = {}) {
        const headers = {
            ...options.headers,
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        const response = await fetch(`${API_URL}${endpoint}`, config);
        if (response.status === 401) {
            window.location.href = 'login.html';
            return;
        }
        return response;
    }

    static async login(username, password) {
        const res = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            const txt = await res.text();
            try {
                const err = JSON.parse(txt);
                throw new Error(err.detail || 'Login failed');
            } catch (e) {
                if (e.message !== 'Login failed') throw e; // Pydantic/JSON error
                throw new Error(txt || 'Login failed');
            }
        }
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);
        localStorage.setItem('username', data.username);
        return data;
    }

    static async register(username, password, role) {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        if (!res.ok) {
            const txt = await res.text();
            const err = JSON.parse(txt);
            throw new Error(err.detail || 'Registration failed');
        }
        return await res.json();
    }

    static async getMyComplaints() {
        const res = await this.request('/complaints/my');
        return await res.json();
    }

    static async getAllComplaints() {
        const res = await this.request('/complaints/all');
        return await res.json();
    }

    static async submitComplaint(formData) {
        // FormData handles content-type automatically
        const res = await this.request('/complaints/', {
            method: 'POST',
            body: formData
        });
        if (!res.ok) throw new Error('Submission failed');
        return await res.json();
    }

    static async updateStatus(id, status) {
        const res = await this.request(`/complaints/${id}/status?status=${status}`, {
            method: 'PUT'
        });
        if (!res.ok) throw new Error('Update failed');
        return await res.json();
    }

    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        window.location.href = 'login.html';
    }
}
