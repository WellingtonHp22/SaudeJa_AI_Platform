# Médias Móveis de Casos e Mortes e Dias Anômalos

Os dados nestes arquivos são uma versão diferente dos dados em nossos principais [arquivos](https://github.com/nytimes/covid-19-data) de casos e mortes dos EUA. Em vez de totais cumulativos, cada arquivo contém o número diário de novos casos e mortes, a média móvel de sete dias e a média móvel de sete dias por 100.000 habitantes.

Estes dados foram reportados por dezenas de jornalistas do Times, extraindo de uma colcha de retalhos de fontes governamentais locais, estaduais e nacionais. A natureza em constante evolução da pandemia de coronavírus significou que a forma como esses funcionários reportaram seus dados nem sempre foi consistente.

Na compilação dos dados, escolhemos priorizar a precisão de nossas contagens cumulativas de casos. Por causa disso, o número de novos casos diários pode às vezes parecer anômalo porque é derivado da diferença nas contagens cumulativas de um dia para outro.

Na criação de nossas médias móveis, baseamo-nos em nossa experiência relatando dados de coronavírus desde o início de 2020. Usando esse julgamento editorial e expertise, elegemos excluir certos pontos de dados do cálculo dessas médias porque eles distorceriam as tendências dos dados em nível municipal, estadual ou nacional. Essas instâncias estão listadas, assim como nosso melhor entendimento da razão para a anomalia dos dados.

Toda a metodologia observada em nossa descrição dos principais dados de casos e mortes continua se aplicando aqui.

## Médias Móveis

Os campos têm as seguintes definições:

* **geoid**: Um identificador geográfico único para cada local. Para municípios e estados, os cinco dígitos finais são os mesmos que o código FIPS quando possível. Em casos onde atribuímos um identificador não padrão, o geoid terminará em `99[0-9]`.  
* **cases**: O número de novos casos de Covid-19 reportados naquele dia, incluindo tanto confirmados quanto prováveis.  
* **cases_avg**: O número médio de novos casos reportados nos sete dias mais recentes de dados.  
* **cases_avg_per_100k**: A `cases_avg` por 100.000 pessoas.  
* **deaths**: O número total de novas mortes por Covid-19 reportadas naquele dia, incluindo tanto confirmadas quanto prováveis.  
* **deaths_avg**: O número médio diário de novas mortes reportadas no período mais recente. Mortes em nível municipal são calculadas em média por 30 dias. Mortes estaduais, territoriais e nacionais são calculadas em média por 7 dias.  
* **deaths_avg_per_100k**: A `deaths_avg` por 100.000 pessoas.  

Porque muitas agências não reportam dados todos os dias, variações na programação em que casos ou mortes são reportados, como em feriados, podem causar padrões irregulares em uma média móvel simples de sete dias.

Para ajustar isso em nossas médias, o número de dias incluídos na média pode ser estendido se houver dias dentro da faixa de tempo sem dados reportados. A média é estendida para dias mais antigos até que pelo menos sete dias de dados estejam incluídos.

Se os dias mais recentes não tiverem dados reportados, então a média é estendida ainda mais para trás até que sete dias de dados estejam incluídos. Dados reportados em um dia que segue um ou mais dias sem dados reportados são assumidos como representando vários dias de dados. Em qualquer média, esse dia e todos os dias anteriores sem reporte são sempre incluídos juntos na média. Isso pode fazer com que algumas médias incluam mais de sete dias.

Para as médias nacionais de casos e mortes dos EUA, a média é a soma do número médio de casos e mortes em todos os estados e territórios a cada dia. Essa média pode não corresponder à média quando calculada a partir do total de casos e mortes dos EUA, a fim de levar em conta relatórios de casos e mortes em horários irregulares em nível estadual.

Veja a seção de metodologia para uma discussão mais detalhada sobre como anomalias de reporte em um único dia afetam a média.

### Dados em Nível Nacional dos EUA

O número diário de casos e mortes recém-reportados em todo o país, incluindo todos os estados, territórios dos EUA e o Distrito de Columbia, pode ser encontrado no arquivo [us.csv](us.csv).  ([Arquivo CSV bruto aqui.](https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us.csv))

```
date,geoid,cases,cases_avg,cases_avg_per_100k,deaths,deaths_avg,deaths_avg_per_100k
2020-01-21,USA,1,0.14,0,0,0,0
...
```

### Dados em Nível Estadual

Os dados em nível estadual podem ser encontrados no arquivo [states.csv](us-states.csv). ([Arquivo CSV bruto aqui.](https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv))

```
date,geoid,state,cases,cases_avg,cases_avg_per_100k,deaths,deaths_avg,deaths_avg_per_100k
2020-01-21,USA-53,Washington,1,0.14,0,0,0,0
...
```

### Dados em Nível de Condado

Dados recentes em nível de condado podem ser encontrados no arquivo [us-counties-recent.csv](us-counties-recent.csv). ([Arquivo CSV bruto aqui.](https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-recent.csv))

```
date,geoid,county,state,cases,cases_avg,cases_avg_per_100k,deaths,deaths_avg,deaths_avg_per_100k
2020-01-21,USA-53061,Snohomish,Washington,1,0.14,0.02,0,0,0
...
```

Este arquivo contém dados apenas para os últimos 30 dias.

Agora existem arquivos em nível de condado para cada ano da pandemia, como [us-counties-2020.csv](us-counties-2020.csv). Para criar um único arquivo cobrindo toda a pandemia, combine cada arquivo anual.

Há também um arquivo mais antigo, [us-counties.csv](us-counties.csv) que contém dados desde o início da pandemia até setembro de 2021. Vale ressaltar que este arquivo de condados é grande demais para ser aberto no Excel e grande demais para continuar sendo atualizado no Github. ([Arquivo CSV bruto aqui.](https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties.csv)). 

## Anomalias

A lista de dias anômalos está no arquivo [anomalies.csv](anomalies.csv). ([Arquivo CSV bruto aqui.](https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/anomalies.csv))

```
date,end_date,county,state,geoid,type,omit_from_rolling_average,omit_from_rolling_average_on_subgeographies,adjusted_daily_count_for_avg,description
2020-04-06,,New York City,New York,USA-36998,deaths,,,The Times began using deaths reported by the New York State Health Department instead of the city's health department.
...
```

Os campos têm as seguintes definições: 

* **date**: A data à qual a anomalia se aplica.  
* **end_date**: Para anomalias que se estendem por vários dias, o último dia ao qual se aplica. Caso contrário, deixado em branco.  
* **geoid**: Um identificador geográfico único para cada lugar. Use isso para corresponder ao arquivo de médias móveis.  
* **type**: Se a anomalia se aplica aos dados de casos, mortes ou ambos.  
* **omit_from_rolling_average**: Isso será `yes` se os dados daquele dia forem excluídos do cálculo das médias móveis. Caso contrário, deixado em branco.  
* **omit_from_rolling_average_on_subgeographies**: Isso será `yes` se os dados daquele dia forem excluídos do cálculo das médias móveis, para todas as subgeografias, ou seja, os condados dentro de um estado. Caso contrário, deixado em branco.  
* **adjusted_daily_count_for_avg**: Se o total diário incluir um grande backlog conhecido, este é o ajuste na contagem de casos ou mortes usado para calcular uma média móvel atual mais precisa.  
* **description**: Uma nota explicando a causa da anomalia, com base na comunicação e/ou reporte de dados por oficiais locais. Essas explicações aparecem na parte inferior das páginas de acompanhamento geográfico.  

### Metodologia de Anomalias

A lista de anomalias publicada aqui é curada e mantida com base em nossa revisão diária dos novos casos e mortes reportados a cada dia, e verificada por declarações públicas publicadas por departamentos de saúde, seja publicamente ou por meio de comunicados à imprensa, ou por nossa própria reportagem e pesquisa adicionais. Não é uma lista completa de todas as anomalias com dados de Covid, nem baseada em qualquer detecção de outliers estatística.

As anomalias identificadas são frequentemente devido a revisões feitas por oficiais para melhorar a qualidade geral dos dados que divulgaram. Muitas pequenas anomalias devido a backlogs de casos ou revisões menores de números previamente anunciados não estão incluídas aqui, particularmente em nível de condado. Não há anomalias listadas do início da pandemia. Ao decidir se deve ou não listar uma anomalia, julgamos se um membro do público precisaria daquela nota para entender e contextualizar a contagem de casos ou mortes daquele dia.

Ao decidir excluir uma anomalia de nossas médias móveis, usamos nosso melhor julgamento sobre se incluir o dia na média móvel distorceria significativamente a tendência geral aparente nos dados. Como flutuações de dados são comuns e as agências variam em seus ritmos típicos de reporte, descobrimos que não é benéfico usar um padrão completamente objetivo, e tendemos a não remover dados das médias móveis. Fatores que consideramos incluem: a proporção de casos ou mortes anômalas no total diário, se a informação é relevante para tendências recentes, e quanta demora ou variação é típica para uma determinada fonte de dados.

Às vezes removemos os números de um dia da média móvel em nível estadual, mas não em nível de condado ou vice-versa, porque os dados em nível de município e estado podem vir de fontes diferentes, ou um estado pode fornecer uma explicação mais detalhada dos casos em nível estadual do que em nível de condado.

Os dados populacionais usados para calcular figuras per capita vêm da estimativa da população de 2019 do U.S. Census Bureau.


## Licença e Atribuição

Estes dados são licenciados sob os mesmos termos que nossos dados sobre [Covid-19 nos Estados Unidos](https://github.com/nytimes/covid-19-data). Em geral, estamos tornando esses dados disponíveis publicamente para amplo uso público não comercial, incluindo por pesquisadores médicos e de saúde pública, formuladores de políticas, analistas e mídia local.

Se você usar estes dados, deve atribuí-los a "The New York Times" em qualquer publicação. Se você quiser uma descrição mais expandida dos dados, pode dizer: "Dados do The New York Times, com base em relatórios de agências de saúde estaduais e locais."

Para trabalhos que seguem o formato APA, recomendamos a seguinte citação: "The New York Times. (2021). Dados sobre o coronavírus (Covid-19) nos Estados Unidos. Recuperado em [Inserir Data Aqui], de https://github.com/nytimes/covid-19-data."

Se você usar em uma apresentação online, agradeceríamos se você vinculasse à nossa página de acompanhamento dos EUA em [https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html](https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html).

Se você usar estes dados, por favor, nos informe pelo e-mail covid-data@nytimes.com.

Veja nossa [LICENÇA](https://github.com/nytimes/covid-19-data/blob/master/LICENSE) para os termos completos de uso destes dados.

## Contate-Nos

Se você tiver dúvidas sobre os dados ou condições de licenciamento, entre em contato conosco pelo e-mail:

covid-data@nytimes.com

## Contribuidores

[A lista de contribuintes é a mesma que a lista para os principais dados sobre o coronavírus nos Estados Unidos](https://github.com/nytimes/covid-19-data)
