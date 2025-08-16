# Rastreamento da Covid-19 em Faculdades e Universidades dos EUA

O New York Times divulgou [contagens de casos de Covid-19 reportados em campi universitários](https://www.nytimes.com/interactive/2021/us/college-covid-tracker.html) nos Estados Unidos durante o ano acadêmico de 2020-21.

Entre julho de 2020 e maio de 2021, conduzimos uma pesquisa contínua de faculdades e universidades americanas — incluindo todas as instituições públicas de quatro anos e todas as faculdades privadas que competem em esportes da N.C.A.A. — para rastrear o número de casos de coronavírus reportados entre estudantes e funcionários. A pesquisa agora inclui mais de 1,900 faculdades. A partir de 2021, o número de casos em 2021 também está incluído.

Estes dados foram atualizados pela última vez em 26 de maio de 2021.

## Dados

Os dados podem ser encontrados no arquivo **[colleges.csv](colleges.csv)**. ([CSV Bruto](https://raw.githubusercontent.com/nytimes/covid-19-data/master/colleges/colleges.csv))

```
date,state,county,city,ipeds_id,college,cases,cases_2021,notes
2021-02-26,Alabama,Madison,Huntsville,100654,Alabama A&M University,41,,
…
2021-02-26,Alabama,Jefferson,Birmingham,100663,University of Alabama at Birmingham,2856,570,"Total é conhecido por incluir um ou mais casos de uma escola de medicina, centro médico, hospital de ensino, ambiente clínico ou outro programa acadêmico em ciências da saúde."
```

Os campos têm as seguintes definições:

**date**: A data da última atualização.  
**state**: O estado onde a faculdade está localizada.  
**county**: O município onde a faculdade está localizada.  
**city**: A cidade onde a faculdade está localizada.  
**ipeds_id**: O número de ID do Sistema Integrado de Dados de Educação Pós-Secundária (IPEDS) para a faculdade.  
**college**: O nome da faculdade ou universidade.  
**cases**: O número total de casos reportados de Covid-19 entre estudantes e funcionários universitários em todas as áreas, incluindo aqueles cujos papéis como médicos, enfermeiros, farmacêuticos ou estudantes de medicina os colocam em maior risco de contrair o vírus, desde o início da pandemia.  
**cases_2021**: O número total de casos de Covid-19 recentemente reportados desde 1º de janeiro de 2021 apenas.
**notes**: Notas metodológicas específicas que se aplicam à instituição, por exemplo, se a contagem inclui casos de uma unidade médica, e se há possibilidade de que casos duplicados tenham sido contados devido à maneira como a instituição reporta os dados.   

Faculdades e universidades que reportaram zero casos serão listadas com um zero para casos, enquanto faculdades que não reportaram dados terão um campo em branco no campo de casos.

## Metodologia

Os dados são baseados em relatórios de faculdades e fontes governamentais e podem estar desatualizados. Os casos incluem os de estudantes, professores, funcionários e outros trabalhadores da faculdade. Faculdades e agências governamentais relatam esses dados de maneira diferente, portanto, tenha cautela ao comparar instituições. Algumas faculdades se recusaram a fornecer dados, forneceram dados parciais ou não responderam a perguntas. Em algumas instituições, os casos podem estar espalhados por vários campi. O total de casos inclui casos positivos confirmados e casos prováveis, quando disponíveis. As faculdades ocasionalmente ajustam seus dados para baixo se novas informações surgirem.

Como as faculdades relatam os dados de maneira diferente, e como os casos continuaram a surgir mesmo nos meses em que a maioria dos campi estava fechada, o The Times está contando todos os casos reportados desde o início da pandemia em 2020.

Sem um sistema nacional de rastreamento, as faculdades estão fazendo suas próprias regras sobre como contar infecções. Embora a pesquisa do The Times seja considerada o relato mais abrangente disponível, também é quase certamente uma subcontagem. Entre as faculdades contatadas pelo The Times, a maioria publicou informações sobre os casos online ou respondeu a pedidos de números de casos, mas outras não responderam, se recusaram a fornecer informações ou forneceram apenas informações parciais. Algumas faculdades relataram zero casos. O The Times obteve dados de casos por meio de pedidos de registros abertos em várias universidades públicas que, de outra forma, não forneceriam números.

Dadas as disparidades em tamanho, planos de reabertura e transparência entre as universidades, não é recomendável usar esses dados para fazer comparações entre campi. Algumas faculdades subtraem casos de suas contagens uma vez que as pessoas se recuperam. Algumas relatam apenas testes realizados no campus. Algumas faculdades relataram alguns casos sem identificar se ocorreram em 2020 ou 2021. Esses casos não estão incluídos em nossos totais.

Quando as faculdades observaram que uma pessoa infectada não teve acesso ao campus no mês anterior ao teste positivo, nós os excluímos de nossa contagem.

O tamanho das faculdades e universidades neste conjunto de dados varia amplamente, mas não calculamos ou publicamos contagens de casos per capita porque as instituições variam em relação a relatar casos entre professores e funcionários e em como a população total de professores, funcionários e estudantes é definida.

Como as faculdades continuam a mudar a forma como relatam os dados, não publicaremos nenhuma série temporal histórica do número de casos em diferentes momentos.

## Licença e Atribuição

Esses dados estão licenciados sob os mesmos termos que nossos [Dados sobre o Coronavírus nos Estados Unidos](https://github.com/nytimes/covid-19-data). Em geral, estamos tornando esses dados disponíveis publicamente para uso público amplo e não comercial, incluindo por pesquisadores médicos e de saúde pública, formuladores de políticas, analistas e meios de comunicação locais.

Se você usar esses dados, deve atribuí-los ao "The New York Times" em qualquer publicação. Se você quiser uma descrição mais expandida dos dados, pode dizer "A pesquisa do The New York Times sobre Faculdades e Universidades dos EUA"

Se você usar em uma apresentação online, agradeceríamos se você pudesse vincular à nossa matéria discutindo esses resultados [https://www.nytimes.com/interactive/2021/us/college-covid-tracker.html](https://www.nytimes.com/interactive/2021/us/college-covid-tracker.html).

Se você usar esses dados, por favor, nos avise pelo e-mail covid-data@nytimes.com.

Veja nossa [LICENÇA](https://github.com/nytimes/covid-19-data/blob/master/LICENSE) para os termos completos de uso desses dados.

## Contate-Nos

Se você tiver dúvidas sobre os dados ou condições de licenciamento, entre em contato conosco pelo e-mail:

covid-data@nytimes.com

## Contribuidores

Weiyi Cai, Danielle Ivory, Kirk Semple, Mitch Smith, Alex Lemonides, Lauryn Higgins, Adeel Hassan, Julia Calderone, Jordan Allen, Anne Barnard, Yuriria Avila, Brillian Bao, Elisha Brown, Alyssa Burr, Sarah Cahalan, Matt Craig, Yves De Jesus, Brandon Dupré, Timmy Facciola, Bianca Fortis, Grace Gorenflo, Benjamin Guggenheim, Barbara Harvey, Jacob LaGesse, Alex Lim, Alex Leeds Matthews, Jaylynn Moffat-Mowatt, Ashlyn O’Hara, Laney Pope, Cierra S. Queen, Natasha Rodriguez, Jess Ruderman, Alison Saldanha, Emily Schwing, Sarena Snider, Brandon Thorp, Kristine White, Bonnie G. Wong, Tiffany Wong e John Yoon.