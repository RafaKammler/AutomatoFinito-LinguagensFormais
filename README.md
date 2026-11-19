# Analisador Léxico com Autômato Finito Determinístico

Trabalho Discente Efetivo de Linguagens Formais, Ciência da Computação, URI Erechim.

Programa em Python que reconhece uma linguagem regular usando um autômato finito determinístico (AFD). A cada símbolo digitado, o autômato muda de estado e a interface mostra a transição realizada. Ao teclar espaço ou enter, a sentença é indicada como reconhecida ou rejeitada.

**Autores:** Nome do Componente 1 e Nome do Componente 2

## Linguagem reconhecida

```
L(G) = { x | x ∈ (0,1)+ e se x começa com 0 então o nº de 0's é par,
                               senão o nº de 0's é ímpar }
```

Alfabeto: `{0, 1}`. A cadeia vazia não pertence à linguagem.

### Autômato

AFD `M = (K, Σ, δ, q0, F)` com `K = {S, A, B, C, D}`, `q0 = S` e `F = {B, D}`.

| Estado | Significado |
|---|---|
| S | nada lido ainda |
| A | começou com 0, número de 0's ímpar |
| B | começou com 0, número de 0's par (final) |
| C | começou com 1, número de 0's par |
| D | começou com 1, número de 0's ímpar (final) |

| δ | 0 | 1 | ε |
|---|---|---|---|
| → S | A | C | |
| A | B | A | |
| B | A | B | ε |
| C | D | C | |
| D | C | D | ε |

### Gramática regular equivalente

Os estados finais são identificados pela produção `ε`.

```
S ::= 0A | 1C
A ::= 0B | 1A
B ::= 0A | 1B | ε
C ::= 0D | 1C
D ::= 0C | 1D | ε
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
| Espaço ou Enter | encerra a sentença e mostra RECONHECIDA ou REJEITADA |
| Backspace | desfaz o último símbolo |
| Esc | limpa a sentença |

Qualquer outro símbolo é ignorado. Ao encerrar uma sentença, o autômato volta ao estado inicial.

A interface exibe o diagrama de transição (com o estado atual, o caminho percorrido e a última transição destacados), a tabela de transições, a lista de passos do reconhecimento e a gramática da linguagem.

## Estrutura do código

O arquivo `analisador_lexico.py` é dividido em três partes:

1. **Configuração rápida (Definição do autômato):** `TEXTO_LINGUAGEM`, `ALFABETO`, `ESTADOS`, `INICIAL`, `FINAIS`, `TABELA_TRANSICAO`, `SIGNIFICADO`, `POSICOES_FIXAS`, `LOOP_PARA_CIMA` e teclas de controle.
2. **Pré-processamento e motor do autômato:** `construir_delta()` monta o dicionário `DELTA` a partir de `TABELA_TRANSICAO`, `calcular_posicoes()` define as coordenadas `POS` no grafo, `simular()` executa o AFD passo a passo, `aceita()` verifica se a sentença foi aceita e `gerar_gramatica()` gera a gramática regular equivalente.
3. **Interface gráfica:** tema de cores e classe `App`, em Tkinter.

## Alterando a linguagem

Basta editar a parte 1 do código:

- `INICIAL` e `FINAIS` devem conter apenas estados declarados em `ESTADOS`;
- em `TABELA_TRANSICAO`, a lista de destinos de cada estado deve seguir a mesma ordem dos símbolos em `ALFABETO`;
- **AFDs incompletos são suportados:** para omitir uma transição, use `None`, `""` ou `"-"` na tabela (o autômato indicará travamento/rejeição ao ler o símbolo);
- `SIGNIFICADO` e `POSICOES_FIXAS` são **opcionais**: estados novos sem entrada recebem uma descrição padrão e são posicionados automaticamente no diagrama;
- estados cujo auto-laço deve ser desenhado para cima devem ser listados em `LOOP_PARA_CIMA`.
