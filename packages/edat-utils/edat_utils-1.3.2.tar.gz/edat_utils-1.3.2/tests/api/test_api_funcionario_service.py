from typing import List, Union
from edat_utils.api import ApiFuncionarioService
from edat_utils.api.models import TipoUsuario, Usuario


def test_get_funcionarios(get_api_funcionario_service: ApiFuncionarioService):
    query = f'startWith: {{nome: "MaR"}}'  # noqa
    funcionarios: Union[List[Usuario], None] = get_api_funcionario_service.get(
        query=query
    )

    if not funcionarios:
        assert False

    assert len(funcionarios) > 0

    for funcionario in funcionarios:
        assert funcionario.tipo_usuario in [
            TipoUsuario.FUNCIONARIO,
            TipoUsuario.FUNCAMP,
            TipoUsuario.DOCENTE,
        ]

        print(funcionario)
        assert funcionario.email
        assert funcionario.telefone
        assert funcionario.nome_unidade

        assert not getattr(funcionario, "nome_sindicato", None)
        assert not getattr(funcionario, "nomeSindicato", None)
        assert not getattr(funcionario, "nome_curso", None)
        assert not getattr(funcionario, "nomeCurso", None)
        # assert False
