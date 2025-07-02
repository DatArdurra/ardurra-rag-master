# Ardurra RAG - Install and Local Dev Guide
 
This project is based on the [Azure OpenAI + Search RAG architecture](https://github.com/Azure-Samples/azure-search-openai-demo) and integrates multiple Azure services including OpenAI, CosmosDB, Search, and Document Intelligence.
 
---
 
## Local Environment Setup
 
### Prerequisites
 
Install the following tools:
 
- [Azure Developer CLI (azd)](https://aka.ms/azure-dev/install)
- [Python 3.9, 3.10, or 3.11](https://www.python.org/downloads/)
  - Ensure `python --version` works in your terminal
  - On Ubuntu: you may need to run `sudo apt install python-is-python3`
- [Node.js (v20+)](https://nodejs.org/download/)
- [Git](https://git-scm.com/downloads)
- [PowerShell 7+](https://github.com/powershell/powershell) *(Windows only)*
  - Ensure `pwsh.exe` works from terminal
  - If not, upgrade PowerShell from the link above
 
---
 
## Clone and Set Up the Repository


1. **Navigate to a folder of your choice**

   Open PowerShell or Command Prompt and move to the directory where you want to clone the repo.  
   For example:

   ```powershell
   cd C:\Projects
   ```

2. **Clone the repository (replace `marketing` with your branch name)**

   ```powershell
   git clone --branch marketing https://github.com/ParthSharma023/ardurra-rag-master.git
   ```

3. **Rename the cloned folder to match your branch name (optional but recommended)**

   ```powershell
   Rename-Item ardurra-rag-master marketing
   ```

   > 💡 **If using Command Prompt instead of PowerShell**, use:
   > ```cmd
   > ren ardurra-rag-master marketing
   > ```

4. **Switch into the new folder**

   ```powershell
   cd marketing
   ```

---

### Azure Authentication
 
1. Login to Azure:
 
   ```bash
   azd auth login
   ```
 
2. Create the following folder structure in your project:
 
   ```
   .azure/marketing/.env
   ```
 
   > **Reach out to `PSharma@ardurra.com` to get the `.env` file.**
 
3. Set this environment as default:
 
   ```bash
   azd env select marketing
   ```
 
---
 
### Start the App
 
#### For Windows PowerShell users:
 
Temporarily allow script execution:
 
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
 
Then start the server:
 
```powershell
./app/start.ps1
```
 
#### For Linux/macOS:
 
```bash
./app/start.sh
```
 
---
 
### Frontend Hot Reloading (Optional)
 
In a new terminal window:
 
```bash
cd app/frontend
npm install         # Only needed once
npm run dev
```
 
Expected output:
 
```shell
> frontend@0.0.0 dev
> vite
 
  VITE v4.5.1  ready in 957 ms
 
  ➜  Local:   http://localhost:5173/
```
 
Visit that URL in your browser to see the live frontend. Vite will auto-reload on changes.
 
All backend API calls are proxied to the Python server, as defined in `vite.config.ts`.
 
---
 
## Notes
 
- No need to run `azd up` if you're using pre-provisioned Azure services.
- Make sure your `.env` file has correct and complete Azure values, especially for OpenAI, CosmosDB, and Search.
- Backend uses `Quart`, OpenTelemetry, and other modern observability tools.
 
---