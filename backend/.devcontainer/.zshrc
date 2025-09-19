export PATH="$HOME/.local/bin:$PATH"

# 启用自动补全
autoload -U compinit && compinit

# 历史搜索
bindkey '^[[A' up-line-or-search
bindkey '^[[B' down-line-or-search

# 提示符美化
setopt PROMPT_SUBST
PROMPT='%F{blue}%n@%m%f %F{green}%~%f %# '

# 别名
alias ll='ls -la'
alias gs='git status'
alias serve='uvicorn app.main:srv --reload --host 0.0.0.0 --port 8000'
alias test='pytest'
alias fmt='ruff check . --fix && black .'