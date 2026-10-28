"""
Trie (arvore de prefixos) implementada do zero.

Uso no sistema: busca por PREFIXO de nomes (ex: digitar "mar" e encontrar
"Mars", "Marte").

As chaves sao normalizadas para minusculo, entao a busca ignora maiusculas.
"""

from typing import Any, List, Optional, Tuple

from src.estruturas.interfaces import IEstruturaBusca


class _No:
    """No da Trie: um dicionario de filhos (letra -> no) e, se um nome
    termina aqui, o valor associado."""

    __slots__ = ("filhos", "fim_de_palavra", "valor")

    def __init__(self):
        self.filhos: dict = {}
        self.fim_de_palavra = False
        self.valor: Any = None


class Trie(IEstruturaBusca):

    def __init__(self):
        self._raiz = _No()
        self._quantidade_elementos = 0
        self._quantidade_nos = 1  # a raiz conta

        # --- metricas de instrumentacao ---
        self._total_buscas = 0
        self._total_nos_visitados = 0
        self._nos_visitados_ultima_busca = 0

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    @staticmethod
    def _normalizar(chave: str) -> str:
        return chave.lower()

    def _encontrar_no(self, chave_normalizada: str) -> Tuple[Optional[_No], int]:
        """Desce a arvore seguindo a chave. Retorna (no_final, nos_visitados).
        no_final e None se o caminho nao existir."""
        atual = self._raiz
        visitados = 1  # a raiz
        for caractere in chave_normalizada:
            atual = atual.filhos.get(caractere)
            if atual is None:
                return None, visitados
            visitados += 1
        return atual, visitados

    def _registrar_busca(self, visitados: int) -> None:
        self._total_buscas += 1
        self._total_nos_visitados += visitados
        self._nos_visitados_ultima_busca = visitados

    # ------------------------------------------------------------------
    # Dados da Trie
    # ------------------------------------------------------------------
    @property
    def quantidade_nos(self) -> int:
        return self._quantidade_nos

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
    # Operacoes da interface
    # ------------------------------------------------------------------
    def inserir(self, chave: str, valor: Any) -> None:
        atual = self._raiz
        for caractere in self._normalizar(chave):
            proximo = atual.filhos.get(caractere)
            if proximo is None:
                proximo = _No()
                atual.filhos[caractere] = proximo
                self._quantidade_nos += 1
            atual = proximo

        # se a chave ja existe, apenas atualiza o valor
        if not atual.fim_de_palavra:
            atual.fim_de_palavra = True
            self._quantidade_elementos += 1
        atual.valor = valor

    def buscar(self, chave: str) -> Optional[Any]:
        no, visitados = self._encontrar_no(self._normalizar(chave))
        self._registrar_busca(visitados)
        if no is not None and no.fim_de_palavra:
            return no.valor
        return None

    def existe(self, chave: str) -> bool:
        no, visitados = self._encontrar_no(self._normalizar(chave))
        self._registrar_busca(visitados)
        return no is not None and no.fim_de_palavra

    def todos_valores(self) -> List[Any]:
        # listagem completa, nao e uma operacao de busca: nao entra na contagem
        valores, _ = self._coletar_valores(self._raiz)
        return valores

    def __len__(self) -> int:
        return self._quantidade_elementos

    # ------------------------------------------------------------------
    # Busca por prefixo (o motivo de existir da Trie)
    # ------------------------------------------------------------------
    def buscar_por_prefixo(self, prefixo: str) -> List[Any]:
        """Retorna os valores de todas as chaves que comecam com 'prefixo',
        em ordem alfabetica. Prefixo vazio retorna todos."""
        no, visitados = self._encontrar_no(self._normalizar(prefixo))
        if no is None:
            self._registrar_busca(visitados)
            return []

        valores, visitados_subarvore = self._coletar_valores(no)
        self._registrar_busca(visitados + visitados_subarvore)
        return valores

    def _coletar_valores(self, no_inicial: _No) -> Tuple[List[Any], int]:
        resultado: List[Any] = []
        visitados = 0
        pilha = [no_inicial]
        while pilha:
            no = pilha.pop()
            if no is not no_inicial:
                visitados += 1
            if no.fim_de_palavra:
                resultado.append(no.valor)

            for caractere in sorted(no.filhos, reverse=True):
                pilha.append(no.filhos[caractere])
        return resultado, visitados

    # ------------------------------------------------------------------
    # Instrumentacao
    # ------------------------------------------------------------------
    def imprimir_estatisticas(self) -> None:
        print("--- Estatisticas da Trie ---")
        print(f"Nomes armazenados:               {self._quantidade_elementos}")
        print(f"Total de nos:                    {self._quantidade_nos}")
        print(f"Total de buscas realizadas:      {self._total_buscas}")
        print(f"Nos visitados (ultima busca):    {self._nos_visitados_ultima_busca}")
        print(f"Nos visitados (total acumulado): {self._total_nos_visitados}")