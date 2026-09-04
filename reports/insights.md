# Insights e recomendações

## Resumo

O pipeline analisou 50.000 transações, somando R$ 34,16 milhões. O motor sinalizou 2.243 operações, equivalentes a 4,49% do volume e R$ 10,32 milhões. Contra os cenários sintéticos conhecidos, recuperou 1.668 casos: precisão de 74,36%, recall de 83,40% e F1 de 78,62%.

## Leitura dos resultados

### 1. Cobertura e carga operacional

O recall elevado mostra boa cobertura dos padrões desenhados, mas 2.243 alertas ainda precisam de priorização. O score e os níveis Alto/Crítico permitem que uma equipe comece por múltiplos sinais e maiores valores.

### 2. Desempenho por cenário

Valor atípico e novo dispositivo/local tiveram 100% de recall. Horário incomum chegou a 91,7%. Alta velocidade e fracionamento ficaram em torno de 62% porque as primeiras operações da sequência ainda não possuem evidência suficiente na janela móvel.

### 3. Falsos positivos

Foram gerados 575 alertas sobre transações marcadas como normais. Isso não significa erro automático: a geração normal também permite dispositivo novo, viagem, valor elevado e rajadas ocasionais. Em produção, confirmação de viagem, histórico do favorecido, biometria comportamental e resposta do cliente ajudariam a refinar os casos.

### 4. Canal

O App apresentou taxa de alertas de 5,53%, acima de ATM (4,37%) e E-commerce (4,12%). A diferença reflete a composição dos cenários simulados, especialmente PIX e sequências rápidas; não deve ser interpretada como evidência de que o canal é intrinsecamente menos seguro.

### 5. Valor financeiro

R$ 10,32 milhões aparecem em transações alertadas. Esse número mede exposição para investigação. Não é fraude confirmada, perda esperada ou economia potencial.

## Recomendações

1. Investigar primeiro casos Críticos, combinações de regras e maiores valores.
2. Agrupar sequências por conta em um único caso para evitar alertas duplicados.
3. Ajustar o limiar conforme a capacidade diária da equipe.
4. Capturar o desfecho da investigação para medir precisão real por regra.
5. Criar listas confiáveis de dispositivos, favorecidos e estabelecimentos.
6. Avaliar limiares específicos por segmento e tipo de transação.
7. Monitorar taxa de alertas, precisão, recall, perda evitada e tempo de tratamento.

