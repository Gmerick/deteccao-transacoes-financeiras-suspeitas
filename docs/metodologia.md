# Metodologia

## 1. Problema de negócio

Equipes de prevenção a fraudes precisam selecionar, entre milhares de movimentações, quais transações merecem investigação primeiro. O projeto transforma sinais comportamentais em um score explicável e uma fila priorizada. Ele não bloqueia operações automaticamente.

## 2. Base sintética

A base representa 50.000 transações de 2.500 contas durante 2025. Foram simulados perfis de renda, valor típico, estado de origem, idade da conta, canal, tipo de operação, dispositivo e estabelecimento.

Quatro por cento das transações receberam um de cinco cenários conhecidos:

| Cenário | Como foi simulado | Objetivo analítico |
|---|---|---|
| Valor atípico | Valor muito acima do padrão individual | Detectar desvio comportamental |
| Horário incomum | Operação entre 00h e 04h com valor elevado | Combinar tempo e valor |
| Alta velocidade | Cinco operações da mesma conta em poucos minutos | Detectar rajadas |
| Novo dispositivo e local | Dispositivo não confiável fora do estado habitual | Detectar mudança contextual |
| Fracionamento | Várias operações arredondadas próximas no mesmo dia | Detectar padrão coordenado |

A semente fixa `2026` garante reprodutibilidade. Nenhum registro representa pessoa, instituição ou fraude real.

## 3. Engenharia de atributos

- média, mediana e desvio-padrão do valor por conta;
- z-score individual da transação;
- quantidade de operações da conta nas últimas 1h e 24h;
- hora, dia da semana e mês;
- divergência entre estado da transação e estado habitual;
- confiança do dispositivo;
- identificação de valores arredondados.

O z-score é calculado por:

```text
z = (valor da transação − média da conta) / desvio-padrão da conta
```

## 4. Regras e score

| Regra | Condição resumida | Pontos |
|---|---|---:|
| Valor atípico | z-score ≥ 3,5 | 30 |
| Alto valor | valor ≥ R$ 15.000 | 20 |
| Alta velocidade | ao menos 3 operações em 1 hora | 25 |
| Horário incomum | 00h–04h e valor ≥ 2,5× a mediana | 20 |
| Novo dispositivo + local | dispositivo novo e estado divergente | 25 |
| Valor arredondado | múltiplo de R$ 1.000 e valor ≥ R$ 1.000 | 10 |
| Possível fracionamento | R$ 3.000–4.500, PIX e ao menos 3 operações em 24h | 20 |

O score é a soma dos pontos, limitado a 100. Operações com score a partir de 20 entram na fila de alertas. O limiar foi escolhido para o case e deve ser calibrado em dados e custos reais.

## 5. Avaliação

Os rótulos simulados permitem calcular:

- **Precisão:** entre os alertas, quantos pertencem aos cenários simulados;
- **Recall:** entre os cenários simulados, quantos foram encontrados;
- **F1:** média harmônica de precisão e recall;
- **Taxa de alertas:** carga operacional imposta à equipe.

Resultado da execução versionada: precisão de 74,36%, recall de 83,40% e F1 de 78,62%. Esses valores medem apenas a recuperação dos padrões injetados, não o desempenho esperado em produção.

## 6. Limitações e uso responsável

- Padrões suspeitos não são prova de fraude ou ilícito.
- A base sintética simplifica comportamento, sazonalidade e dependências reais.
- O cálculo estatístico usa todo o período; uma implantação real deve evitar vazamento temporal e calcular atributos apenas com o histórico disponível no momento.
- Limiares devem considerar custo de investigação, perdas evitadas e experiência do cliente.
- Decisões adversas exigem governança, explicabilidade, monitoramento de vieses e revisão humana.
- Novos padrões exigem revisão periódica das regras e monitoramento de drift.

