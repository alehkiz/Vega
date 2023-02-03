# Sistema de perguntas e respostas



![GitHub repo size](https://img.shields.io/github/repo-size/alehkiz/Vega?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/alehkiz/Vega?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/alehkiz/Vega?style=for-the-badge)
![Github open issues](https://img.shields.io/github/issues/alehkiz/Vega?style=for-the-badge)


Sistema de pergunta e resposta utilizado pelo Detran.SP, com o objetivo de padronização e democratização do conhecimento no órgão. 

* **O sistema foca na busca de termos com o FTS disponível no PosgreSQL:**
  * Sistema é estruturado em três pilares de acordo com o nível de quem faz a pesquisa ou pergunta;
  * Dashboard com todos os dados importantes sobre a utilização dos sistema;
  * Para os administradores o fluxo de pergunta deve sempre ter uma resposta pelo perfil de Suporte, e aprovado por um administrador.
  * Para os usuários são apresentadas as perguntas aprovadas nos ultimos 30 dias.
* Sistema de notificação para informar sobre problemas, incidentes ou erros de forma geral;

### Melhorias futuras:

- [X] Sistema de notificação;
- [] Incluir requisições assincronas;
- [] Incluir a leitura de PDF e adicionar como pesquisa sobre manuais;

## 💻 Pré-requisitos

* versão mais recente de `python`
* Utilize um ambiente virtual: https://docs.python.org/3/tutorial/venv.html
* No ambiente virtual, instale as bibliotecas necessárias: `pip install -r requirements.txt`

## ☕ Subindo o servidor:

Para utilizar, siga estas etapas:

Na raiz do repositórico, inicie o ambiente virual e instale os pacotes necessários, e rode flask run.

Lembre-se que utilizamos o postgres, logo, você deverá ter criado, além de criar o banco de dados com o nome `vega` após criar o banco de dados, rode o comando `flask shell` e no terminal utilize o comando `db.create_all()`, saia e então rode `flask run`

O servidor também roda em Docker, para isso rode o arquivo `docker.sh`

## Disponível em:
https://facilitar.onrender.com

## 📝 Licença

Esse projeto está sob licença. Veja o arquivo [LICENÇA](LICENSE.md) para mais detalhes.

[⬆ Voltar ao topo](#Vega)<br>
