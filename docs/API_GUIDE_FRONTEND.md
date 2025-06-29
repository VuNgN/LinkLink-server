# 🚀 Frontend API Integration Guide

A comprehensive guide for frontend developers to integrate with the Image Upload Server API using JavaScript/TypeScript.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Authentication Flow](#-authentication-flow)
- [API Endpoints](#-api-endpoints)
- [Error Handling](#-error-handling)
- [Complete Examples](#-complete-examples)
- [TypeScript Types](#-typescript-types)
- [Best Practices](#-best-practices)

## 🚀 Quick Start

### Base Configuration

```javascript
// config.js
const API_CONFIG = {
  baseURL: 'http://localhost:8000',
  endpoints: {
    register: '/api/v1/register',
    login: '/api/v1/login',
    refresh: '/api/v1/refresh',
    logout: '/api/v1/logout',
    uploadImage: '/api/v1/upload-image',
    getImages: '/api/v1/images',
    getImage: '/api/v1/image',
    deleteImage: '/api/v1/image'
  }
};

export default API_CONFIG;
```

### API Service Class

```javascript
// apiService.js
import API_CONFIG from './config.js';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.token = localStorage.getItem('accessToken');
    this.refreshToken = localStorage.getItem('refreshToken');
  }

  // Set authorization header
  setAuthHeader(token) {
    this.token = token;
    localStorage.setItem('accessToken', token);
  }

  // Get authorization header
  getAuthHeader() {
    return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
  }

  // Make API request with automatic retry
  async makeRequest(url, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(`${this.baseURL}${url}`, config);
      
      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry the original request
          config.headers = {
            ...config.headers,
            ...this.getAuthHeader()
          };
          return await fetch(`${this.baseURL}${url}`, config);
        }
      }

      return response;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Parse JSON response
  async parseResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
}

export default ApiService;
```

## 🔐 Authentication Flow

### 1. User Registration

```javascript
// authService.js
import ApiService from './apiService.js';

class AuthService extends ApiService {
  async register(username, password) {
    const response = await this.makeRequest(API_CONFIG.endpoints.register, {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    const data = await this.parseResponse(response);
    
    // Store tokens
    this.setAuthHeader(data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    
    return data;
  }

  async login(username, password) {
    const response = await this.makeRequest(API_CONFIG.endpoints.login, {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    const data = await this.parseResponse(response);
    
    // Store tokens
    this.setAuthHeader(data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    
    return data;
  }

  async logout() {
    try {
      await this.makeRequest(API_CONFIG.endpoints.logout, {
        method: 'POST'
      });
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      // Clear tokens regardless of server response
      this.token = null;
      this.refreshToken = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }

  async refreshAccessToken() {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.refresh}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: this.refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        this.setAuthHeader(data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    // Clear invalid tokens
    this.logout();
    return false;
  }

  isAuthenticated() {
    return !!this.token;
  }
}

export default AuthService;
```

### 2. React Hook for Authentication

```javascript
// useAuth.js (React Hook)
import { useState, useEffect, useCallback } from 'react';
import AuthService from './authService.js';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const authService = new AuthService();

  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await authService.login(username, password);
      setUser({ username: data.username });
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await authService.register(username, password);
      setUser({ username: data.username });
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  }, []);

  useEffect(() => {
    // Check if user is already authenticated
    if (authService.isAuthenticated()) {
      setUser({ username: 'user' }); // You might want to decode JWT to get username
    }
    setLoading(false);
  }, []);

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user
  };
}
```

## 📸 Image Management API

### 1. Image Upload Service

```javascript
// imageService.js
import ApiService from './apiService.js';

class ImageService extends ApiService {
  async uploadImage(file) {
    // Validate file
    if (!file) {
      throw new Error('No file provided');
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error('File size exceeds 10MB limit');
    }

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.uploadImage}`, {
      method: 'POST',
      headers: this.getAuthHeader(), // Don't set Content-Type for FormData
      body: formData
    });

    return await this.parseResponse(response);
  }

  async getImages() {
    const response = await this.makeRequest(API_CONFIG.endpoints.getImages, {
      method: 'GET'
    });

    return await this.parseResponse(response);
  }

  async getImage(filename) {
    const response = await this.makeRequest(`${API_CONFIG.endpoints.getImage}/${filename}`, {
      method: 'GET'
    });

    return await this.parseResponse(response);
  }

  async deleteImage(filename) {
    const response = await this.makeRequest(`${API_CONFIG.endpoints.deleteImage}/${filename}`, {
      method: 'DELETE'
    });

    return await this.parseResponse(response);
  }

  // Get image URL for display
  getImageUrl(filename) {
    return `${this.baseURL}/uploads/${filename}`;
  }
}

export default ImageService;
```

### 2. React Hook for Image Management

```javascript
// useImages.js (React Hook)
import { useState, useCallback } from 'react';
import ImageService from './imageService.js';

export function useImages() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const imageService = new ImageService();

  const fetchImages = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await imageService.getImages();
      setImages(data.images || []);
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadImage = useCallback(async (file) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await imageService.uploadImage(file);
      
      // Add new image to list
      setImages(prev => [data, ...prev]);
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteImage = useCallback(async (filename) => {
    try {
      setError(null);
      
      await imageService.deleteImage(filename);
      
      // Remove image from list
      setImages(prev => prev.filter(img => img.filename !== filename));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  return {
    images,
    loading,
    error,
    fetchImages,
    uploadImage,
    deleteImage,
    getImageUrl: (filename) => imageService.getImageUrl(filename)
  };
}
```

## 🎯 Complete Examples

### 1. Login Component (React)

```jsx
// LoginComponent.jsx
import React, { useState } from 'react';
import { useAuth } from './useAuth.js';

export function LoginComponent() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await login(username, password);
      // Redirect or update UI
    } catch (err) {
      // Error is handled by the hook
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2>Login</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div className="form-group">
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          disabled={loading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={loading}
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### 2. Image Upload Component (React)

```jsx
// ImageUploadComponent.jsx
import React, { useState, useRef } from 'react';
import { useImages } from './useImages.js';

export function ImageUploadComponent() {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const { uploadImage, loading, error } = useImages();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = async (file) => {
    try {
      await uploadImage(file);
      // Success feedback
    } catch (err) {
      // Error is handled by the hook
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="upload-container">
      <h3>Upload Image</h3>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={loading}
        />
        
        <div className="upload-content">
          {loading ? (
            <p>Uploading...</p>
          ) : (
            <>
              <p>Drag and drop an image here, or click to select</p>
              <p className="upload-hint">
                Supported formats: JPEG, PNG, GIF, WebP (max 10MB)
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
```

### 3. Image Gallery Component (React)

```jsx
// ImageGalleryComponent.jsx
import React, { useEffect } from 'react';
import { useImages } from './useImages.js';

export function ImageGalleryComponent() {
  const { images, loading, error, fetchImages, deleteImage, getImageUrl } = useImages();

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  const handleDelete = async (filename) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await deleteImage(filename);
      } catch (err) {
        // Error is handled by the hook
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading images...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="image-gallery">
      <h3>Your Images ({images.length})</h3>
      
      {images.length === 0 ? (
        <p>No images uploaded yet.</p>
      ) : (
        <div className="image-grid">
          {images.map((image) => (
            <div key={image.filename} className="image-card">
              <img
                src={getImageUrl(image.filename)}
                alt={image.original_filename}
                className="image-thumbnail"
              />
              
              <div className="image-info">
                <p className="image-name">{image.original_filename}</p>
                <p className="image-size">
                  {(image.file_size / 1024 / 1024).toFixed(2)} MB
                </p>
                <p className="image-date">
                  {new Date(image.upload_date).toLocaleDateString()}
                </p>
              </div>
              
              <button
                onClick={() => handleDelete(image.filename)}
                className="delete-button"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## 🔧 Error Handling

### 1. Error Types and Handling

```javascript
// errorHandler.js
export class ApiError extends Error {
  constructor(message, status, code) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export function handleApiError(error) {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        // Unauthorized - redirect to login
        window.location.href = '/login';
        break;
      case 403:
        // Forbidden - show access denied
        showNotification('Access denied', 'error');
        break;
      case 404:
        // Not found
        showNotification('Resource not found', 'error');
        break;
      case 422:
        // Validation error
        showNotification(error.message, 'error');
        break;
      case 500:
        // Server error
        showNotification('Server error. Please try again later.', 'error');
        break;
      default:
        showNotification(error.message || 'An error occurred', 'error');
    }
  } else {
    // Network or other errors
    showNotification('Network error. Please check your connection.', 'error');
  }
}

function showNotification(message, type) {
  // Implement your notification system
  console.log(`${type.toUpperCase()}: ${message}`);
}
```

### 2. Global Error Handler

```javascript
// globalErrorHandler.js
import { handleApiError } from './errorHandler.js';

export function setupGlobalErrorHandler() {
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    handleApiError(event.reason);
    event.preventDefault();
  });

  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    handleApiError(event.error);
  });
}
```

## 📝 TypeScript Types

### 1. API Types

```typescript
// types/api.ts
export interface User {
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Image {
  filename: string;
  original_filename: string;
  username: string;
  file_path: string;
  file_size: number;
  content_type: string;
  upload_date: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  username: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface ImagesResponse {
  images: Image[];
  total: number;
}

export interface UploadResponse {
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  upload_date: string;
}

export interface ErrorResponse {
  detail: string;
  status_code: number;
}
```

### 2. Service Types

```typescript
// types/services.ts
export interface ApiServiceInterface {
  makeRequest(url: string, options?: RequestInit): Promise<Response>;
  parseResponse<T>(response: Response): Promise<T>;
  setAuthHeader(token: string): void;
  getAuthHeader(): Record<string, string>;
}

export interface AuthServiceInterface {
  register(username: string, password: string): Promise<AuthResponse>;
  login(username: string, password: string): Promise<AuthResponse>;
  logout(): Promise<void>;
  refreshAccessToken(): Promise<boolean>;
  isAuthenticated(): boolean;
}

export interface ImageServiceInterface {
  uploadImage(file: File): Promise<UploadResponse>;
  getImages(): Promise<ImagesResponse>;
  getImage(filename: string): Promise<Image>;
  deleteImage(filename: string): Promise<void>;
  getImageUrl(filename: string): string;
}
```

## 🎨 Best Practices

### 1. Environment Configuration

```javascript
// config/environment.js
const environments = {
  development: {
    apiUrl: 'http://localhost:8000',
    uploadMaxSize: 10 * 1024 * 1024, // 10MB
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  },
  staging: {
    apiUrl: 'https://staging-api.yourapp.com',
    uploadMaxSize: 10 * 1024 * 1024,
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  },
  production: {
    apiUrl: 'https://api.yourapp.com',
    uploadMaxSize: 10 * 1024 * 1024,
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  }
};

const currentEnv = process.env.NODE_ENV || 'development';
export const config = environments[currentEnv];
```

### 2. Request Interceptor

```javascript
// interceptors/requestInterceptor.js
export function setupRequestInterceptor(apiService) {
  // Add request logging in development
  if (process.env.NODE_ENV === 'development') {
    const originalMakeRequest = apiService.makeRequest.bind(apiService);
    
    apiService.makeRequest = async function(url, options) {
      console.log(`🚀 API Request: ${options.method || 'GET'} ${url}`, {
        headers: options.headers,
        body: options.body
      });
      
      const response = await originalMakeRequest(url, options);
      
      console.log(`📥 API Response: ${response.status} ${response.statusText}`);
      
      return response;
    };
  }
}
```

### 3. Loading States Management

```javascript
// hooks/useLoadingState.js
import { useState, useCallback } from 'react';

export function useLoadingState() {
  const [loadingStates, setLoadingStates] = useState({});

  const setLoading = useCallback((key, isLoading) => {
    setLoadingStates(prev => ({
      ...prev,
      [key]: isLoading
    }));
  }, []);

  const isLoading = useCallback((key) => {
    return loadingStates[key] || false;
  }, [loadingStates]);

  const withLoading = useCallback(async (key, asyncFunction) => {
    setLoading(key, true);
    try {
      const result = await asyncFunction();
      return result;
    } finally {
      setLoading(key, false);
    }
  }, [setLoading]);

  return {
    loadingStates,
    setLoading,
    isLoading,
    withLoading
  };
}
```

## 🧪 Testing Examples

### 1. API Service Tests

```javascript
// tests/apiService.test.js
import ApiService from '../apiService.js';

describe('ApiService', () => {
  let apiService;
  
  beforeEach(() => {
    apiService = new ApiService();
    localStorage.clear();
  });

  test('should set auth header correctly', () => {
    const token = 'test-token';
    apiService.setAuthHeader(token);
    
    expect(apiService.token).toBe(token);
    expect(localStorage.getItem('accessToken')).toBe(token);
  });

  test('should get auth header correctly', () => {
    const token = 'test-token';
    apiService.setAuthHeader(token);
    
    const headers = apiService.getAuthHeader();
    expect(headers).toEqual({ 'Authorization': `Bearer ${token}` });
  });

  test('should handle missing token', () => {
    const headers = apiService.getAuthHeader();
    expect(headers).toEqual({});
  });
});
```

### 2. Component Tests

```javascript
// tests/LoginComponent.test.jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginComponent } from '../LoginComponent.jsx';
import { useAuth } from '../useAuth.js';

// Mock the useAuth hook
jest.mock('../useAuth.js');

describe('LoginComponent', () => {
  const mockLogin = jest.fn();
  
  beforeEach(() => {
    useAuth.mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null
    });
  });

  test('should render login form', () => {
    render(<LoginComponent />);
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('should call login on form submit', async () => {
    render(<LoginComponent />);
    
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'testpass' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser', 'testpass');
    });
  });
});
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [React Hooks Documentation](https://reactjs.org/docs/hooks-intro.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Support

If you encounter any issues or have questions about the API integration:

1. Check the [Authentication Testing Guide](AUTHENTICATION_TESTING.md)
2. Review the [Code Explanation](CODE_EXPLANATION.md)
3. Open an issue on GitHub
4. Check the API documentation at `http://localhost:8000/docs`

---

**Happy coding! 🚀** 