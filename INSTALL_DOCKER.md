# Docker Desktop Installation Guide

## Step-by-Step Installation

### 1. Download Docker Desktop

**Direct Download Link**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

Or visit: https://www.docker.com/products/docker-desktop/

### 2. System Requirements

Before installing, ensure your system meets these requirements:

#### Windows Requirements
- ✅ Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- ✅ OR Windows 11 64-bit
- ✅ 4GB RAM minimum (8GB recommended)
- ✅ BIOS-level hardware virtualization support enabled

#### Check Your Windows Version
```powershell
# Run in PowerShell
winver
```

### 3. Enable WSL 2 (Required)

Docker Desktop uses WSL 2 backend on Windows.

#### Enable WSL 2
```powershell
# Run PowerShell as Administrator

# Enable WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer
Restart-Computer
```

#### After Restart - Set WSL 2 as Default
```powershell
# Run PowerShell as Administrator
wsl --set-default-version 2

# Install Ubuntu (optional but recommended)
wsl --install -d Ubuntu
```

### 4. Install Docker Desktop

1. **Run the Installer**
   - Double-click `Docker Desktop Installer.exe`
   - If prompted by User Account Control, click **Yes**

2. **Configuration Options**
   - ✅ **Use WSL 2 instead of Hyper-V** (recommended)
   - ✅ **Add shortcut to desktop** (optional)

3. **Wait for Installation**
   - Installation takes 5-10 minutes
   - Do not interrupt the process

4. **Restart Computer**
   - Click **Close and restart** when prompted
   - Or restart manually

### 5. Start Docker Desktop

1. **Launch Docker Desktop**
   - Find Docker Desktop in Start Menu
   - Or click desktop shortcut
   - Wait for Docker to start (whale icon in system tray)

2. **Accept Terms**
   - Accept Docker Subscription Service Agreement
   - Choose to send usage statistics (optional)

3. **Wait for Docker Engine to Start**
   - Look for "Docker Desktop is running" message
   - Whale icon in system tray should be steady (not animated)

### 6. Verify Installation

Open PowerShell or Command Prompt and run:

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Run test container
docker run hello-world
```

**Expected Output**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### 7. Configure Docker Desktop (Optional)

1. **Open Docker Desktop Settings**
   - Right-click whale icon in system tray
   - Click **Settings**

2. **Recommended Settings**:

   **General**:
   - ✅ Start Docker Desktop when you log in
   - ✅ Use WSL 2 based engine

   **Resources**:
   - **CPUs**: 4 (or half of your total)
   - **Memory**: 4GB (or 25% of your RAM)
   - **Disk**: 60GB

   **Docker Engine**:
   ```json
   {
     "builder": {
       "gc": {
         "defaultKeepStorage": "20GB",
         "enabled": true
       }
     },
     "experimental": false
   }
   ```

### 8. Test with PCA Agent

Once Docker is installed, test with PCA Agent:

```powershell
# Navigate to project
cd "c:\Users\asharm08\OneDrive - dentsu\Desktop\windsurf\PCA_Agent"

# Test Docker
docker --version

# Start PCA Agent with Docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Access services
# API: http://localhost:8000
# Streamlit: http://localhost:8501
# Grafana: http://localhost:3000
```

---

## Troubleshooting

### Issue 1: WSL 2 Installation Failed

**Solution**:
```powershell
# Download and install WSL 2 kernel update
# Visit: https://aka.ms/wsl2kernel
# Or run:
wsl --update
```

### Issue 2: Virtualization Not Enabled

**Solution**:
1. Restart computer
2. Enter BIOS/UEFI (usually F2, F10, or Del during boot)
3. Find "Virtualization Technology" or "Intel VT-x" or "AMD-V"
4. Enable it
5. Save and exit

### Issue 3: Docker Desktop Won't Start

**Solution**:
```powershell
# Reset Docker Desktop
# 1. Quit Docker Desktop
# 2. Run PowerShell as Administrator
# 3. Run:
wsl --shutdown
net stop com.docker.service
net start com.docker.service
```

### Issue 4: "Docker daemon is not running"

**Solution**:
1. Open Docker Desktop application
2. Wait for it to fully start
3. Check whale icon is steady in system tray

### Issue 5: Port Conflicts

**Solution**:
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

---

## Alternative: Use Chocolatey (Advanced)

If you have Chocolatey package manager:

```powershell
# Run PowerShell as Administrator
choco install docker-desktop -y
```

---

## Alternative: Use Winget (Windows 11)

If you have Windows 11 with winget:

```powershell
# Run PowerShell as Administrator
winget install Docker.DockerDesktop
```

---

## Post-Installation Checklist

- [ ] Docker Desktop installed
- [ ] WSL 2 enabled and configured
- [ ] Docker Desktop started
- [ ] `docker --version` works
- [ ] `docker run hello-world` works
- [ ] Docker Desktop settings configured
- [ ] PCA Agent tested with Docker

---

## Quick Start After Installation

Once Docker is installed and running:

```powershell
# 1. Navigate to project
cd "c:\Users\asharm08\OneDrive - dentsu\Desktop\windsurf\PCA_Agent"

# 2. Configure environment
cp .env.docker .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec api python scripts/init_database.py
docker-compose exec api python scripts/init_users.py

# 5. Access services
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Streamlit: http://localhost:8501
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

---

## Need Help?

- **Docker Documentation**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2 Documentation**: https://docs.microsoft.com/en-us/windows/wsl/install
- **Docker Desktop Issues**: https://github.com/docker/for-win/issues
- **PCA Agent Docker Guide**: See DOCKER_SETUP.md

---

**Status**: Follow the steps above to install Docker Desktop on your Windows machine.

Once installed, you'll be able to run the full PCA Agent stack with all services! 🚀
