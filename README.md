
# 🌞 SunBalance - Smart Sun Exposure Tracker ☀️

![SunBalance Logo](https://your-logo-url.com)

**SunBalance** is a web & mobile application that helps users track **UV exposure** and **Vitamin D production** based on real-time UV index data.

---

## 🚀 Features
✅ **User Authentication** (JWT-based Login & Signup)  
✅ **Real-time UV Index Data** (via OpenUV API)  
✅ **GPS & IP-based Location Support**  
✅ **Personalized Sun Exposure Recommendations**  
✅ **Sun Exposure Tracking & Analytics**  
✅ **Dark Mode Support**  

---

## 📸 Screenshots (Optional)
📌 Add images of your app UI (Frontend)

---

## 🎯 Tech Stack
### **Backend**
- 🐍 Django REST Framework (Python)  
- 🗄 PostgreSQL / SQLite  
- 🔐 JWT Authentication (SimpleJWT)  

### **Frontend** (Planned)
- ⚛️ React.js / React Native  
- 🎨 Tailwind CSS / Styled Components  

### **APIs & Integrations**
- 🌍 **OpenUV API** (Real-time UV index data)  
- 📍 **Geolocation API** (GPS & IP-based location)  

---

## 📦 Installation & Setup

### **1️⃣ Clone the Repository**
git clone https://github.com/citosina/SunBalance.git
cd SunBalance

### **2️⃣ Set Up the Virtual Environment** 
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

### **3️⃣ Install Dependencies**

pip install -r requirements.txt
### **4️⃣ Set Up Environment Variables**
Create a .env file inside the project and add:

SECRET_KEY=your-secret-key  
DEBUG=True  
DATABASE_URL=your-database-url  
OPENUV_API_KEY=your-openuv-api-key  

### **5️⃣ Apply Migrations & Start the Server**

python manage.py migrate
python manage.py runserver

##🔗 API Endpoints
📌 Base URL: http://127.0.0.1:8000/api/

## 🔐 Authentication

Method	Endpoint	Description
POST	/api/register/	Register a new user
POST	/api/login/	Authenticate and get JWT token

## ☀️ UV Data & Sun Exposure
Method	Endpoint	Description
GET	/api/smart_location_uv_index/	Get UV index (GPS/IP-based)
POST	/api/sun_exposure/	Log sun exposure

📌 More API details available in the documentation.

## 🔧 Contributing
Want to contribute? Follow these steps:
1️⃣ Fork the repository
2️⃣ Create a feature branch (git checkout -b feature-new-feature)
3️⃣ Commit changes (git commit -m "Added new feature")
4️⃣ Push to GitHub (git push origin feature-new-feature)
5️⃣ Open a Pull Request


## 🌍 Contact
👩‍💻 Created by: @citosina
📧 Email: citosina@icloud.com
🚀 Follow on Twitter: @citosina







