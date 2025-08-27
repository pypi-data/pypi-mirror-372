# mtcli-pa
  
Plugin mtcli para calcular níveis e projeções de price action.
  
---
  
## Instalação
  
```cmd
pip install mtcli-pa
```
  
---
  
## Comandos
  
- níveis e projeções de uma lateralidade: 
`mt pa tr 140800 140200` - calcula terços superior e inferior e projeção de 100% com base no tamanho da lateralidade de máxima = 140800 e mínima = 140200.  
- níveis de retração e projeção de 100% de um rompimento: 
`mt pa bo 140800 140200` - calcula retrações e projeção de um rompimento de alta de máxima = 140800 e mínima = 140200,  
`mt pa bo 140200 140800` - calcula retrações e projeção de um rompimento de baixa de mínima = 140200 e máxima = 140800.  
- próximo pomto de uma linha de tendência/canal: 
`mt pa ln 140500 140800` - calcula o próximo preço da linha que passa por 140500 e 140800.  
