/**
 * Login Service - Extendable Authentication System
 * This module handles user authentication and session management
 */

class AuthService {
  constructor(config = {}) {
    this.config = {
      authServiceUrl: config.authServiceUrl || "http://auth-service:8081",
      tokenKey: config.tokenKey || "auth_token",
      userKey: config.userKey || "user_info",
      rememberMeKey: config.rememberMeKey || "remember_me",
      onSuccess: config.onSuccess || this.defaultOnSuccess,
      onError: config.onError || this.defaultOnError,
      ...config,
    };

    this.token = localStorage.getItem(this.config.tokenKey);
    this.user = JSON.parse(localStorage.getItem(this.config.userKey) || "null");
  }

  /**
   * Authenticate user with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {boolean} rememberMe - Whether to persist login
   * @returns {Promise}
   */
  async login(email, password, rememberMe = false) {
    try {
      const response = await fetch(`${this.config.authServiceUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Login failed");
      }

      const data = await response.json();

      // Store token and user info
      this.token = data.token;
      this.user = data.user || { email };

      localStorage.setItem(this.config.tokenKey, this.token);
      localStorage.setItem(this.config.userKey, JSON.stringify(this.user));

      if (rememberMe) {
        localStorage.setItem(this.config.rememberMeKey, "true");
      } else {
        localStorage.removeItem(this.config.rememberMeKey);
      }

      this.config.onSuccess(this.user);
      return data;
    } catch (error) {
      this.config.onError(error.message);
      throw error;
    }
  }

  /**
   * Logout user and clear session
   */
  logout() {
    this.token = null;
    this.user = null;
    localStorage.removeItem(this.config.tokenKey);
    localStorage.removeItem(this.config.userKey);
    localStorage.removeItem(this.config.rememberMeKey);
  }

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.token;
  }

  /**
   * Get current user
   * @returns {object|null}
   */
  getCurrentUser() {
    return this.user;
  }

  /**
   * Get auth token
   * @returns {string|null}
   */
  getToken() {
    return this.token;
  }

  /**
   * Check if user should be remembered
   * @returns {boolean}
   */
  shouldRememberMe() {
    return localStorage.getItem(this.config.rememberMeKey) === "true";
  }

  /**
   * Validate email format
   * @param {string} email
   * @returns {boolean}
   */
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate password requirements
   * @param {string} password
   * @returns {object} {isValid, errors}
   */
  validatePassword(password) {
    const errors = [];

    if (password.length < 6) {
      errors.push("Password must be at least 6 characters");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Default success callback
   * @param {object} user
   */
  defaultOnSuccess(user) {
    console.log("Login successful:", user);
    // Redirect to dashboard or home page
    setTimeout(() => {
      // Use a relative path so the browser navigates to the index.html in the
      // same folder as the current page. A leading slash ("/index.html")
      // becomes an absolute path which, when opened via file://, points to
      // the filesystem root (e.g. C://index.html).
      window.location.href = "./index.html";
    }, 1500);
  }

  /**
   * Default error callback
   * @param {string} message
   */
  defaultOnError(message) {
    console.error("Login error:", message);
  }
}

/**
 * UI Controller for Login Form
 */
class LoginUIController {
  constructor(authService) {
    this.authService = authService;
    this.form = document.getElementById("loginForm");
    this.emailInput = document.getElementById("email");
    this.passwordInput = document.getElementById("password");
    this.rememberMeCheckbox = document.getElementById("rememberMe");
    this.loginBtn = document.getElementById("loginBtn");
    this.errorMessage = document.getElementById("errorMessage");
    this.successMessage = document.getElementById("successMessage");

    this.init();
  }

  init() {
    if (!this.form) {
      console.error("Login form not found");
      return;
    }

    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
    this.setupRememberMe();
  }

  /**
   * Handle form submission
   * @param {Event} e
   */
  async handleSubmit(e) {
    e.preventDefault();

    const email = this.emailInput.value.trim();
    const password = this.passwordInput.value;
    const rememberMe = this.rememberMeCheckbox.checked;

    // Clear previous messages
    this.clearMessages();

    // Validate inputs
    if (!this.validateForm(email, password)) {
      return;
    }

    // Disable submit button and show loading state
    this.setLoading(true);

    try {
      await this.authService.login(email, password, rememberMe);
      this.showSuccess("Login successful! Redirecting...");
    } catch (error) {
      this.showError(error.message || "Login failed. Please try again.");
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Validate form inputs
   * @param {string} email
   * @param {string} password
   * @returns {boolean}
   */
  validateForm(email, password) {
    if (!email || !password) {
      this.showError("Please fill in all fields");
      return false;
    }

    if (!this.authService.validateEmail(email)) {
      this.showError("Please enter a valid email address");
      return false;
    }

    const passwordValidation = this.authService.validatePassword(password);
    if (!passwordValidation.isValid) {
      this.showError(passwordValidation.errors[0]);
      return false;
    }

    return true;
  }

  /**
   * Show error message
   * @param {string} message
   */
  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.style.display = "block";
    this.successMessage.style.display = "none";
  }

  /**
   * Show success message
   * @param {string} message
   */
  showSuccess(message) {
    this.successMessage.textContent = message;
    this.successMessage.style.display = "block";
    this.errorMessage.style.display = "none";
  }

  /**
   * Clear all messages
   */
  clearMessages() {
    this.errorMessage.style.display = "none";
    this.successMessage.style.display = "none";
  }

  /**
   * Set loading state
   * @param {boolean} isLoading
   */
  setLoading(isLoading) {
    this.loginBtn.disabled = isLoading;
    if (isLoading) {
      this.loginBtn.innerHTML = '<span class="spinner"></span>Logging in...';
    } else {
      this.loginBtn.innerHTML = "Login";
    }
  }

  /**
   * Setup remember me functionality
   */
  setupRememberMe() {
    if (this.authService.shouldRememberMe()) {
      this.rememberMeCheckbox.checked = true;
      // Optionally pre-fill email for returning users
      const user = this.authService.getCurrentUser();
      if (user && user.email) {
        this.emailInput.value = user.email;
      }
    }
  }
}
// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Create auth service instance with custom config
  const authService = new AuthService({
    authServiceUrl: window.__ENV__["AUTH_SERVICE_URL"],
    // Custom callbacks can be added here
  });

  // Initialize UI controller
  new LoginUIController(authService);
});
