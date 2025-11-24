# VPS Deployment Steps

## 🚀 Deploy Latest Changes to VPS

### Step 1: SSH into VPS
```bash
ssh root@your-vps-ip
# or
ssh your-username@your-vps-ip
```

### Step 2: Navigate to Project Directory
```bash
cd /path/to/madrasha
# Common paths: /var/www/madrasha or /home/user/madrasha
```

### Step 3: Pull Latest Code
```bash
git pull origin main
```

### Step 4: Run Database Migration
```bash
python3 migrate_vps_database.py
```

This will:
- ✅ Create `masala` table for Islamic content
- ✅ Add `sms_count` column to `user` table
- ✅ Create `sms_log` table for audit trail
- ✅ Preserve all existing data

### Step 5: Restart Application
```bash
# If using systemd
sudo systemctl restart madrasha

# If using gunicorn directly
sudo systemctl restart gunicorn

# If using supervisor
sudo supervisorctl restart madrasha

# Or kill and restart manually
pkill -f "gunicorn"
gunicorn -c gunicorn.conf.py app:app
```

### Step 6: Verify Deployment
```bash
# Check application status
sudo systemctl status madrasha

# Check logs
sudo journalctl -u madrasha -f

# Or check log file
tail -f /var/log/madrasha/error.log
```

### Step 7: Test the Application
Visit your VPS URL and test:
- ✅ Login with existing accounts
- ✅ Super Admin SMS management
- ✅ Teacher Masala posting
- ✅ Junior Ustad login (create new account: phone 01700000002, password 123456)
- ✅ Student login

## 🔑 Test Credentials

### Create Junior Ustad Account (if not exists)
```bash
python3 << 'EOF'
from app import app, db
from models import User, UserRole
from werkzeug.security import generate_password_hash

app.app_context().push()

# Check if Junior Ustad exists
ju = User.query.filter_by(phoneNumber='01700000002').first()
if not ju:
    ju = User(
        first_name='Junior',
        last_name='Ustad',
        phoneNumber='01700000002',
        password_hash=generate_password_hash('123456'),
        role=UserRole.JUNIOR_USTADH,
        sms_count=0
    )
    db.session.add(ju)
    db.session.commit()
    print("✅ Junior Ustad created")
else:
    print("✓ Junior Ustad already exists")
EOF
```

## 🆕 New Features in This Release

### 1. Masala System
- Teachers can post Islamic stories/articles
- Categories: হাদিস (Hadith), কুরআন (Quran), সিরাত (Seerah), ফিকহ (Fiqh), আদব (Adab)
- Facebook and WhatsApp sharing
- Homepage display of latest 3 posts

### 2. SMS Credit Management
- Super Admin can add/deduct SMS credits
- Positive values: add credits (+100)
- Negative values: deduct credits (-50)
- Overdraft protection
- Full audit logging

### 3. Junior Ustad Role
- New user role for assistant teachers
- Same capabilities as regular teachers
- Separate role identification

### 4. UI Updates
- Bengali study modes terminology
- Baby Class added to batch system
- Limited subjects: Bangla, English, Math, Arabic
- Contact information in footer

## 🔍 Troubleshooting

### Migration Fails
```bash
# Check database connection
python3 -c "from app import app, db; app.app_context().push(); print(db.engine.url)"

# Manual table creation
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Tables created')"
```

### Application Won't Start
```bash
# Check Python dependencies
pip3 install -r requirements.txt

# Check configuration
python3 -c "from app import app; print(app.config)"

# Check port availability
sudo lsof -i :5000
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/madrasha
sudo chmod -R 755 /path/to/madrasha
```

## 📊 Verify Database Changes

```bash
python3 << 'EOF'
from app import app, db
from sqlalchemy import inspect

app.app_context().push()

inspector = inspect(db.engine)

print("\n=== TABLES ===")
for table in inspector.get_table_names():
    print(f"✓ {table}")

print("\n=== USER TABLE COLUMNS ===")
for col in inspector.get_columns('user'):
    print(f"  - {col['name']}: {col['type']}")

print("\n=== MASALA TABLE COLUMNS ===")
if 'masala' in inspector.get_table_names():
    for col in inspector.get_columns('masala'):
        print(f"  - {col['name']}: {col['type']}")
else:
    print("  ⚠ Masala table not found")
EOF
```

## ✅ Post-Deployment Checklist

- [ ] Code pulled from GitHub
- [ ] Database migration completed
- [ ] Application restarted
- [ ] No errors in logs
- [ ] Super Admin login works
- [ ] Teacher login works
- [ ] Junior Ustad login works
- [ ] Student login works
- [ ] SMS credit add/deduct works
- [ ] Masala posting works
- [ ] Homepage loads correctly
- [ ] Browser cache cleared for testing

---

**Need Help?** Check logs at `/var/log/madrasha/` or run `sudo journalctl -u madrasha -f`
