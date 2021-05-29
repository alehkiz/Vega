# Material de apoio para Vega
## Roles [Nível de acesso]
Os níveis de acesso são númerados e ficam entre 0 e 4 sendo que cada um deles é identificado como:

 0. Administrador
 1. Gerenciados de Usuários
 2. Gerenciador de Conteúdo
 3. Colaborador de Conteúdo
 4. Suporte
 5. Visualizador

>admin = Role()

>admin.level = 0

>admin.name = 'admin'

>admin.description = 'Adminitrador'

>man_user = Role()

>man_user.level = 1

>man_user.name = 'manager_user'

>man_user.description = 'Gerenciador de Usuários'

>man_cont = Role()

>man_cont.level = 2

>man_cont.name = 'manager_content'

>man_cont.description = 'Gerenciador de Conteúdo'

>aux_cont = Role()

>aux_cont.level = 3

>aux_cont.name = 'aux_content'

>aux_cont.description = 'Colaborador de Conteúdo'

>support_cont = Role()

>support_cont.level = 5

>support_cont.name = 'support'

>support_cont.description = 'Suporte'

>view_cont = Role()

>view_cont.level = 5

>view_cont.name = 'viewer_content'

>view_cont.description = 'Visualizador de Conteúdo'

>db.session.add(admin)

>db.session.add(man_user)

>db.session.add(man_cont)

>db.session.add(view_cont)

>db.session.add(support_cont)

>db.session.commit()

