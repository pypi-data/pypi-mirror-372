# Usage Examples

This page demonstrates common backup scenarios using fnb for different use cases.

## Web Server Backup

Example configuration for backing up web server document root and logs.

```toml
[fetch.webroot]
label = "webroot"
summary = "Fetch web server document root"
host = "user@webserver"
source = "/var/www/html/"
target = "./backup/webroot/"
options = ["-auvz", "--delete", "--exclude=cache/", "--exclude=tmp/"]
enabled = true

[backup.webroot]
label = "webroot"
summary = "Backup web server document root to cloud"
host = "none"
source = "./backup/webroot/"
target = "~/OneDrive/Backups/webserver/htdocs/"
options = ["-auvz", "--delete"]
enabled = true

[fetch.weblogs]
label = "weblogs"
summary = "Fetch web server logs"
host = "user@webserver"
source = "/var/log/apache2/"
target = "./backup/weblogs/"
options = ["-auvz", "--delete", "--include=*.log", "--include=**/", "--exclude=*"]
enabled = true

[backup.weblogs]
label = "weblogs"
summary = "Backup web server logs to cloud"
host = "none"
source = "./backup/weblogs/"
target = "~/OneDrive/Backups/webserver/logs/"
options = ["-auvz", "--delete"]
enabled = true
```

### Workflow Commands

```bash
# Complete web server backup workflow
fnb sync webroot
fnb sync weblogs

# Preview operations first
fnb sync webroot --dry-run
fnb sync weblogs --dry-run
```

## Database Backup

Configuration for backing up database dumps and related files.

```toml
[fetch.database]
label = "database"
summary = "Fetch database dumps from DB server"
host = "dbuser@dbserver.example.com"
source = "/home/dbuser/backups/daily/"
target = "./backup/database/"
options = ["-auvz", "--delete", "--include=*.sql", "--include=*.sql.gz", "--include=**/", "--exclude=*"]
enabled = true

[backup.database]
label = "database"
summary = "Backup database dumps to external storage"
host = "none"
source = "./backup/database/"
target = "/mnt/backup-drive/database/"
options = ["-auvz", "--delete", "--progress"]
enabled = true

[fetch.dbconfig]
label = "dbconfig"
summary = "Fetch database configuration files"
host = "dbuser@dbserver.example.com"
source = "/etc/mysql/"
target = "./backup/mysql-config/"
options = ["-auvz", "--delete", "--exclude=*.pid", "--exclude=*.sock"]
enabled = true
```

### Database Workflow

```bash
# Backup database and configuration
fnb sync database
fnb sync dbconfig

# Check backup status
fnb status

# Fetch only (without external backup)
fnb fetch database
fnb fetch dbconfig
```

## Development Project Backup

Configuration for backing up development projects and dependencies.

```toml
[fetch.project]
label = "project"
summary = "Fetch project source code from remote repository"
host = "dev@dev-server.local"
source = "/home/dev/projects/myapp/"
target = "./backup/projects/myapp/"
options = ["-auvz", "--delete", "--exclude=node_modules/", "--exclude=.git/", "--exclude=__pycache__/"]
enabled = true

[backup.project]
label = "project"
summary = "Backup project to cloud storage"
host = "none"
source = "./backup/projects/"
target = "~/Dropbox/Development/Backups/"
options = ["-auvz", "--delete"]
enabled = true

[fetch.dependencies]
label = "dependencies"
summary = "Fetch project dependencies cache"
host = "dev@dev-server.local"
source = "/home/dev/.cache/pip/"
target = "./backup/pip-cache/"
options = ["-auvz", "--delete", "--exclude=*.tmp"]
enabled = false
```

### Development Workflow

```bash
# Daily development backup
fnb sync project

# Weekly dependency cache backup
fnb fetch dependencies
fnb backup dependencies

# Preview before major sync
fnb sync project --dry-run
```

## Multi-Server Infrastructure

Configuration for backing up multiple servers with different roles.

```toml
# Production web server
[fetch.prod-web]
label = "prod-web"
summary = "Production web server content"
host = "admin@prod-web.example.com"
source = "/var/www/"
target = "./backup/servers/prod-web/"
options = ["-auvz", "--delete", "--exclude=logs/", "--exclude=cache/"]
enabled = true

# Staging server
[fetch.staging]
label = "staging"
summary = "Staging server content"
host = "admin@staging.example.com"
source = "/var/www/"
target = "./backup/servers/staging/"
options = ["-auvz", "--delete"]
enabled = true

# Application server logs
[fetch.app-logs]
label = "app-logs"
summary = "Application server logs"
host = "admin@app-server.example.com"
source = "/var/log/myapp/"
target = "./backup/logs/application/"
options = ["-auvz", "--delete", "--compress"]
enabled = true

# Centralized backup
[backup.servers]
label = "servers"
summary = "All server backups to NAS"
host = "none"
source = "./backup/servers/"
target = "/mnt/nas/server-backups/"
options = ["-auvz", "--delete", "--progress"]
enabled = true

[backup.logs]
label = "logs"
summary = "All logs to archive storage"
host = "none"
source = "./backup/logs/"
target = "/mnt/archive/logs/"
options = ["-auvz", "--delete", "--compress"]
enabled = true
```

### Infrastructure Workflow

```bash
# Backup all servers
fnb fetch prod-web
fnb fetch staging
fnb fetch app-logs

# Centralized backup
fnb backup servers
fnb backup logs

# Complete infrastructure sync
for server in prod-web staging app-logs; do
    fnb fetch $server
done
fnb backup servers
fnb backup logs
```

## Personal Data Backup

Configuration for personal files and documents backup.

```toml
[fetch.documents]
label = "documents"
summary = "Personal documents from home server"
host = "user@home-server.local"
source = "/home/user/Documents/"
target = "./backup/documents/"
options = ["-auvz", "--delete", "--exclude=.DS_Store", "--exclude=Thumbs.db"]
enabled = true

[fetch.photos]
label = "photos"
summary = "Photo collection from NAS"
host = "user@nas.local"
source = "/volume1/photos/"
target = "./backup/photos/"
options = ["-auvz", "--delete", "--progress", "--exclude=@eaDir/"]
enabled = true

[backup.documents]
label = "documents"
summary = "Documents to cloud storage"
host = "none"
source = "./backup/documents/"
target = "~/Google Drive/Backups/Documents/"
options = ["-auvz", "--delete"]
enabled = true

[backup.photos]
label = "photos"
summary = "Photos to external drive"
host = "none"
source = "./backup/photos/"
target = "/Volumes/BackupDrive/Photos/"
options = ["-auvz", "--delete", "--progress"]
enabled = true
```

### Personal Workflow

```bash
# Weekly document backup
fnb sync documents

# Monthly photo backup (large files)
fnb sync photos --create-dirs

# Quick status check
fnb status
```

## Advanced Scenarios

### Selective File Backup

```toml
[fetch.important-files]
label = "important-files"
summary = "Only important file types"
host = "user@server.com"
source = "/home/user/work/"
target = "./backup/work-files/"
options = [
    "-auvz",
    "--include=*.pdf",
    "--include=*.docx",
    "--include=*.xlsx",
    "--include=*.pptx",
    "--include=**/",
    "--exclude=*"
]
enabled = true
```

### Bandwidth-Limited Backup

```toml
[fetch.large-files]
label = "large-files"
summary = "Large files with bandwidth limit"
host = "user@server.com"
source = "/media/videos/"
target = "./backup/videos/"
options = ["-auvz", "--progress", "--bwlimit=500", "--partial"]
enabled = true
```

### Time-Based Exclusions

```toml
[fetch.recent-logs]
label = "recent-logs"
summary = "Only recent log files"
host = "admin@server.com"
source = "/var/log/app/"
target = "./backup/recent-logs/"
options = ["-auvz", "--delete", "--max-age=7d"]
enabled = true
```

## Environment-Specific Configuration

### Development Environment

```bash
# .env.development
SSH_PASSWORD_dev_server=dev_password
SSH_PASSWORD_staging_server=staging_password
```

### Production Environment

```bash
# .env.production
SSH_PASSWORD_prod_server=secure_production_password
SSH_PASSWORD_db_server=database_password
```

### Usage with Different Environments

```bash
# Load development environment
fnb --config config/dev.toml sync project

# Load production environment
fnb --config config/prod.toml sync database
```

## Troubleshooting Examples

### Common Error Scenarios

```bash
# Preview operations to debug issues
fnb fetch webroot --dry-run

# Create missing directories
fnb fetch webroot --create-dirs

# Use specific SSH password
fnb fetch webroot --ssh-password mypassword

# Check configuration
fnb status --config ./custom-config.toml
```

### Debugging Connection Issues

```bash
# Test SSH connectivity first
ssh user@webserver

# Use verbose rsync output (add -v to options in config)
options = ["-auvzv", "--delete"]

# Test with minimal options
options = ["-av"]
```

For more configuration details, see the [Configuration Guide](configuration.md).
