# DooService CLI

DooService CLI is a professional command-line tool for managing complex Odoo instances using a declarative approach. Define your entire infrastructure in a single `dooservice.yml` file and manage instances, repositories, backups, deployments, and GitHub integration from the command line.

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

# Verify installation
dooservice --help
```

### Docker Installation

```bash
# Run with Docker
docker run -v $(pwd):/workspace -v /var/run/docker.sock:/var/run/docker.sock \
  dooservice/cli:latest --help
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/your-org/dooservice-cli.git
cd dooservice-cli

# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync --all-extras

# Verify installation
uv run dooservice --help
```

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

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
   dooservice config validate
   ```

3. **Create Your First Instance**
   ```bash
   # Create and start instance (with preview)
   dooservice instance create my-instance --dry-run
   dooservice instance create my-instance --start
   ```

4. **Access Your Instance**
   Your Odoo instance will be running at `http://localhost:8069` (or your configured port)

5. **Manage Your Instance**
   ```bash
   # Check status
   dooservice instance status my-instance
   
   # View logs
   dooservice instance logs my-instance --follow
   
   # Create backup
   dooservice backup create my-instance
   ```

## 📖 Command Reference

### Instance Management
```bash
# Create and manage instances
dooservice instance create <name> [--start] [--dry-run]
dooservice instance start <name>
dooservice instance stop <name>
dooservice instance status <name>
dooservice instance logs <name> [--follow] [--tail <lines>]
dooservice instance sync <name> [--dry-run]
dooservice instance delete <name> [--dry-run]
dooservice instance exec-web <name>
dooservice instance exec-db <name>
```

### Repository Management
```bash
# Update addon repositories
dooservice repo update <repository_name>
dooservice repo update-all
```

### Configuration Management
```bash
# Validate and manage configuration
dooservice config validate
dooservice lock generate
```

### Backup Operations
```bash
# Create and manage backups
dooservice backup create <instance> [--dry-run] [--description <text>]
dooservice backup restore <backup_id> <target_instance> [--dry-run]
dooservice backup list [--instance <name>]
dooservice backup delete <backup_id>
```

### Snapshot Management
```bash
# Create and manage snapshots
dooservice snapshot create <instance> [--tag <tag>] [--dry-run]
dooservice snapshot restore <snapshot_id> <target> [--dry-run]
dooservice snapshot list [--instance <name>]
dooservice snapshot delete <snapshot_id>
```

### GitHub Integration
```bash
# Authentication
dooservice github login
dooservice github logout
dooservice github status

# SSH Key Management
dooservice github key list
dooservice github key add <title> <key_file>
dooservice github key remove <key_id>

# Repository Watchers
dooservice github watch add <repo> <instance> [--action <action>]
dooservice github watch remove <repo> <instance>
dooservice github watch list

# Webhook Synchronization
dooservice github listen start [--port <port>] [--host <host>]
dooservice github listen stop
dooservice github listen status
dooservice github listen logs [--follow]

# Webhook Synchronization Service
dooservice github sync start [--port <port>] [--daemon]
dooservice github sync stop
dooservice github sync status
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

- 📖 [Documentation](https://github.com/your-org/dooservice-cli)
- 🐛 [Issues](https://github.com/your-org/dooservice-cli/issues)
- 💬 [Discussions](https://github.com/your-org/dooservice-cli/discussions)

