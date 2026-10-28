"""
Arvore B implementada do zero.

Uso no sistema: indexar os corpos celestes por DISTANCIA (km). Como a
Arvore B mantem as chaves sempre ordenadas, ela permite:
  - listagem ORDENADA por distancia sem precisar ordenar (percurso em ordem).
"""

from typing import Any, List, Optional, Tuple

from src.estruturas.interfaces import IEstruturaBusca


class _No:
    """No da Arvore B. chaves[i] guarda a lista valores[i]; num no interno,
    filhos[i] contem chaves menores que chaves[i] e filhos[i+1] maiores."""

    __slots__ = ("chaves", "valores", "filhos", "folha")

    def __init__(self, folha: bool):
        self.chaves: List[float] = []
        self.valores: List[List[Any]] = []
        self.filhos: List["_No"] = []
        self.folha = folha


class ArvoreB(IEstruturaBusca):

    def __init__(self, grau_minimo: int = 3):
        if grau_minimo < 2:
            raise ValueError("grau_minimo deve ser >= 2")
        self._t = grau_minimo
        self._raiz = _No(folha=True)

        self._quantidade_elementos = 0   # valores armazenados
        self._quantidade_chaves = 0      # chaves (distancias) distintas
        self._quantidade_nos = 1         # a raiz conta
        self._altura = 1

        # --- metricas de instrumentacao ---
        self._total_divisoes = 0
        self._total_buscas = 0
        self._total_nos_visitados = 0
        self._nos_visitados_ultima_busca = 0

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    @staticmethod
    def _primeiro_indice_maior_ou_igual(no: _No, chave: float) -> int:
        """Posicao da primeira chave do no que seja >= chave (ou len(chaves))."""
        i = 0
        while i < len(no.chaves) and no.chaves[i] < chave:
            i += 1
        return i

    def _localizar(self, chave: float) -> Tuple[Optional[Tuple[_No, int]], int]:
        """Desce a arvore procurando a chave. Retorna (achado, nos_visitados),
        onde achado e (no, indice) ou None se a chave nao existir."""
        atual = self._raiz
        visitados = 0
        while True:
            visitados += 1
            i = self._primeiro_indice_maior_ou_igual(atual, chave)
            if i < len(atual.chaves) and atual.chaves[i] == chave:
                return (atual, i), visitados
            if atual.folha:
                return None, visitados
            atual = atual.filhos[i]

    def _registrar_busca(self, visitados: int) -> None:
        self._total_buscas += 1
        self._total_nos_visitados += visitados
        self._nos_visitados_ultima_busca = visitados

    # ------------------------------------------------------------------
    # Dados da Arvore B
    # ------------------------------------------------------------------
    @property
    def grau_minimo(self) -> int:
        return self._t

    @property
    def altura(self) -> int:
        return self._altura

    @property
    def quantidade_nos(self) -> int:
        return self._quantidade_nos

    @property
    def total_divisoes(self) -> int:
        return self._total_divisoes

    @property
    def total_buscas(self) -> int:
        return self._total_buscas

    @property
    def total_nos_visitados(self) -> int:
        return self._total_nos_visitados

    @property
    def nos_visitados_ultima_busca(self) -> int:
        return self._nos_visitados_ultima_busca

    # ------------------------------------------------------------------
    # Insercao
    # ------------------------------------------------------------------
    def inserir(self, chave: float, valor: Any) -> None:
        # chave ja existe: so mexe na lista de valores dela
        achado, _ = self._localizar(chave)
        if achado is not None:
            no, i = achado
            lista = no.valores[i]
            for j, existente in enumerate(lista):
                if existente == valor:
                    lista[j] = valor  # mesmo elemento: atualiza
                    return
            lista.append(valor)
            self._quantidade_elementos += 1
            return

        # chave nova. Se a raiz esta cheia, a arvore cresce em altura
        if len(self._raiz.chaves) == 2 * self._t - 1:
            nova_raiz = _No(folha=False)
            nova_raiz.filhos.append(self._raiz)
            self._raiz = nova_raiz
            self._quantidade_nos += 1
            self._altura += 1
            self._dividir_filho(nova_raiz, 0)

        self._inserir_em_no_nao_cheio(self._raiz, chave, valor)
        self._quantidade_chaves += 1
        self._quantidade_elementos += 1

    def _dividir_filho(self, pai: _No, i: int) -> None:
        """Divide o filho cheio pai.filhos[i] em dois nos de t-1 chaves; a
        chave do meio sobe para o pai."""
        t = self._t
        filho = pai.filhos[i]
        irmao = _No(folha=filho.folha)

        chave_do_meio = filho.chaves[t - 1]
        valores_do_meio = filho.valores[t - 1]

        irmao.chaves = filho.chaves[t:]
        irmao.valores = filho.valores[t:]
        filho.chaves = filho.chaves[:t - 1]
        filho.valores = filho.valores[:t - 1]
        if not filho.folha:
            irmao.filhos = filho.filhos[t:]
            filho.filhos = filho.filhos[:t]

        pai.chaves.insert(i, chave_do_meio)
        pai.valores.insert(i, valores_do_meio)
        pai.filhos.insert(i + 1, irmao)

        self._quantidade_nos += 1
        self._total_divisoes += 1

    def _inserir_em_no_nao_cheio(self, no: _No, chave: float, valor: Any) -> None:
        """Desce ate a folha certa dividindo, no caminho, todo filho cheio
        (assim nunca precisa voltar para cima). A chave e sempre nova aqui."""
        while True:
            i = self._primeiro_indice_maior_ou_igual(no, chave)
            if no.folha:
                no.chaves.insert(i, chave)
                no.valores.insert(i, [valor])
                return
            if len(no.filhos[i].chaves) == 2 * self._t - 1:
                self._dividir_filho(no, i)
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

    # ------------------------------------------------------------------
    # Operacoes da interface (busca)
    # ------------------------------------------------------------------
    def buscar(self, chave: float) -> Optional[List[Any]]:
        """Retorna a lista de corpos com exatamente essa distancia, ou None."""
        achado, visitados = self._localizar(chave)
        self._registrar_busca(visitados)
        if achado is None:
            return None
        no, i = achado
        return list(no.valores[i])

    def existe(self, chave: float) -> bool:
        achado, visitados = self._localizar(chave)
        self._registrar_busca(visitados)
        return achado is not None

    def todos_valores(self) -> List[Any]:
        resultado: List[Any] = []
        self._coletar_faixa(self._raiz, float("-inf"), float("inf"), resultado)
        return resultado

    def __len__(self) -> int:
        return self._quantidade_elementos

    # ------------------------------------------------------------------
    # Busca por faixa (o motivo de existir da Arvore B no sistema)
    # ------------------------------------------------------------------
    def buscar_por_faixa(self, minimo: float, maximo: float) -> List[Any]:
        """Valores com minimo <= chave <= maximo, em ordem crescente."""
        if minimo > maximo:
            self._registrar_busca(0)
            return []
        resultado: List[Any] = []
        visitados = self._coletar_faixa(self._raiz, minimo, maximo, resultado)
        self._registrar_busca(visitados)
        return resultado

    def _coletar_faixa(self, no: _No, minimo: float, maximo: float,
                       resultado: List[Any]) -> int:
        visitados = 1
        n = len(no.chaves)

        i = 0
        while i < n and no.chaves[i] < minimo:
            i += 1

        while True:
            # o filho i guarda chaves entre chaves[i-1] e chaves[i]
            if not no.folha:
                visitados += self._coletar_faixa(no.filhos[i], minimo, maximo, resultado)
            if i >= n or no.chaves[i] > maximo:
                break
            resultado.extend(no.valores[i])
            i += 1
        return visitados

    # ------------------------------------------------------------------
    # Instrumentacao
    # ------------------------------------------------------------------
    def imprimir_estatisticas(self) -> None:
        print("--- Estatisticas da Arvore B ---")
        print(f"Altura:                          {self._altura}")
        print(f"Total de divisoes de no:         {self._total_divisoes}")
     
       