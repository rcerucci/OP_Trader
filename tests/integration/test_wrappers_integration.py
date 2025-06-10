import numpy as np
import logging
import pytest
from src.env.wrappers.action_wrapper import ActionWrapper
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.wrappers.reward_wrapper import RewardWrapper
from src.env.wrappers.normalization_wrapper import NormalizationWrapper
from src.env.wrappers.observation_wrapper import ObservationWrapper

class DummyEnv:
    """
    Ambiente RL minimalista compatível com todos os wrappers Op_Trader.
    """
    def __init__(self):
        self.action_space = type(
            'Space', (), {
                'dtype': np.float32,
                'shape': (2,),
                'contains': lambda self, x: np.all(np.abs(x) <= 1)
            })()
        self.observation_space = type(
            'Obs', (), {'shape': (2,)})()
        self.episode_steps = 0
        self.done = False
        self.last_action = None

    def reset(self, **kwargs):
        self.episode_steps = 0
        self.done = False
        return np.zeros((2,), dtype=np.float32), {"reset": True}

    def step(self, action):
        self.last_action = action
        self.episode_steps += 1
        # Observation "crua" para o wrapper de observação/normalização
        obs = np.array([self.episode_steps, -self.episode_steps], dtype=np.float32)
        reward = float(np.clip(action[0] + action[1], -1, 1))
        terminated = self.episode_steps >= 3
        truncated = False
        info = {"step": self.episode_steps}
        return obs, reward, terminated, truncated, info

    def close(self):
        pass

@pytest.fixture
def integration_logger():
    logger = logging.getLogger("FullIntegrationLogger")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(h)
    logger.propagate = True
    return logger

def test_all_wrappers_full_integration(tmp_path, integration_logger):
    env = DummyEnv()

    # Funções customizadas
    def clip_action(a): return np.clip(a, -1, 1)
    def double_reward(r): return 2 * r
    def obs_transform(obs): return obs / 10.0  # Exemplo de transformação de observação

    # Empilha todos wrappers: Logging <- Reward <- Observation <- Normalization <- Action <- DummyEnv
    wrapped = LoggingWrapper(
        RewardWrapper(
            ObservationWrapper(
                NormalizationWrapper(
                    ActionWrapper(
                        env,
                        action_fn=clip_action,
                        logger=integration_logger,
                        log_dir=str(tmp_path)
                    ),
                    logger=integration_logger
                ),
                obs_fn=obs_transform,
                logger=integration_logger
            ),
            reward_fn=double_reward,
            logger=integration_logger,
            log_dir=str(tmp_path),
        ),
        logger=integration_logger,
        log_level="DEBUG",
        log_dir=str(tmp_path),
    )

    obs, info = wrapped.reset()
    done = False
    total_reward = 0
    steps = 0
    all_observations = []
    while not done:
        action = np.array([2.0, -2.0])  # Será clipado para [1.0, -1.0]
        obs, reward, terminated, truncated, info = wrapped.step(action)
        all_observations.append(obs)
        total_reward += reward
        steps += 1
        done = terminated or truncated

    assert steps == 3
    logs = wrapped.get_logs()
    assert isinstance(logs, dict) or isinstance(logs, list)
    wrapped.save_logs()
    import os
    saved_logs = [f for f in os.listdir(tmp_path) if f.endswith(".csv") or f.endswith(".json")]
    assert saved_logs, "Nenhum arquivo de log salvo pelos wrappers!"

    # Checagens dos wrappers
    # - Observações normalizadas
    for o in all_observations:
        assert np.all(np.abs(o) <= 1), "Observação não normalizada pelo pipeline!"
    # - Reward transformada
    assert np.isclose(total_reward, 0.0)
    wrapped.close()
