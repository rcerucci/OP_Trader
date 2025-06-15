#!/usr/bin/env python3
"""
src/data/data_pipeline.py

Pipeline principal Op_Trader: recebe todos os parâmetros explicitamente do runner,
propaga para os módulos internos sem fallback/config/CLI, realiza todas as etapas 
(coleção, limpeza, correção, features, normalização, schema, auditoria).

Nunca faz parsing de config.ini nem de argumentos CLI.
Pronto para produção, CI/CD, automação e downstream.

Autor: Equipe Op_Trader
Data: 2025-06-14
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.data.data_libs.data_collector_mt5 import DataCollectorMT5
from src.data.data_libs.data_cleaner_wrapper import DataCleanerWrapper
from src.data.data_libs.feature_engineer import FeatureEngineer
from src.data.data_libs.feature_calculator import FeatureCalculator
from src.data.data_libs.feature_selector import FeatureSelector
from src.data.data_libs.scaler import ScalerUtils
from src.data.data_libs.schema_utils import (
    align_dataframe_to_schema,
    load_feature_list,
    validate_dataframe_schema,
)
from src.utils.file_saver import build_filename, get_timestamp, save_dataframe
from src.utils.hash_utils import generate_config_hash
from src.utils.logging_utils import get_logger
from src.utils.pipeline_hash_utils import save_pipeline_hash_json

__all__ = ["DataPipeline"]

class DataPipeline:
    """
    Orquestrador principal do pipeline de dados Op_Trader.

    Todos os parâmetros são recebidos explicitamente do runner.
    Nenhum fallback/config/CLI é feito internamente.
    """

    def __init__(
        self,
        *,
        config: dict,
        mode: str,
        pipeline_type: str,
        symbol: str,
        timeframe: str,
        features: list,
        features_params: dict,
        start_date: str,
        end_date: str,
        volume_sources: list,
        volume_column: str,
        dirs: dict,
        gap_params: dict,
        outlier_params: dict,
        scaler_params: dict,
        debug: bool = False,
        callbacks: dict = None,
    ):
        self.config = config
        self.mode = mode
        self.pipeline_type = pipeline_type
        self.symbol = symbol
        self.timeframe = timeframe
        self.features = features
        self.features_params = features_params or {}
        self.start_date = start_date
        self.end_date = end_date
        self.volume_sources = volume_sources
        self.volume_column = volume_column
        self.dirs = dirs
        self.gap_params = gap_params
        self.outlier_params = outlier_params
        self.scaler_params = scaler_params
        self.debug = debug
        self.callbacks = callbacks or {}

        self.logger = get_logger("op_trader.data_pipeline", "DEBUG" if debug else None)
        self.timestamp: str = get_timestamp()
        self.outputs: Dict[str, str] = {}
        self._corretora: str | None = None
        self._cfg_hash: str = ""

    def run(self) -> pd.DataFrame:
        """Executa pipeline completo com rastreabilidade centralizada."""
        if self.mode == "streaming":
            return self.run_streaming()

        self.logger.info(
            "=== Iniciando DataPipeline [%s] para %s/%s ===",
            self.pipeline_type.upper(),
            self.symbol,
            self.timeframe,
        )

        # === PASSO 1: COLETA BRUTA ===
        collector = DataCollectorMT5(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
            volume_sources=self.volume_sources,
            volume_column=self.volume_column,
            debug=self.debug,
        )
        df_raw, corretora, ohlc_decimals = collector.collect_batch()
        self._corretora = corretora
        cfg_hash = generate_config_hash(self._snapshot_config())
        self._cfg_hash = cfg_hash
        self._save("raw", df_raw, cfg_hash)

        # === PASSO 2: LIMPEZA INICIAL ===
        COLUMNS_REQUIRED_RAW = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        decimal_precision = 10  # Defina aqui ou receba como param do runner
        df_clean = DataCleanerWrapper(debug=self.debug).clean(
            df_raw, decimal_precision, columns_required=COLUMNS_REQUIRED_RAW
        )
        self._save("cleaned", df_clean, cfg_hash)

        # === PASSO 3: CORREÇÃO GAPS/OUTLIERS ===
        from src.data.data_libs.outlier_gap_corrector import OutlierGapCorrector
        gap_params = self.gap_params
        outlier_params = self.outlier_params
        freq_pandas = self._timeframe_to_pandas_freq(self.timeframe)
        corr = OutlierGapCorrector(
            freq=freq_pandas,
            debug=self.debug,
            mode=self.mode,
            gap_params=gap_params,
            outlier_params=outlier_params,
        )
        df_corr = corr.fix_outliers(corr.fix_gaps(df_clean))
        self._save("corrected", df_corr, cfg_hash)

        # === PASSO 4: FEATURE ENGINEERING ===
        feat_engineer = FeatureEngineer(
            features=self.features,
            params=self.features_params,
            debug=self.debug
        )
        df_features = feat_engineer.transform(df_corr)

        features_json_path = "config/features.json"
        with open(features_json_path) as f:
            all_outputs = json.load(f)['all_features']

        columns_required = [
            'datetime', 'open', 'high', 'low', 'close', 'volume',
            'gap_fixed', 'volume_fixed', 'outlier_fixed'
        ] + all_outputs

        cleaner = DataCleanerWrapper(debug=self.debug)
        df_features_clean = cleaner.clean(
            df_features, decimal_precision, columns_required=columns_required
        )

        for col in ['gap_fixed', 'volume_fixed', 'outlier_fixed']:
            if col in df_features_clean.columns:
                df_features_clean[col] = df_features_clean[col].astype(int)
        self._save("features", df_features_clean, cfg_hash)

        # === FINALIZAÇÃO ===
        if self.pipeline_type == "ppo":
            df_final = self._finalize_ppo(df_features_clean, cfg_hash)
        elif self.pipeline_type == "mlp":
            df_final = self._finalize_mlp(df_features_clean, cfg_hash)
        else:
            self._finalize_mlp(df_features_clean, cfg_hash)
            df_final = self._finalize_ppo(df_features_clean, cfg_hash)

        self._save_pipeline_hash_json()
        return df_final

    def _save(self, etapa: str, df: pd.DataFrame, cfg_hash: str, *, ext: str = "csv") -> None:
        """Salva DataFrame em diretório apropriado."""
        target_dir = self.dirs.get(etapa, "data/")
        step_name = f"{etapa}_{self.pipeline_type}"
        filename = build_filename(
            prefix=target_dir,
            step=step_name,
            broker="mt5",
            corretora=self._corretora or "mt5",
            asset=self.symbol,
            timeframe=self.timeframe,
            period=f"{self.start_date}_{self.end_date}" if self.start_date and self.end_date else "",
            timestamp=f"{cfg_hash}_{self.timestamp}",
            extension=ext,
        )
        save_dataframe(df, filename)
        self.logger.info("Salvo: %s", filename)
        self.outputs[etapa] = filename

    def _finalize_ppo(self, df_features: pd.DataFrame, cfg_hash: str) -> pd.DataFrame:
        """Alinha ao schema, seleciona features e salva artefato PPO."""
        from src.data.data_libs.feature_selector import FeatureSelector, FeatureSelectorConfig
        
        # 1. Preserva datetime se existir
        datetime_col = None
        if 'datetime' in df_features.columns:
            datetime_col = df_features['datetime'].copy()
        
        # 2. Preserva colunas OHLC + Volume (essenciais para PPO)
        essential_ohlc = ['open', 'high', 'low', 'close', 'volume']
        preserved_cols = {}
        for col in essential_ohlc:
            if col in df_features.columns:
                preserved_cols[col] = df_features[col].copy()
                self.logger.debug(f"Preservando coluna essencial: {col}")
        
        # 3. Carrega schema completo original (65 features)
        schema = load_feature_list("config/feature_schema.json")
        df_aligned = align_dataframe_to_schema(df_features, schema)
        
        # 4. Configuração para seleção de features PPO
        fs_config = FeatureSelectorConfig(
            target_column="delta_points",
            model_type="ppo",
            correlation_threshold=0.95,
            importance_threshold=0.01,
            test_size=0.2,
            random_state=42,
            n_estimators=100,
            permutation_repeats=3,
            scaler_type="standard",
            normalize=False
        )
        
        # 5. Executa seleção de features
        try:
            selector = FeatureSelector(df_aligned, fs_config)
            selector.fit(show_progress=True)
            recommended_features = selector.get_recommendations()
            
            # Log das features selecionadas
            self.logger.info(f"Features selecionadas: {len(recommended_features)}/{len(df_aligned.columns)-1}")
            self.logger.debug(f"Features: {recommended_features}")
            
            # 6. Monta lista final de colunas para PPO
            # Ordem: datetime + OHLC essenciais + features selecionadas (sem duplicatas e sem target)
            final_cols = []
            
            # Adiciona datetime primeiro se existir
            if datetime_col is not None:
                final_cols.append('datetime')
            
            # Adiciona OHLC essenciais (sempre preservados)
            for col in essential_ohlc:
                if col in preserved_cols:
                    final_cols.append(col)
            
            # Adiciona features selecionadas (excluindo essenciais já adicionados e target)
            for col in recommended_features:
                if (col not in final_cols and 
                    col != fs_config.target_column and 
                    col in df_aligned.columns):
                    final_cols.append(col)
            
            # 7. Cria DataFrame final com colunas ordenadas
            df_final = pd.DataFrame()
            
            # Restaura datetime
            if datetime_col is not None:
                df_final['datetime'] = datetime_col
            
            # Restaura colunas OHLC essenciais
            for col in essential_ohlc:
                if col in preserved_cols:
                    df_final[col] = preserved_cols[col]
            
            # Adiciona features selecionadas
            for col in recommended_features:
                if (col not in df_final.columns and 
                    col != fs_config.target_column and 
                    col in df_aligned.columns):
                    df_final[col] = df_aligned[col]
            
            df_aligned = df_final
            
            # 8. Salva relatório de seleção
            report_path = f"reports/feature_selection_ppo_{cfg_hash[:8]}.md"
            os.makedirs("reports", exist_ok=True)
            selector.export_report(report_path)
            
            # 9. Cria esquemas PPO baseados na seleção de features
            ppo_features = list(df_aligned.columns)
            
            # Salva feature_ppo.json (features selecionadas finais)
            ppo_schema = {
                "all_features": ppo_features
            }
            ppo_path = "config/feature_ppo.json"
            os.makedirs("config", exist_ok=True)
            with open(ppo_path, 'w') as f:
                import json
                json.dump(ppo_schema, f, indent=2)
            
            # Salva feature_schema_ppo.json (com metadados)
            ppo_schema_full = {
                "schema_file": "feature_ppo.json",
                "all_features": ppo_features
            }
            ppo_schema_path = "config/feature_schema_ppo.json"
            with open(ppo_schema_path, 'w') as f:
                json.dump(ppo_schema_full, f, indent=2)
            
            self.logger.info(f"Schemas PPO salvos: {ppo_path} e {ppo_schema_path}")
            self.logger.info(f"Features no schema PPO: {len(ppo_features)} ({ppo_features})")
            
        except Exception as e:
            self.logger.warning(f"Erro na seleção de features: \"{e}\". Usando schema básico PPO.")
            
            # 10. Fallback: usa schema básico com OHLC + algumas features principais
            df_final = pd.DataFrame()
            
            # Restaura datetime
            if datetime_col is not None:
                df_final['datetime'] = datetime_col
            
            # Restaura colunas OHLC essenciais
            for col in essential_ohlc:
                if col in preserved_cols:
                    df_final[col] = preserved_cols[col]
            
            # Adiciona features básicas disponíveis
            basic_features = ['ema_fast', 'ema_slow', 'rsi', 'macd_hist', 'atr', 'bb_width', 'return_pct']
            for col in basic_features:
                if col in df_aligned.columns and col not in df_final.columns:
                    df_final[col] = df_aligned[col]
            
            df_aligned = df_final
            
            # Salva schema básico de fallback
            ppo_schema = {"all_features": list(df_aligned.columns)}
            ppo_path = "config/feature_ppo.json"
            os.makedirs("config", exist_ok=True)
            with open(ppo_path, 'w') as f:
                import json
                json.dump(ppo_schema, f, indent=2)
        
        # 11. Formatação final datetime
        if 'datetime' in df_aligned.columns:
            df_aligned['datetime'] = pd.to_datetime(df_aligned['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 12. Verificação final - garante que delta_points foi removido
        if 'delta_points' in df_aligned.columns:
            df_aligned = df_aligned.drop(columns=['delta_points'])
            self.logger.info("Coluna 'delta_points' removida (usada apenas para seleção de features)")
        
        self.logger.info(f"DataFrame final PPO - Shape: {df_aligned.shape}")
        self.logger.info(f"Colunas finais: {list(df_aligned.columns)}")
        
        # 13. Validação básica (verifica se tem OHLC essenciais)
        required_ohlc = ['open', 'high', 'low', 'close']
        missing_ohlc = [col for col in required_ohlc if col not in df_aligned.columns]
        if missing_ohlc:
            self.logger.error(f"❌ Colunas OHLC ausentes: {missing_ohlc}")
            self.logger.error("Isso é crítico para PPO - verificar dados de entrada!")
        else:
            self.logger.info("✅ Todas as colunas OHLC essenciais presentes")
        
        # Verificação adicional de volume
        if 'volume' in df_aligned.columns:
            self.logger.info("✅ Coluna 'volume' presente")
        else:
            self.logger.warning("⚠️ Coluna 'volume' ausente")
        
        # 14. Salva resultado final
        self._save("final_ppo", df_aligned, cfg_hash)
        
        return df_aligned

    def _finalize_mlp(self, df_features: pd.DataFrame, cfg_hash: str) -> pd.DataFrame:
        """Alinha ao schema, seleciona features, normaliza e salva artefatos MLP."""
        from src.data.data_libs.feature_selector import FeatureSelector, FeatureSelectorConfig
        import os
        import json
        from pathlib import Path
        
        # 1. Preserva datetime se existir
        datetime_col = None
        if 'datetime' in df_features.columns:
            datetime_col = df_features['datetime'].copy()
        
        # 2. Preserva colunas OHLC + Volume originais (para cálculo de rewards)
        essential_ohlc = ['open', 'high', 'low', 'close', 'volume']
        preserved_cols = {}
        for col in essential_ohlc:
            if col in df_features.columns:
                preserved_cols[col] = df_features[col].copy()
                self.logger.debug(f"Preservando coluna essencial original: {col}")
        
        # 3. Carrega schema completo original (65 features)
        schema = load_feature_list("config/feature_schema.json")
        df_aligned = align_dataframe_to_schema(df_features, schema)
        
        # 4. Configuração para seleção de features MLP
        fs_config = FeatureSelectorConfig(
            target_column="delta_points",
            model_type="mlp",
            correlation_threshold=0.90,  # Menos restritivo que PPO
            importance_threshold=0.005,  # Threshold menor para capturar mais features
            test_size=0.2,
            random_state=42,
            n_estimators=100,
            permutation_repeats=3,
            scaler_type="standard",
            normalize=True  # MLP sempre normaliza
        )
        
        # 5. Executa seleção de features
        try:
            selector = FeatureSelector(df_aligned, fs_config)
            selector.fit(show_progress=True)
            recommended_features = selector.get_recommendations()
            
            # Log das features selecionadas
            self.logger.info(f"Features selecionadas: {len(recommended_features)}/{len(df_aligned.columns)-1}")
            self.logger.debug(f"Features: {recommended_features}")
            
            # 6. Monta lista final de colunas para MLP
            # Ordem: datetime + OHLC essenciais + features selecionadas (sem duplicatas e sem target)
            final_cols = []
            
            # Adiciona datetime primeiro se existir
            if datetime_col is not None:
                final_cols.append('datetime')
            
            # Adiciona OHLC essenciais (sempre preservados)
            for col in essential_ohlc:
                if col in preserved_cols:
                    final_cols.append(col)
            
            # Adiciona features selecionadas (excluindo essenciais já adicionados e target)
            for col in recommended_features:
                if (col not in final_cols and 
                    col != fs_config.target_column and 
                    col in df_aligned.columns):
                    final_cols.append(col)
            
            # 7. Cria DataFrame com features selecionadas
            df_selected = pd.DataFrame()
            
            # Restaura datetime
            if datetime_col is not None:
                df_selected['datetime'] = datetime_col
            
            # Restaura colunas OHLC essenciais (originais)
            for col in essential_ohlc:
                if col in preserved_cols:
                    df_selected[col] = preserved_cols[col]
            
            # Adiciona features selecionadas
            for col in recommended_features:
                if (col not in df_selected.columns and 
                    col != fs_config.target_column and 
                    col in df_aligned.columns):
                    df_selected[col] = df_aligned[col]
            
            # 8. Salva relatório de seleção
            report_path = f"reports/feature_selection_mlp_{cfg_hash[:8]}.md"
            os.makedirs("reports", exist_ok=True)
            selector.export_report(report_path)
            
        except Exception as e:
            self.logger.warning(f"Erro na seleção de features: \"{e}\". Usando schema básico MLP.")
            
            # 9. Fallback: usa schema básico com OHLC + features temporais + principais
            df_selected = pd.DataFrame()
            
            # Restaura datetime
            if datetime_col is not None:
                df_selected['datetime'] = datetime_col
            
            # Restaura colunas OHLC essenciais
            for col in essential_ohlc:
                if col in preserved_cols:
                    df_selected[col] = preserved_cols[col]
            
            # Adiciona features básicas disponíveis (incluindo temporais)
            basic_features = [
                'ema_fast', 'ema_slow', 'rsi', 'macd_hist', 'atr', 'bb_width', 'return_pct',
                'candle_direction', 'volume_relative', 'pullback',
                'day_of_week', 'sin_dow', 'cos_dow', 'hour', 'sin_hour', 'cos_hour'
            ]
            for col in basic_features:
                if col in df_aligned.columns and col not in df_selected.columns:
                    df_selected[col] = df_aligned[col]
        
        # 10. Separar colunas para normalização vs preservação
        # Colunas que NÃO devem ser normalizadas (para cálculo de rewards)
        preserve_cols = ['datetime'] if 'datetime' in df_selected.columns else []
        preserve_original_ohlc = ['open', 'high', 'low', 'close', 'volume']
        
        # Colunas que devem ser normalizadas (todas exceto datetime)
        normalize_cols = [col for col in df_selected.columns if col not in preserve_cols]
        
        # 11. Normalização usando ScalerUtils
        scaler = ScalerUtils(debug=self.debug)
        
        # Aplica normalização nas colunas selecionadas
        self.logger.info(f"Normalizando {len(normalize_cols)} colunas: {normalize_cols}")
        df_normalized = scaler.fit_transform(df_selected[normalize_cols])
        
        # 12. Constrói DataFrame final com dados originais + normalizados
        df_final = pd.DataFrame()
        
        # Adiciona datetime se existir (sem normalizar)
        if 'datetime' in df_selected.columns:
            df_final['datetime'] = df_selected['datetime']
        
        # Adiciona dados OHLC originais com sufixo _orig (para rewards)
        for col in preserve_original_ohlc:
            if col in preserved_cols:
                df_final[f'{col}'] = preserved_cols[col]
        
        # Adiciona todas as colunas normalizadas
        for col in df_normalized.columns:
            df_final[col] = df_normalized[col]
        
        # 13. Formatação final datetime
        if 'datetime' in df_final.columns:
            df_final['datetime'] = pd.to_datetime(df_final['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 14. Verificação final - garante que delta_points foi removido
        if 'delta_points' in df_final.columns:
            df_final = df_final.drop(columns=['delta_points'])
            self.logger.info("Coluna 'delta_points' removida (usada apenas para seleção de features)")
        
        # 15. Cria schemas MLP baseados no DataFrame final
        mlp_features = list(df_final.columns)
        
        # Salva feature_mlp.json (features do DataFrame final)
        mlp_schema = {
            "all_features": mlp_features
        }
        mlp_path = "config/feature_mlp.json"
        os.makedirs("config", exist_ok=True)
        with open(mlp_path, 'w') as f:
            json.dump(mlp_schema, f, indent=2)
        
        # Salva feature_schema_mlp.json (com metadados)
        mlp_schema_full = {
            "schema_file": "feature_mlp.json",
            "all_features": mlp_features
        }
        mlp_schema_path = "config/feature_schema_mlp.json"
        with open(mlp_schema_path, 'w') as f:
            json.dump(mlp_schema_full, f, indent=2)
        
        self.logger.info(f"Schemas MLP salvos: {mlp_path} e {mlp_schema_path}")
        self.logger.info(f"Features no schema MLP: {len(mlp_features)} ({mlp_features})")
        
        # 16. Salva o scaler na pasta correta com tags
        os.makedirs("data/scalers", exist_ok=True)
        scaler_filename = f"scaler_mlp_{cfg_hash[:8]}.pkl"
        scaler_path = Path("data/scalers") / scaler_filename
        scaler.save_scaler(scaler_path)
        
        # Atualiza outputs
        self.outputs["scaler"] = str(scaler_path)
        
        self.logger.info(f"Scaler salvo em: {scaler_path}")
        self.logger.info(f"DataFrame final MLP - Shape: {df_final.shape}")
        self.logger.info(f"Colunas finais: {list(df_final.columns)}")
        
        # 17. Validação básica
        # Verifica se tem OHLC originais para rewards
        required_orig = [f'{col}' for col in ['open', 'high', 'low', 'close']]
        missing_orig = [col for col in required_orig if col not in df_final.columns]
        if missing_orig:
            self.logger.error(f"❌ Colunas OHLC originais ausentes: {missing_orig}")
            self.logger.error("Isso é crítico para cálculo de rewards - verificar dados de entrada!")
        else:
            self.logger.info("✅ Todas as colunas OHLC originais presentes para rewards")
        
        # Verifica se tem OHLC normalizados para o modelo
        required_norm = ['open', 'high', 'low', 'close']
        missing_norm = [col for col in required_norm if col not in df_final.columns]
        if missing_norm:
            self.logger.error(f"❌ Colunas OHLC normalizadas ausentes: {missing_norm}")
            self.logger.error("Isso é crítico para MLP - verificar normalização!")
        else:
            self.logger.info("✅ Todas as colunas OHLC normalizadas presentes para o modelo")
        
        # Verificação adicional de volume
        if 'volume' in df_final.columns and 'volume' in df_final.columns:
            self.logger.info("✅ Colunas 'volume' (original e normalizada) presentes")
        else:
            self.logger.warning("⚠️ Problema com colunas de volume")
        
        # 18. Salva resultado final
        self._save("final_mlp", df_final, cfg_hash)
        self.outputs["final_mlp"] = self.outputs.get("final_mlp")
        
        return df_final

    def _build_output_path(self, etapa: str, prefix: str, cfg_hash: str, *, ext: str = "csv") -> str:
        """Gera caminho completo (sem salvar) para artefatos auxiliares."""
        target_dir = self.dirs.get(etapa, "data/")
        step_name = f"{prefix}_{self.pipeline_type}"
        return build_filename(
            prefix=target_dir,
            step=step_name,
            broker="mt5",
            corretora=self._corretora or "mt5",
            asset=self.symbol,
            timeframe=self.timeframe,
            period=f"{self.start_date}_{self.end_date}" if self.start_date and self.end_date else "",
            timestamp=f"{cfg_hash}_{self.timestamp}",
            extension=ext,
        )

    def _snapshot_config(self) -> Dict[str, Any]:
        """Snapshot dos parâmetros críticos – base para config_hash."""
        return {
            "pipeline_type": self.pipeline_type,
            "mode": self.mode,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "features": self.features,
            "features_params": self.features_params,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gap_params": self.gap_params,
            "outlier_params": self.outlier_params,
            "scaler_params": self.scaler_params,
        }

    @staticmethod
    def _timeframe_to_pandas_freq(timeframe: str) -> str:
        tf_map = {
            "M1": "1min", "M5": "5min", "M15": "15min", "M30": "30min",
            "H1": "1H", "H4": "4H", "D1": "1D", "W1": "1W", "MN1": "1M"
        }
        tf = timeframe.upper()
        if tf not in tf_map:
            raise ValueError(f"Timeframe inválido: {timeframe}")
        return tf_map[tf]

    def _save_pipeline_hash_json(self):
        """Salva JSON centralizador de rastreamento do pipeline."""
        hash_dir = "data/hash"
        os.makedirs(hash_dir, exist_ok=True)
        hash_filename = os.path.join(
            hash_dir, f"hash_{self.pipeline_type}_{self._cfg_hash}_{self.timestamp}.json"
        )
        save_pipeline_hash_json(
            hash_path=hash_filename,
            config_hash=self._cfg_hash,
            timestamp=self.timestamp,
            config=self._snapshot_config(),
            paths=self.outputs,
            features=self.features,
            corretora=self._corretora or "mt5",
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
            status={k: "ok" if v else "pending" for k, v in self.outputs.items()},
            log_path=None,
        )
        self.logger.info(f"Hash centralizador salvo: {hash_filename}")

# EOF
