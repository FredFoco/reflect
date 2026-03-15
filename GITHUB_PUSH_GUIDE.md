# 🚀 GitHub Push - Guia Passo a Passo

## Seu Username: `FredFoco`

---

## PASSO 1: Criar Personal Access Token (PAT)

### O que é PAT?
É como uma senha segura para o Git acessar seu GitHub sem usar sua senha real.

### Como Criar:

1. Vá para: **https://github.com/settings/tokens/new**

2. Preencha:
   - **Token name**: `reflect-push` (ou qualquer nome)
   - **Expiration**: `90 days` (ou o que preferir)

3. Selecione as permissões (checkboxes):
   - ✅ `repo` (acesso completo a repositórios)

4. Clique: **Generate Token**

5. **COPIE O TOKEN** (você não verá de novo!)
   - Exemplo: `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

---

## PASSO 2: Criar Repositório no GitHub

1. Vá para: **https://github.com/new**

2. Preencha:
   - **Repository name**: `reflect`
   - **Description**: `CS50 Final Project - Journaling app with emotional tracking and AI insights`
   - **Visibility**: Public
   - **NÃO** inicialize com README, .gitignore ou license

3. Clique: **Create Repository**

4. Você será redirecionado para a página do repositório vazio

---

## PASSO 3: Fazer o Push (Terminal)

Execute estes comandos **na ordem**:

```bash
cd /Users/fredcuha/Desktop/Final\ Project\ CS50\ 2026

git remote add origin https://github.com/FredFoco/reflect.git
git branch -M main
git push -u origin main
```

### Quando Pedir Credenciais:

**Usuário**: `FredFoco`  
**Senha**: Cole o TOKEN que você copiou no Passo 1

---

## ✅ Resultado

Depois de fazer esses 3 passos, você terá:
- ✅ Repositório no GitHub: `github.com/FredFoco/reflect`
- ✅ Todo o código enviado
- ✅ Pronto para submissão no CS50

---

## 📋 Checklist Completo

- [ ] **PASSO 1**: Criar PAT (token)
- [ ] **PASSO 2**: Criar repositório no GitHub
- [ ] **PASSO 3**: Fazer push com os comandos acima

---

## 💡 Se Algo Der Errado

### Erro: "remote already exists"
```bash
git remote remove origin
git remote add origin https://github.com/FredFoco/reflect.git
git push -u origin main
```

### Erro: "Authentication failed"
- Verifique se copiou o TOKEN correto
- Tente novamente com o TOKEN completo

### Erro: "Repository not found"
- Confirme que criou o repositório no GitHub
- Verifique se o nome está correto: `github.com/FredFoco/reflect`

---

## ✨ Depois de Fazer Push

Você verá no GitHub:
- ✅ 28 arquivos
- ✅ Histórico de commits
- ✅ Toda documentação
- ✅ Código pronto para submissão

---

## 🎯 Resumo Rápido

**3 Passos Simples:**
1. Criar PAT (token) no GitHub
2. Criar repositório `reflect` no GitHub
3. Executar 3 comandos no terminal

**Tempo total: ~5 minutos** ⏱️

---

**Sucesso! 🚀**

