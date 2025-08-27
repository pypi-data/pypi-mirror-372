import numpy as np
import pandas as pd


def bfrequencies(
    df: pd.DataFrame,
    column_name: str,
    *,
    include_na: bool = True,
    sort_by: str = "index",  # "index" ou "count"
    ascending: bool = True,
    percent: bool = True,  # True = retorna %; False = proporção 0–1
    decimals: int = 2,
) -> pd.DataFrame:
    """
    Gera uma tabela de distribuição de frequências para uma coluna do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        column_name (str): Nome da coluna a ser analisada.
        include_na (bool, opcional): Se True, inclui valores NaN/None na contagem.
            Padrão True.
        sort_by (str, opcional): Como ordenar a distribuição.
            "index" = ordena pelo valor único (rótulo) da coluna.
            "count" = ordena pela frequência absoluta.
            Padrão "index".
        ascending (bool, opcional): Ordem crescente (True) ou decrescente (False).
            Padrão True.
        percent (bool, opcional): Se True, retorna frequência relativa em porcentagem (0–100).
            Se False, retorna proporção (0–1). Padrão True.
        decimals (int, opcional): Casas decimais para arredondar a frequência relativa.
            Padrão 2.

    Returns:
        pd.DataFrame: DataFrame com colunas:
            - value: valor distinto da coluna analisada
            - frequency: frequência absoluta
            - relative_frequency: frequência relativa (% ou proporção)
            - cumulative_frequency: frequência absoluta acumulada
            - cumulative_relative_frequency: frequência relativa acumulada

    Exemplo:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"sexo": ["M","F","M","M","F", None]})
        >>> table_distribution_maker(df, "sexo")
          value  frequency  relative_frequency  cumulative_frequency  cumulative_relative_frequency
        0     F          2               33.33                     2                        33.33
        1  None          1               16.67                     3                        50.00
        2     M          3               50.00                     6                       100.00
    """
    # 1) Frequência absoluta
    s = df[column_name].value_counts(
        dropna=not include_na, sort=False
    )  # sem ordenar aqui

    # 2) Ordenação
    if sort_by == "index":
        s = s.sort_index(ascending=ascending)
    elif sort_by == "count":
        s = s.sort_values(ascending=ascending)
    else:
        raise ValueError('sort_by deve ser "index" ou "count".')

    # 3) Frequência relativa (proporção ou %)
    rel = s / s.sum()
    if percent:
        rel = (rel * 100).round(decimals)
    else:
        rel = rel.round(decimals)

    # 4) Acumuladas
    cum = s.cumsum()
    cum_rel = rel.cumsum().round(decimals)

    # 5) Montagem do DataFrame de retorno
    out = pd.DataFrame(
        {
            "value": s.index,
            "frequency": s.values,
            "relative_frequency": rel.values,
            "cumulative_frequency": cum.values,
            "cumulative_relative_frequency": cum_rel.values,
        }
    ).reset_index(drop=True)

    return out


def bfrequencies_from_counts(
    df: pd.DataFrame,
    label_col: str = "value",
    freq_col: str = "frequency",
    *,
    sort_by: str = "index",  # "index" (rótulo) ou "count" (frequência)
    ascending: bool = True,
    percent: bool = True,  # True = 0–100; False = 0–1
    decimals: int = 2,
    keep_na: bool = True,  # mantém linhas com rótulo NaN/None
    aggregate_duplicates: bool = True,  # soma frequências de rótulos repetidos
) -> pd.DataFrame:
    """
    Constrói a distribuição de frequências A PARTIR de uma tabela já agregada
    contendo rótulos e contagens.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame com, no mínimo, as colunas de rótulo e de frequência.
    label_col : str
        Nome da coluna com os rótulos/categorias (default: "value").
    freq_col : str
        Nome da coluna com as frequências absolutas (default: "frequency").
    sort_by : {"index","count"}
        Como ordenar o resultado: por rótulo ("index") ou por frequência ("count").
    ascending : bool
        Ordem crescente (True) ou decrescente (False).
    percent : bool
        Se True, retorna a frequência relativa em 0–100; se False, em 0–1.
    decimals : int
        Casas decimais para arredondar as relativas.
    keep_na : bool
        Se False, descarta linhas cujo rótulo é NaN/None.
    aggregate_duplicates : bool
        Se True, soma frequências de rótulos repetidos. Se False, lança erro
        ao encontrar duplicatas.

    Retorno
    -------
    pd.DataFrame com colunas:
      - value
      - frequency
      - relative_frequency
      - cumulative_frequency
      - cumulative_relative_frequency
    """
    if label_col not in df.columns or freq_col not in df.columns:
        raise KeyError(
            f"Colunas '{label_col}' e/ou '{freq_col}' não encontradas no DataFrame."
        )

    data = df[[label_col, freq_col]].copy()

    # descarta NAs no rótulo, se solicitado
    if not keep_na:
        data = data[~data[label_col].isna()]

    # valida frequência: numérica e não-negativa
    if not np.issubdtype(data[freq_col].dtype, np.number):  # type: ignore
        try:
            data[freq_col] = pd.to_numeric(data[freq_col])
        except Exception as e:
            raise TypeError(f"Coluna '{freq_col}' deve ser numérica. Erro: {e}") from e

    if (data[freq_col] < 0).any():
        raise ValueError(f"Coluna '{freq_col}' não pode conter valores negativos.")

        # agrega duplicatas por rótulo, se houver
    if aggregate_duplicates:
        s = data.groupby(label_col, dropna=not keep_na, sort=False)[freq_col].sum()
    else:
        dups = data[label_col].duplicated(keep=False)
        if dups.any():
            vals = data.loc[dups, label_col].unique().tolist()
            raise ValueError(
                f"Rótulos duplicados encontrados: {vals}. "
                f"Defina aggregate_duplicates=True para somar."
            )
        s = data.set_index(label_col)[freq_col]
        # preserva NAs conforme keep_na (já filtrado acima)

    # ordenação
    if sort_by == "index":
        s = s.sort_index(ascending=ascending)
    elif sort_by == "count":
        s = s.sort_values(ascending=ascending)
    else:
        raise ValueError('sort_by deve ser "index" ou "count".')

    total = s.sum()

    # frequências relativas
    if total > 0:
        rel = s / total
        if percent:
            rel = (rel * 100).round(decimals)
        else:
            rel = rel.round(decimals)
    else:
        # total == 0 → evita divisão por zero
        rel = s.astype(float).copy()
        rel[:] = 0.0

    # acumuladas
    cum = s.cumsum()
    if total > 0:
        cum_rel = (cum / total) * (100.0 if percent else 1.0)
        cum_rel = cum_rel.round(decimals)
    else:
        cum_rel = cum.astype(float)
        cum_rel[:] = 0.0

    out = pd.DataFrame(
        {
            "value": s.index,
            "frequency": s.values,
            "relative_frequency": rel.values,
            "cumulative_frequency": cum.values,
            "cumulative_relative_frequency": cum_rel.values,
        }
    ).reset_index(drop=True)

    return out
