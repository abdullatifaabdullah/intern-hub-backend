# Frontend Integration Guide

This guide outlines everything you need to know to connect your frontend to the InternHub backend.

## 📍 **Backend Connection Details**

### Base URL
- **Development**: `http://localhost:8000`
- **API Prefix**: All endpoints are prefixed with `/api/v2`
- **Full Base URL**: `http://localhost:8000/api/v2`

### Health Check
- **Endpoint**: `GET http://localhost:8000/healthz`
- **Response**: `{ "status": "ok", ... }`

---

## 🔐 **Authentication (JWT-Based)**

### Token Flow
1. **Sign In** → Get access token + refresh token
2. **Store tokens** (access token in memory, refresh token in localStorage/cookies)
3. **Include access token** in Authorization header for all protected requests
4. **Refresh access token** when it expires (30 minutes) using refresh token
5. **Sign Out** → Clear tokens

### Authentication Endpoints

#### 1. Sign In
```http
POST /api/v2/auth/sign-in
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,  // seconds (30 minutes)
  "refresh_token": "eyJhbGc..."  // optional, 30 days validity
}
```

#### 2. Refresh Access Token
```http
POST /api/v2/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

**Response:** Same as sign-in (new access_token + refresh_token)

#### 3. Get Current User
```http
GET /api/v2/auth/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "student"  // or "admin"
}
```

#### 4. Sign Out
```http
POST /api/v2/auth/sign-out
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."  // optional
}
```

### Implementation Notes

**Required Headers for Protected Routes:**
```javascript
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json"
}
```

**Token Storage Recommendations:**
- **Access Token**: Store in memory (React state/context) or httpOnly cookie (more secure)
- **Refresh Token**: Store in localStorage or httpOnly cookie
- **Never store tokens in regular cookies** (XSS risk)

**Token Expiration:**
- Access token: **30 minutes**
- Refresh token: **30 days** (43200 minutes)
- Implement automatic token refresh before expiration

---

## 👥 **User Roles**

The system has two user roles:
- **`student`**: Can apply to internships, view own applications
- **`admin`**: Can create/edit/delete internships, view all applications, manage application statuses

### Role-Based Endpoints

**Student-Only:**
- `POST /api/v2/internships/{id}/applications` - Apply to internship
- `GET /api/v2/applications/me` - View own applications

**Admin-Only:**
- `POST /api/v2/internships` - Create internship
- `PATCH /api/v2/internships/{id}` - Update internship
- `DELETE /api/v2/internships/{id}` - Delete internship
- `GET /api/v2/internships/me` - View own created internships
- `GET /api/v2/internships/{id}/applications` - View applications for an internship
- `PATCH /api/v2/applications/{id}` - Update application status

---

## 📚 **API Endpoints Reference**

### Internships

#### List All Internships
```http
GET /api/v2/internships?page=1&limit=20&sort=-created_at&include[]=creator
```

**Query Parameters:**
- `page` (default: 1, min: 1)
- `limit` (default: 20, min: 1, max: 100)
- `sort` (optional): `-created_at` (newest first), `created_at` (oldest first), `title`, etc.
- `include[]` (optional): `creator` to include creator user info

**Response:**
```json
[
  {
    "id": 1,
    "title": "Software Engineering Intern",
    "description": "...",
    "company": "Tech Corp",
    "location": "Remote",
    "application_deadline": "2024-12-31T23:59:59",
    "created_at": "2024-01-01T00:00:00",
    "created_by": 1
  }
]
```

#### Get Internship by ID
```http
GET /api/v2/internships/{id}?include[]=creator
```

#### Create Internship (Admin Only)
```http
POST /api/v2/internships
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Software Engineering Intern",
  "description": "We are looking for...",
  "company": "Tech Corp",
  "location": "Remote",
  "application_deadline": "2024-12-31T23:59:59"
}
```

#### Update Internship (Admin Only)
```http
PATCH /api/v2/internships/{id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title",  // All fields optional
  "description": "...",
  "company": "...",
  "location": "...",
  "application_deadline": "2024-12-31T23:59:59"
}
```

#### Delete Internship (Admin Only)
```http
DELETE /api/v2/internships/{id}
Authorization: Bearer {access_token}
```

#### List My Created Internships (Admin Only)
```http
GET /api/v2/internships/me?page=1&limit=20&include[]=creator
```

### Applications

#### Apply to Internship (Student Only)
```http
POST /api/v2/internships/{internship_id}/applications
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "cover_letter": "I am interested in..."  // optional
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "internship_id": 1,
  "cover_letter": "I am interested in...",
  "status": null,  // null initially
  "created_at": "2024-01-01T00:00:00"
}
```

#### List My Applications (Student Only)
```http
GET /api/v2/applications/me?page=1&limit=20&include[]=internship&sort=-created_at
```

**Query Parameters:**
- `include[]=internship` - Include full internship details
- `page`, `limit`, `sort` - Same as internships

#### List Applications for Internship (Admin Only)
```http
GET /api/v2/internships/{internship_id}/applications?include[]=user&page=1&limit=20
```

**Query Parameters:**
- `include[]=user` - Include applicant user info

#### Update Application Status (Admin Only)
```http
PATCH /api/v2/applications/{application_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "accepted"  // or "rejected", "pending", etc.
}
```

### Users

#### Get Current User Info
```http
GET /api/v2/users/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "student"
}
```

---

## 🌐 **CORS Configuration**

The backend is currently configured to allow requests from:
- `http://localhost:3000` (default React dev server)

**If your frontend runs on a different port**, update `CORS_ORIGINS` in the backend's `.env` file:

```env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]  # Vite default
```

Or modify `app/core/config.py` if needed.

---

## ⚠️ **Error Handling**

### Common HTTP Status Codes

- **200**: Success
- **201**: Created (for POST requests)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (missing/invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Authentication Errors

When you receive a `401 Unauthorized`:
1. Try refreshing the access token using the refresh token
2. If refresh fails, redirect to login page
3. Clear all stored tokens

---

## 📝 **Data Models**

### User
```typescript
interface User {
  id: number;
  email: string;
  role: "admin" | "student";
}
```

### Internship
```typescript
interface Internship {
  id: number;
  title: string;
  description: string;
  company: string;
  location: string | null;
  application_deadline: string;  // ISO 8601 datetime
  created_at: string;  // ISO 8601 datetime
  created_by: number;  // User ID of creator
  creator?: User;  // Optional, included when ?include[]=creator
}
```

### Application
```typescript
interface Application {
  id: number;
  user_id: number;
  internship_id: number;
  cover_letter: string | null;
  status: string | null;  // e.g., "pending", "accepted", "rejected"
  created_at: string;  // ISO 8601 datetime
  internship?: Internship;  // Optional, included when ?include[]=internship
  user?: User;  // Optional, included when ?include[]=user
}
```

---

## 🛠️ **Frontend Implementation Checklist**

### Setup
- [ ] Configure API base URL: `http://localhost:8000/api/v2`
- [ ] Set up HTTP client (axios, fetch, etc.) with base URL
- [ ] Configure CORS if frontend runs on different port

### Authentication
- [ ] Implement sign-in form and API call
- [ ] Store access token (memory or httpOnly cookie)
- [ ] Store refresh token (localStorage or httpOnly cookie)
- [ ] Add Authorization header to all protected requests
- [ ] Implement automatic token refresh before expiration
- [ ] Handle 401 errors with token refresh or redirect to login
- [ ] Implement sign-out functionality

### User Management
- [ ] Fetch current user info on app load (`/auth/me`)
- [ ] Store user role for conditional rendering
- [ ] Implement role-based route protection

### Internships
- [ ] List all internships with pagination
- [ ] Display internship details
- [ ] (Admin) Create internship form
- [ ] (Admin) Edit internship form
- [ ] (Admin) Delete internship with confirmation
- [ ] Filter/sort internships

### Applications
- [ ] (Student) Apply to internship form
- [ ] (Student) List my applications with internship details
- [ ] (Admin) List applications for an internship
- [ ] (Admin) Update application status

### Error Handling
- [ ] Global error handler for API errors
- [ ] Display user-friendly error messages
- [ ] Handle network errors
- [ ] Handle token expiration gracefully

### UI/UX
- [ ] Loading states for async operations
- [ ] Empty states for no data
- [ ] Form validation (client-side)
- [ ] Responsive design
- [ ] Accessible forms and buttons

---

## 🔧 **Example Frontend Code Snippets**

### Axios Setup with Interceptors

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v2',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = getAccessToken(); // Your token getter
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const newToken = await refreshAccessToken();
        // Retry original request with new token
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return api.request(error.config);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

### React Hook Example

```typescript
import { useState, useEffect } from 'react';
import api from './api';

function useInternships(page = 1, limit = 20) {
  const [internships, setInternships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchInternships() {
      try {
        setLoading(true);
        const response = await api.get('/internships', {
          params: { page, limit, sort: '-created_at' }
        });
        setInternships(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchInternships();
  }, [page, limit]);

  return { internships, loading, error };
}
```

---

## 📌 **Important Notes**

1. **Token Security**: Never expose tokens in URLs, logs, or error messages
2. **HTTPS in Production**: Always use HTTPS for production deployments
3. **Environment Variables**: Use environment variables for API base URL
4. **Type Safety**: Use TypeScript if possible for type safety
5. **Date Handling**: All dates are in ISO 8601 format (UTC)
6. **Pagination**: Always implement pagination for list endpoints
7. **Rate Limiting**: Be mindful of API call frequency (currently no rate limiting configured)

---

## 🚀 **Testing Your Connection**

1. **Start the backend**: Run `start.bat` or `uvicorn app.main:app --reload`
2. **Check health**: `GET http://localhost:8000/healthz`
3. **Test sign-in**: Use default admin credentials:
   - Email: `admin@internhub.local`
   - Password: `ChangeMe123!`
4. **Test protected endpoint**: Use the returned access token

---

## 📞 **Need Help?**

- Check backend logs for detailed error messages
- Verify CORS settings match your frontend URL
- Ensure tokens are being sent in Authorization header
- Check network tab in browser DevTools for request/response details





