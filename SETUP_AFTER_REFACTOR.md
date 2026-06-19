# Backend Refactor — Setup Instructions

Yeh backend ab custom-role architecture pe hai. Sirf Super Admin system role hai.
Baaki sab roles custom hain, har organization apne banati hai.

## IMPORTANT — Pehle Database Khali Karo

Yeh refactor purane role system se alag hai, isliye DB fresh chahiye.

### Step 1 — Purani files replace karo
Is backend folder ko apne existing backend se replace karo.
(Apni .env file safe rakhna — woh ismein nahi hai.)

### Step 2 — .env banao (agar nahi hai)
backend/.env mein yeh hona chahiye:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 3 — Database bilkul khali karo
PostgreSQL mein (pgAdmin ya psql se):
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```
Ya poora database drop karke naya banao.

### Step 4 — Fresh migrations banao aur apply karo
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 5 — Permissions seed karo
```bash
python manage.py seed_permissions
```
Yeh saari permissions (leads.view, leads.export, employees.create, etc.) database mein daalega.

### Step 6 — Organization 1 + Super Admin banao
```bash
python manage.py seed_organization --email owner@yourcompany.com --password YourPass@123 --name "Owner Name"
```
Yeh banayega:
- Organization 1 (is_primary=True) — owner ki organization
- Super Admin user us organization ke andar

Login credentials wahi hongi jo tumne upar di.

---

## Naya Architecture — Kaise Kaam Karta Hai

### Roles
- **Super Admin** — sirf yeh system role hai (is_super_admin flag). Owner.
  - Saari permissions + organizations bana sakta hai (sirf Org 1 ka super admin)
  - Apna account delete nahi kar sakta, sirf profile edit
- **Custom roles** — har organization apne banati hai (Roles page se)
  - Har role = permissions ka set
  - Frontend dashboard + sidebar inhi permissions se dynamic banta hai

### User Creation Rules
- Koi user bina organization + role ke nahi ban sakta
- Employee banate waqt kam se kam ek custom role zaroori (required)
- Har user kisi na kisi organization ka hissa hota hai

### Organization Creation
- Sirf Organization 1 (primary) ka Super Admin nayi organizations bana sakta hai
- API: POST /api/tenant/organizations/
- Kisi aur org ka koi user organization nahi bana sakta

### Permission Enforcement
Har API view pe specific permission check hai:
- GET leads → leads.view
- POST leads → leads.create
- export → leads.export
- etc.

"view_all" permission ka matlab: poori organization ka data dikhe.
Agar nahi hai, toh user sirf apni assigned cheezein dekhta hai.

---

## API Changes (frontend ko inki zaroorat)

### Login response ab yeh deta hai:
```json
{
  "access": "...",
  "refresh": "...",
  "user": {
    "id": 1,
    "email": "...",
    "full_name": "...",
    "is_super_admin": false,
    "tenant": { "id": 2, "name": "...", "is_primary": false, "features": {...} },
    "roles": ["Manager"],
    "permissions": ["leads.view", "leads.create", "clients.view", ...]
  }
}
```

Frontend ko `permissions` array se dashboard aur sidebar banana hai.

### Removed endpoints:
- POST /api/auth/register/ (self-register hata)
- POST /api/tenant/register/ (public tenant register hata)

### New endpoints:
- POST /api/tenant/organizations/ (super admin org banata hai)

### Employee creation ab role_ids required:
POST /api/auth/employees/
```json
{
  "full_name": "...", "email": "...", "password": "...",
  "role_ids": [1]   // REQUIRED — kam se kam ek custom role
}
```

---

## UPDATE — Departments Ab Custom Hain

Pehle departments hardcoded the (sales/tech/seo). Ab fully custom:
- Har organization apne departments banati hai (Departments page se)
- Leads/Clients/Tasks/Reports/Delivery ab department se proper FK link rakhte hain
- Department create karne ke liye `departments.create` permission chahiye

API:
- POST /api/departments/ — naya department (name, description, head)
- Leads/clients banate waqt department field mein department ID bhejni hoti hai (optional)

Bulk upload mein department column mein department ka **naam** likho —
system automatically us naam se department dhoondh ke link karega.
