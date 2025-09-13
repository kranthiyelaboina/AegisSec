<<<<<<< HEAD
# AutomatedPenetrationTesting
=======
# 🛡️ AegisSec

An AI-powered penetration testing automation tool that leverages DeepSeek to intelligently recommend and execute security testing tools with smart command chaining.

**Developed by RunTime Terrors**

## ✨ Features

- **🤖 Intelligent Tool Recommendation**: Uses DeepSeek AI to suggest the best penetration testing tools based on your criteria
- **🔗 Smart Command Chaining**: AI reads tool outputs and intelligently chains commands for comprehensive testing
- **🎯 User Tool Selection**: Choose specific tools from AI recommendations instead of auto-execution
- **📊 Executive Reports**: Generates business-friendly reports understandable by non-technical users
- **🛠️ Kali Linux Optimized**: Prioritizes pre-installed Kali Linux tools for maximum compatibility
- **⚡ Automated Execution**: Runs tools automatically with error handling and retry logic
- **🧠 AI Advisor Mode**: Interactive Q&A with DeepSeek for security guidance
- **📈 Security Scoring**: Calculates overall security scores with actionable recommendations
- **💾 Session Persistence**: Resume previous scans and maintain testing history
- **🎨 Rich CLI Interface**: Beautiful formatting with progress indicators and color coding

## 🚀 Quick Start

### Option 1: Easy Launch (Recommended)

**Windows:**
```batch
.\run.bat
```

**Linux/Kali:**
```bash
chmod +x run.sh
./run.sh
```

### Option 2: Manual Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API Key:**
```bash
python setup.py
```
- Enter your OpenRouter API key
- Select AI model preference (deepseek/deepseek-chat-v3.1 recommended)
- Configure logging level

3. **Launch AegisSec:**
```bash
python main.py
```

## 🔧 Configuration

Get your OpenRouter API key from: https://openrouter.ai/keys

The setup script will guide you through:
- API key configuration
- Model selection
- Logging preferences
- Dependency verification

## 🎯 Usage Example

```
🛡️ AegisSec Security Scanner
Developed by RunTime Terrors

Select Mode:
1. CLI Mode
2. GUI Mode (Coming Soon)
> 1

Main Menu:
1. Start Penetration Test
2. Check Tool Status  
3. View Reports
4. AI Advisor Mode
5. Settings
6. Exit
> 1

Select test type:
1. Network Mapping & Discovery
2. Web Application Security ⭐ (Optimized for Kali)
3. Brute Force Attacks
4. Vulnerability Scanning ⭐ (Recommended)
5. Wireless Security Testing
6. Custom Criteria
> 2

Enter target: example.com

🤖 AI Tool Recommendations:
ID  Tool     Status        Purpose                    Priority
1   nmap     ✅ Installed  Port scanning & discovery  HIGH
2   nikto    ✅ Installed  Web vulnerability scan     HIGH  
3   dirb     ✅ Installed  Directory enumeration      MEDIUM
4   sqlmap   ✅ Installed  SQL injection testing      HIGH

Select tools: 1,2,4

🚀 Starting Intelligent Test...
[1/3] nmap: Scanning ports... ✅ (2.3s)
      🤖 AI: Found HTTP on port 80, HTTPS on port 443
[2/3] nikto: Web vulnerability scan... ✅ (15.7s)  
      🤖 AI: WordPress detected, recommending focused scan
[3/3] sqlmap: Testing for SQL injection... ✅ (8.2s)

📊 Security Score: 67% (Needs Improvement)
✅ Report saved: reports/example_comprehensive_report.html
```

## 🛠️ Supported Tools

### 🏆 Kali Linux Priority Tools (Pre-installed)
- **nmap** - Network discovery and port scanning
- **nikto** - Web vulnerability scanner  
- **dirb** - Web directory/file brute forcer
- **hydra** - Network login brute forcer
- **sqlmap** - SQL injection testing tool
- **john** - Password hash cracker
- **hashcat** - Advanced password recovery
- **gobuster** - Directory/DNS busting tool
- **wpscan** - WordPress security scanner

### 🔧 Additional Tools (Auto-installable)
- **metasploit** - Penetration testing framework
- **burpsuite** - Web application security testing
- **wireshark** - Network protocol analyzer
- **aircrack-ng** - Wireless network security tools
- **recon-ng** - Web reconnaissance framework

## 📊 Intelligent Features

### 🧠 AI Command Chaining
- Reads nmap output to inform web scanning tools
- Detects CMS and suggests appropriate scanners  
- Identifies injection points for focused testing
- Adapts commands based on discovered services

### 🎯 Smart Tool Selection
- Prioritizes Kali Linux pre-installed tools
- Considers tool compatibility and effectiveness
- Suggests optimal tool combinations
- Provides execution order recommendations

### 📈 Executive Reporting
- Business-friendly language
- Security score with clear ratings
- Priority action items
- Risk categorization (Network, Web, Auth, Config)
- Non-technical explanations

## 🔒 Security Considerations

- ⚠️ **Authorization Required**: Only run on systems you own or have explicit permission to test
- 🛡️ **Command Validation**: Built-in safety checks prevent dangerous system commands
- 🔐 **API Key Security**: Store API keys securely, consider using environment variables
- 📋 **Log Security**: Tool outputs may contain sensitive information
- 🎯 **Responsible Disclosure**: Follow responsible disclosure practices for findings

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, Linux (Kali recommended), macOS
- **Internet**: Required for AI API calls
- **Tools**: Kali Linux pre-installed tools (for optimal experience)
- **API**: OpenRouter API key for DeepSeek access

## 🤝 Support & Development

- **Developed by**: RunTime Terrors Team
- **AI Engine**: DeepSeek v3.1 via OpenRouter
- **License**: MIT
- **Issues**: Report bugs or request features
- **Contributions**: Pull requests welcome

## 📚 Advanced Usage

### Custom Tool Integration
```python
# Add custom tools to config/config.json
"tools": {
  "custom_tools": ["custom_scanner", "proprietary_tool"]
}
```

### API Integration
```python
# Direct API usage
from src.deepseek_client import DeepSeekClient
client = DeepSeekClient(config_manager)
recommendations = client.get_tool_recommendations("scan example.com")
```

### Batch Processing
```bash
# Multiple targets
echo "target1.com\ntarget2.com" | python main.py --batch
```

---

**🛡️ AegisSec - Securing your digital assets with AI-powered intelligence**  
*Developed with ❤️ by RunTime Terrors*
>>>>>>> master
