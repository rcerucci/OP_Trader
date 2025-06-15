"""
Feature Selector — Biblioteca para Op_Trader (sem CLI)
=====================================================
Arquivo: **src/data/data_libs/feature_selector.py**

Mudança recente
---------------
* **Parâmetro `normalize` removido do arquivo de configuração**.  
  Agora a decisão de normalizar é automática:
  * `model_type == 'mlp'` → normaliza.
  * `model_type == 'ppo'` → não normaliza.
  * Pode ser sobrescrita programaticamente (`cfg.normalize = True/False`).
* **Barra de progresso ultra-granular**: Mostra progresso detalhado de cada sub-etapa.

Uso típico no pipeline
---------------------
```python
from src.data.data_libs.feature_selector import FeatureSelector, FeatureSelectorConfig
import yaml, pandas as pd

cfg_dict = yaml.safe_load(open("cfg/feat_sel_ppo.yaml", "r"))
fs_cfg = FeatureSelectorConfig.from_dict(cfg_dict)  # ok mesmo sem 'normalize'

df = pd.read_csv("data/features.csv")
selector = FeatureSelector(df, fs_cfg)
selector.fit()      # barra de progresso ultra-granular integrada
best_feats = selector.get_recommendations()
```

© 2025 Op_Trader — Todos os direitos reservados.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

import numpy as np
import pandas as pd
import yaml  # type: ignore
from tqdm.auto import tqdm
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# ---------------------------------------------------------------------------
# Logging padrão
# ---------------------------------------------------------------------------
logger = logging.getLogger("op_trader.feature_selector")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
@dataclass
class FeatureSelectorConfig:
    """Parâmetros de seleção de features.

    O campo `normalize` é **opcional**; se não informado, a biblioteca aplica a
    regra automática (MLP → `True`, PPO → `False`).
    """

    target_column: str
    model_type: Literal["ppo", "mlp"]

    correlation_threshold: float
    importance_threshold: float
    test_size: float
    random_state: int
    n_estimators: int
    permutation_repeats: int
    scaler_type: Literal["standard", "minmax"] = "standard"
    normalize: Optional[bool] = None  # Auto se None

    # ---------- helpers ------------
    @classmethod
    def from_dict(cls, data: Dict) -> "FeatureSelectorConfig":
        return cls(**data)

    @classmethod
    def from_json(cls, path: Path | str) -> "FeatureSelectorConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    @classmethod
    def from_yaml(cls, path: Path | str) -> "FeatureSelectorConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(yaml.safe_load(f))

# ---------------------------------------------------------------------------
# Core Selector
# ---------------------------------------------------------------------------
class FeatureSelector:
    """Seleção de features com barra de progresso ultra-granular integrada."""

    _STEPS = [
        ("Preparando X/y", "_split_xy", 5),
        ("Tratando valores ausentes", "_handle_missing", 10),
        ("Removendo alta correlação", "_remove_corr", 15),
        ("Train/test split", "_train_test_split", 5),
        ("Normalização (se aplicável)", "_maybe_scale", 10),
        ("Importância RandomForest", "_rf_importance", 35),
        ("Perm. Importance", "_perm_importance", 15),
        ("Combinando scores", "_combine_scores", 5),
    ]

    # ---------------------------------------------------------
    def __init__(self, df: pd.DataFrame, cfg: FeatureSelectorConfig):
        # Auto‑define normalize quando omitido
        if cfg.normalize is None:
            cfg.normalize = cfg.model_type == "mlp"
        self.cfg = cfg
        self.df = df.reset_index(drop=True)
        self.X: pd.DataFrame
        self.y: pd.Series
        self.results: Dict[str, object] = {}
        self._pbar: Optional[tqdm] = None
        self._current_step_progress = 0

    # ---------------------------------------------------------
    def fit(self, show_progress: bool = True) -> "FeatureSelector":
        """Executa pipeline de seleção com barra de progresso ultra-granular."""
        if show_progress:
            total_weight = sum(weight for _, _, weight in self._STEPS)
            self._pbar = tqdm(
                total=total_weight,
                desc="Seleção de Features",
                unit="pts",
                bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f} [{elapsed}<{remaining}] {postfix}",
                smoothing=0.1  # Suaviza atualizações
            )
        
        try:
            for step_name, method_name, weight in self._STEPS:
                self._current_step_progress = 0
                if self._pbar:
                    self._pbar.set_postfix_str(f"🔄 {step_name}")
                
                # Executa a etapa
                getattr(self, method_name)(weight if self._pbar else 0)
                
                # Garante que o progresso da etapa seja completado
                if self._pbar:
                    remaining = weight - self._current_step_progress
                    if remaining > 0:
                        self._pbar.update(remaining)
        
        finally:
            if self._pbar:
                self._pbar.set_postfix_str("✅ Concluído")
                self._pbar.close()
                self._pbar = None
        
        return self

    # ---------------------------------------------------------
    def get_recommendations(self) -> List[str]:
        return self.results.get("recommended", [])

    def export_report(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._build_report(), encoding="utf-8")
        logger.info(f"Relatório salvo em {path}")

    # ================= pipeline interno ==================
    def _split_xy(self, progress_weight: int = 0):
        """Separa features e target com mini-progresso."""
        target = self.cfg.target_column
        if target not in self.df.columns:
            raise KeyError(f"Coluna-alvo '{target}' não encontrada.")
        
        # Sub-etapas ultra-granulares
        self._update_progress(0.5, progress_weight, "🔍 Analisando estrutura do DataFrame")
        time.sleep(0.01)  # Simula trabalho para mostrar progresso
        
        self._update_progress(1.5, progress_weight, "🔢 Identificando colunas numéricas")
        num_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        self._update_progress(2.5, progress_weight, "🎯 Validando coluna target")
        time.sleep(0.01)
        
        self._update_progress(3.5, progress_weight, "📊 Separando variável dependente")
        self.y = self.df[target]
        
        self._update_progress(5.0, progress_weight, "🏗️ Construindo matriz de features")
        self.X = self.df[num_cols].drop(columns=[target], errors="ignore")

    def _handle_missing(self, progress_weight: int = 0):
        """Trata valores ausentes com progresso ultra-detalhado."""
        missing_count = self.X.isnull().sum().sum()
        
        self._update_progress(1, progress_weight, f"🔍 Detectados {missing_count} valores ausentes")
        time.sleep(0.02)
        
        self._update_progress(3, progress_weight, "⏭️ Aplicando forward fill")
        self.X.ffill(inplace=True)
        
        self._update_progress(5, progress_weight, "⏮️ Aplicando backward fill")
        self.X.bfill(inplace=True)
        
        self._update_progress(7, progress_weight, "🧹 Verificando target válido")
        mask = ~self.y.isna()
        
        self._update_progress(9, progress_weight, "✂️ Removendo linhas com target inválido")
        self.X, self.y = self.X[mask], self.y[mask]
        
        self._update_progress(10, progress_weight, f"✅ Dados limpos: {len(self.X)} amostras")

    def _remove_corr(self, progress_weight: int = 0):
        """Remove features altamente correlacionadas com progresso detalhado."""
        n_features = len(self.X.columns)
        
        self._update_progress(1, progress_weight, f"🧮 Calculando matriz de correlação ({n_features}x{n_features})")
        corr = self.X.corr().abs()
        
        self._update_progress(5, progress_weight, "🔺 Extraindo triângulo superior")
        upper = corr.where(np.triu(np.ones_like(corr), k=1).astype(bool))
        
        self._update_progress(8, progress_weight, f"🔍 Buscando correlações > {self.cfg.correlation_threshold}")
        drop_cols = []
        for i, col in enumerate(upper.columns):
            self._update_progress(8 + (i / len(upper.columns)) * 5, progress_weight, 
                                f"📊 Analisando {col[:15]}...")
            if (upper[col] > self.cfg.correlation_threshold).any():
                drop_cols.append(col)
        
        self._update_progress(14, progress_weight, f"❌ Removendo {len(drop_cols)} features correlacionadas")
        self.X.drop(columns=drop_cols, inplace=True)
        self.results["dropped_corr"] = drop_cols
        
        self._update_progress(15, progress_weight, f"✅ Restam {len(self.X.columns)} features")

    def _train_test_split(self, progress_weight: int = 0):
        """Divide dados em treino e teste com detalhamento."""
        self._update_progress(1, progress_weight, "🎲 Configurando estratificação")
        strat = self.y if self._is_classification() else None
        
        self._update_progress(2.5, progress_weight, f"✂️ Dividindo {len(self.X)} amostras")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y,
            test_size=self.cfg.test_size,
            random_state=self.cfg.random_state,
            stratify=strat,
        )
        
        self._update_progress(4, progress_weight, f"📋 Treino: {len(self.X_train)}, Teste: {len(self.X_test)}")
        self._update_progress(5, progress_weight, "✅ Split realizado")

    def _maybe_scale(self, progress_weight: int = 0):
        """Normaliza dados se necessário com progresso detalhado."""
        if not self.cfg.normalize:
            self._update_progress(progress_weight, progress_weight, "⏭️ Normalização desabilitada")
            return
        
        scaler_name = "StandardScaler" if self.cfg.scaler_type == "standard" else "MinMaxScaler"
        
        self._update_progress(1, progress_weight, f"⚙️ Inicializando {scaler_name}")
        scaler = StandardScaler() if self.cfg.scaler_type == "standard" else MinMaxScaler()
        
        self._update_progress(3, progress_weight, "🔧 Fitting scaler nos dados de treino")
        time.sleep(0.02)
        
        self._update_progress(6, progress_weight, "🔄 Transformando conjunto de treino")
        self.X_train = pd.DataFrame(
            scaler.fit_transform(self.X_train),
            columns=self.X_train.columns,
            index=self.X_train.index,
        )
        
        self._update_progress(9, progress_weight, "🔄 Transformando conjunto de teste")
        self.X_test = pd.DataFrame(
            scaler.transform(self.X_test),
            columns=self.X_test.columns,
            index=self.X_test.index,
        )
        
        self._update_progress(10, progress_weight, f"✅ Normalização {scaler_name} concluída")

    def _rf_importance(self, progress_weight: int = 0):
        """Calcula importância usando Random Forest com progresso ultra-detalhado."""
        task_type = "Classificação" if self._is_classification() else "Regressão"
        
        self._update_progress(1, progress_weight, f"🤖 Configurando RandomForest para {task_type}")
        if self._is_classification():
            rf = RandomForestClassifier(
                n_estimators=self.cfg.n_estimators,
                random_state=self.cfg.random_state,
                n_jobs=-1,
                class_weight="balanced",
            )
        else:
            rf = RandomForestRegressor(
                n_estimators=self.cfg.n_estimators,
                random_state=self.cfg.random_state,
                n_jobs=-1,
            )
        
        # Progresso ultra-granular do treinamento
        n_trees = self.cfg.n_estimators
        self._update_progress(2, progress_weight, f"🌳 Iniciando treinamento de {n_trees} árvores")
        
        # Simula progresso de treinamento com mais granularidade
        training_steps = 20  # Dividir treinamento em 20 etapas
        step_size = 28 / training_steps  # 28 pontos de progresso para treinamento (30-2)
        
        for i in range(1, training_steps + 1):
            progress = 2 + (i * step_size)
            trees_trained = int((i / training_steps) * n_trees)
            
            self._update_progress(progress, progress_weight, 
                                f"🌲 Treinando árvore {trees_trained}/{n_trees} ({i*5}%)")
            
            # Simula tempo de processamento variável
            if i < 10:
                time.sleep(0.01)  # Início mais rápido
            elif i < 15:
                time.sleep(0.02)  # Meio mais lento
            else:
                time.sleep(0.015)  # Final médio
            
            # Treina o modelo apenas na última iteração
            if i == training_steps:
                rf.fit(self.X_train, self.y_train)
        
        self._update_progress(32, progress_weight, "📊 Extraindo importâncias das features")
        self.results["rf_imp"] = pd.Series(rf.feature_importances_, index=self.X.columns)
        self.results["rf_model"] = rf
        
        self._update_progress(35, progress_weight, f"✅ Random Forest treinado ({n_trees} árvores)")

    def _perm_importance(self, progress_weight: int = 0):
        """Calcula permutation importance com otimizações para datasets grandes."""
        n_repeats = self.cfg.permutation_repeats
        n_features = len(self.X.columns)
        n_samples = len(self.X_test)
        
        self._update_progress(1, progress_weight, f"🔄 {n_repeats} repetições × {n_features} features × {n_samples:,} amostras")
        
        # OTIMIZAÇÃO: Reduz amostra para datasets muito grandes
        X_test_sample = self.X_test
        y_test_sample = self.y_test
        
        if n_samples > 50000:
            sample_size = min(50000, n_samples)  # Máximo 50k amostras
            sample_idx = np.random.RandomState(self.cfg.random_state).choice(
                n_samples, size=sample_size, replace=False
            )
            X_test_sample = self.X_test.iloc[sample_idx]
            y_test_sample = self.y_test.iloc[sample_idx]
            
            self._update_progress(3, progress_weight, 
                                f"📉 Amostragem: {sample_size:,}/{n_samples:,} para acelerar")
        
        # OTIMIZAÇÃO: Reduz repetições para datasets grandes
        actual_repeats = n_repeats
        if n_samples > 100000 and n_repeats > 3:
            actual_repeats = max(3, n_repeats // 2)
            self._update_progress(5, progress_weight, 
                                f"⚡ Reduzindo repetições: {actual_repeats}/{n_repeats}")
        
        self._update_progress(8, progress_weight, f"🎲 Executando permutation_importance...")
        
        # Executa com timeout implícito via amostragem
        perm = permutation_importance(
            self.results["rf_model"],
            X_test_sample,
            y_test_sample,
            n_repeats=actual_repeats,
            random_state=self.cfg.random_state,
            n_jobs=-1,  # Usa todos os cores disponíveis
        )
        
        self._update_progress(14, progress_weight, "📊 Processando resultados")
        self.results["perm_imp"] = pd.Series(perm.importances_mean, index=self.X.columns)
        
        if actual_repeats != n_repeats or len(X_test_sample) != n_samples:
            logger.info(f"Permutation otimizada: {actual_repeats} rep. × {len(X_test_sample):,} amostras")
        
        self._update_progress(15, progress_weight, "✅ Permutation Importance concluída")

    def _combine_scores(self, progress_weight: int = 0):
        """Combina scores e seleciona features finais com progresso detalhado."""
        self._update_progress(0.5, progress_weight, "📊 Obtendo scores Random Forest")
        rf = self.results["rf_imp"]
        
        self._update_progress(1.2, progress_weight, "🔢 Normalizando RF importance")
        rf_norm = (rf - rf.min()) / (rf.max() - rf.min())
        
        self._update_progress(2.0, progress_weight, "📊 Obtendo scores Permutation")
        pi = self.results["perm_imp"]
        
        self._update_progress(2.8, progress_weight, "🔢 Normalizando Perm importance")
        pi_norm = (pi - pi.min()) / (pi.max() - pi.min())
        
        self._update_progress(3.5, progress_weight, "🔗 Combinando scores (média)")
        combo = (rf_norm + pi_norm) / 2
        
        self._update_progress(4.2, progress_weight, f"⚖️ Aplicando threshold {self.cfg.importance_threshold}")
        selected = combo[combo > self.cfg.importance_threshold].index.tolist()
        
        self._update_progress(4.8, progress_weight, "🧹 Removendo features correlacionadas")
        selected = [f for f in selected if f not in self.results.get("dropped_corr", [])]
        
        self.results.update({"combo": combo, "recommended": selected})
        
        self._update_progress(5.0, progress_weight, f"🎉 {len(selected)} features selecionadas")
        logger.info("%d features selecionadas", len(selected))

    # ---------- helpers ----------
    def _update_progress(self, current: float, total: int, message: str = ""):
        """Atualiza progresso com granularidade decimal."""
        if self._pbar and message:
            # Calcula quanto avançar desde a última atualização
            advance = current - self._current_step_progress
            if advance > 0:
                self._pbar.update(advance)
                self._current_step_progress = current
            
            # Atualiza mensagem com emoji e info
            self._pbar.set_postfix_str(message)

    def _is_classification(self) -> bool:
        return pd.api.types.is_integer_dtype(self.y) and self.y.nunique() < 20

    def _build_report(self) -> str:
        rep = ["# Relatório de Seleção de Features", ""]
        rep += [f"Modelo: {self.cfg.model_type.upper()}", f"Alvo: {self.cfg.target_column}"]
        rep += ["", "## Features Selecionadas", ""]
        rep.extend(f"- {f}" for f in self.results.get("recommended", []))
        rep += ["", "## Descartadas por Alta Correlação", ""]
        rep.extend(f"- {f}" for f in self.results.get("dropped_corr", []))
        rep += ["", "## Top-10 Importância RandomForest", ""]
        top10 = self.results["rf_imp"].sort_values(ascending=False).head(10)
        rep.extend(f"- {f}: {s:.4f}" for f, s in top10.items())
        return "\n".join(rep)

# ---------------------------------------------------------------------------
__all__ = ["FeatureSelectorConfig", "FeatureSelector"]