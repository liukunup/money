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
alias serve='npm run dev'
alias build='npm run build'
alias lint='npm run lint'
alias update='ncu -u && npm install'