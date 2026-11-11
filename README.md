# Analisador Léxico com Autômato Finito Determinístico

Trabalho Discente Efetivo de Linguagens Formais, Ciência da Computação, URI Erechim.

Programa em Python que reconhece uma linguagem regular usando um autômato finito determinístico (AFD). A cada símbolo digitado, o autômato muda de estado e a interface mostra a transição realizada. Ao teclar espaço, a sentença é indicada como reconhecida ou rejeitada.

**Autores:** Nome do Componente 1 e Nome do Componente 2

## Linguagem reconhecida

```
L(G) = { x | x ∈ (0,1)+ e se x começa com 0 então o nº de 0's é par,
                               senão o nº de 0's é ímpar }
```

Alfabeto: `{0, 1}`. A cadeia vazia não pertence à linguagem.

### Autômato

AFD `M = (K, Σ, δ, q0, F)` com `K = {A, B, C, D, E}`, `q0 = A` e `F = {C, E}`.

| Estado | Significado |
|---|---|
| A | nada lido |
| B | começou com 0, número de 0's ímpar |
| C | começou com 0, número de 0's par (final) |
| D | começou com 1, número de 0's par |
| E | começou com 1, número de 0's ímpar (final) |

| δ | 0 | 1 | ε |
|---|---|---|---|
| → A | B | D | |
| B | C | B | |
| C | B | C | ε |
| D | E | D | |
| E | D | E | ε |

### Gramática regular equivalente

Os estados finais são identificados pela produção `ε`.

```
A ::= 0B | 1D
B ::= 0C | 1B
C ::= 0B | 1C | ε
D ::= 0E | 1D
E ::= 0D | 1E | ε
```

## Requisitos

- Python 3
- Tkinter (já incluído no Python para Windows e macOS)

No Linux (Debian/Ubuntu), o Tkinter é um pacote separado:

```bash
sudo apt install python3-tk
```

## Execução

```bash
python3 analisador_lexico.py
```

## Uso

| Tecla | Ação |
|---|---|
| `0` ou `1` | lê o símbolo e muda o estado do autômato |
| Espaço | encerra a sentença e mostra RECONHECIDA ou REJEITADA |
| Backspace | desfaz o último símbolo |
| Esc | limpa a sentença |

Qualquer outro símbolo é ignorado. Ao encerrar uma sentença, o autômato volta ao estado inicial.

A interface exibe o diagrama de transição (com o estado atual e o caminho percorrido destacados), a tabela de transições, a lista de passos do reconhecimento e a gramática da linguagem.

## Estrutura do código

O arquivo `analisador_lexico.py` é dividido em três partes:

1. **Definição do autômato:** `ESTADOS`, `INICIAL`, `FINAIS`, `DELTA`, `SIGNIFICADO` e `POS`.
2. **Lógica:** `simular()` executa o AFD consultando a tabela `DELTA`, `aceita()` verifica se o estado é final e `gerar_gramatica()` monta a gramática a partir do autômato.
3. **Interface:** classe `App`, em Tkinter.

## Alterando a linguagem

Basta editar a parte 1. Para que o programa funcione, é preciso respeitar:

- todo estado em `ESTADOS` tem uma transição em `DELTA` para cada símbolo do alfabeto (tabela total);
- todo estado tem entrada em `SIGNIFICADO` e em `POS`;
- `INICIAL` e `FINAIS` contêm apenas estados que existem em `ESTADOS`;
- estados com laço desenhado na fileira de cima do diagrama devem estar em `LOOP_PARA_CIMA`.