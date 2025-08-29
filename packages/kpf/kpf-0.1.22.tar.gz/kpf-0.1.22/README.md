# kpf - A better way to port-forward with kubectl

This is a Python utility that (attempts) to dramatically improve the experience of port-forwarding with kubectl.

It is essentially a wrapper around `kubectl port-forward` that adds an interactive service selection with automatic reconnect when the pods are restarted or your network connection is interrupted (computer goes to sleep, etc).

## Features

- 🔄 **Automatic Restart**: Monitors endpoint changes and restarts port-forward automatically
- 🎯 **Interactive Selection**: Choose services with a colorful, intuitive interface
- 🌈 **Color-coded Status**: Green for services with endpoints, red for those without
- 🔍 **Multi-resource Support**: Services, pods, deployments, and more
- 📊 **Rich Tables**: Beautiful formatted output with port information
- 🏷️ **Namespace Aware**: Work with specific namespaces or across all namespaces

## Installation

**Note**: `oh-my-zsh` kubectl plugin will conflict with this `kpf` command. If you prefer this tool, you can alias at the bottom of your `~/.zshrc` file or use a different alias.

### Homebrew (Recommended)

```bash
brew tap jessegoodier/kpf
brew install kpf
```

Or install directly:

```bash
brew install jessegoodier/kpf/kpf
```

### Using uv

If you have `uv` installed, you can "install" `kpf` with:

```bash
alias kpf="uvx kpf"
```

Install uv with pipx:

```bash
pipx install uv
```

## Usage

### Interactive Mode (Recommended)

**Warm Tip**: You can use the interactive mode to find the service you want, and it will output the command to connect to that service directly next time.

**Note**: You might think that "warm tip" is something that AI wrote, but that's not the case. It really is just a little bit less than a hot tip.

![screenshot](kpf-screenshot.png)

Select services interactively:

Interactive selection in current namespace:

```bash
kpf --prompt
```

Interactive selection in specific namespace:

```bash
kpf --prompt -n production

Show all services across all namespaces:

```bash
kpf --all
```

Include pods and deployments with ports defined:

```bash
kpf --all-ports
```

Combine a few options (interactive mode, all services, and endpoint status checking, debug mode):

```bash
kpf -pAdl
```

### Check Mode

Add endpoint status checking to service selection (slower but shows endpoint health):

```bash
# Interactive selection with endpoint status
kpf --prompt --check

# Show all services with endpoint status
kpf --all --check

# Include pods and deployments with status
kpf --all-ports --check
```

### Legacy Mode

Direct port-forward (backward compatible):

```bash
# Traditional kubectl port-forward syntax
kpf svc/frontend 8080:8080 -n production
kpf pod/my-pod 3000:3000
```

### Command Options

```sh
There is no default command. You must specify one of the arguments below.

Example usage:
  kpf svc/frontend 8080:8080 -n production      # Direct port-forward (backwards compatible with kpf alias)
  kpf --prompt (or -p)                          # Interactive service selection
  kpf --prompt -n production                    # Interactive selection in specific namespace
  kpf --all (or -A)                             # Show all services across all namespaces
  kpf --all-ports (or -l)                       # Show all services with their ports
  kpf --prompt --check -n production            # Interactive selection with endpoint status
```

## Examples

### Interactive Service Selection

Fast mode (without endpoint checking):

```bash
$ kpf --prompt -n kube-system

Services in namespace: kube-system

#    Type     Name                    Ports
1    SERVICE  kube-dns               53, 9153
2    SERVICE  metrics-server         443
3    SERVICE  kubernetes-dashboard   443

Select a service [1]: 1
Local port (press Enter for 53): 5353
```

With endpoint status checking:

```bash
$ kpf --prompt --check -n kube-system

Services in namespace: kube-system

#    Type     Name                    Ports           Status
1    SERVICE  kube-dns               53, 9153         ✓
2    SERVICE  metrics-server         443              ✓
3    SERVICE  kubernetes-dashboard   443              ✗

✓ = Has endpoints  ✗ = No endpoints

Select a service [1]: 1
Local port (press Enter for 53): 5353
```

### Cross-Namespace Discovery

```bash
$ kpf --all

Services across all namespaces

#    Namespace    Type     Name           Ports        Status
1    default      SERVICE  kubernetes     443          ✓
2    kube-system  SERVICE  kube-dns      53, 9153     ✓
3    production   SERVICE  frontend      80, 443      ✓
4    production   SERVICE  backend       8080         ✗
```

## How It Works

1. **Port-Forward Thread**: Runs kubectl port-forward in a separate thread
2. **Endpoint Watcher**: Monitors endpoint changes using `kubectl get ep -w`
3. **Automatic Restart**: When endpoints change, gracefully restarts the port-forward
4. **Service Discovery**: Uses kubectl to discover services and their endpoint status

## Requirements

- kubectl configured with cluster access

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/jessegoodier/kpf.git
cd kpf

# Install with development dependencies
uv venv
uv pip install -e ".[dev]"
source .venv/bin/activate
```

### Code Quality Tools

```bash
# Format and lint code
uvx ruff check . --fix
uvx ruff format .

# Sort imports
uvx isort .

# Run tests
uv run pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
