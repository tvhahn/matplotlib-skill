FROM node:22

ARG TZ
ENV TZ="$TZ"

ARG CLAUDE_CODE_VERSION=latest

# Install basic development tools, Python, and networking utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
  less \
  git \
  procps \
  sudo \
  fzf \
  zsh \
  man-db \
  unzip \
  gnupg2 \
  gh \
  iproute2 \
  dnsutils \
  jq \
  nano \
  vim \
  tmux \
  make \
  build-essential \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  wget \
  curl \
  llvm \
  libncurses5-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libffi-dev \
  liblzma-dev \
  python3.11 \
  python3.11-dev \
  pandoc \
  sqlite3 \
  zip \
  locales \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Generate en_US.UTF-8 locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Ensure default node user has access to /usr/local/share
RUN mkdir -p /usr/local/share/npm-global && \
  chown -R node:node /usr/local/share

ARG USERNAME=node

# Install uv globally
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    cp /root/.local/bin/uvx /usr/local/bin/uvx

# Persist bash history
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  && mkdir /commandhistory \
  && touch /commandhistory/.bash_history \
  && chown -R $USERNAME /commandhistory

# Set DEVCONTAINER environment variable
ENV DEVCONTAINER=true

# Create workspace and config directories
RUN mkdir -p /workspace /home/node/.claude && \
  chown -R node:node /workspace /home/node/.claude

WORKDIR /workspace

# Install git-delta for better diffs
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  sudo dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# Install Python 3.12
RUN uv python install 3.12

# Install c1 command for launching Claude in tmux sessions
RUN cat <<'SCRIPT' > /usr/local/bin/c1
#!/bin/bash
session_num="${1}"
TMUX_SESSION="claude${session_num:+-$session_num}"

if [ -n "$TMUX" ]; then
    # Already inside tmux — create if needed, then switch
    if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        tmux new-session -d -s "$TMUX_SESSION" "claude --dangerously-skip-permissions; zsh"
    fi
    tmux switch-client -t "$TMUX_SESSION"
else
    # Not in tmux — attach or create
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        tmux attach -t "$TMUX_SESSION"
    else
        tmux new-session -s "$TMUX_SESSION" "claude --dangerously-skip-permissions; zsh"
    fi
fi
SCRIPT
RUN chmod +x /usr/local/bin/c1

# Enable corepack for pnpm support
RUN corepack enable

# Set up non-root user
USER node

# Configure npm and shell
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=$PATH:/usr/local/share/npm-global/bin
ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano

# Install zsh with powerlevel10k
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
  -a "source /usr/share/doc/fzf/examples/completion.zsh" \
  -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  -x

# Keep SSH agent accessible inside tmux and docker exec sessions
RUN cat <<'ZSHRC' >> ~/.zshenv

# SSH agent: use existing socket (VS Code) or fall back to host-mounted socket
if [ -z "$SSH_AUTH_SOCK" ] || ! [ -S "$SSH_AUTH_SOCK" ]; then
    [ -S "/tmp/ssh-auth-host.sock" ] && export SSH_AUTH_SOCK="/tmp/ssh-auth-host.sock"
fi

# Stable symlink so tmux sessions survive VS Code reconnects
if [ -n "$SSH_AUTH_SOCK" ] && [ -S "$SSH_AUTH_SOCK" ] && [ "$SSH_AUTH_SOCK" != "$HOME/.ssh/ssh_auth_sock" ]; then
    mkdir -p ~/.ssh
    ln -sf "$SSH_AUTH_SOCK" "$HOME/.ssh/ssh_auth_sock"
    export SSH_AUTH_SOCK="$HOME/.ssh/ssh_auth_sock"
fi
ZSHRC

# Configure tmux: mouse scrolling + refresh SSH/display env vars on attach
RUN cat <<'EOF' > ~/.tmux.conf
set -g mouse on
set-option -g update-environment "SSH_AUTH_SOCK SSH_CONNECTION DISPLAY"
EOF

# Install Claude Code using native installer
RUN curl -fsSL https://claude.ai/install.sh | bash -s ${CLAUDE_CODE_VERSION}
ENV PATH="/home/node/.local/bin:$PATH"

# Install OpenAI Codex
RUN npm install -g @openai/codex

# Configure Codex for devcontainer (container is the safety boundary)
RUN mkdir -p /home/node/.codex && cat <<'EOF' > /home/node/.codex/config.toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
web_search = "live"
EOF
