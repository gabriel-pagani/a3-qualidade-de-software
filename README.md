# A3 - Qualidade de Software

O  trabalho  consiste  em  aplicar  o  processo  de  gestão  de  configuração  de  software  em  sistema 
legado. Neste  processo  deverá  ser  realizado  a  cobertura  e  análise  estática  do  código  para  melhorar  a 
qualidade do software legado.

### 👥 Integrantes

| Aluno | RA | GitHub |
| :---- | :- | :----- |
| André Leonardo da Silva | 1072415366 | [@ffcand](https://github.com/ffcand) |
| Gabriel Pagani de Souza | 1072410845 | [@gabriel-pagani](https://github.com/gabriel-pagani) |
| Matheus Joseph de Freitas Coloni | 1072411389 | [@MatheusColoni](https://github.com/MatheusColoni) |
| Rennan Rosa Guedes | 1072418210 | [@Guedesrosa](https://github.com/Guedesrosa) |

### ⚙️ Requisitos Funcionais

- **RF01 - Autenticação (Senha Mestre):** O sistema deve exigir uma senha mestre para liberar acesso ao cofre de senhas.
- **RF02 - Gerenciamento de Senhas:** O usuário deve ser capaz de criar, ler, atualizar e excluir as suas credenciais no cofre.
- **RF03 - Categorização de Senhas:** O sistema deve permitir que o usuário classifique e gerencie grupos/tipos de senhas (ex: redes sociais, contas bancárias, etc.).
- **RF04 - Criptografia Automática:** O sistema deve encriptar uma senha antes de salvá-la no banco e desencriptá-la no momento da requisição feita pelo usuário autenticado.
- **RF05 - Interface Gráfica:** O sistema deve fornecer uma interface gráfica de usuário para facilitar a gestão do cofre.

### 🛡️ Requisitos Não Funcionais

- **RNF01 - Armazenamento Local:** Todos os dados devem permanecer exclusivamente armazenados de forma local, garantindo que não haja tráfego de dados sensíveis pela internet.
- **RNF02 - Segurança de Criptografia:** Os dados devem ser obrigatoriamente protegidos com algoritmos sólidos de criptografia.
- **RNF03 - Portabilidade:** O software deve rodar em ambientes e sistemas operacionais comuns (Linux, Windows e macOS) bastando ter o interpretador Python 3 disponível.
- **RNF04 - Desempenho e Rapidez:** As operações de pesquisa e descriptografia do cofre no banco devem ocorrer de forma quase que instantânea na interface gráfica.
- **RNF05 - Qualidade e Manutenibilidade:** O código deve aderir aos padrões de estilo do Python (analisado via linters) e possuir cobertura de código medida através de testes automatizados.
- **RNF06 - Usabilidade:** A interface gráfica deve ser responsiva e intuitiva, com foco na fluidez da navegação para usuários de qualquer nível técnico.
