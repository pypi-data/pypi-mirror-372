# DooService CLI

DooService CLI is a professional command-line tool for managing complex Odoo instances using a declarative approach. Define your entire infrastructure in a single `dooservice.yml` file and manage instances, repositories, backups, snapshots, and GitHub integration from the command line.

## ✨ Features

- **🔧 Declarative Configuration**: Define all Odoo instances, repositories, and deployments in a single YAML file
- **🚀 Full Instance Lifecycle**: Create, start, stop, sync, and delete instances with simple commands  
- **📁 Repository Management**: Automatically clone and update Odoo addon repositories from Git
- **🐳 Docker Integration**: Native Docker support for deploying Odoo and PostgreSQL containers
- **💾 Backup System**: Create, restore, list, and manage instance backups with database and filestore support
- **📸 Snapshot Management**: Capture complete instance states including configuration, repositories, and modules
- **🐙 GitHub Integration**: OAuth authentication, SSH key management, and webhook-based auto-sync
- **🎣 Webhook Synchronization**: HTTP daemon with signature verification for real-time GitHub updates
- **🔍 Dry-Run Mode**: Preview all operations before executing them with `--dry-run`
- **⚡ High Performance**: Built with clean architecture principles and optimized for speed

## 📦 Installation

### Production Installation

```bash
# Using pipx (recommended)
pipx install dooservice-cli

# Using pip
pip install dooservice-cli

# Using uv (modern Python package manager)
uv tool install dooservice-cli

# Verify installation
dooservice cli --help
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/apiservicesac/dooservice-cli-py.git
cd dooservice-cli-py

# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 1: Install globally for development
uv tool install --editable .

# Option 2: Install dependencies only (requires uv run prefix)
uv sync --all-extras

# Verify installation
# For global install:
dooservice cli --help

# For local development:
uv run dooservice cli --help
```

## 🚀 Quick Start

1. **Initialize Configuration**
   ```bash
   # Copy example configuration
   cp dooservice.yml.example dooservice.yml
   
   # Edit the configuration to match your needs
   nano dooservice.yml
   ```

2. **Validate Configuration**
   ```bash
   dooservice cli config validate
   ```

3. **Create Your First Instance**
   ```bash
   # Create and start instance (with preview)
   dooservice cli instance create my-instance --dry-run
   dooservice cli instance create my-instance --start
   ```

4. **Access Your Instance**
   Your Odoo instance will be running at `http://localhost:8069` (or your configured port)

5. **Manage Your Instance**
   ```bash
   # Check status
   dooservice cli instance status my-instance
   
   # View logs
   dooservice cli instance logs my-instance --follow
   
   # Create backup
   dooservice cli backup create my-instance
   ```

## 📖 Command Reference

> **Note**: All commands require the `cli` subcommand. Use `dooservice cli <command>` format.

### Instance Management
```bash
# Create and manage instances
dooservice cli instance create <name> [--start] [--dry-run]
dooservice cli instance start <name>
dooservice cli instance stop <name>
dooservice cli instance status <name>
dooservice cli instance logs <name> [--follow] [--tail <lines>]
dooservice cli instance sync <name> [--dry-run]
dooservice cli instance delete <name> [--dry-run]
dooservice cli instance exec-web <name>
dooservice cli instance exec-db <name>
```

### Repository Management
```bash
# Manage instance repositories
dooservice cli repo list <instance>
dooservice cli repo status <instance>
dooservice cli repo sync <instance>
```

### Configuration Management
```bash
# Validate and manage configuration
dooservice cli config validate [--file <config_file>]
dooservice cli lock generate
```

### Backup Operations
```bash
# Create and manage backups
dooservice cli backup create <instance> [--description <text>]
dooservice cli backup test <instance>
dooservice cli backup databases <instance>
dooservice cli backup config <instance>

# Automatic backup scheduling
dooservice cli backup auto start <instance>
dooservice cli backup auto stop <instance>
dooservice cli backup auto status <instance>
```

### Snapshot Management
```bash
# Create and manage snapshots
dooservice cli snapshot create <instance> [--tag <tag>] [--description <text>] [--no-backup]
dooservice cli snapshot list [--instance <name>] [--tag <tag>]
dooservice cli snapshot restore <snapshot_id> <target_instance> [--no-data] [--no-modules] [--yes]
dooservice cli snapshot delete <snapshot_id> [--yes]
```

### GitHub Integration
```bash
# Authentication
dooservice cli github login
dooservice cli github logout
dooservice cli github status

# SSH Key Management
dooservice cli github key list
dooservice cli github key add <title> <key_file>
dooservice cli github key remove <key_id>

# Repository Watchers
dooservice cli github watch add <repo> <instance>
dooservice cli github watch remove <repo> <instance>
dooservice cli github watch list
dooservice cli github watch sync

# Webhook Server Management
dooservice cli github webhook start [--port <port>] [--host <host>]
dooservice cli github webhook stop
dooservice cli github webhook status
dooservice cli github webhook logs [--follow]
dooservice cli github webhook restart
```


## 📚 Configuration

The `dooservice.yml` file is the heart of DooService CLI. It defines your entire Odoo infrastructure in a declarative way.

### Basic Structure

```yaml
# Global repositories that can be used by instances
repositories:
  my-addons:
    url: "https://github.com/your-org/odoo-addons.git"
    branch: "main"

# Instance definitions
instances:
  production:
    odoo_version: "17.0"
    data_dir: "/opt/odoo-data/production"
    
    ports:
      web: 8069
      db: 5432
    
    repositories:
      - my-addons
    
    env_vars:
      ODOO_DB_NAME: "production_db"
      ODOO_DB_PASSWORD: "secure_password"
    
    deployment:
      docker:
        web:
          image: "odoo:17.0"
          container_name: "production-odoo"
        db:
          image: "postgres:15"
          container_name: "production-db"
```

### Advanced Features

- **🔄 Variable Substitution**: Use `${data_dir}` and `${env_vars.VARIABLE}` placeholders
- **🐳 Docker Health Checks**: Configure container health monitoring  
- **📁 Custom Paths**: Define paths for configs, addons, logs, and filestore
- **🔒 Environment Variables**: Secure configuration with environment-based secrets
- **🎯 Multiple Environments**: Define development, staging, and production instances
- **🐙 GitHub Integration**: OAuth authentication and webhook-based repository synchronization
- **🎣 Webhook Automation**: Automatic instance updates on repository changes

See `dooservice.yml.example` for a complete configuration example.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://github.com/apiservicesac/dooservice-cli-py#readme)
- 🐛 [Issues](https://github.com/apiservicesac/dooservice-cli-py/issues)
- 🏠 [Homepage](https://apiservicesac.com)

