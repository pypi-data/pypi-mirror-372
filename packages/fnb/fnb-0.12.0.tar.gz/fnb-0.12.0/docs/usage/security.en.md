# Security Guide

This guide covers secure authentication methods for fnb, moving beyond plain-text password storage in `.env` files.

## Overview

By default, fnb supports SSH password authentication via `.env` files, but this approach stores passwords in plain text. This guide presents more secure alternatives and best practices.

## Authentication Methods (Recommended Order)

### 1. SSH Key Authentication (Most Secure)

SSH key authentication eliminates the need for password storage entirely.

#### Setup SSH Keys

```bash
# Generate SSH key pair (creates private/public key files)
ssh-keygen -t ed25519 -f ~/.ssh/fnb_key

# Copy public key to remote server (adds to ~/.ssh/authorized_keys)
ssh-copy-id -i ~/.ssh/fnb_key.pub user@server.com

# Configure SSH to use the key
echo "Host server.com
  IdentityFile ~/.ssh/fnb_key
  IdentitiesOnly yes" >> ~/.ssh/config
```

**Command Explanations:**

- `ssh-keygen`: Creates a new SSH key pair (private key + public key)
    - `-t ed25519`: Uses modern Ed25519 algorithm (recommended)
    - `-f ~/.ssh/fnb_key`: Specifies output file path (default: `id_ed25519` and `id_ed25519.pub` )
- `ssh-copy-id`: Copies your public key to the remote server
    - `-i ~/.ssh/fnb_key.pub`: Specifies which public key to copy (default to `~/.ssh/id_ed25519.pub`)
    - Automatically adds the key to `~/.ssh/authorized_keys` on remote server

#### Benefits

- **No password storage** - Most secure option
- **Automatic authentication** - No manual intervention needed
- **Key rotation** - Easy to revoke and replace keys
- **Standard practice** - Widely adopted security standard

#### Configuration

When using SSH keys, remove password entries from your `.env` file:

```bash
# Remove these lines from .env
# FNB_PASSWORD_USER_SERVER_COM=mypassword
# FNB_PASSWORD_DEFAULT=defaultpassword
```

### 2. macOS Keychain Integration

Store passwords securely in macOS Keychain instead of plain-text files.

#### Setup Keychain Storage

```bash
# Store password in keychain
security add-generic-password \
  -s "fnb-ssh" \
  -a "user@server.com" \
  -w "your-password"

# Retrieve password from keychain
security find-generic-password \
  -s "fnb-ssh" \
  -a "user@server.com" \
  -w
```

**Command Explanations:**

- `security add-generic-password`: Stores a password in macOS Keychain
    - `-s "fnb-ssh"`: Service name (identifier for this password entry)
    - `-a "user@server.com"`: Account name (usually the SSH connection string)
    - `-w "your-password"`: Password to store (can also prompt interactively without this option)
- `security find-generic-password`: Retrieves a password from Keychain
    - `-s "fnb-ssh"`: Service name to search for
    - `-a "user@server.com"`: Account name to match
    - `-w`: Output only the password (without this, shows all metadata)

#### Implementation Notes

This method requires extending fnb's `env.py` module to support keychain integration. The current implementation only supports `.env` files.

### 3. dotenvx Encryption

Use dotenvx to encrypt `.env` files while maintaining compatibility with existing fnb workflows.

#### Setup dotenvx

```bash
# Install dotenvx
npm install -g @dotenvx/dotenvx

# Or using other package managers
brew install dotenvx/brew/dotenvx
curl -fsS https://dotenvx.sh/install.sh | sh
```

#### Encrypt Existing .env File

```bash
# Encrypt your existing .env file
dotenvx encrypt

# This encrypts the .env file in-place and creates .env.keys
# The original .env content is now encrypted
```

#### File Structure After Encryption

```
.env           # Encrypted file (safe to commit)
.env.keys      # Decryption keys (DO NOT commit)
```

#### Usage with fnb

```bash
# Run fnb with encrypted environment
dotenvx run -- fnb fetch backup-server

# Or set the decryption key in environment
export DOTENV_KEY="dotenv://:key_1234...@dotenvx.com/vault/.env.vault?environment=production"
fnb fetch backup-server

# Decrypt for manual inspection (reference only)
dotenvx decrypt
```

#### Benefits

- **Backward compatible** - Works with existing fnb implementation
- **Encrypted storage** - Passwords encrypted at rest
- **Environment separation** - Different keys for dev/staging/production
- **Version control safe** - Encrypted `.env` can be safely committed

#### Git Configuration

```bash
# Add to .gitignore
echo ".env.keys" >> .gitignore

# Encrypted .env CAN be committed (it's encrypted)
git add .env
```

### 4. GPG Encryption

Encrypt password files using GPG for an additional security layer.

#### Setup GPG Encryption

```bash
# Create encrypted password file
echo "mypassword" | gpg --symmetric --armor > ~/.config/fnb/password.gpg

# Set restrictive permissions
chmod 600 ~/.config/fnb/password.gpg

# Decrypt when needed
gpg --decrypt ~/.config/fnb/password.gpg
```

**Command Explanations:**

- `gpg --symmetric --armor`: Encrypts data using symmetric encryption
    - `--symmetric`: Uses passphrase-based encryption (no public/private keys needed)
    - `--armor`: Creates ASCII-armored output (text format, easier to handle)
    - Output is encrypted with a passphrase you provide interactively
- `gpg --decrypt`: Decrypts GPG-encrypted files
    - Prompts for the passphrase used during encryption
    - `--quiet`: Can be added to suppress status messages
    - `--batch`: Can be added for non-interactive mode (requires passphrase via other means)

#### Integration with fnb
This method requires extending the current implementation to decrypt passwords at runtime.

### 5. Interactive Password Input

fnb automatically falls back to interactive password input when no stored passwords are found.

#### Current Behavior

When no password is found in environment variables or other sources, fnb automatically falls back to interactive password input:

1. fnb attempts to retrieve password from configured sources
2. If no password is found (`ssh_password = None`)
3. rsync executes without password automation
4. SSH prompts user for password in terminal
5. User enters password interactively

#### Benefits

- **No configuration required** - Works out of the box
- **Highest security** - No stored passwords
- **Standard SSH behavior** - Familiar user experience
- **Fallback mechanism** - Always available when other methods fail

#### Usage Example

```bash
# No .env file or password configuration
fnb fetch backup-server

# Output:
# Fetching backup-server from user@server:~/data/ to ./backup/
# user@server's password: [user types password]
# Fetch completed successfully: backup-server
```

#### When This Mode Activates

- No `.env` file exists
- Environment variables `FNB_PASSWORD_*` are not set
- Other password sources (keychain, GPG) are not configured or fail
- SSH key authentication is not set up

## Current .env File Security

If you must continue using `.env` files, follow these security practices:

### File Permissions

```bash
# Set restrictive permissions
chmod 600 .env
chmod 600 ~/.config/fnb/.env

# Verify permissions
ls -la .env
# Should show: -rw------- (600)
```

### Environment Variable Format

```bash
# Host-specific passwords (recommended)
FNB_PASSWORD_USER_EXAMPLE_COM=hostspecificpassword

# Default password (less secure)
FNB_PASSWORD_DEFAULT=defaultpassword
```

### Git Security

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore

# Remove .env from git history if accidentally committed
git rm --cached .env
git commit -m "Remove .env from version control"
```

## Security Best Practices

### 1. Principle of Least Privilege
- Use SSH keys with specific access scopes
- Avoid shared or default passwords
- Regularly rotate credentials

### 2. Environment Isolation
- Use separate SSH keys for different environments
- Maintain environment-specific `.env` files with restricted access
- Never commit `.env` files to version control

### 3. Monitoring and Auditing
- Monitor SSH key usage through server logs
- Regular security audits of stored credentials
- Document all authentication methods used

### 4. Backup Security
- Encrypt backup destinations when possible
- Secure backup storage locations
- Regular backup integrity verification

## Migration from Plain-text Passwords

### Step 1: Audit Current Setup
```bash
# Check current .env files
ls -la .env ~/.config/fnb/.env

# Review configured hosts
fnb status
```

### Step 2: Implement SSH Keys
```bash
# For each host in your configuration
ssh-keygen -t ed25519 -f ~/.ssh/fnb_key_hostname
ssh-copy-id -i ~/.ssh/fnb_key_hostname.pub user@hostname
```

### Step 3: Update SSH Configuration
```bash
# Add to ~/.ssh/config
Host hostname1
  IdentityFile ~/.ssh/fnb_key_hostname1
  IdentitiesOnly yes

Host hostname2
  IdentityFile ~/.ssh/fnb_key_hostname2
  IdentitiesOnly yes
```

### Step 4: Test and Cleanup
```bash
# Test connections
ssh user@hostname1
ssh user@hostname2

# Remove passwords from .env files
# Keep files for other environment variables if needed
```

## Troubleshooting

### SSH Key Issues
```bash
# Check SSH agent
ssh-add -l

# Add key to agent if needed
ssh-add ~/.ssh/fnb_key

# Test connection
ssh -v user@server.com
```

### Permission Issues
```bash
# Fix SSH directory permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/fnb_key*
chmod 644 ~/.ssh/fnb_key*.pub
```

### Keychain Issues (macOS)
```bash
# List stored passwords
security dump-keychain | grep fnb-ssh

# Update stored password
security delete-generic-password -s "fnb-ssh" -a "user@server.com"
security add-generic-password -s "fnb-ssh" -a "user@server.com" -w "newpassword"
```

## See Also

- [Configuration Guide](configuration.md) - Basic fnb configuration
- [Examples](examples.md) - Configuration examples with security considerations
- [Contributing](../development/contributing.md) - Security considerations for development
