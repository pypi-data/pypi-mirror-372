__all__ = ["ema"]

from lt_tensor.common import *
from lt_utils.common import *
from copy import deepcopy
import math


class EMA:
    @property
    def device(self):
        return self.ema_model.device

    def cuda(self):
        self.ema_model.cuda()
        return self

    def cpu(self):
        self.ema_model.cpu()
        return self

    def xpu(self):
        self.ema_model.xpu()
        return self

    def __init__(
        self,
        model: Model,
        beta=0.999,
        update_buffers=True,
        scheduler=None,
        total_steps=None,
    ):
        """
        Exponential Moving Average with optional scheduler.

        Args:
            model (Model): model to track.
            beta (float): base decay factor (used if scheduler=None).
            update_buffers (bool): whether to track buffers (BN stats etc).
            scheduler (callable): function(step, total_steps) -> beta
            total_steps (int): total planned steps (for schedulers).
        """
        self.beta = beta
        self.update_buffers = update_buffers
        self.scheduler = scheduler
        self.total_steps = total_steps
        self.global_step = 0

        self.model = model
        self.ema_model: Model = deepcopy(model).eval()

        for p in self.ema_model.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def update(self):
        """Update EMA weights with current model weights."""
        self.global_step += 1

        if self.scheduler is not None and self.total_steps is not None:
            beta = self.scheduler(self.global_step, self.total_steps)
        else:
            beta = self.beta

        msd = self.model.state_dict()
        for k, v in self.ema_model.state_dict().items():
            if k in msd:
                if torch.is_floating_point(msd[k]):
                    v.copy_(v * beta + msd[k] * (1.0 - beta))
                else:
                    if self.update_buffers:
                        v.copy_(msd[k])

    def state_dict(self):
        return self.ema_model.state_dict()

    def load_state_dict(self, state_dict):
        self.ema_model.load_state_dict(state_dict)

    def to(self, device):
        self.ema_model.to(device)
        return self

    def __call__(self, *args, **kwargs):
        return self.ema_model(*args, **kwargs)

    def inference(self, *args, **kwargs):
        return self.ema_model.inference(*args, **kwargs)

    def train_step(self, *args, **kwargs):
        return self.ema_model.train_step(*args, **kwargs)

    def print_trainable_parameters(self):
        return self.model.print_trainable_parameters()

    def save_weights(self, path: Path | str, replace: bool = False):
        self.ema_model.save_weights(path, replace)

    def load_weights(
        self,
        path: Union[Path, str],
        raise_if_not_exists: bool = False,
        strict: bool = False,
        assign: bool = False,
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        **pickle_load_args,
    ):
        return self.ema_model.load_weights(
            path=path,
            raise_if_not_exists=raise_if_not_exists,
            strict=strict,
            assign=assign,
            weights_only=weights_only,
            mmap=mmap,
            **pickle_load_args,
        )


def cosine_beta_schedule(step, total_steps, beta_min=0.999, beta_max=0.9999):
    p = step / total_steps
    c = 0.5 * (1 + math.cos(math.pi * p))
    return beta_max - (beta_max - beta_min) * c


def gamma_beta_schedule(
    step, total_steps=None, beta_min=0.999, beta_max=0.9999, gamma=0.99995
):
    return beta_min + (beta_max - beta_min) * (1 - (gamma**step))


def hybrid_beta_schedule(
    step,
    total_steps,
    warmup_steps=30_000,
    beta_min=0.999,
    beta_mid=0.9995,
    beta_max=0.9999,
    gamma=0.99995,
):
    if step < warmup_steps:
        p = step / warmup_steps
        c = 0.5 * (1 + math.cos(math.pi * (1 - p)))
        return beta_min + (beta_mid - beta_min) * c
    adj = step - warmup_steps
    return beta_mid + (beta_max - beta_mid) * (1 - gamma**adj)


def cyclical_beta_schedule(
    step,
    total_steps=None,
    beta_min=0.998,
    beta_max=0.9999,
    cycle_length=10_000,
    mode="cosine",
):
    sc = (step % cycle_length) / cycle_length
    if mode == "triangular":
        scale = sc * 2 if sc <= 0.5 else 2 - 2 * sc
    else:  # cosine
        scale = 0.5 * (1 - math.cos(2 * math.pi * sc))
    return beta_min + (beta_max - beta_min) * scale


def wavering_beta_schedule(
    step,
    total_steps,
    beta_center=0.9995,
    beta_amp=0.0003,
    wave_period=20_000,
    drift=1e-7,
):
    wave = math.cos(2 * math.pi * (step / wave_period))
    beta = beta_center + beta_amp * wave + drift * step
    return max(0.0, min(0.99999, beta))
