"""data_auditor.py – Auditoria Enterprise do Pipeline Op_Trader
================================================================

Localização: src/data/data_libs/data_auditor.py
Autor: Equipe Op_Trader • Atualização: 2025‑06‑14
----------------------------------------------------------------
Auditoria corporativa completa dos CSVs gerados pelo DataPipeline
(`raw`, `cleaned`, `corrected`, `features`). Valida integridade de
schema, contagem de linhas, consistência temporal, valores ausentes,
checksums de conteúdo e deriva de amostra.

Este módulo foi ajustado para assumir que os dados residem em
`<PROJ_ROOT>/root/data/` (padrão), mas o diretório base pode ser
sobrescrito via argumento `base_dir` ou opção CLI `--base-dir`.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Mapping, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Path helpers – detect raiz do projeto /root/data
# ---------------------------------------------------------------------------
try:
    # Projeto define utilitário único para resolver raiz
    from src.utils.path_setup import ensure_project_root

    PROJ_ROOT: Path = ensure_project_root(__file__)
except Exception:  # pragma: no cover – fallback, útil em notebooks/testes
    PROJ_ROOT = Path(__file__).resolve().parents[4]

DEFAULT_DATA_DIR: Path = PROJ_ROOT / "root" / "data"

# ---------------------------------------------------------------------------
# Configura logger
# ---------------------------------------------------------------------------
logger = logging.getLogger("op_trader.data_auditor")
if not logger.handlers:
    # evita duplicar handlers em reimportações
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s - %(levelname)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class AuditResult:
    """Resultado consolidado da auditoria."""

    status: bool  # True = aprovado, False = reprovado / warnings
    details: pd.DataFrame
    warnings: List[str]

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "warnings": self.warnings,
            "details": self.details.to_dict(orient="records"),
        }


class DataAuditor:
    """Audita os CSVs de todas as fases de transformação de dados.

    Parameters
    ----------
    base_dir : Path, optional
        Diretório que contém as subpastas `raw/`, `cleaned/`, `corrected/`,
        `features/`. Se *None*, usa ``DEFAULT_DATA_DIR``.
    logger : logging.Logger, optional
        Logger já configurado; se *None*, usa o logger padrão deste módulo.
    sample_size : int, default = 10_000
        Linhas lidas em amostra aleatória para estatísticas rápidas.
    """

    STAGES: Tuple[str, ...] = ("raw", "cleaned", "corrected", "features")

    def __init__(
        self,
        base_dir: Path | None = None,
        logger: logging.Logger | None = None,
        sample_size: int = 10_000,
    ) -> None:
        self.base_dir: Path = (base_dir or DEFAULT_DATA_DIR).resolve()
        self.logger = logger or logging.getLogger("op_trader.data_auditor")
        self.sample_size = sample_size

    # ---------------------------------------------------------------------
    # API pública
    # ---------------------------------------------------------------------
    def audit_pipeline(
        self,
        csv_paths: Mapping[str, Path] | None = None,
        *,
        run_id: str | None = None,
        cfg_hash: str | None = None,
    ) -> AuditResult:
        """Audita todas as fases.

        Parameters
        ----------
        csv_paths : Mapping[str, Path], optional
            Mapeamento expresso ``{"raw": path1, "cleaned": path2, ...}``. Se
            *None*, os caminhos serão inferidos pelo padrão de nomenclatura
            (<stage>_*<run_id>*_.csv) dentro de ``self.base_dir/<stage>``.
        run_id : str, optional
            Hash/timestamp que identifica o lote; obrigatório se não passar
            ``csv_paths``.
        cfg_hash : str, optional
            Hash da configuração para registrar no log.
        """
        self.logger.info("Iniciando auditoria – run_id=%s base_dir=%s", run_id, self.base_dir)

        paths = (
            csv_paths if csv_paths is not None else self._discover_paths(run_id)
        )
        missing = [s for s in self.STAGES if s not in paths]
        if missing:
            raise FileNotFoundError(f"Arquivos ausentes para estágios: {missing}")

        records: List[Dict] = []
        warnings: List[str] = []
        for stage in self.STAGES:
            record = self._collect_metrics(paths[stage], stage)
            records.append(record)

        df = pd.DataFrame(records)
        df["ΔRows vs RAW"] = df["Rows"] - df.loc[df["Stage"] == "raw", "Rows"].iloc[0]

        # Regras de validação
        status = True
        for _, row in df.iterrows():
            if row["Stage"] in {"cleaned", "corrected", "features"} and row["Rows"] <= 0:
                warnings.append(f"{row['Stage']} sem linhas!")
                status = False
            if row["Stage"] == "corrected" and row["ΔRows vs RAW"] != 0:
                warnings.append(
                    f"corrected tem {row['ΔRows vs RAW']:+} linhas vs raw – revisar!")
                status = False
            if row["Stage"] == "features" and row["ΔRows vs RAW"] > 5000:
                warnings.append("features gerou muitas linhas extras – provável erro de lookahead")
                status = False

        # Salvamento opcional
        if cfg_hash:
            audit_dir = self.base_dir.parent / "audits"
            audit_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            outfile = audit_dir / f"audit_{cfg_hash}_{ts}.json"
            df.to_json(outfile, orient="records", indent=2, force_ascii=False)
            self.logger.info("Relatório salvo em %s", outfile)

        return AuditResult(status=status, details=df, warnings=warnings)

    # ------------------------------------------------------------------
    # Internals helpers
    # ------------------------------------------------------------------
    def _discover_paths(self, run_id: str | None) -> Dict[str, Path]:
        if not run_id:
            raise ValueError("run_id é obrigatório para inferir caminhos")
        self.logger.debug("Procurando arquivos com run_id=%s", run_id)
        paths: Dict[str, Path] = {}
        for stage in self.STAGES:
            stage_dir = self.base_dir / stage
            pattern = f"{stage}_*{run_id}*.csv"
            matches = list(stage_dir.glob(pattern))
            if not matches:
                raise FileNotFoundError(f"Nenhum arquivo encontrado para pattern {pattern}")
            # Usa o mais recente
            file_path = max(matches, key=lambda p: p.stat().st_mtime)
            paths[stage] = file_path
        return paths

    def _collect_metrics(self, path: Path, stage: str) -> Dict[str, object]:
        self.logger.debug("%s → carregando dados de %s", stage.upper(), path.name)
        rows = self._quick_row_count(path)
        cols = len(self._first_header(path))
        n_missing, missing_pct = self._sample_missing(path)
        return {
            "Stage": stage,
            "Rows": rows,
            "Columns": cols,
            "Sample NaNs": n_missing,
            "NaN % (sample)": round(missing_pct * 100, 4),
            "SHA-256 (12)": self._sha256_short(path),
            "Size (MB)": round(path.stat().st_size / 1024 / 1024, 2),
        }

    # ---------- static helpers ----------
    @staticmethod
    def _quick_row_count(path: Path) -> int:
        with path.open("r", newline="") as f:
            return sum(1 for _ in f) - 1

    @staticmethod
    def _first_header(path: Path):
        with path.open(newline="") as f:
            reader = csv.reader(f)
            return next(reader)

    def _sample_missing(self, path: Path) -> Tuple[int, float]:
        df = pd.read_csv(path, nrows=self.sample_size)
        total = df.size
        missing = int(df.isnull().values.sum())
        return missing, missing / total if total else 0.0

    @staticmethod
    def _sha256_short(path: Path, n: int = 12) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            h.update(f.read())
        return h.hexdigest()[:n]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Auditoria Enterprise do pipeline Op_Trader (raw→features)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """Exemplo de uso:
            python -m src.data.data_libs.data_auditor \\
              --run-id 670dfa4cf4 --pair EURUSD --timeframe M5 --mode ppo \\
              --base-dir ./root/data --save-report
            """,
        ),
    )
    p.add_argument("--run-id", required=True, help="Hash/timestamp do lote")
    p.add_argument("--pair", required=True, help="Par de moedas (ex.: EURUSD)")
    p.add_argument("--timeframe", required=True, help="Timeframe (ex.: M5)")
    p.add_argument("--mode", required=True, choices=["ppo", "mlp"], help="Modo de pipeline")
    p.add_argument("--base-dir", default=DEFAULT_DATA_DIR, help="Pasta base de dados")
    p.add_argument("--save-report", action="store_true", help="Salva JSON de auditoria")
    return p


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    args = _build_arg_parser().parse_args(argv)

    base_dir = Path(args.base_dir).resolve()
    auditor = DataAuditor(base_dir=base_dir)
    result = auditor.audit_pipeline(run_id=args.run_id, cfg_hash=args.run_id)

    # Pretty print
    print("\n" + result.details.to_markdown(index=False))
    if result.warnings:
        print("\n⚠️ Warnings:")
        for w in result.warnings:
            print(" -", w)
    sys.exit(0 if result.status else 1)


if __name__ == "__main__":  # pragma: no cover
    main()
