# 🌐 Minimal Frontend for Matatu Fleet Management System

This is a **minimal, functional frontend** that directly interfaces with your FastAPI backend. It's designed for testing, development, and as a foundation for your future frontend development.

## 🎯 Features

### ✅ **Implemented Features**
- **System Health Check** - Monitor backend services status
- **Authentication** - Login, register, logout functionality
- **Manager Functions**:
  - Driver registration with unique ID generation
  - Vehicle registration with GPS integration
  - View drivers and vehicles lists
- **Admin Functions**:
  - Fleet management
  - User management
- **Real-time API Response Display** - See all API calls and responses
- **Role-based UI** - Different sections for different user roles

### 🔧 **Technical Features**
- **No Dependencies** - Pure HTML, CSS, JavaScript
- **CORS Support** - Built-in CORS handling
- **Token Management** - Automatic JWT token storage and usage
- **Error Handling** - Clear error and success messages
- **Responsive Design** - Works on desktop and mobile
- **API Documentation** - Direct links to Swagger docs

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)
```bash
# Start both backend and frontend
./start-dev.sh
```

### Option 2: Manual Start
```bash
# 1. Start backend services
docker-compose up -d

# 2. Start frontend server
cd frontend
python3 server.py
```

### Option 3: Direct File Access
Simply open `frontend/index.html` in your browser (may have CORS issues)

## 🔗 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🧪 Testing Workflow

### 1. **System Health Check**
- Click "Check System Health" to verify all services are running
- Should show: Database ✅, Redis ✅, Supabase ✅

### 2. **Get Manager Token (Quick Test)**
- Click "Get Manager Test Token" for instant access
- This creates a test manager token for Samuel Rembo

### 3. **Test Manager Functions**
```
Driver Registration:
- First Name: John
- Last Name: Doe  
- Phone: +254712345678
- License: DL123456789

Vehicle Registration:
- Fleet Number: KCS-001
- License Plate: KCA123A
- Capacity: 14
- Route: Nairobi-Thika
- GPS Device ID: GPS001
```

### 4. **View Data**
- Click "Get Drivers" to see registered drivers
- Click "Get Vehicles" to see registered vehicles

## 📋 API Endpoints Covered

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /debug/create-manager-token` - Test token creation

### Manager Functions
- `POST /api/v1/manager/drivers` - Register driver
- `GET /api/v1/manager/drivers` - List drivers
- `POST /api/v1/manager/vehicles` - Register vehicle
- `GET /api/v1/manager/vehicles` - List vehicles

### Admin Functions
- `GET /api/v1/admin/fleets` - List fleets
- `GET /api/v1/admin/users` - List users

### System
- `GET /health` - Health check

## 🎨 UI Structure

```
🏥 System Health
├── Health check button and status

🔐 Authentication  
├── Login form (phone + password)
├── Registration form (phone + name + role)
└── Manager test token button

👨‍💼 Manager Functions (Manager role only)
├── Driver Registration form
├── Vehicle Registration form  
└── View data buttons

👑 Admin Functions (Admin role only)
├── Fleet management
└── User management

📋 API Responses
└── Real-time display of all API calls
```

## 🔧 Customization

### Adding New Endpoints
1. Add HTML form in the appropriate section
2. Create JavaScript function to call the API
3. Use the `apiCall()` utility function

Example:
```javascript
async function newFunction() {
    const data = { field: 'value' };
    await apiCall('/new/endpoint', 'POST', data, true);
}
```

### Styling
- Modify the `<style>` section in `index.html`
- Current styling is minimal and functional
- Easy to replace with CSS frameworks later

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs auth-service

# Restart services
docker-compose restart
```

### CORS Issues
- Use the Python server (`python3 server.py`)
- Don't open HTML file directly in browser

### Port Conflicts
- Backend: Change port in `docker-compose.yml`
- Frontend: Change `PORT` in `server.py`

## 🚀 Next Steps

This minimal frontend gives you:
1. **Working interface** to test all backend functionality
2. **Foundation** for building a proper frontend
3. **API integration examples** for your development team
4. **Testing tool** for backend development

### Future Enhancements
- Add CSS framework (Bootstrap, Tailwind)
- Implement proper form validation
- Add data tables with sorting/filtering
- Create separate pages for different functions
- Add real-time updates with WebSockets
- Implement proper error handling UI

## 📝 Notes

- **Security**: This is for development only - don't use in production
- **Data**: All test data is stored in your PostgreSQL database
- **Tokens**: JWT tokens are stored in localStorage
- **CORS**: Built-in CORS support for API calls

---

**Happy Testing! 🎉**

This minimal frontend mirrors your backend exactly and gives you a solid foundation to build upon!
