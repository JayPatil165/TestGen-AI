/**
 * Sample JavaScript module for testing scanner.
 * This file contains various JS/ES6 constructs.
 */

// Simple function
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow function
const add = (a, b) => a + b;

// Function with default params
function createUser(name, email, role = 'user') {
    return {
        name,
        email,
        role,
        createdAt: new Date()
    };
}

// Async function
async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
}

// Class definition
class UserManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.users = [];
    }
    
    async getUser(id) {
        const user = this.users.find(u => u.id === id);
        return user || null;
    }
    
    addUser(user) {
        this.users.push(user);
        return user;
    }
    
    removeUser(id) {
        const index = this.users.findIndex(u => u.id === id);
        if (index !== -1) {
            this.users.splice(index, 1);
            return true;
        }
        return false;
    }
}

// Class extending another
class AdminManager extends UserManager {
    constructor(apiUrl) {
        super(apiUrl);
        this.permissions = ['read', 'write', 'delete'];
    }
    
    hasPermission(permission) {
        return this.permissions.includes(permission);
    }
}

// Export
export { greet, add, createUser, fetchUserData, UserManager, AdminManager };
